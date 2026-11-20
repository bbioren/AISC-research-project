"""Assignment C: a third strategy from the literature. Pick one by Tue Nov 25.

Option 1 (default): masking + summarization hybrid
  Lindenbauer et al. 2025, "The Complexity Trap". They say mixing observation
  masking with an occasional LLM summary cuts cost even more. Find out how they
  combine the two (what triggers a summary, what gets masked). Once A's and B's
  classes exist you can build on them. Until then, write the combining logic and
  test it with ScriptedLLM.

Option 2: MemGPT-style paging
  Packer et al. 2023, "MemGPT: Towards LLMs as Operating Systems". The context
  acts like a small main memory, older stuff gets paged out to storage, and the
  agent can search it and page things back in with function calls. For our bash
  agent that means hidden observations go into a store and the agent gets
  commands to search and pull them back (see `handle_command` and
  `extra_instructions` in base.py).

If you go with option 2, rename the class and file to `paging` and update
strategies/__init__.py and configs/experiment.yaml.
Write down which one you picked, every setting, and where it came from in
docs/assignments/C_third_strategy.md.

Same rules as every other strategy (tests/test_contract.py). Anything the model
doesn't see in full goes in hidden_ids / summarized_ids, and any extra LLM calls
get charged through ContextView.extra_*.
"""

from ctxbench.llm import LLM
from ctxbench.messages import ContextView, Turn
from ctxbench.strategies.base import ContextStrategy, body, pinned  # noqa: F401


class HybridMaskingSummarization(ContextStrategy):
    name = "hybrid"

    def __init__(self, llm: LLM, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm

    def build_view(self, history: list[Turn]) -> ContextView:
        raise NotImplementedError("Assignment C: implement the strategy you picked (see the comment at the top).")
