"""Failure attribution: did a run fail *because* information was hidden from the model?

This is the analysis the literature hasn't done (see README "Novelty"). The
heuristics below are a first pass meant to be iterated on and validated by hand
on a sample of trajectories -- treat the labels as candidates, not ground truth.

For each unresolved run we use the gold patch (from SWE-bench) to find which
files actually needed editing, then ask, for each gold file:

  never_seen       -- no observation ever mentioned it. A search/localization
                      failure; context management is not the cause.
  seen_then_hidden -- it appeared in an observation, but by the last step every
                      such observation was masked/summarized away, and the agent's
                      patch does not touch it. Candidate information-loss failure.
  seen_visible     -- it was still visible at the end. Not a context-loss failure.

We also count "rediscoveries": the agent re-running an earlier command after
that command's output was hidden -- a direct measure of steps wasted by masking.
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

    # Rediscovery: an action whose command matches an earlier action whose output was hidden at that time.
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
