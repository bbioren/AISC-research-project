"""The `ctxbench` command. `ctxbench -h` lists everything.

  ctxbench subset   --n 50 --seed 0              # pick the task subset (only once, then commit it)
  ctxbench run      configs/experiment.yaml      # run each strategy on each task
  ctxbench eval-cmd configs/experiment.yaml      # print the commands for SWE-bench scoring
  ctxbench report   configs/experiment.yaml      # table of tokens, cost and resolve rate
  ctxbench attribute configs/experiment.yaml     # failure analysis on the runs that failed
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_config(path: str) -> dict:
    cfg = yaml.safe_load(Path(path).read_text())
    cfg.setdefault("results_dir", "results")
    return cfg


def run_dir(cfg: dict) -> Path:
    return ROOT / cfg["results_dir"] / cfg["run_name"]


def cmd_subset(a):
    from ctxbench.data import make_subset

    out = ROOT / "configs" / f"subset_{a.n}_seed{a.seed}.txt"
    ids = make_subset(a.n, a.seed, out)
    print(f"wrote {len(ids)} instance ids to {out.relative_to(ROOT)}")


def cmd_run(a):
    from ctxbench.agent import Agent
    from ctxbench.data import load_instances, read_subset
    from ctxbench.env import DockerEnv
    from ctxbench.llm import LLM
    from ctxbench.strategies import make_strategy

    cfg = load_config(a.config)
    ids = read_subset(ROOT / cfg["subset"])
    if a.limit:
        ids = ids[: a.limit]
    by_id = {r["instance_id"]: r for r in load_instances(cfg.get("dataset", "princeton-nlp/SWE-bench_Verified"))}
    llm = LLM(**cfg["model"])
    only = set(a.strategy or [])

    for s in cfg["strategies"]:
        name, params = s["name"], s.get("params", {})
        label = s.get("label", name)
        if only and label not in only:
            continue
        out_dir = run_dir(cfg) / label
        out_dir.mkdir(parents=True, exist_ok=True)
        preds = out_dir.parent / f"{label}.predictions.jsonl"
        for iid in ids:
            out = out_dir / f"{iid}.json"
            if out.exists() and not a.overwrite:
                continue  # already done, so reruns pick up where they left off
            strategy = make_strategy(name, llm=LLM(**cfg.get("summarizer_model", cfg["model"])), **params)
            agent = Agent(llm, strategy, **cfg.get("agent", {}))
            print(f"[{label}] {iid} ...", flush=True)
            try:
                with DockerEnv(iid, cfg["image_template"]) as env:
                    res = agent.run(iid, by_id[iid]["problem_statement"], env)
            except Exception as e:  # print it and move on to the next task
                print(f"  error: {e}")
                continue
            out.write_text(json.dumps(asdict(res)))
            print(f"  {res.exit_reason} steps={res.steps} tokens={res.prompt_tokens} cost=${res.cost:.3f}")
        # Rebuild the predictions file SWE-bench needs from every run saved so far.
        with preds.open("w") as fh:
            for f in sorted(out_dir.glob("*.json")):
                r = json.loads(f.read_text())
                fh.write(json.dumps({"instance_id": r["instance_id"], "model_name_or_path": f"{cfg['run_name']}__{label}", "model_patch": r["patch"]}) + "\n")


def cmd_eval_cmd(a):
    cfg = load_config(a.config)
    for s in cfg["strategies"]:
        label = s.get("label", s["name"])
        preds = run_dir(cfg) / f"{label}.predictions.jsonl"
        print(
            "python -m swebench.harness.run_evaluation "
            f"--dataset_name {cfg.get('dataset', 'princeton-nlp/SWE-bench_Verified')} "
            f"--predictions_path {preds.relative_to(ROOT)} --max_workers 4 --run_id {cfg['run_name']}__{label}"
        )
    print("\n# After these finish, copy each '<model>.<run_id>.json' report to results/<run_name>/reports/<label>.json")


def _resolved(cfg, label):
    from ctxbench.metrics import load_resolved

    return load_resolved(run_dir(cfg) / "reports" / f"{label}.json")


def cmd_report(a):
    from ctxbench.metrics import load_runs, summarize, to_markdown

    cfg = load_config(a.config)
    runs = load_runs(run_dir(cfg))
    table = {label: summarize(rs, _resolved(cfg, label)) for label, rs in runs.items()}
    md = to_markdown(table)
    print(md)
    (run_dir(cfg) / "summary.md").write_text(md + "\n")


def cmd_attribute(a):
    from collections import Counter

    from ctxbench.attribution import attribute_run
    from ctxbench.data import load_instances
    from ctxbench.metrics import load_runs

    cfg = load_config(a.config)
    gold = {r["instance_id"]: r["patch"] for r in load_instances(cfg.get("dataset", "princeton-nlp/SWE-bench_Verified"))}
    out = []
    for label, rs in load_runs(run_dir(cfg)).items():
        resolved = _resolved(cfg, label) or set()
        rows = [attribute_run(r, gold[r["instance_id"]]) for r in rs if r["instance_id"] not in resolved]
        labels = Counter(v["label"] for row in rows for v in row["gold_files"].values())
        print(f"{label}: {len(rows)} unresolved, info-loss candidates={sum(r['info_loss_candidate'] for r in rows)}, "
              f"rediscoveries={sum(r['rediscoveries'] for r in rows)}, gold-file labels={dict(labels)}")
        out += rows
    (run_dir(cfg) / "attribution.json").write_text(json.dumps(out, indent=1))


def fake_history(n_steps: int, obs_lines: int = 3):
    """A made-up trajectory for trying out strategies: each step reads a file and gets its contents back."""
    from ctxbench.messages import Turn

    h = [Turn("system", "SYSTEM PROMPT", "system", 0, "system"), Turn("user", "TASK: fix the bug in utils.py", "task", 0, "task")]
    for s in range(1, n_steps + 1):
        h.append(Turn("assistant", f"Let me look at file{s}.py\n```bash\ncat file{s}.py\n```", "action", s, f"act-{s}"))
        lines = "\n".join(f"file{s}.py:{i}: some code" for i in range(1, obs_lines + 1))
        h.append(Turn("user", f"(exit code 0)\n{lines}", "observation", s, f"obs-{s}"))
    return h


def cmd_show_view(a):
    import ast

    from ctxbench.llm import ScriptedLLM
    from ctxbench.strategies import make_strategy

    params = {}
    for kv in a.param:
        k, _, v = kv.partition("=")
        try:
            params[k] = ast.literal_eval(v)
        except (ValueError, SyntaxError):
            params[k] = v
    llm = ScriptedLLM(lambda msgs: "<summary would go here>")
    strategy = make_strategy(a.strategy, llm=llm, **params)
    history = fake_history(a.steps, a.obs_lines)
    try:
        view = strategy.build_view(history)
    except NotImplementedError as e:
        print(f"{a.strategy} isn't implemented yet: {e}")
        return
    print(f"history: {len(history)} turns, {sum(len(t.content) for t in history)} chars")
    print(f"sent:    {len(view.messages)} messages, {sum(len(m['content']) for m in view.messages)} chars")
    print(f"hidden: {view.hidden_ids}\nsummarized: {view.summarized_ids}")
    print(f"extra tokens charged: {view.extra_prompt_tokens} prompt / {view.extra_completion_tokens} completion\n")
    for i, m in enumerate(view.messages):
        preview = m["content"].replace("\n", " | ")
        print(f"[{i:>2}] {m['role']:<9} {preview[:100]}" + ("..." if len(preview) > 100 else ""))


def load_dotenv(path: Path = ROOT / ".env") -> None:
    import os

    if path.exists():
        for line in path.read_text().splitlines():
            k, sep, v = line.partition("=")
            if sep and not k.strip().startswith("#") and v.strip():
                os.environ.setdefault(k.strip(), v.strip())


def main():
    load_dotenv()
    p = argparse.ArgumentParser(prog="ctxbench")
    sub = p.add_subparsers(required=True)
    s = sub.add_parser("subset"); s.add_argument("--n", type=int, default=50); s.add_argument("--seed", type=int, default=0); s.set_defaults(f=cmd_subset)
    s = sub.add_parser("run"); s.add_argument("config"); s.add_argument("--limit", type=int); s.add_argument("--strategy", action="append"); s.add_argument("--overwrite", action="store_true"); s.set_defaults(f=cmd_run)
    s = sub.add_parser("eval-cmd"); s.add_argument("config"); s.set_defaults(f=cmd_eval_cmd)
    s = sub.add_parser("report"); s.add_argument("config"); s.set_defaults(f=cmd_report)
    s = sub.add_parser("attribute"); s.add_argument("config"); s.set_defaults(f=cmd_attribute)
    s = sub.add_parser("show-view", help="print what a strategy sends the model on a fake history (no Docker/API key)")
    s.add_argument("--strategy", default="full_history"); s.add_argument("--steps", type=int, default=12)
    s.add_argument("--obs-lines", type=int, default=3)
    s.add_argument("--param", action="append", default=[], help="strategy param, e.g. --param window=3")
    s.set_defaults(f=cmd_show_view)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
