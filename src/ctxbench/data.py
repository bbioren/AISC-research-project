"""Loads our 50 SWE-bench Verified tasks. Everyone uses the same ones (configs/subset_50.txt)."""

from pathlib import Path

DATASET = "princeton-nlp/SWE-bench_Verified"
SUBSET = Path(__file__).resolve().parents[2] / "configs" / "subset_50.txt"


def load_tasks():
    from datasets import load_dataset

    wanted = set(SUBSET.read_text().split())
    return [dict(r) for r in load_dataset(DATASET, split="test") if r["instance_id"] in wanted]
