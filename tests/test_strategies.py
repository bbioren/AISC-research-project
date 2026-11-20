"""Run with `pytest`. Strategies nobody has written yet show up as skipped.

The first few tests are rules every strategy follows. Below them are a couple of
starter tests per strategy. Add your own for the paper's exact settings.
"""

import copy
import subprocess

import pytest

from ctxbench.agent import run_agent
from ctxbench.cli import fake_history
from ctxbench.env import LocalEnv
from ctxbench.llm import FakeLLM
from ctxbench.strategies import STRATEGIES


def view(name, steps):
    """Build `name` and run it on a fake history. Skips the test if it isn't written yet."""
    llm = FakeLLM(lambda m: "SUMMARY")
    history = fake_history(steps)
    try:
        return STRATEGIES[name](llm).build_view(history), history, llm
    except NotImplementedError:
        pytest.skip(f"{name} isn't written yet")


# Rules for every strategy

@pytest.mark.parametrize("name", STRATEGIES)
@pytest.mark.parametrize("steps", [1, 40])
def test_rules(name, steps):
    v, history, _ = view(name, steps)
    assert v.messages[0]["content"] == "SYSTEM PROMPT"  # system prompt first
    assert v.messages[1]["content"] == "TASK: fix the bug"  # then the task
    sent = "\n".join(m["content"] for m in v.messages)
    for t in history:
        if t.kind == "observation" and t.id not in v.hidden_ids:
            assert t.content in sent, f"{t.id} isn't sent in full, so it should be in hidden_ids"


@pytest.mark.parametrize("name", STRATEGIES)
def test_does_not_change_history(name):
    llm = FakeLLM(lambda m: "SUMMARY")
    history = fake_history(40)
    before = copy.deepcopy(history)
    try:
        STRATEGIES[name](llm).build_view(history)
    except NotImplementedError:
        pytest.skip(f"{name} isn't written yet")
    assert history == before


# A: masking

def test_masking_hides_old_keeps_new():
    v, history, llm = view("masking", 40)
    assert "obs-1" in v.hidden_ids and "obs-40" not in v.hidden_ids
    assert llm.calls == []  # masking never calls the model


# B: summarization

def test_summarization_leaves_short_history_alone():
    v, _, llm = view("summarization", 1)
    assert llm.calls == [] and v.hidden_ids == []


def test_summarization_summarizes_long_history_and_counts_the_cost():
    v, _, llm = view("summarization", 40)
    assert len(llm.calls) >= 1 and v.extra_tokens > 0
    assert any("SUMMARY" in m["content"] for m in v.messages)


# C: hybrid

def test_hybrid_compresses_long_history():
    v, _, _ = view("hybrid", 40)
    assert v.hidden_ids


# The agent loop itself, on a toy repo (no Docker or API key)

def test_agent_fixes_toy_repo(tmp_path):
    subprocess.run("git init -q && echo 'x = 1' > a.py && git add . && git -c user.email=t@t -c user.name=t commit -qm init",
                   shell=True, cwd=tmp_path, check=True)
    replies = iter(["```bash\ncat a.py\n```", "```bash\necho 'x = 2' > a.py\n```", "submit"])
    result = run_agent(FakeLLM(lambda m: next(replies)), STRATEGIES["full_history"](None), LocalEnv(tmp_path), "make x 2")
    assert result["exit"] == "submitted" and "+x = 2" in result["patch"]
