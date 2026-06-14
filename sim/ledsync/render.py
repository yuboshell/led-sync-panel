"""Render a panel reading as a synthetic camera frame: matte-black board, two
one-hot LED rows (fine on top, coarse below). Direct-emission red LEDs."""
from dataclasses import dataclass

from PIL import Image, ImageDraw

from ledsync.codec import Codec, Reading

PANEL_BG = (10, 10, 12)      # matte black
LED_ON = (220, 40, 40)       # lit red LED
LED_OFF = (48, 14, 14)       # unlit


@dataclass(frozen=True)
class Layout:
    codec: Codec
    cell: int = 40
    radius: int = 14
    pad: int = 20
    row_gap: int = 22

    @property
    def cols(self):
        return max(self.codec.fine_n, self.codec.coarse_n)

    @property
    def width(self):
        return self.pad * 2 + self.cols * self.cell

    @property
    def height(self):
        return self.pad * 2 + self.row_gap + 4 * self.radius

    @property
    def fine_y(self):
        return self.pad + self.radius

    @property
    def coarse_y(self):
        return self.pad + 3 * self.radius + self.row_gap

    def cell_x(self, index):
        return self.pad + index * self.cell + self.cell // 2


def _draw_row(draw, layout, n, active_index, y):
    for i in range(n):
        x = layout.cell_x(i)
        colour = LED_ON if i == active_index else LED_OFF
        draw.ellipse([x - layout.radius, y - layout.radius,
                      x + layout.radius, y + layout.radius], fill=colour)


def render_reading(reading: Reading, codec: Codec, layout: Layout = None):
    layout = layout or Layout(codec)
    img = Image.new("RGB", (layout.width, layout.height), PANEL_BG)
    draw = ImageDraw.Draw(img)
    _draw_row(draw, layout, codec.fine_n, reading.fine_pos, layout.fine_y)
    _draw_row(draw, layout, codec.coarse_n, reading.coarse_pos, layout.coarse_y)
    return img
