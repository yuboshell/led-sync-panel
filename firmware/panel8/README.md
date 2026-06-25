# Step 1 — 8-LED panel bring-up (74HC595)

Clocks a test pattern out to one 74HC595 over SPI and shows it on 8 LEDs — proving the
**data → shift → latch → LED** chain before scaling to the full panel.

## Wiring (Figure 1, 595 mounted **notch-DOWN**)
| Pico | → | 595 |
|---|---|---|
| GP18 | → | SRCLK (pin 11) — shift clock (SPI0 SCK) |
| GP19 | → | SER (pin 14) — serial data (SPI0 TX) |
| GP17 | → | RCLK (pin 12) — latch (plain GPIO) |

Plus: **VCC(16)→3V3, GND(8)→GND, OE(13)→GND** (outputs on), **MR(10)→3V3** (no reset);
each **QA..QH → 240 Ω → LED → GND**.

## What it does
- **Walking dot** — one LED steps down the comb, 3 passes (~3 Hz).
- **Binary counter** 0–255 — every output and combination (~8 Hz).

MSB-first SPI maps bit7→QH … bit0→QA. The latch (RCLK) is what makes all eight
outputs change at the same instant — no PWM.

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
