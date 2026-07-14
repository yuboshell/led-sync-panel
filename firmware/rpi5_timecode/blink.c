// Stage 1 — blink one LED on GPIO 18 to validate the Pi 5 → breadboard connection.
//
// Equivalent of firmware/blink/main.c (Pico H), ported to Linux sysfs GPIO.
// Circuit: Pi 5 Pin 12 (GPIO 18) → 240 Ω → LED long leg(+); LED short leg(−) → GND.
//
// Build:  gcc -Wall -O2 -o blink blink.c
// Run:    ./blink          (Ctrl+C to stop)

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <time.h>

#define GPIO_PIN  "18"
#define GPIO_PATH "/sys/class/gpio"

static volatile int running = 1;

static void sigint_handler(int sig) {
    (void)sig;
    running = 0;
}

// Write a string to a sysfs file.
static int sysfs_write(const char *path, const char *value) {
    int fd = open(path, O_WRONLY);
    if (fd < 0) { perror(path); return -1; }
    if (write(fd, value, strlen(value)) < 0) { perror(path); close(fd); return -1; }
    close(fd);
    return 0;
}

// Export the GPIO pin via sysfs (if not already exported).
static int gpio_export(void) {
    if (access(GPIO_PATH "/gpio" GPIO_PIN, F_OK) == 0)
        return 0;  // already exported
    return sysfs_write(GPIO_PATH "/export", GPIO_PIN);
}

// Unexport the GPIO pin.
static void gpio_unexport(void) {
    sysfs_write(GPIO_PATH "/unexport", GPIO_PIN);
}

// Set direction to "out".
static int gpio_set_output(void) {
    return sysfs_write(GPIO_PATH "/gpio" GPIO_PIN "/direction", "out");
}

// Set the pin value ("0" or "1").
static int gpio_set(const char *val) {
    return sysfs_write(GPIO_PATH "/gpio" GPIO_PIN "/value", val);
}

static void sleep_ms(int ms) {
    struct timespec ts = { .tv_sec = ms / 1000, .tv_nsec = (ms % 1000) * 1000000L };
    nanosleep(&ts, NULL);
}

int main(void) {
    signal(SIGINT, sigint_handler);

    if (gpio_export() < 0) {
        fprintf(stderr, "Failed to export GPIO %s.\n"
                        "Try: sudo usermod -a -G gpio $USER  (then reboot)\n"
                        "Or run with sudo.\n", GPIO_PIN);
        return 1;
    }

    // Small delay for sysfs to create the direction file
    usleep(100000);

    if (gpio_set_output() < 0) {
        fprintf(stderr, "Failed to set GPIO %s as output.\n", GPIO_PIN);
        gpio_unexport();
        return 1;
    }

    printf("Blinking LED on GPIO %s (Pin 12). Press Ctrl+C to stop.\n", GPIO_PIN);

    while (running) {
        gpio_set("1");
        sleep_ms(250);
        gpio_set("0");
        sleep_ms(250);
    }

    // Cleanup: turn off LED and unexport
    gpio_set("0");
    gpio_unexport();
    printf("\nStopped. GPIO %s unexported.\n", GPIO_PIN);
    return 0;
}
