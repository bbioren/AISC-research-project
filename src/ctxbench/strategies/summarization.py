"""ASSIGNMENT B: LLM summarization (OpenHands-style condenser).

Source papers / code:
  * OpenHands (Wang et al., ICLR 2025) and its docs/code -- "LLM summarizing condenser": when the
    history gets too long, older events are replaced by an LLM-written summary,
    while the initial instructions are kept.
  * Lindenbauer et al., 2025, "The Complexity Trap" -- the summarization
    condition they compare masking against.

Your job: implement `build_view` to match the OpenHands condenser as configured
in *The Complexity Trap*. Find out:
  - when summarization triggers (number of turns? tokens?) and how much recent history is kept
  - the summarization prompt (copy it if it's published; cite where from)
  - whether summaries are cumulative (old summary re-summarized) or not
Record every choice and its source in docs/assignments/B_summarization.md.

Rules (checked by tests/test_contract.py):
  - Never mutate `history`; system prompt + task always visible.
  - Turns folded into a summary go in `ContextView.summarized_ids`; observations
    among them also go in `hidden_ids`.
  - The summarizer's own token usage and cost MUST be charged to the run via
    `ContextView.extra_prompt_tokens / extra_completion_tokens / extra_cost`.
    (The literature's main finding about summarization is about this cost.)
  - Call the summarizer only when needed, not every step.

Use `self.llm.complete(messages)`; it returns an LLMResponse with
`.text, .prompt_tokens, .completion_tokens, .cost`. In tests, `ScriptedLLM`
stands in for a real model.
"""

from ctxbench.llm import LLM
from ctxbench.messages import ContextView, Turn
from ctxbench.strategies.base import ContextStrategy, body, pinned  # noqa: F401


class LLMSummarization(ContextStrategy):
    name = "summarization"

    def __init__(self, llm: LLM, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
        # Add your own parameters (trigger, keep_recent, ...) and put their
        # paper-matched values in configs/experiment.yaml.

    def build_view(self, history: list[Turn]) -> ContextView:
        raise NotImplementedError("Assignment B: implement LLM summarization (see module docstring).")
