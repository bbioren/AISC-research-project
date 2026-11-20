from __future__ import annotations

from abc import ABC, abstractmethod

from ctxbench.messages import ContextView, Turn


class ContextStrategy(ABC):
    """Picks what part of the trajectory the model gets to see on each step.

    Every strategy has to follow a few rules:
      * `build_view` always includes the system prompt and the task.
      * It never changes `history`.
      * Anything the model doesn't see in full goes in `hidden_ids` or
        `summarized_ids`. The failure analysis depends on this.
    """

    name: str = "base"

    def __init__(self, **kwargs):
        self.config = kwargs

    @abstractmethod
    def build_view(self, history: list[Turn]) -> ContextView: ...

    # Only needed if your strategy gives the agent extra commands, like a `recall` command.
    def handle_command(self, command: str, history: list[Turn]) -> str | None:
        """If this strategy handles `command`, return the output to show the agent. Otherwise return None."""
        return None

    def extra_instructions(self) -> str:
        """Gets added to the system prompt. Use it to explain any extra commands your strategy adds."""
        return ""


def pinned(history: list[Turn]) -> list[Turn]:
    """The system prompt and the task. Every strategy has to keep these visible."""
    return [t for t in history if t.kind in ("system", "task")]


def body(history: list[Turn]) -> list[Turn]:
    return [t for t in history if t.kind not in ("system", "task")]
