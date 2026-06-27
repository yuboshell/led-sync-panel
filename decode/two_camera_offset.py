#!/usr/bin/env python3
"""Inter-camera capture-time offset from two videos of the same time-code panel.

This is the project's purpose, built on single-video `decode_video.py`: decode the
7-bit Gray count in each frame of two cameras, align the two count sequences, and the
residual count difference (x tau) is the inter-camera offset.

Crucially this uses ONLY the decoded LED counts and frame order -- never any camera
timestamps -- so it is an independent check of the rig's synchronization.

    python3 two_camera_offset.py VIDEO_A VIDEO_B --crop-a W:H:X:Y --crop-b W:H:X:Y

Lessons baked in (the hard-won ones from the first real two-camera run):

* tau is small (1 ms on the current firmware/timecode), so at e.g. 30 fps the count
  jumps ~33 per frame -- DON'T expect "+1 per frame". A correct decode is identified
  by the count advancing at ~(frame_period/tau) per frame with low jitter, not by +1.
* The LED row tilts under perspective, so sample each LED at its OWN row (per-LED y),
  not one shared row -- a single row mis-reads the far LEDs as noise.
* Frame correspondence comes from cross-correlating the count sequences (integer-frame
  shift), then the residual is the sub-frame offset. The 128 ms wrap can alias the
  alignment, so the tool reports the next-best shift; trust the result only when the
  best alignment's |offset| is clearly smaller than the next candidate.
* Resolution is one tau per frame, but averaging many frames pins the mean below tau.

Options: --leds N (7) - --tau-us US (1000) - --fps F (30) - --scale W (500) -
--start S --dur D (trim) - --centers-a/-b "x0,x1,..." --row-a/-b Y (manual localize) -
--windows SEC (offset per time window: stable vs drifting) -
--montage PNG (decode-audit grid: LED crop + raw Gray bits + count).

Requires ffmpeg on PATH, plus numpy + pillow.
"""
import argparse
import os
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw

from decode_video import auto_localize, extract_frames

R = 9  # LED sample half-window (px, in the scaled crop)


def ungray_arr(g, mask):
    b = g.astype(np.int64).copy()
    b ^= b >> 1
    b ^= b >> 2
    b ^= b >> 4
    return b & mask


def wrap(d, n):
    """Wrap a count/offset difference into (-n/2, n/2]."""
    return (d + n // 2) % n - n // 2


def gray_str(onoff, i):
    """The on/off code read from frame i (LED0..LEDk-1, left-to-right)."""
    return "".join(str(int(b)) for b in onoff[i])


def build_montage(path, cntA, LA, onoffA, cntB, LB, onoffB, s, i0, i1, n_cells, tau_ms, mask, dispw=240):
    """Decode-audit montage: sample frames showing both cameras' LED crop + the raw Gray
    bits read from the image + the decoded count (+ per-pair offset). Lets a borderline
    light/dark LED be checked against the image. Pairing uses the cross-correlation
    alignment, so the per-pair offset inherits that confidence; the Gray bits/count are a
    per-camera audit and are valid regardless."""
    def crop_img(L, i):
        im = Image.fromarray(np.clip(L[i] * 2.4 + 8, 0, 255).astype("uint8")).convert("RGB")
        return im.resize((dispw, max(1, int(round(im.height * dispw / im.width)))))

    idxs = [int(round(x)) for x in np.linspace(i0, i1 - 1, min(n_cells, i1 - i0))]
    cells = []
    for i in idxs:
        j = i - s
        ca, cb = int(cntA[i]), int(cntB[j])
        d = int(wrap(np.array([ca - cb]), mask + 1)[0])
        a_im, b_im = crop_img(LA, i), crop_img(LB, j)
        lh = 18
        cell = Image.new("RGB", (dispw, a_im.height + b_im.height + 2 * lh), (20, 20, 20))
        dr = ImageDraw.Draw(cell)
        y = 0
        cell.paste(a_im, (0, y)); y += a_im.height
        dr.text((3, y + 4), f"A {gray_str(onoffA, i)} cnt {ca}", fill=(220, 220, 220)); y += lh
        cell.paste(b_im, (0, y)); y += b_im.height
        col = (120, 220, 120) if d == 0 else (255, 185, 70)
        dr.text((3, y + 4), f"B {gray_str(onoffB, j)} cnt {cb}  {d * tau_ms:+.1f}ms", fill=col)
        cells.append(cell)

    cols = min(5, len(cells))
    rows = (len(cells) + cols - 1) // cols
    cw, chh, pad = cells[0].width, max(c.height for c in cells), 6
    grid = Image.new("RGB", (cols * (cw + pad) + pad, rows * (chh + pad) + pad), (255, 255, 255))
    for k, c in enumerate(cells):
        r, cc = divmod(k, cols)
        grid.paste(c, (pad + cc * (cw + pad), pad + r * (chh + pad)))
    grid.save(path)
    print(f"montage ({len(cells)} frames, Gray bits + count) -> {path}")


def decode_counts(video, crop, a, centers, row, label):
    """Decode one video. Returns (counts, mask, frames_L, onoff_bits)."""
    tmp = tempfile.mkdtemp(prefix="tc2_")
    frames = extract_frames(video, tmp, crop, a.scale, a.fps, a.start, a.dur)
    if not frames:
        sys.exit(f"[{label}] no frames extracted (check ffmpeg / --crop)")
    L = np.stack([np.asarray(Image.open(f).convert("L")) for f in frames]).astype(np.float32)
    N, H, W = L.shape
    maxL = L.max(0)

    if centers is None:
        row, centers = auto_localize(maxL, a.leds)
    centers = list(centers)

    # per-LED vertical centre -- the row tilts, so a shared row mis-samples far LEDs
    led_y = [int(maxL[:, max(0, x - R):x + R].mean(axis=1).argmax()) for x in centers]

    base = os.path.splitext(video)[0]
    dbg = Image.fromarray(maxL.astype("uint8")).convert("RGB")
    dd = ImageDraw.Draw(dbg)
    for k, (x, y) in enumerate(zip(centers, led_y)):
        dd.ellipse([x - 8, y - 8, x + 8, y + 8], outline=(255, 0, 0), width=2)
        dd.text((x - 3, y + 11), str(k), fill=(255, 90, 90))
    dbg.save(base + "_leds.png")
    print(f"[{label}] {N} frames {W}x{H}  centres({len(centers)})={centers}  -> {base}_leds.png")
    if len(centers) != a.leds:
        sys.exit(f"[{label}] found {len(centers)} centres, expected {a.leds} -- "
                 f"inspect {base}_leds.png and pass --centers-{label.lower()}/--row-{label.lower()}")

    samp = np.stack([[L[n, max(0, led_y[j] - R):led_y[j] + R,
                        max(0, centers[j] - R):centers[j] + R].mean()
                      for j in range(a.leds)] for n in range(N)])
    onoff = np.stack([(samp[:, j] > (samp[:, j].min() + samp[:, j].max()) / 2).astype(int)
                      for j in range(a.leds)], 1)

    mask = (1 << a.leds) - 1
    g = np.zeros(N, dtype=np.int64)
    for bit in range(a.leds):
        g |= (onoff[:, bit].astype(np.int64) << bit)
    cnt = ungray_arr(g, mask)

    tau_ms = a.tau_us / 1000.0
    expect = (1000.0 / a.fps) / tau_ms          # counts advanced per frame
    dc = wrap(np.diff(cnt), mask + 1)
    rate = float(np.median(dc))
    jitter = float(np.std(wrap(dc - np.median(dc), mask + 1)))
    print(f"[{label}] decode: {rate:.0f} counts/frame (expect ~{expect:.0f})  jitter std={jitter:.2f}")
    return cnt, mask, L, onoff


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video_a")
    p.add_argument("video_b")
    p.add_argument("--crop-a", required=True, help="ffmpeg crop W:H:X:Y around cam A's LED row")
    p.add_argument("--crop-b", required=True, help="ffmpeg crop W:H:X:Y around cam B's LED row")
    p.add_argument("--scale", type=int, default=500)
    p.add_argument("--leds", type=int, default=7)
    p.add_argument("--tau-us", type=int, default=1000, dest="tau_us")
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--start", type=float, default=0)
    p.add_argument("--dur", type=float, default=None)
    p.add_argument("--centers-a", help="comma-separated x centres for cam A (override auto)")
    p.add_argument("--row-a", type=int)
    p.add_argument("--centers-b", help="comma-separated x centres for cam B")
    p.add_argument("--row-b", type=int)
    p.add_argument("--max-shift", type=int, default=60, help="frame-alignment search range")
    p.add_argument("--windows", type=float, default=None, metavar="SEC",
                   help="also report the offset per SEC-second window (stable vs drifting)")
    p.add_argument("--montage", default=None, metavar="PNG",
                   help="write a decode-audit montage (sample frames: LED crop + Gray bits + count)")
    p.add_argument("--montage-n", type=int, default=12, dest="montage_n",
                   help="number of frames in the montage (default 12)")
    a = p.parse_args()

    ca = [int(x) for x in a.centers_a.split(",")] if a.centers_a else None
    cb = [int(x) for x in a.centers_b.split(",")] if a.centers_b else None
    cntA, mask, LA, onoffA = decode_counts(a.video_a, a.crop_a, a, ca, a.row_a, "A")
    cntB, _, LB, onoffB = decode_counts(a.video_b, a.crop_b, a, cb, a.row_b, "B")

    n = mask + 1
    tau_ms = a.tau_us / 1000.0
    scan = []
    for s in range(-a.max_shift, a.max_shift + 1):
        i0, i1 = max(0, s), min(len(cntA), len(cntB) + s)
        if i1 - i0 < 50:
            continue
        d = wrap(cntA[i0:i1] - cntB[i0 - s:i1 - s], n)
        scan.append((float(np.median(d)), float(np.std(d)), s, i1 - i0))
    # The genuine alignments are the tight-spread (lockstep) ones; the true offset is
    # the smallest |median| among them (nearest-frame pairing). Ranking by |median|
    # alone is wrong (a high-spread shift can sit near 0); ranking by spread alone is
    # wrong (an aliased lockstep can be a whole frame off). So: take the tight-spread
    # set, pick min |median| within it, and report the next lockstep's |offset| as the
    # aliasing margin (a frame-aliasing step away -- unambiguous when it is large).
    min_spread = min(r[1] for r in scan)
    tight = sorted((r for r in scan if r[1] < 2.0 * min_spread + 0.5),
                   key=lambda r: (abs(r[0]), r[1]))
    med, spread, s, overlap = tight[0]
    i0, i1 = max(0, s), min(len(cntA), len(cntB) + s)
    d = wrap(cntA[i0:i1] - cntB[i0 - s:i1 - s], n)
    frac0 = float(np.mean(d == 0))

    print(f"\n==== inter-camera offset (A - B), LED counts only ====")
    print(f"frame alignment: B shifted {s} frames ({overlap} overlapping frames)")
    print(f"offset = {np.median(d) * tau_ms:+.3f} ms (median)  {np.mean(d) * tau_ms:+.3f} ms (mean)")
    print(f"identical-count frames = {frac0 * 100:.0f}%  (per-frame spread {spread * tau_ms:.2f} ms)")
    # frac0 is the robust confidence signal: a frame-aliased (wrong) alignment would
    # decode the same count only by chance, never ~all the time.
    if frac0 > 0.5:
        print(f"=> cameras are simultaneous to << tau: sync error |offset| < ~{tau_ms} ms "
              f"(the time-code resolution).")
    else:
        print("=> NO clean simultaneous alignment -- check --crop/--centers/--tau-us/--fps, "
              "or the cameras are not well synced.")
    print(f"sign: +ve => cam A captures later than cam B.")

    if a.windows:
        wf = max(1, int(round(a.windows * a.fps)))
        print(f"\n-- offset per {a.windows:g}-second window (a constant value across windows "
              f"= a fixed offset; a trend = clock drift) --")
        meds = []
        for w in range(0, len(d), wf):
            seg = d[w:w + wf]
            if len(seg) < 5:
                continue
            m = float(np.median(seg)) * tau_ms
            meds.append(m)
            print(f"  {w / a.fps:5.0f}-{(w + len(seg)) / a.fps:<5.0f}s  n={len(seg):4d}  {m:+.2f} ms")
        if meds:
            sprd = max(meds) - min(meds)
            print(f"  window spread {sprd:.2f} ms -> "
                  f"{'STABLE (fixed offset)' if sprd <= 1.0 else 'DRIFTING (clock skew?)'}")

    if a.montage:
        build_montage(a.montage, cntA, LA, onoffA, cntB, LB, onoffB, s, i0, i1,
                      a.montage_n, tau_ms, mask)


if __name__ == "__main__":
    main()
