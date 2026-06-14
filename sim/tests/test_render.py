"""Render a frame the way a camera would see it: a matte-black panel with two
one-hot LED rows. Only the active cell in each row lights."""
from ledsync.codec import Codec, Reading
from ledsync.render import Layout, render_reading


def _lit(px, xy):
    r, g, b = px[xy][:3]
    return r > 150 and g < 90 and b < 90  # a red LED is on


def test_render_lights_the_active_cell_and_leaves_others_dark():
    codec = Codec(fine_n=16, coarse_n=16)
    layout = Layout(codec)
    img = render_reading(Reading(fine_pos=4, coarse_pos=1), codec, layout)
    px = img.load()
    assert _lit(px, (layout.cell_x(4), layout.fine_y))          # active fine cell
    assert not _lit(px, (layout.cell_x(0), layout.fine_y))      # other fine cell dark
    assert _lit(px, (layout.cell_x(1), layout.coarse_y))        # active coarse cell
    assert not _lit(px, (layout.cell_x(2), layout.coarse_y))    # other coarse cell dark
