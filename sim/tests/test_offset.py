"""The whole point of the rig: two unsynced cameras film the same panel; the
difference in the panel-time each one decodes IS their capture-time offset."""
import pytest

from ledsync.camera import Camera
from ledsync.codec import Codec
from ledsync.offset import recover_offset
from ledsync.panel import Panel


def test_recovers_small_inter_camera_offset():
    panel = Panel(codec=Codec(fine_n=16, coarse_n=16), tau=200e-6)
    cam = Camera(line_time=10e-6, panel_row=0)  # capture instant == frame start
    delta = 0.003  # 3 ms = 15 steps, within one fine wrap (3.2 ms)
    recovered = recover_offset(panel, cam, 0.0, cam, delta)
    assert recovered == pytest.approx(delta, abs=panel.tau)


def test_coarse_row_disambiguates_offset_that_fine_alone_aliases():
    # The §6 vernier result, made executable.
    panel = Panel(codec=Codec(fine_n=16, coarse_n=16), tau=200e-6)
    cam = Camera(line_time=10e-6, panel_row=0)
    delta = 0.020  # 20 ms = 100 steps: 6+ fine wraps (3.2 ms each), within full range (51.2 ms)

    full = recover_offset(panel, cam, 0.0, cam, delta)
    fine_only = recover_offset(panel, cam, 0.0, cam, delta, use_coarse=False)

    assert full == pytest.approx(delta, abs=panel.tau)          # coarse row -> correct
    assert fine_only != pytest.approx(delta, abs=panel.tau)     # fine alone -> wrong
    assert fine_only == pytest.approx(delta % (panel.codec.fine_n * panel.tau),
                                      abs=panel.tau)             # aliased into one wrap
