"""The panel is a clock: its counter advances one step every tau seconds."""
from ledsync.codec import Codec
from ledsync.panel import Panel


def test_count_advances_one_step_per_tau():
    panel = Panel(codec=Codec(fine_n=16, coarse_n=16), tau=200e-6)
    assert panel.count_at(0.0) == 0
    assert panel.count_at(199e-6) == 0     # within the first step
    assert panel.count_at(200e-6) == 1     # tick
    assert panel.count_at(640e-6) == 3     # 3.2 steps -> floor 3


def test_count_at_is_robust_to_float_division_at_step_boundaries():
    panel = Panel(codec=Codec(fine_n=16, coarse_n=16), tau=200e-6)
    # 0.6 ms is exactly 3 steps, but 0.0006/0.0002 == 2.9999999999999996 in float
    assert panel.count_at(0.6e-3) == 3
    assert panel.count_at(15 * 200e-6) == 15


def test_reading_at_is_what_the_panel_displays():
    panel = Panel(codec=Codec(fine_n=16, coarse_n=16), tau=200e-6)
    # at 20 steps the display shows fine=4, coarse=1 (see test_codec)
    reading = panel.reading_at(20 * 200e-6)
    assert (reading.fine_pos, reading.coarse_pos) == (4, 1)
