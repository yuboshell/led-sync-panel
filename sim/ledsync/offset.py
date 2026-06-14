"""Recover the capture-time offset between two cameras filming the same panel.

Each camera decodes the panel-time it sampled; the cyclic difference of those
times is the inter-camera offset. The panel counter is cyclic, so the difference
is taken to the nearest equivalent in (-range/2, +range/2].
"""
from ledsync.camera import Camera
from ledsync.panel import Panel


def _cyclic_nearest(steps, modulus):
    steps %= modulus
    if steps > modulus // 2:
        steps -= modulus
    return steps


def recover_offset(panel: Panel, cam_a: Camera, frame_start_a,
                   cam_b: Camera, frame_start_b, use_coarse=True):
    read_a = panel.reading_at(cam_a.capture_instant(frame_start_a))
    read_b = panel.reading_at(cam_b.capture_instant(frame_start_b))
    if use_coarse:
        count_a, count_b = panel.codec.decode(read_a), panel.codec.decode(read_b)
        modulus = panel.codec.n_codes
    else:
        # fine row only: no coarse digit to disambiguate beyond one fine wrap
        count_a, count_b = read_a.fine_pos, read_b.fine_pos
        modulus = panel.codec.fine_n
    steps = _cyclic_nearest(count_b - count_a, modulus)
    return steps * panel.tau
