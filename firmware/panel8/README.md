# Step 1 — 7-LED panel bring-up (74HC595)

Clocks a test pattern out to one 74HC595 over SPI and shows it on 7 LEDs — proving the
**data → shift → latch → LED** chain before scaling to the full panel.

## Wiring (Option C breadboard diagram; 595 mounted **notch-UP**)
| Pico | → | 595 |
|---|---|---|
| GP18 | → | SRCLK (pin 11) — shift clock (SPI0 SCK) |
| GP19 | → | SER (pin 14) — serial data (SPI0 TX) |
| GP17 | → | RCLK (pin 12) — latch (plain GPIO) |

Plus: **VCC(16)→3V3, GND(8)→GND, OE(13)→GND** (outputs on), **MR(10)→3V3** (no reset),
and a **0.1 µF cap across VCC↔GND**. Outputs: **QB..QH → 240 Ω → LED → GND** (7 LEDs).
**QA (pin 15) is left unused** — it's the lone output on the chip's far side, and seven
LEDs prove the chain just as well. (For more LEDs later, chain a second 595: QH′ → next SER.)

## What it does
- **Walking dot** — one LED steps down the comb (QB→QH), 3 passes (~3 Hz).
- **Binary counter on QB–QH** — `n<<1` keeps QA off; exercises all 128 combinations (~8 Hz).

MSB-first SPI maps bit7→QH … bit1→QB (bit0→QA, unused). The latch (RCLK) is what makes
all the outputs change at the same instant — no PWM.

## Build & flash
Same toolchain as `../blink` (xpack arm-none-eabi-gcc + pico-sdk — see `../blink/README.md`):
```bash
export PATH="$(echo ~/pico/toolchain/xpack-arm-none-eabi-gcc-*/bin):$PATH"
export PICO_SDK_PATH=~/pico-sdk
cp "$PICO_SDK_PATH/external/pico_sdk_import.cmake" .
mkdir build && cd build && cmake .. && make        # -> panel8.uf2
# hold BOOTSEL while plugging in USB (RPI-RP2 appears), then:
picotool load -x build/panel8.uf2
```
