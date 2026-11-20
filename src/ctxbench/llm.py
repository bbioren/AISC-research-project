"""Calls the model through LiteLLM, so any provider works by changing the model name."""

from dataclasses import dataclass


@dataclass
class Response:
    text: str
    tokens: int  # prompt + completion
    prompt_tokens: int
    cost: float


class LLM:
    def __init__(self, model):
        self.model = model

    def complete(self, messages):
        import litellm  # imported here so the tests don't need it

        r = litellm.completion(model=self.model, messages=messages, temperature=0.0)
        try:
            cost = litellm.completion_cost(completion_response=r)
        except Exception:
            cost = 0.0  # LiteLLM doesn't know this model's price
        return Response(r.choices[0].message.content or "", r.usage.total_tokens, r.usage.prompt_tokens, cost)


class FakeLLM:
    """For tests and show-view. Replies with whatever `reply(messages)` returns."""

    def __init__(self, reply):
        self.reply = reply
        self.calls = []

    def complete(self, messages):
        self.calls.append(messages)
        prompt = sum(len(m["content"]) for m in messages) // 4  # roughly 4 characters per token
        text = self.reply(messages)
        return Response(text, prompt + len(text) // 4, prompt, 0.0)
