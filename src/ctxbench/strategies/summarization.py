"""Assignment B: LLM summarization (the OpenHands condenser).

Papers / code:
  * OpenHands (Wang et al., ICLR 2025) plus its docs and code. Their "LLM
    summarizing condenser" swaps older events for a summary written by an LLM
    once the history gets too long, and keeps the original instructions.
  * Lindenbauer et al. 2025, "The Complexity Trap". Their summarization condition
    is what they compare masking against.

Write build_view so it matches the condenser the way The Complexity Trap set it up.
Things to find out:
  - what triggers a summary (number of turns? tokens?) and how much recent history stays
  - the prompt they use to summarize (copy it if it's published, and say where it's from)
  - whether the old summary gets folded into the new one or not
Put each setting and where you found it in docs/assignments/B_summarization.md.

tests/test_contract.py checks that you:
  - don't modify `history`, and keep the system prompt + task visible
  - put turns you folded into a summary in `ContextView.summarized_ids`, and any
    observations among them in `hidden_ids` too
  - charge the summarizer's own tokens and cost to the run through
    `ContextView.extra_prompt_tokens / extra_completion_tokens / extra_cost`.
    Don't skip this one. Most of what's known about summarization is about this cost.
  - only call the summarizer when you need to, not on every step

To call the model use `self.llm.complete(messages)`. It gives back an LLMResponse
with `.text, .prompt_tokens, .completion_tokens, .cost`. The tests use
`ScriptedLLM` instead of a real model.
"""

from ctxbench.llm import LLM
from ctxbench.messages import ContextView, Turn
from ctxbench.strategies.base import ContextStrategy, body, pinned  # noqa: F401


class LLMSummarization(ContextStrategy):
    name = "summarization"

    def __init__(self, llm: LLM, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
        # Add whatever parameters you need (trigger, keep_recent, ...) and set them
        # to the paper's values in configs/experiment.yaml.

    def build_view(self, history: list[Turn]) -> ContextView:
        raise NotImplementedError("Assignment B: implement LLM summarization (see the comment at the top).")
