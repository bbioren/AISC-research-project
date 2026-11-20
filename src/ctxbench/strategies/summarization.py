"""B: LLM summarization (the OpenHands condenser).

Papers: OpenHands (Wang et al., ICLR 2025) and The Complexity Trap (Lindenbauer et al. 2025).
Match how The Complexity Trap set it up. Find out, with page numbers:
  - what triggers a summary, and how much recent history is kept as-is
  - the prompt used to summarize
  - whether the old summary gets folded into the next one

Call the model with `self.llm.complete(messages)`. It returns .text, .tokens and .cost.
Add those tokens and that cost to the ContextView's extra_tokens / extra_cost, or
summarization will look free. And don't re-summarize on every step.
"""

from ctxbench.messages import ContextView
from ctxbench.strategies.base import ContextStrategy, body, pinned  # noqa: F401


class LLMSummarization(ContextStrategy):
    name = "summarization"

    def __init__(self, llm):
        self.llm = llm

    def build_view(self, history):
        raise NotImplementedError("B: write this")
