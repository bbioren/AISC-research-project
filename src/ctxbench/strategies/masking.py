"""ASSIGNMENT A: Observation masking.

Source papers:
  * Yang et al., 2024, "SWE-agent: Agent-Computer Interfaces Enable Automated
    Software Engineering" -- the original observation-collapsing scheme.
  * Lindenbauer et al., 2025, "The Complexity Trap" -- the masking baseline we
    are reproducing, compared against summarization on SWE-bench Verified.

Your job: implement `build_view` so it matches what *The Complexity Trap* did as
closely as our harness allows. Find in the paper (and its code, if released):
  - how many recent observations stay visible (the window), and how it's counted
  - exactly what replaces a hidden observation (placeholder text)
  - whether actions / reasoning are ever hidden, or only tool output
Record every choice and its source (page/section) in docs/assignments/A_masking.md.

Rules (checked by tests/test_contract.py):
  - Never mutate `history`; return a new ContextView.
  - System prompt and task statement are always visible (use `pinned`).
  - Every observation you don't show verbatim goes in `ContextView.hidden_ids`.
"""

from ctxbench.messages import ContextView, Turn
from ctxbench.strategies.base import ContextStrategy, body, pinned  # noqa: F401  (you'll need these)


class ObservationMasking(ContextStrategy):
    name = "masking"

    def __init__(self, window: int = 5, **kwargs):
        super().__init__(window=window, **kwargs)
        self.window = window

    def build_view(self, history: list[Turn]) -> ContextView:
        raise NotImplementedError("Assignment A: implement observation masking (see module docstring).")
