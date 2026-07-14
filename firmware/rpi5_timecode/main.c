// Raspberry Pi 5 — LED sync panel driver (SPI → 74HC595 → 7 LEDs)
//
// Two modes, selectable at runtime:
//
//   ./timecode --panel8           Stage 2: walking-dot + binary-counter test
//   ./timecode                    Stage 3: 7-bit Gray time code (default)
//   ./timecode --step-us=500000   Stage 3 slow demo (0.5 s/step, one LED flips per step)
//
// This is the Raspberry Pi 5 (Linux) port of the Pico H firmware in:
//   ../panel8/main.c   (walking dot + binary counter)
//   ../timecode/main.c (Gray-coded time code)
//
// Wiring (see SETUP_GUIDE.md):
//   Pi 5 Pin 19 (GPIO10/MOSI)  → 595 SER   (pin 14)  — serial data
//   Pi 5 Pin 23 (GPIO11/SCLK)  → 595 SRCLK (pin 11)  — shift clock
//   Pi 5 Pin 24 (GPIO8/CE0)    → 595 RCLK  (pin 12)  — latch (auto from SPI CS)
//   VCC(16)→3V3  GND(8)→GND  OE(13)→GND  MR(10)→3V3
//   QB..QH → 240 Ω → LED → GND  (7 LEDs; QA unused)
//
// The key trick: Linux's SPI driver pulls CE0 LOW before the transfer and HIGH
// after. The rising edge on RCLK latches all 8 outputs at once — no extra GPIO
// toggle needed. This replaces the Pico's manual gpio_put(LATCH, 1/0) dance.
//
// Decode (per camera frame, same as Pico):
//   read QB..QH as 7-bit g        (QB = bit0 ... QH = bit6)
//   ungray: b=g; b^=b>>1; b^=b>>2; b^=b>>4  → count
//   t ≈ count × τ                 (modulo the 128·τ wrap)

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <linux/types.h>
#include <linux/spi/spidev.h>
#include <time.h>
#include <getopt.h>

#define SPI_DEVICE  "/dev/spidev0.0"
#define SPI_SPEED   1000000          // 1 MHz — matches the Pico
#define NSTEPS      128              // 7-bit count 0..127
#define DEFAULT_STEP_US 500          // default τ = 0.5 ms (2000 steps/s)

static volatile int running = 1;
static int spi_fd = -1;

static void sigint_handler(int sig) {
    (void)sig;
    running = 0;
}

// ---------- SPI helpers ----------

static int spi_open(void) {
    int fd = open(SPI_DEVICE, O_RDWR);
    if (fd < 0) { perror("open " SPI_DEVICE); return -1; }

    uint32_t mode  = SPI_MODE_0;
    uint8_t  bits  = 8;
    uint32_t speed = SPI_SPEED;

    if (ioctl(fd, SPI_IOC_WR_MODE32,       &mode)  < 0) { perror("SPI mode");  close(fd); return -1; }
    if (ioctl(fd, SPI_IOC_WR_BITS_PER_WORD, &bits)  < 0) { perror("SPI bits");  close(fd); return -1; }
    if (ioctl(fd, SPI_IOC_WR_MAX_SPEED_HZ,  &speed) < 0) { perror("SPI speed"); close(fd); return -1; }

    return fd;
}

// Send one byte to the 595 via SPI.  CE0 rising edge auto-latches RCLK.
static void put595(uint8_t byte) {
    struct spi_ioc_transfer tr = {
        .tx_buf        = (unsigned long)&byte,
        .rx_buf        = 0,
        .len           = 1,
        .delay_usecs   = 0,
        .speed_hz      = SPI_SPEED,
        .bits_per_word = 8,
    };
    if (ioctl(spi_fd, SPI_IOC_MESSAGE(1), &tr) < 0)
        perror("SPI transfer");
}

// ---------- Timing helpers ----------

static void sleep_ms(int ms) {
    struct timespec ts = { .tv_sec = ms / 1000, .tv_nsec = (ms % 1000) * 1000000L };
    nanosleep(&ts, NULL);
}

// Advance a timespec by `us` microseconds (handles overflow into seconds).
static void timespec_add_us(struct timespec *ts, long us) {
    ts->tv_nsec += us * 1000L;
    while (ts->tv_nsec >= 1000000000L) {
        ts->tv_sec  += 1;
        ts->tv_nsec -= 1000000000L;
    }
}

// ---------- Mode: panel8 (walking dot + binary counter) ----------

// MSB-first SPI maps bit7→QH … bit1→QB (bit0→QA, unused).
// Walking dot: one lit LED at a time, QB first.
static const uint8_t SWEEP[7] = {0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80};

static void run_panel8(void) {
    printf("Running panel8 test pattern. Press Ctrl+C to stop.\n");
    while (running) {
        // Walking dot — 3 passes
        for (int pass = 0; pass < 3 && running; pass++)
            for (int i = 0; i < 7 && running; i++) {
                put595(SWEEP[i]);
                sleep_ms(300);
            }
        // Binary counter on QB..QH — n<<1 keeps QA off
        for (int n = 0; n < 128 && running; n++) {
            put595((uint8_t)(n << 1));
            sleep_ms(120);
        }
    }
}

// ---------- Mode: timecode (7-bit Gray counter) ----------

static void run_timecode(long step_us) {
    printf("Running timecode (step = %ld µs, period = %ld µs). Press Ctrl+C to stop.\n",
           step_us, (long)NSTEPS * step_us);

    uint32_t count = 0;
    struct timespec next;
    clock_gettime(CLOCK_MONOTONIC, &next);

    while (running) {
        uint8_t gray = (uint8_t)(count ^ (count >> 1));  // 7-bit Gray of count
        put595((uint8_t)(gray << 1));                     // gray → QB..QH; QA=0

        count = (count + 1) % NSTEPS;

        // Drift-free: sleep until absolute τ boundary
        timespec_add_us(&next, step_us);
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
    }
}

// ---------- Main ----------

static void usage(const char *prog) {
    fprintf(stderr,
        "Usage: %s [OPTIONS]\n"
        "\n"
        "Modes:\n"
        "  --timecode       7-bit Gray time code (default)\n"
        "  --panel8         walking-dot + binary-counter test pattern\n"
        "\n"
        "Options:\n"
        "  --step-us=N      step period in microseconds (default: %d)\n"
        "                   use 500000 for a slow demo (0.5 s/step)\n"
        "  --help           show this help\n",
        prog, DEFAULT_STEP_US);
}

int main(int argc, char *argv[]) {
    int mode_panel8  = 0;
    long step_us     = DEFAULT_STEP_US;

    static struct option long_opts[] = {
        {"timecode", no_argument,       NULL, 't'},
        {"panel8",   no_argument,       NULL, 'p'},
        {"step-us",  required_argument, NULL, 's'},
        {"help",     no_argument,       NULL, 'h'},
        {NULL, 0, NULL, 0}
    };

    int opt;
    while ((opt = getopt_long(argc, argv, "tps:h", long_opts, NULL)) != -1) {
        switch (opt) {
            case 't': mode_panel8 = 0; break;
            case 'p': mode_panel8 = 1; break;
            case 's': step_us = atol(optarg); break;
            case 'h': usage(argv[0]); return 0;
            default:  usage(argv[0]); return 1;
        }
    }

    signal(SIGINT, sigint_handler);

    spi_fd = spi_open();
    if (spi_fd < 0) {
        fprintf(stderr,
            "Cannot open %s.\n"
            "Is SPI enabled?  sudo raspi-config nonint do_spi 0 && sudo reboot\n"
            "Permission?      sudo usermod -a -G spi $USER  (then reboot)\n",
            SPI_DEVICE);
        return 1;
    }

    if (mode_panel8)
        run_panel8();
    else
        run_timecode(step_us);

    // Cleanup: turn off all LEDs
    put595(0x00);
    close(spi_fd);
    printf("\nStopped. All LEDs off.\n");
    return 0;
}
