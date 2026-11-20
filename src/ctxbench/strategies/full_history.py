from ctxbench.messages import ContextView, Turn
from ctxbench.strategies.base import ContextStrategy


class FullHistory(ContextStrategy):
    """Baseline: no context management. Everything is sent every step.

    This is the "conversation history" condition from the ideation doc, and the
    reference point every other strategy's cost and success is compared to.
    """

    name = "full_history"

    def build_view(self, history: list[Turn]) -> ContextView:
        return ContextView(messages=[t.as_message() for t in history])
