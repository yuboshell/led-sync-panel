# Raspberry Pi 5 — LED Sync Panel Firmware

Port of the Pico H firmware (`../blink`, `../panel8`, `../timecode`) to run
natively on a **Raspberry Pi 5** under Linux. Same 74HC595 shift register,
same 7 LEDs, same Gray-coded time code — different board.

## Physical Setup

👉 **Read [SETUP_GUIDE.md](SETUP_GUIDE.md) first** — it has the complete
pin-by-pin wiring instructions with diagrams for each stage.

## Prerequisites (on the Pi 5)

```bash
# 1. Install the C compiler
sudo apt-get update && sudo apt-get install -y build-essential

# 2. Enable SPI
sudo raspi-config nonint do_spi 0
sudo reboot

# 3. Verify SPI is active
ls /dev/spidev0.*          # should show spidev0.0 and spidev0.1
```

## Build

```bash
cd firmware/rpi5_timecode
make                       # builds both: ./blink and ./timecode
```

## Run

### Stage 1 — Blink (single LED on GPIO 18)
```bash
./blink                    # blinks at ~2 Hz (250 ms on/off)
                           # Ctrl+C to stop
```

### Stage 2 — Panel8 test (74HC595 + 7 LEDs)
```bash
./timecode --panel8        # walking dot + binary counter at visible speed
                           # Ctrl+C to stop
```

### Stage 3 — Time Code (production)
```bash
# Slow demo — one LED changes per step, visible by eye:
./timecode --step-us=500000

# Production — 500 µs/step (2000 steps/s), verify with camera:
./timecode
```

### All options
```
./timecode --help

Usage: ./timecode [OPTIONS]

Modes:
  --timecode       7-bit Gray time code (default)
  --panel8         walking-dot + binary-counter test pattern

Options:
  --step-us=N      step period in microseconds (default: 500)
                   use 500000 for a slow demo (0.5 s/step)
  --help           show this help
```

## How It Works

The Pico used the RP2040's hardware SPI + a manual GPIO latch pin.
On the Pi 5 we use the Linux `spidev` driver:

1. Open `/dev/spidev0.0` (SPI0, chip-enable 0)
2. Configure: 1 MHz, SPI Mode 0, MSB-first, 8-bit
3. Each `ioctl(SPI_IOC_MESSAGE)` shifts 8 bits into the 595 and auto-toggles
   CE0 (connected to RCLK) — the rising edge latches all outputs at once

The timing loop uses `clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, ...)`
for drift-free stepping, same principle as the Pico's `sleep_until()`.

## Decode

Same as the Pico — point a camera at the LEDs, then:
```bash
cd ../../decode
pip install -r requirements.txt
python decode_video.py <video_file>
```
