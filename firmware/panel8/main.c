// 8-LED bring-up — clock a test pattern out to a 74HC595 over SPI, latch on GP17.
//
// Wiring (matches Figure 1, with the 595 mounted notch-DOWN):
//   GP18 -> SRCLK (pin 11)   shift clock   (SPI0 SCK)
//   GP19 -> SER   (pin 14)   serial data   (SPI0 TX)
//   GP17 -> RCLK  (pin 12)   latch         (plain GPIO, pulsed by hand)
//   VCC(16)->3V3   GND(8)->GND   OE(13)->GND (outputs on)   MR(10)->3V3 (no reset)
//   each QA..QH -> 240 ohm -> LED -> GND
#include "pico/stdlib.h"
#include "hardware/spi.h"

#define LATCH 17        // GP17 -> RCLK
#define SCK   18        // GP18 -> SRCLK (SPI0 SCK)
#define TX    19        // GP19 -> SER   (SPI0 TX)

// MSB-first SPI maps bit7->QH ... bit0->QA. With the 595 mounted notch-DOWN the
// LEDs read top->bottom as QA,QH,QG,QF,QE,QD,QC,QB, so this table walks one lit
// LED cleanly down the comb.
static const uint8_t SWEEP[8] = {0x01, 0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02};

static void put595(uint8_t bits) {
    spi_write_blocking(spi0, &bits, 1);   // SDK blocks until all 8 bits are shifted out
    gpio_put(LATCH, 1); sleep_us(1);      // rising edge of RCLK latches to the outputs
    gpio_put(LATCH, 0);
}

int main() {
    spi_init(spi0, 1000 * 1000);          // 1 MHz
    spi_set_format(spi0, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_MSB_FIRST);  // mode 0 suits the 595
    gpio_set_function(SCK, GPIO_FUNC_SPI);
    gpio_set_function(TX,  GPIO_FUNC_SPI);
    gpio_init(LATCH); gpio_set_dir(LATCH, GPIO_OUT); gpio_put(LATCH, 0);

    while (true) {
        // 1) walking dot — one LED at a time down the comb, 3 passes (~3 Hz)
        for (int pass = 0; pass < 3; pass++)
            for (int i = 0; i < 8; i++) { put595(SWEEP[i]); sleep_ms(300); }
        // 2) binary counter 0..255 — exercises every output + combination (~8 Hz)
        for (int n = 0; n < 256; n++) { put595((uint8_t)n); sleep_ms(120); }
    }
}
