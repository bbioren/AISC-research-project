"""The message types the agent loop and all the strategies share.

The agent always keeps the whole trajectory as a list of `Turn`s. Strategies
never change that list, they just decide what part of it the model gets to see
on each step. We hang on to the full history so we can do the failure analysis
later, since that's how we find out what the model didn't see.
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
    step: int  # which agent step this came from (0 for the system prompt and task)
    id: str = ""  # e.g. "obs-7" is the observation from step 7
    meta: dict = field(default_factory=dict)

    def as_message(self, content: str | None = None) -> dict:
        return {"role": self.role, "content": self.content if content is None else content}


@dataclass
class ContextView:
    """What a strategy sends the model on one step, plus some notes we use for analysis."""

    messages: list[dict]
    hidden_ids: list[str] = field(default_factory=list)  # turns the model can't see in full
    summarized_ids: list[str] = field(default_factory=list)  # turns that got rolled into a summary
    extra_prompt_tokens: int = 0  # tokens the strategy used itself, like summarizer calls
    extra_completion_tokens: int = 0
    extra_cost: float = 0.0
