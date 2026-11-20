"""Loading SWE-bench Verified and our task subset.

We sample the subset once with a fixed seed and save it under configs/, so every
condition and every person runs on exactly the same tasks.
"""

from __future__ import annotations

import random
from pathlib import Path

DATASET = "princeton-nlp/SWE-bench_Verified"


def load_instances(dataset: str = DATASET, split: str = "test") -> list[dict]:
    from datasets import load_dataset

    return [dict(r) for r in load_dataset(dataset, split=split)]


def make_subset(n: int, seed: int = 0, out: Path | None = None, dataset: str = DATASET) -> list[str]:
    ids = sorted(r["instance_id"] for r in load_instances(dataset))
    chosen = sorted(random.Random(seed).sample(ids, n))
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(chosen) + "\n")
    return chosen


def read_subset(path: Path) -> list[str]:
    return [l.strip() for l in path.read_text().splitlines() if l.strip() and not l.startswith("#")]


def files_in_patch(patch: str) -> list[str]:
    """Files a diff changes. The failure analysis uses this to compare against the correct patch."""
    return sorted({l[6:].strip() for l in patch.splitlines() if l.startswith("+++ b/")})
