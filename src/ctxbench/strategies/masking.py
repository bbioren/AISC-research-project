"""Assignment A: observation masking.

Papers:
  * Yang et al. 2024, "SWE-agent: Agent-Computer Interfaces Enable Automated
    Software Engineering". This is where collapsing old observations started.
  * Lindenbauer et al. 2025, "The Complexity Trap". Their masking baseline is the
    one we're reproducing (they compare it to summarization on SWE-bench Verified).

Write build_view so it does what The Complexity Trap's masking did, as close as
our setup allows. Things to find in the paper (and their code if it's out):
  - how many recent observations stay visible, and how they count them
  - what text replaces an observation once it's hidden
  - whether they ever hide the agent's actions/reasoning or only command output
Put each setting and where you found it (page/section) in docs/assignments/A_masking.md.

tests/test_contract.py checks that you:
  - don't modify `history`; return a new ContextView instead
  - always keep the system prompt and task visible (use `pinned`)
  - list every observation you don't show in full in `ContextView.hidden_ids`
"""

from ctxbench.messages import ContextView, Turn
from ctxbench.strategies.base import ContextStrategy, body, pinned  # noqa: F401  (you'll need these)


class ObservationMasking(ContextStrategy):
    name = "masking"

    def __init__(self, window: int = 5, **kwargs):
        super().__init__(window=window, **kwargs)
        self.window = window

    def build_view(self, history: list[Turn]) -> ContextView:
        raise NotImplementedError("Assignment A: implement observation masking (see the comment at the top).")
