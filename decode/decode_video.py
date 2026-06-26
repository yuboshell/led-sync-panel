#!/usr/bin/env python3
"""Decode the LED time-code panel from camera footage.

Decodes the output of firmware/timecode: a 7-bit GRAY counter on QB..QH that steps
every tau. Pipeline:

    ffmpeg frame extraction -> LED localization (max-image peaks) -> per-LED on/off
    -> un-Gray -> count -> timestamp (count * tau).

It also VERIFIES the decode: the count must increment by +1 each step, and no frame
may straddle a tick by more than +-1 (the Gray guarantee -- plain binary would not).
This is the real-footage counterpart of sim/ (which proves the same chain in simulation).

Usage
-----
    python3 decode_video.py VIDEO.MOV --crop W:H:X:Y [options]

Localization is automatic; it writes VIDEO_leds.png (the max-over-time image with the
detected LED centres marked) so you can check it. If the auto-detect is wrong (e.g. a
reflection gets picked up), pass the centres by hand:

    python3 decode_video.py VIDEO.MOV --crop W:H:X:Y --centers x0,x1,...  --row Y

Options: --leds N (7), --tau-us US (50000), --fps F (60), --scale W (500),
         --start S --dur D (trim), --centers ... --row Y (manual localization).

Requires ffmpeg on PATH, plus numpy + pillow.
"""
import argparse, glob, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw


def extract_frames(video, outdir, crop, scale, fps, start, dur):
    vf = f"fps={fps}"
    if crop:  vf += f",crop={crop}"
    if scale: vf += f",scale={scale}:-1"
    cmd = ["ffmpeg", "-y"]
    if start: cmd += ["-ss", str(start)]
    if dur:   cmd += ["-t", str(dur)]
    cmd += ["-i", video, "-vf", vf, os.path.join(outdir, "f%05d.png")]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return sorted(glob.glob(os.path.join(outdir, "*.png")))


def auto_localize(maxL, n_leds):
    """Find the LED row + column peaks in the max-over-time image (LEDs lit at some point)."""
    H, W = maxL.shape
    yd = int((maxL > maxL.max() * 0.82).sum(1).argmax())            # row with the most saturated px
    band = np.convolve(maxL[max(0, yd - 12):yd + 12].mean(0), np.ones(7) / 7, "same")
    thr = band.max() * 0.5
    peaks = []
    for i in range(3, W - 3):
        if band[i] > thr and band[i] >= band[i - 1] and band[i] >= band[i + 1]:
            if not peaks or i - peaks[-1] > W // (n_leds + 3):
                peaks.append(i)
            elif band[i] > band[peaks[-1]]:
                peaks[-1] = i
    return yd, peaks


def ungray(g):
    b = g; b ^= b >> 1; b ^= b >> 2; b ^= b >> 4
    return b


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video")
    p.add_argument("--crop", help="ffmpeg crop W:H:X:Y around the LED row")
    p.add_argument("--scale", type=int, default=500)
    p.add_argument("--leds", type=int, default=7)
    p.add_argument("--tau-us", type=int, default=50000, dest="tau_us")
    p.add_argument("--fps", type=int, default=60)
    p.add_argument("--start", type=float, default=0)
    p.add_argument("--dur", type=float, default=None)
    p.add_argument("--centers", help="comma-separated x centres (override auto-localize)")
    p.add_argument("--row", type=int, help="LED row y (use with --centers)")
    a = p.parse_args()
    mask = (1 << a.leds) - 1

    tmp = tempfile.mkdtemp(prefix="tcdecode_")
    frames = extract_frames(a.video, tmp, a.crop, a.scale, a.fps, a.start, a.dur)
    if not frames:
        sys.exit("no frames extracted (check ffmpeg / --crop)")
    L = np.stack([np.asarray(Image.open(f).convert("L")) for f in frames]).astype(np.float32)
    N, H, W = L.shape
    print(f"{N} frames @ {a.fps} fps, {W}x{H}")

    maxL = L.max(0)
    if a.centers:
        centers = [int(x) for x in a.centers.split(",")]
        row = a.row if a.row is not None else int((maxL > maxL.max() * 0.82).sum(1).argmax())
    else:
        row, centers = auto_localize(maxL, a.leds)
        print(f"auto-localized: row={row}, {len(centers)} centres {centers}")

    base = os.path.splitext(a.video)[0]
    dbg = Image.fromarray(maxL.astype("uint8")).convert("RGB")
    dd = ImageDraw.Draw(dbg)
    for k, x in enumerate(centers):
        dd.ellipse([x - 8, row - 8, x + 8, row + 8], outline=(255, 0, 0), width=2)
        dd.text((x - 3, row + 11), str(k), fill=(255, 90, 90))
    dbg.save(base + "_leds.png")
    print(f"debug image -> {base}_leds.png  (verify the {a.leds} centres; override with --centers/--row)")
    if len(centers) != a.leds:
        sys.exit(f"found {len(centers)} centres, expected {a.leds} -- inspect the debug image, pass --centers/--row")

    r = 9
    samp = np.stack([[L[n, max(0, row - r):row + r, max(0, x - r):x + r].mean() for x in centers]
                     for n in range(N)])
    onoff = np.stack([(samp[:, j] > (samp[:, j].min() + samp[:, j].max()) / 2).astype(int)
                      for j in range(a.leds)], 1)
    print("toggle cascade L->R (a binary count halves down the row):",
          [int(np.abs(np.diff(onoff[:, j])).sum()) for j in range(a.leds)])

    # decode: try both bit orders, keep the one whose count increments cleanly
    best = None
    for order in (list(range(a.leds)), list(range(a.leds - 1, -1, -1))):
        g = np.zeros(N, dtype=int)
        for bit, led in enumerate(order):
            g |= (onoff[:, led].astype(int) << bit)
        cnt = np.array([ungray(int(v)) & mask for v in g])
        seq = []
        for n in range(N):
            if not seq or seq[-1][0] != cnt[n]: seq.append([int(cnt[n]), 1])
            else: seq[-1][1] += 1
        stable = [s for s in seq if s[1] >= 2]
        good = sum(1 for x, y in zip(stable, stable[1:]) if (y[0] - x[0]) % (mask + 1) == 1)
        score = good / max(1, len(stable) - 1)
        if best is None or score > best[0]:
            best = (score, order, cnt, stable, good)

    score, order, cnt, stable, good = best
    pf = [min((cnt[n + 1] - cnt[n]) % (mask + 1), (cnt[n] - cnt[n + 1]) % (mask + 1)) for n in range(N - 1)]
    garbage = sum(1 for x in pf if x > 1)
    tau = a.tau_us / 1e6
    print(f"\nbit order           : {'left->right' if order[0] == 0 else 'right->left'} = LSB..MSB")
    print(f"clean +1 increments : {score * 100:.1f}%  ({good}/{max(0, len(stable) - 1)} steps)")
    print(f"garbage straddles   : {garbage} frames jump > +-1   (Gray guarantees 0)")
    print(f"tau = {tau * 1000:.1f} ms, wraps every {(mask + 1) * tau:.2f} s")
    print("count (stable states, first 60):", [s[0] for s in stable[:60]])
    if score > 0.98 and garbage == 0:
        print("\nVERDICT: clean, robust Gray time-code -- encode->film->decode confirmed.")


if __name__ == "__main__":
    main()
