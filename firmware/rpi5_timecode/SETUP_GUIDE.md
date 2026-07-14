# 🔧 SETUP GUIDE — Raspberry Pi 5 LED Sync Panel

Step-by-step physical wiring instructions to connect the LED sync panel
breadboard to a **Raspberry Pi 5** (replacing the Pico H).

> **Prerequisite:** You should have already run the software setup on your Pi 5:
>
> ```
> sudo apt-get update && sudo apt-get install -y build-essential
> sudo raspi-config nonint do_spi 0
> sudo reboot
> ```
>
> Verify SPI is active: `ls /dev/spidev0.*` should show `spidev0.0` and `spidev0.1`.

---

## What You Need

| # | Part                            | Qty | Notes                                           |
| - | ------------------------------- | --- | ----------------------------------------------- |
| 1 | Raspberry Pi 5 (any RAM)        | 1   | With power supply, microSD, and Raspberry Pi OS |
| 2 | Full-size breadboard (830 pts)  | 1   | Or the protoboard you already have              |
| 3 | 74HC595 shift register (DIP-16) | 1   | SN74HC595N — same chip as the Pico build       |
| 4 | Red LEDs (5 mm or 10 mm)        | 7   | Any standard through-hole LED                   |
| 5 | 240 Ω resistors (¼ W)         | 7   | One per LED (current-limiting)                  |
| 6 | 0.1 µF ceramic capacitor       | 1   | Decoupling cap across 595 VCC↔GND              |
| 7 | Male-to-female jumper wires     | ~10 | Pi 5 header (male pins) → breadboard (rows)    |
| 8 | Breadboard jumper wires         | ~10 | For on-board connections                        |

---

## Raspberry Pi 5 — GPIO Header Pinout (40-pin)

Looking at the Pi 5 with the GPIO header on the **right side**, pin 1 is
the top-left pin (nearest the board edge). Odd pins are on the left column,
even on the right.

```
                    3V3  (1) (2)  5V
                  GPIO2  (3) (4)  5V
                  GPIO3  (5) (6)  GND
                  GPIO4  (7) (8)  GPIO14
                    GND  (9) (10) GPIO15
                 GPIO17 (11) (12) GPIO18
                 GPIO27 (13) (14) GND
                 GPIO22 (15) (16) GPIO23
                    3V3 (17) (18) GPIO24
  SPI0 MOSI ►  GPIO10  (19) (20) GND
                  GPIO9 (21) (22) GPIO25
  SPI0 SCLK ►  GPIO11  (23) (24) GPIO8   ◄ SPI0 CE0
                    GND (25) (26) GPIO7
                  GPIO0 (27) (28) GPIO1
                  GPIO5 (29) (30) GND
                  GPIO6 (31) (32) GPIO12
                 GPIO13 (33) (34) GND
                 GPIO19 (35) (36) GPIO16
                 GPIO26 (37) (38) GPIO20
                    GND (39) (40) GPIO21
```

**The 3 pins we use are marked with ►:**

- **Pin 19** — GPIO 10 (SPI0 MOSI) → serial data to 595
- **Pin 23** — GPIO 11 (SPI0 SCLK) → shift clock to 595
- **Pin 24** — GPIO 8 (SPI0 CE0) → latch clock to 595

Plus **Pin 1 or 17** for 3.3V power, and **Pin 6, 14, or 20** for GND.

---

## Stage 1 — Single LED Blink (Validation)

This stage proves the Pi 5 can drive a GPIO pin to your breadboard.
**No shift register needed** — just one LED.

### Wiring

```
  Pi 5 Pin 12  (GPIO 18) ──── 240 Ω resistor ──── LED (+) long leg
                                                    LED (-) short leg ──── GND rail

  Pi 5 Pin 6   (GND)     ──── breadboard GND rail
```

### Diagram

```
  [Raspberry Pi 5]
       Pin 12 (GPIO18) ───[240Ω]───►|─── GND
       Pin 6  (GND)    ─────────────────── GND rail
```

### Test

```bash
cd firmware/rpi5_timecode
make blink
./blink           # LED should blink at ~2 Hz (250 ms on/off)
# Press Ctrl+C to stop
```

✅ **If the LED blinks, GPIO works. Move to Stage 2.**

---

## Stage 2 — 74HC595 Shift Register + 7 LEDs

### 74HC595 Pin Layout (DIP-16, notch UP)

```
           ┌──── notch ────┐
    QB  1 ─┤               ├─ 16  VCC
    QC  2 ─┤               ├─ 15  QA    (unused)
    QD  3 ─┤               ├─ 14  SER   ← data in
    QE  4 ─┤   74HC595     ├─ 13  OE    → GND (always on)
    QF  5 ─┤               ├─ 12  RCLK  ← latch
    QG  6 ─┤               ├─ 11  SRCLK ← shift clock
    QH  7 ─┤               ├─ 10  MR    → 3V3 (no reset)
   GND  8 ─┤               ├─  9  QH'   (cascade, unused)
           └───────────────┘
```

### Wiring Table

Connect these wires from the **Raspberry Pi 5 header** to the **74HC595** on the breadboard:

| Wire # | From (Pi 5)                           | To (74HC595)             | Purpose                   |
| ------ | ------------------------------------- | ------------------------ | ------------------------- |
| 1      | **Pin 19** (GPIO 10, SPI0 MOSI) | **Pin 14** (SER)   | Serial data               |
| 2      | **Pin 23** (GPIO 11, SPI0 SCLK) | **Pin 11** (SRCLK) | Shift clock               |
| 3      | **Pin 24** (GPIO 8, SPI0 CE0)   | **Pin 12** (RCLK)  | Latch (auto from SPI)     |
| 4      | **Pin 1 or 17** (3V3)           | **Pin 16** (VCC)   | 3.3V power                |
| 5      | **Pin 1 or 17** (3V3)           | **Pin 10** (MR)    | Tie HIGH (disable reset)  |
| 6      | **Pin 6** (GND)                 | **Pin 8** (GND)    | Ground                    |
| 7      | **Pin 6** (GND)                 | **Pin 13** (OE)    | Tie LOW (outputs enabled) |

> **Decoupling capacitor:** Place a **0.1 µF ceramic cap** across pins 16 (VCC) and 8 (GND) of the 595, as close to the chip as possible. This prevents noise glitches.

### LED Wiring (7 LEDs)

Each LED connects from one 595 output through a 240 Ω resistor to GND:

| 595 Output | 595 Pin | → | Resistor | → | LED (+) | LED (−) → GND |
| ---------- | ------- | -- | -------- | -- | ------- | --------------- |
| QB         | Pin 1   | → | 240 Ω   | → | LED 1   | → GND rail     |
| QC         | Pin 2   | → | 240 Ω   | → | LED 2   | → GND rail     |
| QD         | Pin 3   | → | 240 Ω   | → | LED 3   | → GND rail     |
| QE         | Pin 4   | → | 240 Ω   | → | LED 4   | → GND rail     |
| QF         | Pin 5   | → | 240 Ω   | → | LED 5   | → GND rail     |
| QG         | Pin 6   | → | 240 Ω   | → | LED 6   | → GND rail     |
| QH         | Pin 7   | → | 240 Ω   | → | LED 7   | → GND rail     |

> **QA (pin 15) is left unused** — same as the Pico build. Seven LEDs are sufficient for the 7-bit time code.

### Full Wiring Diagram

```
[Raspberry Pi 5]                                [Breadboard]

Pin 1  (3V3)  ─────────────────────────── 595 pin 16 (VCC)
                                     ├─── 595 pin 10 (MR)
                                     └─── 0.1µF cap ─┐
Pin 6  (GND)  ─────────────────────────── 595 pin 8  (GND)
                                     ├─── 0.1µF cap ─┘
                                     ├─── 595 pin 13 (OE)
                                     └─── LED GND rail

Pin 19 (GPIO10/MOSI)  ────────────────── 595 pin 14 (SER)
Pin 23 (GPIO11/SCLK)  ────────────────── 595 pin 11 (SRCLK)
Pin 24 (GPIO8/CE0)    ────────────────── 595 pin 12 (RCLK)

                    595 pin 1  (QB) ──[240Ω]──►|── GND    LED 1
                    595 pin 2  (QC) ──[240Ω]──►|── GND    LED 2
                    595 pin 3  (QD) ──[240Ω]──►|── GND    LED 3
                    595 pin 4  (QE) ──[240Ω]──►|── GND    LED 4
                    595 pin 5  (QF) ──[240Ω]──►|── GND    LED 5
                    595 pin 6  (QG) ──[240Ω]──►|── GND    LED 6
                    595 pin 7  (QH) ──[240Ω]──►|── GND    LED 7
```

### Test

```bash
cd firmware/rpi5_timecode
make timecode
./timecode --panel8        # walking dot + binary counter (visible speed)
# Press Ctrl+C to stop
```

✅ **If LEDs sweep and count, SPI + 595 chain works. Move to Stage 3.**

---

## Stage 3 — Time-Code (Production)

**No rewiring needed** — same circuit as Stage 2, just a different program mode.

### Test (slow demo — visible by eye)

```bash
./timecode --step-us=500000    # 0.5 s per step — one LED changes per step
                                # all 7 cycle over ~64 s
```

You should see **exactly one LED change state per step** (this is the Gray code property).

### Production run (camera speed)

```bash
./timecode                     # default: 500 µs/step (2000 steps/s)
```

Too fast to see by eye — verify with a camera using the decode pipeline:

```bash
cd ../../decode
pip install -r requirements.txt
python decode_video.py <your_video_file>
```

---

## Pico vs. Pi 5 — Quick Reference

|                               | Pico H                        | Raspberry Pi 5          |
| ----------------------------- | ----------------------------- | ----------------------- |
| **SER (data)**          | GP19                          | GPIO 10 (Pin 19)        |
| **SRCLK (shift clock)** | GP18                          | GPIO 11 (Pin 23)        |
| **RCLK (latch)**        | GP17 (manual GPIO)            | GPIO 8 / CE0 (auto SPI) |
| **Power**               | 3V3 (Out)                     | Pin 1/17 (3.3V)         |
| **Ground**              | GND                           | Pin 6/14/20 (GND)       |
| **SPI speed**           | 1 MHz                         | 1 MHz                   |
| **Build**               | cmake + arm-gcc cross-compile | gcc native on Pi        |
| **Flash**               | picotool load .uf2            | just`./timecode`      |

---

## Troubleshooting

| Problem                                     | Check                                                                               |
| ------------------------------------------- | ----------------------------------------------------------------------------------- |
| No LEDs light up                            | Is SPI enabled?`ls /dev/spidev0.0`. Is OE tied to GND? Is VCC connected?          |
| All LEDs on or garbage                      | Check SER/SRCLK/RCLK wiring order — easy to swap MOSI↔SCLK                        |
| LEDs flicker randomly                       | Add/check the 0.1 µF decoupling cap. Check GND is shared between Pi and breadboard |
| `Permission denied` on `/dev/spidev0.0` | Run`sudo usermod -a -G spi $USER` then reboot                                     |
| Blink LED doesn't work                      | Check GPIO 18 (Pin 12), not GPIO 12. Check LED polarity (long leg = +)              |
