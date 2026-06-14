#!/usr/bin/env python3
"""End-to-end demo of the LED time-code panel measurement.

Simulates two unsynchronised cameras filming one panel, decodes the panel-time
each one sees, and recovers their capture-time offset — the quantity the real rig
measures. Also renders the two synthetic frames so you can see what the cameras
would capture. All logic here is exercised by tests/ (run: pytest).

    python decode_sim.py
"""
from PIL import Image, ImageDraw

from ledsync.camera import Camera
from ledsync.codec import Codec
from ledsync.offset import recover_offset
from ledsync.panel import Panel
from ledsync.render import Layout, render_reading

PANEL = Panel(codec=Codec(fine_n=16, coarse_n=16), tau=200e-6)
CAM = Camera(line_time=10e-6, panel_row=0)  # ideal sampling, isolates the offset


def report():
    fine_wrap = PANEL.codec.fine_n * PANEL.tau
    half_range = PANEL.codec.n_codes * PANEL.tau / 2
    print(f"Panel: fine={PANEL.codec.fine_n} x coarse={PANEL.codec.coarse_n} "
          f"= {PANEL.codec.n_codes} codes  |  step tau={PANEL.tau*1e6:.0f} us")
    print(f"Fine row wraps every {fine_wrap*1e3:.1f} ms; "
          f"unambiguous offset range = +/- {half_range*1e3:.1f} ms\n")
    print(f"{'true offset':>12} {'recovered':>11} {'status':>22}   "
          f"{'fine-only':>10} {'fine-only ok?':>13}")
    print("-" * 74)
    for delta_ms in (0.6, 3.0, 8.0, 20.0, 40.0):
        delta = delta_ms / 1e3
        full = recover_offset(PANEL, CAM, 0.0, CAM, delta)
        fine = recover_offset(PANEL, CAM, 0.0, CAM, delta, use_coarse=False)
        if delta <= half_range:
            status = f"ok ({(full-delta)*1e6:+.0f} us)"
        else:
            status = "wraps (beyond +/- range)"
        fine_ok = "yes" if abs(fine - delta) <= PANEL.tau else "NO (aliased)"
        print(f"{delta_ms:>10.1f}ms {full*1e3:>9.2f}ms {status:>22}   "
              f"{fine*1e3:>8.2f}ms {fine_ok:>13}")
    print("\nWithin +/- range the coarse row keeps the measurement correct past one "
          "fine wrap;\nfine alone aliases. Real inter-camera offsets are far smaller "
          "than the range.")


def save_frames(delta=0.020, path="frames/two-cameras.png"):
    """Render what camera A and the Δ-offset camera B each capture, stacked."""
    ra = PANEL.reading_at(CAM.capture_instant(0.0))
    rb = PANEL.reading_at(CAM.capture_instant(delta))
    layout = Layout(PANEL.codec)
    fa, fb = render_reading(ra, PANEL.codec, layout), render_reading(rb, PANEL.codec, layout)

    label_h, gap = 26, 14
    w = fa.width
    out = Image.new("RGB", (w, fa.height * 2 + label_h * 2 + gap), (255, 255, 255))
    draw = ImageDraw.Draw(out)
    ta = PANEL.codec.decode(ra) * PANEL.tau
    tb = PANEL.codec.decode(rb) * PANEL.tau
    draw.text((6, 6), f"Camera A  (frame start 0 ms)   decodes t = {ta*1e3:.2f} ms",
              fill=(20, 20, 20))
    out.paste(fa, (0, label_h))
    y2 = label_h + fa.height + gap
    draw.text((6, y2 + 6), f"Camera B  (frame start {delta*1e3:.0f} ms)   "
              f"decodes t = {tb*1e3:.2f} ms   ->  offset = {(tb-ta)*1e3:.2f} ms",
              fill=(20, 20, 20))
    out.paste(fb, (0, y2 + label_h))
    out.save(path)
    print(f"\nWrote {path}  ({out.width}x{out.height}) — the two LED rows differ "
          f"by the {delta*1e3:.0f} ms offset.")


if __name__ == "__main__":
    report()
    save_frames()
