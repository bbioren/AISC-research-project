from ctxbench.messages import ContextView
from ctxbench.strategies.base import ContextStrategy


class FullHistory(ContextStrategy):
    """The baseline: no context management, the model sees everything every step."""

    name = "full_history"

    def build_view(self, history):
        return ContextView(messages=[t.as_message() for t in history])
