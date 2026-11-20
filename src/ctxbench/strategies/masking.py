"""A: observation masking.

Papers: SWE-agent (Yang et al. 2024) and The Complexity Trap (Lindenbauer et al. 2025).
Match what The Complexity Trap did. Find out, with page numbers:
  - how many recent observations stay visible
  - what text replaces a hidden one
  - whether only command output gets hidden, or the model's own replies too
"""

from ctxbench.messages import ContextView
from ctxbench.strategies.base import ContextStrategy, body, pinned  # noqa: F401


class ObservationMasking(ContextStrategy):
    name = "masking"

    def __init__(self, window=5):
        self.window = window

    def build_view(self, history):
        raise NotImplementedError("A: write this")
