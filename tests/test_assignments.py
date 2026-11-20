"""Tests for each assignment. They check what your strategy does, not how you wrote it.

These are just to get you started. Once you know the paper's exact settings,
add tests for them here, like "with window=W, only the last W observations are
visible". They're skipped until your strategy exists.
"""

import pytest

from ctxbench.llm import ScriptedLLM
from ctxbench.strategies import make_strategy


def view(name, history, **params):
    llm = ScriptedLLM(lambda msgs: "SUMMARY")
    s = make_strategy(name, llm=llm, **params)
    try:
        return s, s.build_view(history), llm
    except NotImplementedError:
        pytest.skip(f"{name} not implemented yet")


# A: masking
def test_masking_keeps_most_recent_observation_and_hides_oldest(history_factory):
    h = history_factory(20)
    _, v, _ = view("masking", h)
    sent = "\n".join(m["content"] for m in v.messages)
    assert h[-1].content in sent  # the newest one should still be visible
    assert "obs-1" in v.hidden_ids  # the oldest one should be hidden


def test_masking_keeps_actions(history_factory):
    h = history_factory(20)
    _, v, _ = view("masking", h)
    sent = "\n".join(m["content"] for m in v.messages)
    assert all(t.content in sent for t in h if t.kind == "action")


def test_masking_makes_no_llm_calls(history_factory):
    _, _, llm = view("masking", history_factory(20))
    assert llm.calls == []


# B: summarization
def test_summarization_short_history_untouched(history_factory):
    _, v, llm = view("summarization", history_factory(1))
    assert llm.calls == [] and not v.summarized_ids


def test_summarization_long_history_summarized_and_charged(history_factory):
    _, v, llm = view("summarization", history_factory(40))
    assert len(llm.calls) >= 1
    assert any("SUMMARY" in m["content"] for m in v.messages)
    assert v.summarized_ids and v.extra_prompt_tokens > 0


def test_summarization_not_called_every_step(history_factory):
    s, _, llm = view("summarization", history_factory(40))
    h = history_factory(41)
    s.build_view(h)
    assert len(llm.calls) <= 1, "summarizing again on every step makes summarization look way more expensive than it really is"


# C: third strategy
def test_hybrid_compresses_long_history(history_factory):
    _, v, _ = view("hybrid", history_factory(40))
    assert v.hidden_ids or v.summarized_ids
