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

## Two-camera offset (`two_camera_offset.py`) — the project's purpose

Decode two simultaneous videos, align their count sequences, and the residual count
difference (× τ) is the inter-camera capture-time offset. It uses **only the decoded
LED counts and frame order — never any camera timestamps** — so it is an independent
check of the rig's synchronization.

```bash
python3 two_camera_offset.py VIDEO_A VIDEO_B --crop-a W:H:X:Y --crop-b W:H:X:Y \
        [--centers-a x0,x1,... --centers-b ...] --tau-us 1000 --fps 30
```
It writes each camera's `*_leds.png` (check localization) and prints the offset, the
per-frame spread, and the **identical-count fraction** — the confidence signal: a wrong
frame alignment decodes the same count only by chance, never ~always.

Two extra modes:

- **`--windows SEC`** — also report the offset per `SEC`-second window. A constant value
  across windows is a *fixed* offset (e.g. rolling shutter); a trend is a *clock drift*.
  (The window-to-window stability is robust even where the absolute offset aliases at
  fine τ; the per-window value still inherits the alignment's identical-count confidence.)
- **`--montage out.png`** — write a decode-audit grid: sample frames with each camera's
  LED crop, the **raw on/off Gray bits read from the image**, and the decoded count, so a
  borderline light/dark LED can be checked against the picture.

### Verified run (2026-06-26, 2 cameras of the 11×Pixel rig, 4K30)
Two Pixel phones filming the panel (`firmware/timecode`, τ = 1 ms):
```bash
python3 two_camera_offset.py cam01.mp4 cam02.mp4 \
        --crop-a 860:200:2230:1585 --crop-b 1000:230:860:1405 \
        --centers-a 28,95,160,222,290,358,428 --tau-us 1000 --fps 30
```
→ **offset ≈ 0 ms** (median 0, mean −0.07 ms; **92 % of 337 paired frames decode the
identical count**). The two cameras capture simultaneously to within the 1 ms time-code
resolution — confirmed independently of the phone clocks.

### Lessons (the hard-won ones)
- **τ is 1 ms, not 50 ms.** At 30 fps the count jumps ~33 per frame, so the "+1 per
  step" check from single-video decode is meaningless here. A correct decode is instead
  identified by the count advancing ~(frame period / τ) per frame with low jitter.
- **Sample each LED at its own row.** The LED row tilts under perspective, so a single
  shared row mis-reads the far LEDs as noise. Per-LED vertical centring fixes it.
- **Never use camera timestamps for the offset.** The eval must stand on the LED counts
  alone or it is circular (you'd be validating the timestamps with themselves). Frame
  correspondence comes from cross-correlating the two count sequences.
- **Mind the 128 ms wrap.** It must stay longer than one frame interval or the frame
  alignment is ambiguous; if you shorten τ, add LED bits to keep the wrap long. Confirm
  an alignment by its identical-count fraction, not by any single shift's offset.
- **Resolution is τ.** Averaging many frames pins the *mean* offset below τ (here
  −0.07 ms), but a single frame resolves only to ±1 ms; finer needs a faster shutter
  **and** a smaller τ (exposure ≲ τ, else the Gray code smears — see the panel doc).

## Requires
`ffmpeg` on PATH, plus `numpy` + `pillow`:
```bash
pip install -r requirements.txt
```
