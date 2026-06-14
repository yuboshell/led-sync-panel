"""A rolling-shutter camera does not expose a frame all at once: sensor row r is
exposed at frame_start + r * line_time. The panel occupies some band of rows, so
the camera samples the panel's code at that row's instant, not at frame start."""
from ledsync.camera import Camera
from ledsync.codec import Codec
from ledsync.panel import Panel


def test_camera_samples_panel_at_its_rolling_shutter_row_instant():
    panel = Panel(codec=Codec(fine_n=16, coarse_n=16), tau=200e-6)
    cam = Camera(line_time=10e-6, panel_row=50)
    # capture instant = 0 + 50 * 10us = 500us = 2.5 steps -> the panel shows count 2
    assert cam.capture_instant(frame_start=0.0) == 500e-6
    assert cam.read_count(panel, frame_start=0.0) == 2
