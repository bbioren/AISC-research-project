"""Small wrapper around the model. It goes through LiteLLM, so you can switch
providers just by changing the model string ("gpt-4o-mini", "claude-haiku-4-5",
"openrouter/..."). It also keeps track of tokens and cost."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class LLMResponse:
    text: str
    prompt_tokens: int
    completion_tokens: int
    cost: float


class LLM:
    def __init__(self, model: str, temperature: float = 0.0, max_tokens: int = 2048):
        self.model, self.temperature, self.max_tokens = model, temperature, max_tokens

    def complete(self, messages: list[dict]) -> LLMResponse:
        import litellm  # imported here so the tests don't need litellm installed

        r = litellm.completion(
            model=self.model, messages=messages, temperature=self.temperature, max_tokens=self.max_tokens
        )
        try:
            cost = float(litellm.completion_cost(completion_response=r))
        except Exception:
            cost = 0.0  # LiteLLM doesn't know this model's price, but we still have the tokens
        return LLMResponse(
            text=r.choices[0].message.content or "",
            prompt_tokens=r.usage.prompt_tokens,
            completion_tokens=r.usage.completion_tokens,
            cost=cost,
        )


class ScriptedLLM(LLM):
    """Fake model for tests. It just plays back a list of replies you give it, or calls a function."""

    def __init__(self, replies: list[str] | Callable[[list[dict]], str]):
        super().__init__(model="scripted")
        self.replies, self.calls = replies, []

    def complete(self, messages: list[dict]) -> LLMResponse:
        self.calls.append(messages)
        text = self.replies(messages) if callable(self.replies) else self.replies[len(self.calls) - 1]
        prompt_tokens = sum(len(m["content"]) for m in messages) // 4  # about 4 characters per token, close enough for tests
        return LLMResponse(text=text, prompt_tokens=prompt_tokens, completion_tokens=len(text) // 4, cost=0.0)
