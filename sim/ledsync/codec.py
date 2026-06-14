"""Positional (mixed-radix) time-code for the LED panel.

The panel displays a counter as two one-hot rows:
  - fine row  (fine_n positions): the low-order digit, sweeps every step
  - coarse row (coarse_n positions): the high-order digit, advances per fine wrap

count = coarse_pos * fine_n + fine_pos, unambiguous over [0, fine_n*coarse_n).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Reading:
    fine_pos: int
    coarse_pos: int


@dataclass(frozen=True)
class Codec:
    fine_n: int
    coarse_n: int

    @property
    def n_codes(self):
        return self.fine_n * self.coarse_n

    def encode(self, count):
        count %= self.n_codes
        return Reading(fine_pos=count % self.fine_n,
                       coarse_pos=count // self.fine_n)

    def decode(self, reading):
        return reading.coarse_pos * self.fine_n + reading.fine_pos
