# Step 0 — simplest blink

The minimal circuit: **Pico GP15 → 240 Ω → LED → one jumper → GND.** If this blinks,
the Pico, the C/C++ toolchain, and your breadboard wiring all work — before the 595 panel.

## Circuit
- **240 Ω resistor:** `Lb20` (GP15's row) → `Lb23`
- **LED:** long leg (+) `Lc23` → short leg (−) `Lc25`
- **jumper:** `La25` (cathode row) → `La18` (a Pico GND pin's row)

GP15 = pin 20; GND = pin 18 (or any GND pin). 240 Ω gives ~4–5 mA, within the GPIO's default drive.

## Build (CLI, macOS)
```bash
brew install cmake picotool && brew install --cask gcc-arm-embedded
git clone -b master https://github.com/raspberrypi/pico-sdk.git
( cd pico-sdk && git submodule update --init )
cp pico-sdk/external/pico_sdk_import.cmake .          # into this firmware/blink/ dir
mkdir build && cd build
export PICO_SDK_PATH=../../../pico-sdk
cmake .. && make                                     # -> blink.uf2
```

## Flash
```bash
# hold BOOTSEL while plugging in the USB cable, then:
picotool load blink.uf2 && picotool reboot
# the LED blinks twice a second
```
