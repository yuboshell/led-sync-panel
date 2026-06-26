// Step-1 time-code — a 7-bit GRAY-coded counter on QB-QH, advancing on a fixed step tau.
//
// This is the bring-up's plain binary counter upgraded into a real, camera-decodable
// time code. Gray coding means ONLY ONE LED changes per step (including the 127->0 wrap),
// so a camera frame whose exposure straddles a tick decodes to within +/-1 of the true
// count -- never to a garbage multi-bit value (which plain binary risks when several LEDs
// flip at once). The latch keeps the BOARD clean; Gray handles the CAMERA straddle.
// Deferred to later steps (see the archived full-panel design): sub-frame resolution via
// a coarse vernier row, and scaling past 7 LEDs.
//
// Wiring is identical to the bring-up (Option C, 595 notch-UP) -- no rewiring, just reflash:
//   GP18->SRCLK(11)  GP19->SER(14)  GP17->RCLK(12)
//   VCC(16)->3V3  GND(8)->GND  OE(13)->GND  MR(10)->3V3   QB..QH -> 240 ohm -> LED -> GND
//
// Decode (in software, per camera frame):
//   read QB..QH as a 7-bit value g     (QB = bit0 ... QH = bit6)
//   ungray: b=g; b^=b>>1; b^=b>>2; b^=b>>4;   -> count
//   t ~= count * tau                   (modulo the 128-step wrap = NSTEPS*tau)
#include "pico/stdlib.h"
#include "hardware/spi.h"

#define LATCH 17                 // GP17 -> RCLK
#define SCK   18                 // GP18 -> SRCLK (SPI0 SCK)
#define TX    19                 // GP19 -> SER   (SPI0 TX)

#define STEP_US 50000u           // step interval tau = 50 ms (20 steps/s). Tune vs your camera fps.
#define NSTEPS  128u             // 7-bit count 0..127; wraps every NSTEPS*tau = 6.4 s

static void put595(uint8_t bits) {
    spi_write_blocking(spi0, &bits, 1);   // MSB-first: bit7->QH ... bit1->QB, bit0->QA (unused)
    gpio_put(LATCH, 1); sleep_us(1);      // rising RCLK latches all 8 outputs at one instant
    gpio_put(LATCH, 0);
}

int main() {
    spi_init(spi0, 1000 * 1000);          // 1 MHz
    spi_set_format(spi0, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_MSB_FIRST);
    gpio_set_function(SCK, GPIO_FUNC_SPI);
    gpio_set_function(TX,  GPIO_FUNC_SPI);
    gpio_init(LATCH); gpio_set_dir(LATCH, GPIO_OUT); gpio_put(LATCH, 0);

    uint32_t count = 0;
    absolute_time_t next = get_absolute_time();
    while (true) {
        uint8_t gray = (uint8_t)(count ^ (count >> 1));   // 7-bit Gray of count
        put595((uint8_t)(gray << 1));                     // gray -> QB..QH (bit1..bit7); QA(bit0)=0
        count = (count + 1) % NSTEPS;
        next = delayed_by_us(next, STEP_US);              // drift-free: tick on absolute tau boundaries
        sleep_until(next);
    }
}
