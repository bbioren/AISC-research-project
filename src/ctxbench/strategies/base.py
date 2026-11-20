from ctxbench.messages import ContextView, Turn


class ContextStrategy:
    """Picks what part of the history the model sees on each step.

    Rules every strategy follows (tests/test_strategies.py checks them):
      * always include the system prompt and the task, first
      * never change `history`
      * put every observation the model can't see in full in `hidden_ids`
    """

    name = "base"

    def build_view(self, history: list[Turn]) -> ContextView:
        raise NotImplementedError


def pinned(history):
    """The system prompt and the task."""
    return [t for t in history if t.kind in ("system", "task")]


def body(history):
    """Everything after the system prompt and the task."""
    return [t for t in history if t.kind not in ("system", "task")]
