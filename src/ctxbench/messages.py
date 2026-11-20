"""The two types everything else passes around."""

from dataclasses import dataclass, field


@dataclass
class Turn:
    """One message in the agent's history."""

    role: str  # "system", "user" or "assistant"
    content: str
    kind: str  # "system", "task", "action" (the model's reply) or "observation" (command output)
    step: int  # which agent step it came from (0 for the system prompt and task)
    id: str  # e.g. "obs-7" is the output of step 7's command

    def as_message(self, content=None):
        """The dict we send to the model. Pass `content` to send different text instead."""
        return {"role": self.role, "content": self.content if content is None else content}


@dataclass
class ContextView:
    """What a strategy sends the model on one step."""

    messages: list
    hidden_ids: list = field(default_factory=list)  # observations the model can't see in full this step
    extra_tokens: int = 0  # tokens the strategy spent itself, e.g. on a summary call
    extra_cost: float = 0.0
