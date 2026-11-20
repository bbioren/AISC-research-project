"""Turns the saved runs and SWE-bench reports into one results table."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, median


def load_runs(run_dir: Path) -> dict[str, list[dict]]:
    """Reads results/<run_name>/<strategy>/*.json and groups the runs by strategy."""
    out: dict[str, list[dict]] = {}
    for sdir in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        runs = [json.loads(f.read_text()) for f in sorted(sdir.glob("*.json"))]
        if runs:
            out[sdir.name] = runs
    return out


def load_resolved(report_path: Path | None) -> set[str] | None:
    """Gets the ids of the tasks that passed from a SWE-bench report."""
    if not report_path or not report_path.exists():
        return None
    return set(json.loads(report_path.read_text()).get("resolved_ids", []))


def summarize(runs: list[dict], resolved: set[str] | None) -> dict:
    row = {
        "n": len(runs),
        "submitted": sum(r["exit_reason"] == "submitted" for r in runs),
        "mean_prompt_tokens": round(mean(r["prompt_tokens"] for r in runs)),
        "median_prompt_tokens": round(median(r["prompt_tokens"] for r in runs)),
        "mean_peak_context": round(mean(r["peak_context_tokens"] for r in runs)),
        "mean_cost_usd": round(mean(r["cost"] for r in runs), 4),
        "total_cost_usd": round(sum(r["cost"] for r in runs), 2),
        "mean_steps": round(mean(r["steps"] for r in runs), 1),
        "mean_wall_s": round(mean(r["wall_time_s"] for r in runs), 1),
    }
    if resolved is not None:
        k = sum(r["instance_id"] in resolved for r in runs)
        row["resolved"] = k
        row["resolve_rate"] = round(k / len(runs), 3)
    return row


def to_markdown(table: dict[str, dict]) -> str:
    cols = sorted({c for row in table.values() for c in row}, key=lambda c: (c != "n", c))
    lines = ["| strategy | " + " | ".join(cols) + " |", "|" + "---|" * (len(cols) + 1)]
    for s, row in table.items():
        lines.append(f"| {s} | " + " | ".join(str(row.get(c, "")) for c in cols) + " |")
    return "\n".join(lines)
