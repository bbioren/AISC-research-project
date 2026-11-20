from __future__ import annotations

from abc import ABC, abstractmethod

from ctxbench.messages import ContextView, Turn


class ContextStrategy(ABC):
    """Decides which view of the full trajectory the model sees on each step.

    Contract:
      * `build_view` must always include the system prompt and the task statement.
      * It must not mutate `history`.
      * Anything not shown verbatim goes in `hidden_ids` / `summarized_ids`, so
        attribution can reason about information loss.
    """

    name: str = "base"

    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    def build_view(self, history: list[Turn]) -> ContextView: ...

    # Optional hook for strategies that expose extra agent commands (e.g. `recall`).
    def handle_command(self, command: str, history: list[Turn]) -> str | None:
        """Return an observation string if this strategy handles `command`, else None."""
        return None

    def extra_instructions(self) -> str:
        """Text appended to the system prompt describing strategy-specific commands."""
        return ""


def pinned(history: list[Turn]) -> list[Turn]:
    """System prompt + task statement: always visible under every strategy."""
    return [t for t in history if t.kind in ("system", "task")]


def body(history: list[Turn]) -> list[Turn]:
    return [t for t in history if t.kind not in ("system", "task")]
