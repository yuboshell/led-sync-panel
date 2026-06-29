# Step 1 — minimal time-code (7-bit Gray, camera-decodable)

The bring-up's plain binary counter, upgraded into a **real time code**: a 7-bit counter
shown in **Gray code** on the 7 LEDs (QB–QH), advancing on a fixed step **τ**. This is the
first time the **encode → film → decode → offset** loop runs on real hardware, not just `sim/`.

## Why Gray code
A camera frame's exposure is a *window*; the count can tick *during* it. With plain binary,
a multi-bit tick (e.g. `0111111 → 1000000`, six LEDs flipping) caught mid-exposure can decode
to **garbage**. **Gray code changes only one LED per step** (including the 127→0 wrap), so a
straddled frame is off by **at most ±1** — never garbage. The latch keeps the *board* clean;
Gray handles the *camera* straddle.

## Wiring
Identical to the bring-up (Option C, 595 notch-UP) — **no rewiring, just reflash.**
| Pico | → | 595 |
|---|---|---|
| GP18 | → | SRCLK (11) |
| GP19 | → | SER (14) |
| GP17 | → | RCLK (12) |

Plus VCC→3V3, GND→GND, OE→GND, MR→3V3; QB..QH → 240 Ω → LED → GND (QA unused).

## What it does
- Each step τ (currently **0.5 ms**, `STEP_US`), output `gray(count) = count ^ (count>>1)` on
  QB–QH, with `count` advancing 0→127 and wrapping (period = 128·τ = **64 ms**).
- Drift-free stepping (`sleep_until` on absolute τ boundaries), so `count × τ` is a faithful
  timestamp within one wrap.
- **Tune `STEP_US`** to your camera. **50 ms** (20/s) is the easy single-camera regime. Finer
  τ buys sub-frame resolution for **two-camera sync**: **1 ms** works on a phone, **0.5 ms**
  (2000/s — the current value) is the practical floor. Each frame then needs a **shutter ≤ τ**
  (≤ 1/2000 s at 0.5 ms), else the Gray code smears to garbage — and judge a finer-τ run by the
  per-frame **spread**, not the identical-count fraction (finer resolution lowers that fraction
  legitimately, as it resolves sub-τ residual the coarser step rounded to zero).

## Decode (per camera frame)
```
read QB..QH as 7-bit g            # QB = bit0 ... QH = bit6
b = g; b ^= b>>1; b ^= b>>2; b ^= b>>4   # Gray -> binary
count = b
t ≈ count * τ                     # modulo the 128·τ wrap
```
Two cameras' decoded counts (mod wrap) differ by their capture-time offset.

## Build & flash
Same toolchain as `../blink` / `../panel8`:
```bash
export PATH="$(echo ~/pico/toolchain/xpack-arm-none-eabi-gcc-*/bin):$PATH"
export PICO_SDK_PATH=~/pico-sdk
cp "$PICO_SDK_PATH/external/pico_sdk_import.cmake" .
mkdir build && cd build && cmake .. && make        # -> timecode.uf2
# FIRST load (over no-USB firmware): hold BOOTSEL while plugging in USB, then:
picotool load -x build/timecode.uf2
```
**After this firmware is running, updates need no button** — it brings up the USB reset
interface, so just rebuild and:
```bash
picotool load -fx build/timecode.uf2   # -f reboots to BOOTSEL over USB, loads, and runs
```

## Demo / diagnostic mode — `flash.sh`
Build + no-touch-flash at any step, to switch between camera speed and a slow, watchable
version in one command:
```bash
./flash.sh        # production: 0.5 ms/step (too fast to see by eye)
./flash.sh 500    # demo: 500 ms/step — Gray code flips one LED per step, so all 7 visibly
                  #       cycle over ~30 s. For showing people, or confirming every LED works.
```
`STEP_US` is a build-time override (`cmake -DSTEP_US=<microseconds>`); `main.c`'s default stays 0.5 ms.
