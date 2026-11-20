from ctxbench.messages import ContextView, Turn
from ctxbench.strategies.base import ContextStrategy


class FullHistory(ContextStrategy):
    """The baseline. No context management, the model gets everything on every step.

    This is the "conversation history" option from the ideation doc. Every other
    strategy gets compared to it on cost and on how many tasks it solves.
    """

    name = "full_history"

    def build_view(self, history: list[Turn]) -> ContextView:
        return ContextView(messages=[t.as_message() for t in history])
