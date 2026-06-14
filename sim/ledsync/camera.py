"""A rolling-shutter camera viewing the panel.

The sensor reads rows top-to-bottom; row r is exposed at frame_start + r*line_time.
The panel sits at sensor row `panel_row`, so the camera samples the panel's code at
that row's instant. This is exactly the effect the real rig exploits to read time
to sub-frame precision.
"""
from dataclasses import dataclass

from ledsync.panel import Panel


@dataclass(frozen=True)
class Camera:
    line_time: float   # seconds per sensor row (rolling-shutter readout)
    panel_row: int     # sensor row at which the panel's code appears

    def capture_instant(self, frame_start):
        return frame_start + self.panel_row * self.line_time

    def read_count(self, panel: Panel, frame_start):
        reading = panel.reading_at(self.capture_instant(frame_start))
        return panel.codec.decode(reading)
