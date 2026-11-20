"""Thin model wrapper. Uses LiteLLM so any provider works with one model string
(e.g. "gpt-4o-mini", "claude-haiku-4-5", "openrouter/..."). Records tokens + cost."""

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
        import litellm  # imported lazily so tests don't need it

        r = litellm.completion(
            model=self.model, messages=messages, temperature=self.temperature, max_tokens=self.max_tokens
        )
        try:
            cost = float(litellm.completion_cost(completion_response=r))
        except Exception:
            cost = 0.0  # unknown model pricing; tokens are still recorded
        return LLMResponse(
            text=r.choices[0].message.content or "",
            prompt_tokens=r.usage.prompt_tokens,
            completion_tokens=r.usage.completion_tokens,
            cost=cost,
        )


class ScriptedLLM(LLM):
    """Deterministic fake for tests and dry runs: replays a list of replies (or a function)."""

    def __init__(self, replies: list[str] | Callable[[list[dict]], str]):
        super().__init__(model="scripted")
        self.replies, self.calls = replies, []

    def complete(self, messages: list[dict]) -> LLMResponse:
        self.calls.append(messages)
        text = self.replies(messages) if callable(self.replies) else self.replies[len(self.calls) - 1]
        prompt_tokens = sum(len(m["content"]) for m in messages) // 4  # rough chars/4 estimate
        return LLMResponse(text=text, prompt_tokens=prompt_tokens, completion_tokens=len(text) // 4, cost=0.0)
