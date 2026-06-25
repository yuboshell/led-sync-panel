# Step 0 — simplest blink

The minimal circuit: **Pico GP15 → 240 Ω → LED → one jumper → GND.** If this blinks,
the Pico, the C/C++ toolchain, and your breadboard wiring all work — before the 595 panel.
**Flashed + verified working 2026-06-24.**

## Circuit
- **240 Ω resistor:** `Lb20` (GP15's row) → `Lb23`
- **LED:** long leg (+) `Lc23` → short leg (−) `Lc25`
- **jumper:** `La25` (cathode row) → `La18` (a Pico GND pin's row)

GP15 = pin 20; GND = pin 18 (or any GND pin). 240 Ω gives ~4–5 mA, within the GPIO's default drive.

## Build (CLI, macOS — verified 2026-06-24, Apple Silicon)
```bash
brew install cmake picotool
# NOTE: brew's `arm-none-eabi-gcc` ships NO newlib (link fails), and the `gcc-arm-embedded`
# cask is broken in current Homebrew — so use the complete, self-contained xpack toolchain:
mkdir -p ~/pico/toolchain
URL=$(curl -fsSL https://api.github.com/repos/xpack-dev-tools/arm-none-eabi-gcc-xpack/releases/latest \
      | grep -oE 'https://[^"]*darwin-arm64\.tar\.gz' | head -1)
curl -fL "$URL" | tar -xz -C ~/pico/toolchain
export PATH="$(echo ~/pico/toolchain/xpack-arm-none-eabi-gcc-*/bin):$PATH"

git clone -b master https://github.com/raspberrypi/pico-sdk.git ~/pico-sdk
export PICO_SDK_PATH=~/pico-sdk

cp "$PICO_SDK_PATH/external/pico_sdk_import.cmake" .
mkdir build && cd build && cmake .. && make          # -> blink.uf2
```

## Flash
```bash
# Use a DATA micro-USB cable (charge-only cables won't enumerate — the Mac sees nothing).
# Hold BOOTSEL while plugging in USB -> an "RPI-RP2" drive appears, then:
picotool load -x build/blink.uf2
```
macOS may warn **"Disk not ejected properly"** right after — that's expected: `-x` reboots the Pico
out of BOOTSEL to run the firmware, so it drops the RPI-RP2 drive itself. **The blinking LED = success.**
