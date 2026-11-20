"""C: masking + summarization hybrid.

Paper: The Complexity Trap (Lindenbauer et al. 2025). They say mixing the two cuts
cost further. Find out, with page numbers, how they combine them: what gets masked,
and what triggers a summary.

Same rules as B for charging summary calls to extra_tokens / extra_cost.
"""

from ctxbench.messages import ContextView
from ctxbench.strategies.base import ContextStrategy, body, pinned  # noqa: F401


class Hybrid(ContextStrategy):
    name = "hybrid"

    def __init__(self, llm):
        self.llm = llm

    def build_view(self, history):
        raise NotImplementedError("C: write this")
