"""ASSIGNMENT C: a third strategy from the literature. Pick ONE by Tue Nov 25.

Option 1 (default) -- Hybrid masking + summarization
  Lindenbauer et al., 2025, "The Complexity Trap": they report that combining
  observation masking with occasional LLM summarization lowers cost further.
  Find how they combine the two (what triggers summarization, what's masked).
  You can build on A's and B's classes once they exist; until then, write the
  combining logic against the interface and test with ScriptedLLM.

Option 2 -- MemGPT-style paging
  Packer et al., 2023, "MemGPT: Towards LLMs as Operating Systems": context is
  a small "main memory"; older content is paged out to external storage the
  agent can search and page back in with function calls. Adapt that to our
  bash agent: hidden observations go to a store, and the agent gets commands
  to search/retrieve them (see `handle_command` and `extra_instructions` in
  base.py).

If you choose option 2, rename the class/file to `paging`, and update the
registry in strategies/__init__.py and configs/experiment.yaml.
Record your choice, every setting, and its source in docs/assignments/C_third_strategy.md.

Rules: same contract as every strategy (tests/test_contract.py). Anything the
model doesn't see verbatim goes in hidden_ids / summarized_ids; any extra LLM
calls are charged via ContextView.extra_*.
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
        raise NotImplementedError("Assignment C: implement your chosen third strategy (see module docstring).")
