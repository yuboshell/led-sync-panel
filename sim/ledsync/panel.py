"""The LED panel as a clock: a counter driven at one step per tau seconds,
displayed through the positional codec."""
import math
from dataclasses import dataclass

from ledsync.codec import Codec


@dataclass(frozen=True)
class Panel:
    codec: Codec
    tau: float  # step time, seconds

    def count_at(self, t):
        """Ground-truth step index since t=0 (monotonic, not wrapped).

        A tiny epsilon absorbs float-division error so an instant landing exactly
        on a step boundary (e.g. 0.0006/0.0002 == 2.9999...) counts as the step.
        """
        return math.floor(t / self.tau + 1e-9)

    def reading_at(self, t):
        """What the panel visibly displays at time t (wrapped by the codec)."""
        return self.codec.encode(self.count_at(t))
