"""Failure analysis: did a run fail because the model couldn't see something anymore?

As far as we can tell nobody has really done this analysis yet. The rules below
are a rough first try. We need to check them by hand on a bunch of trajectories,
so treat the labels as guesses until then.

For each failed run we look at the correct patch from SWE-bench to see which
files actually needed to change. Then for each of those files:

  never_seen       - no output ever mentioned it. The agent never found the right
                     place, so context management isn't what went wrong.
  seen_then_hidden - it showed up in some output, but by the last step all of that
                     output had been masked or summarized, and the agent's patch
                     doesn't touch the file. This one might be a lost-information failure.
  seen_visible     - it was still visible at the end, so losing context wasn't the problem.

We also count "rediscoveries", which is when the agent runs a command again after
its earlier output got hidden. That's basically how many steps masking wasted.
"""

from __future__ import annotations

import os
from collections import Counter

from ctxbench.agent import parse_command
from ctxbench.data import files_in_patch


def _mentions(text: str, path: str) -> bool:
    return path in text or os.path.basename(path) in text


def attribute_run(run: dict, gold_patch: str) -> dict:
    history = run["history"]
    observations = [t for t in history if t["kind"] == "observation"]
    final_hidden = set(run["views"][-1]["hidden"]) if run["views"] else set()
    pred_files = set(files_in_patch(run["patch"]))

    per_file = {}
    for f in files_in_patch(gold_patch):
        seen = [o["id"] for o in observations if _mentions(o["content"], f)]
        if not seen:
            label = "never_seen"
        elif all(i in final_hidden for i in seen) and f not in pred_files:
            label = "seen_then_hidden"
        else:
            label = "seen_visible"
        per_file[f] = {"label": label, "observations": seen}

    # A rediscovery is the agent repeating an earlier command whose output was already hidden by then.
    actions = [t for t in history if t["kind"] == "action"]
    hidden_at = {v["step"]: set(v["hidden"]) for v in run["views"]}
    seen_cmds: dict[str, int] = {}
    rediscoveries = 0
    for a in actions:
        cmd = parse_command(a["content"])
        if not cmd or cmd == "submit":
            continue
        prev = seen_cmds.get(cmd)
        if prev is not None and f"obs-{prev}" in hidden_at.get(a["step"], set()):
            rediscoveries += 1
        seen_cmds[cmd] = a["step"]

    labels = Counter(v["label"] for v in per_file.values())
    return {
        "instance_id": run["instance_id"],
        "strategy": run["strategy"],
        "gold_files": per_file,
        "info_loss_candidate": labels["seen_then_hidden"] > 0,
        "rediscoveries": rediscoveries,
    }
