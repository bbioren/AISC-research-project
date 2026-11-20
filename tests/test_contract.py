"""Rules EVERY context strategy must follow. Runs against everything in the registry.

Unimplemented strategies are skipped (not failed), so this file goes green as
assignments land. Once yours is implemented, all of these must pass.
"""

import copy

import pytest

from ctxbench.llm import ScriptedLLM
from ctxbench.strategies import REGISTRY, make_strategy


def build(name, history):
    llm = ScriptedLLM(lambda msgs: "SUMMARY OF EARLIER WORK")
    strat = make_strategy(name, llm=llm)
    try:
        return strat, strat.build_view(history)
    except NotImplementedError:
        pytest.skip(f"{name} not implemented yet")


@pytest.mark.parametrize("name", sorted(REGISTRY))
@pytest.mark.parametrize("n_steps", [1, 8, 40])
class TestContract:
    def test_does_not_mutate_history(self, name, n_steps, history_factory):
        h = history_factory(n_steps)
        before = copy.deepcopy(h)
        build(name, h)
        assert h == before

    def test_system_and_task_always_first(self, name, n_steps, history_factory):
        _, v = build(name, history_factory(n_steps))
        assert v.messages[0] == {"role": "system", "content": "SYSTEM PROMPT"}
        assert v.messages[1] == {"role": "user", "content": "TASK: fix the bug"}

    def test_messages_well_formed(self, name, n_steps, history_factory):
        _, v = build(name, history_factory(n_steps))
        for m in v.messages:
            assert set(m) == {"role", "content"} and m["role"] in ("system", "user", "assistant")
            assert isinstance(m["content"], str)

    def test_hidden_ids_are_real_observations(self, name, n_steps, history_factory):
        h = history_factory(n_steps)
        _, v = build(name, h)
        obs_ids = {t.id for t in h if t.kind == "observation"}
        assert set(v.hidden_ids) <= obs_ids

    def test_visible_observations_not_listed_as_hidden(self, name, n_steps, history_factory):
        h = history_factory(n_steps)
        _, v = build(name, h)
        sent = "\n".join(m["content"] for m in v.messages)
        for t in h:
            if t.kind == "observation" and t.id in v.hidden_ids:
                continue
            if t.kind == "observation" and t.id not in v.summarized_ids:
                assert t.content in sent, f"{t.id} is neither visible nor marked hidden/summarized"

    def test_long_history_gets_shorter_unless_baseline(self, name, n_steps, history_factory):
        if name == "full_history" or n_steps < 40:
            pytest.skip("only checked for compressing strategies on long histories")
        h = history_factory(n_steps, obs_lines=30)
        _, v = build(name, h)
        full = sum(len(t.content) for t in h)
        assert sum(len(m["content"]) for m in v.messages) < 0.5 * full
