"""Message model shared by the agent loop and every context strategy.

The agent keeps the *full* trajectory as a list of `Turn`s. A context strategy
never mutates that list; it only decides what view of it is sent to the model
on each step. Keeping the full history around is what makes failure
attribution possible later (we can always ask "what did the model NOT see?").
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Kind = Literal["system", "task", "action", "observation", "note"]


@dataclass
class Turn:
    role: Literal["system", "user", "assistant"]
    content: str
    kind: Kind
    step: int  # agent step that produced this turn (0 for system/task)
    id: str = ""  # stable id, e.g. "obs-7" for the observation at step 7
    meta: dict = field(default_factory=dict)

    def as_message(self, content: str | None = None) -> dict:
        return {"role": self.role, "content": self.content if content is None else content}


@dataclass
class ContextView:
    """What a strategy decided to send this step, plus bookkeeping for analysis."""

    messages: list[dict]
    hidden_ids: list[str] = field(default_factory=list)  # turns not visible verbatim
    summarized_ids: list[str] = field(default_factory=list)  # turns folded into a summary
    extra_prompt_tokens: int = 0  # tokens the strategy itself spent (e.g. summarizer calls)
    extra_completion_tokens: int = 0
    extra_cost: float = 0.0
