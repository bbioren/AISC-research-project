"""The `ctxbench` command.

  ctxbench show-view --strategy masking          # what a strategy sends the model, on a fake history
  ctxbench run --strategy masking --limit 2      # run the agent on real SWE-bench tasks (needs Docker + API key)
"""

import argparse
import json
import os
from pathlib import Path

from ctxbench.llm import LLM, FakeLLM
from ctxbench.messages import Turn
from ctxbench.strategies import STRATEGIES

ROOT = Path(__file__).resolve().parents[2]


def fake_history(steps):
    h = [Turn("system", "SYSTEM PROMPT", "system", 0, "system"), Turn("user", "TASK: fix the bug", "task", 0, "task")]
    for s in range(1, steps + 1):
        h.append(Turn("assistant", f"```bash\ncat file{s}.py\n```", "action", s, f"act-{s}"))
        h.append(Turn("user", f"(exit code 0)\ncontents of file{s}.py", "observation", s, f"obs-{s}"))
    return h


def show_view(args):
    strategy = STRATEGIES[args.strategy](FakeLLM(lambda m: "<a summary would go here>"))
    history = fake_history(args.steps)
    view = strategy.build_view(history)
    print(f"history has {len(history)} turns, the model gets sent {len(view.messages)} messages")
    print(f"hidden: {view.hidden_ids}   extra tokens: {view.extra_tokens}\n")
    for i, m in enumerate(view.messages):
        print(f"[{i:>2}] {m['role']:<9} {m['content'].replace(chr(10), ' | ')[:100]}")


def run(args):
    from ctxbench.agent import run_agent
    from ctxbench.data import load_tasks
    from ctxbench.env import DockerEnv

    llm = LLM(args.model)
    out_dir = ROOT / "results" / args.strategy
    out_dir.mkdir(parents=True, exist_ok=True)
    for task in load_tasks()[: args.limit]:
        out = out_dir / f"{task['instance_id']}.json"
        if out.exists():
            continue  # already done, so a rerun picks up where it left off
        print(task["instance_id"], flush=True)
        env = DockerEnv(task["instance_id"])
        try:
            result = run_agent(llm, STRATEGIES[args.strategy](llm), env, task["problem_statement"])
        finally:
            env.close()
        result["instance_id"] = task["instance_id"]
        out.write_text(json.dumps(result))
        print(f"  {result['exit']}, {result['steps']} steps, {result['tokens']} tokens, ${result['cost']:.3f}")

    # SWE-bench wants all the patches in one file
    preds = ROOT / "results" / f"{args.strategy}.jsonl"
    with preds.open("w") as f:
        for p in sorted(out_dir.glob("*.json")):
            r = json.loads(p.read_text())
            f.write(json.dumps({"instance_id": r["instance_id"], "model_name_or_path": args.strategy, "model_patch": r["patch"]}) + "\n")
    print(f"\nTo score: python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Verified "
          f"--predictions_path {preds.relative_to(ROOT)} --max_workers 4 --run_id {args.strategy}")


def main():
    env_file = ROOT / ".env"  # API keys
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            key, _, value = line.partition("=")
            if value.strip() and not key.startswith("#"):
                os.environ.setdefault(key.strip(), value.strip())

    p = argparse.ArgumentParser(prog="ctxbench")
    sub = p.add_subparsers(required=True)
    s = sub.add_parser("show-view")
    s.add_argument("--strategy", default="full_history", choices=STRATEGIES)
    s.add_argument("--steps", type=int, default=10)
    s.set_defaults(f=show_view)
    s = sub.add_parser("run")
    s.add_argument("--strategy", required=True, choices=STRATEGIES)
    s.add_argument("--limit", type=int, default=50)
    s.add_argument("--model", default="gpt-4o-mini")
    s.set_defaults(f=run)
    args = p.parse_args()
    args.f(args)


if __name__ == "__main__":
    main()
