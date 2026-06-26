# decode/ — decode the time-code panel from camera footage

The real-footage counterpart of `sim/`. `sim/` *proves* the encode → decode → offset
chain in simulation; this decodes an **actual camera video** of the panel running
`firmware/timecode` (a 7-bit **Gray** counter stepping every τ).

`decode_video.py` does: **ffmpeg frame extraction → LED localization (max-image) →
per-LED on/off → un-Gray → count → timestamp**, and then **verifies** the result —
the count must increment by +1 each step, and no frame may straddle a tick by more
than ±1 (the Gray guarantee; plain binary would not hold).

## Use
```bash
python3 decode_video.py VIDEO.MOV --crop W:H:X:Y
```
It writes `VIDEO_leds.png` (the max-over-time image with the detected LED centres
marked) so you can **check localization**. If a reflection gets mis-picked, pass the
centres by hand:
```bash
python3 decode_video.py VIDEO.MOV --crop W:H:X:Y --centers x0,x1,... --row Y
```
Options: `--leds N` (7) · `--tau-us` (50000) · `--fps` (60) · `--scale W` (500) ·
`--start S --dur D` (trim).

## Verified run (2026-06-26, `IMG_3584.MOV`)
```bash
python3 decode_video.py IMG_3584.MOV --crop 660:240:820:500 \
        --centers 81,131,188,246,293,357,403 --row 93 --start 2 --dur 10
```
→ **100% clean +1 increments, 0 garbage straddles** — the first hardware confirmation
of the encode → film → decode loop. (One auto-detected "LED" was a reflection past the
row, hence the manual `--centers`.)

## Next
**Two-camera offset** (the project's purpose): decode two simultaneous videos, align
their count sequences modulo the wrap, and the difference is the inter-camera
capture-time offset. That builds directly on this single-video decode.

## Requires
`ffmpeg` on PATH, plus `numpy` + `pillow`:
```bash
pip install -r requirements.txt
```
