"""Tests for the shared code (agent loop, parsing, failure analysis). No API keys, internet or Docker needed."""

import subprocess

import pytest

from ctxbench.agent import Agent, parse_command
from ctxbench.attribution import attribute_run
from ctxbench.env import LocalEnv
from ctxbench.llm import ScriptedLLM
from ctxbench.strategies import make_strategy


def test_full_history_sends_everything(history_factory):
    h = history_factory(10)
    v = make_strategy("full_history").build_view(h)
    assert len(v.messages) == len(h) and not v.hidden_ids


@pytest.mark.parametrize(
    "text,expected",
    [("think\n```bash\nls\n```", "ls"), ("done\nsubmit", "submit"), ("```bash\na\n```\n```bash\nb\n```", None), ("no command", None)],
)
def test_parse_command(text, expected):
    assert parse_command(text) == expected


def test_agent_loop_end_to_end_on_toy_repo(tmp_path):
    subprocess.run(
        "git init -q && echo 'x = 1' > a.py && git add . && git -c user.email=t@t -c user.name=t commit -qm init",
        shell=True, cwd=tmp_path, check=True,
    )
    llm = ScriptedLLM(["look\n```bash\ncat a.py\n```", "fix\n```bash\necho 'x = 2' > a.py\n```", "submit"])
    res = Agent(llm, make_strategy("full_history"), step_limit=10).run("toy__toy-1", "make x 2", LocalEnv(str(tmp_path)))
    assert res.exit_reason == "submitted" and "+x = 2" in res.patch and res.steps == 3


def test_attribution_flags_seen_then_hidden():
    gold = "--- a/pkg/core.py\n+++ b/pkg/core.py\n@@\n-a\n+b\n"
    run = {
        "instance_id": "x", "strategy": "masking", "patch": "",
        "history": [
            {"kind": "action", "content": "search\n```bash\ngrep -rn bug\n```", "step": 1, "id": "act-1"},
            {"kind": "observation", "content": "pkg/core.py:10: bug here", "step": 1, "id": "obs-1"},
            {"kind": "action", "content": "again\n```bash\ngrep -rn bug\n```", "step": 2, "id": "act-2"},
        ],
        "views": [{"step": 1, "hidden": []}, {"step": 2, "hidden": ["obs-1"]}],
    }
    out = attribute_run(run, gold)
    assert out["gold_files"]["pkg/core.py"]["label"] == "seen_then_hidden"
    assert out["info_loss_candidate"] and out["rediscoveries"] == 1
