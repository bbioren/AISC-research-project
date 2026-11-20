"""The agent loop. Same for every strategy; the strategy is the only thing that changes.

Each step: the strategy picks what the model sees, the model replies with one
```bash block, we run it, and the output becomes the next observation. It stops
when the model says `submit` (or runs out of steps or money). The final
`git diff` is the patch.
"""

import re
from dataclasses import asdict

from ctxbench.messages import Turn

SYSTEM_PROMPT = """You are a software engineer fixing an issue in the repository in your current directory.
Work step by step. In every reply, think briefly, then give EXACTLY ONE shell command in a ```bash block.
You only see command output, so use commands like `grep -rn`, `sed -n '1,80p' file`, `python -c`, and
write edits with `sed -i`, `cat <<'EOF' > file`, or a small python script.
Do not modify test files. When the issue is fixed, reply with the command `submit` on its own."""


def parse_command(text):
    blocks = re.findall(r"```(?:bash|sh)\s*\n(.*?)```", text, re.S)
    if len(blocks) == 1:
        return blocks[0].strip()
    if not blocks and text.strip().endswith("submit"):
        return "submit"
    return None


def run_agent(llm, strategy, env, task, max_steps=50, max_cost=1.0, max_output_chars=10_000):
    history = [Turn("system", SYSTEM_PROMPT, "system", 0, "system"), Turn("user", task, "task", 0, "task")]
    result = {"exit": "max_steps", "steps": 0, "tokens": 0, "cost": 0.0, "peak_prompt_tokens": 0, "hidden_per_step": []}

    for step in range(1, max_steps + 1):
        result["steps"] = step
        view = strategy.build_view(history)
        reply = llm.complete(view.messages)
        result["tokens"] += reply.tokens + view.extra_tokens
        result["cost"] += reply.cost + view.extra_cost
        result["peak_prompt_tokens"] = max(result["peak_prompt_tokens"], reply.prompt_tokens)
        result["hidden_per_step"].append(view.hidden_ids)
        history.append(Turn("assistant", reply.text, "action", step, f"act-{step}"))

        if result["cost"] > max_cost:
            result["exit"] = "max_cost"
            break
        command = parse_command(reply.text)
        if command == "submit":
            result["exit"] = "submitted"
            break
        if command is None:
            output = "Reply with exactly one ```bash block."
        else:
            code, output = env.run(command)
            output = f"(exit code {code})\n{output}"
            if len(output) > max_output_chars:
                output = output[: max_output_chars // 2] + "\n[... cut ...]\n" + output[-max_output_chars // 2 :]
        history.append(Turn("user", output, "observation", step, f"obs-{step}"))

    result["patch"] = env.run("git diff")[1]
    result["history"] = [asdict(t) for t in history]
    return result
