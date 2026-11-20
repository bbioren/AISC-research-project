"""Minimal bash-only agent loop (in the style of mini-swe-agent).

Each step the model replies with reasoning plus exactly one ```bash block. The
command runs in the environment, its output becomes an observation, repeat.
The agent finishes by running `submit`, and the final `git diff` is the patch.

The loop is deliberately simple and identical across conditions: the ONLY thing
that varies between experimental conditions is the ContextStrategy.
"""

from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass, field

from ctxbench.env import Environment
from ctxbench.llm import LLM
from ctxbench.messages import Turn
from ctxbench.strategies.base import ContextStrategy

SYSTEM_PROMPT = """You are a software engineer fixing an issue in the repository in your current directory.
Work step by step. In every reply, think briefly, then give EXACTLY ONE shell command in a ```bash block.
You only see command output, so use commands like `grep -rn`, `sed -n '1,80p' file`, `python -c`, and
write edits with `sed -i`, `cat <<'EOF' > file`, or a small python script.
Do not modify test files. When the issue is fixed, reply with the command `submit` on its own.
{extra}"""

TASK_TEMPLATE = "Resolve this GitHub issue:\n\n{problem_statement}"

_BASH = re.compile(r"```(?:bash|sh)\s*\n(.*?)```", re.S)


@dataclass
class RunResult:
    instance_id: str
    strategy: str
    patch: str
    exit_reason: str  # submitted | step_limit | cost_limit | format_errors | error
    steps: int
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost: float = 0.0
    wall_time_s: float = 0.0
    peak_context_tokens: int = 0  # largest single-request prompt
    history: list[dict] = field(default_factory=list)
    views: list[dict] = field(default_factory=list)  # per-step: what was hidden/summarized
    recall_log: list[dict] = field(default_factory=list)


def parse_command(text: str) -> str | None:
    blocks = _BASH.findall(text)
    if len(blocks) == 1:
        return blocks[0].strip()
    if not blocks and text.strip().splitlines()[-1:] == ["submit"]:
        return "submit"
    return None


def truncate(output: str, max_chars: int) -> str:
    if len(output) <= max_chars:
        return output
    half = max_chars // 2
    return f"{output[:half]}\n[... {len(output) - max_chars} chars truncated ...]\n{output[-half:]}"


class Agent:
    def __init__(
        self,
        llm: LLM,
        strategy: ContextStrategy,
        step_limit: int = 50,
        cost_limit: float = 1.0,
        obs_max_chars: int = 10_000,
        cmd_timeout: int = 120,
        max_format_errors: int = 3,
    ):
        self.llm, self.strategy = llm, strategy
        self.step_limit, self.cost_limit = step_limit, cost_limit
        self.obs_max_chars, self.cmd_timeout, self.max_format_errors = obs_max_chars, cmd_timeout, max_format_errors

    def run(self, instance_id: str, problem_statement: str, env: Environment) -> RunResult:
        t0 = time.time()
        sys_prompt = SYSTEM_PROMPT.format(extra=self.strategy.extra_instructions())
        history = [
            Turn("system", sys_prompt, "system", 0, "system"),
            Turn("user", TASK_TEMPLATE.format(problem_statement=problem_statement), "task", 0, "task"),
        ]
        res = RunResult(instance_id, self.strategy.name, patch="", exit_reason="step_limit", steps=0)
        format_errors = 0

        for step in range(1, self.step_limit + 1):
            res.steps = step
            view = self.strategy.build_view(history)
            res.views.append({"step": step, "hidden": view.hidden_ids, "summarized": view.summarized_ids})
            resp = self.llm.complete(view.messages)
            res.prompt_tokens += resp.prompt_tokens + view.extra_prompt_tokens
            res.completion_tokens += resp.completion_tokens + view.extra_completion_tokens
            res.cost += resp.cost + view.extra_cost
            res.peak_context_tokens = max(res.peak_context_tokens, resp.prompt_tokens)
            history.append(Turn("assistant", resp.text, "action", step, f"act-{step}"))

            if res.cost > self.cost_limit:
                res.exit_reason = "cost_limit"
                break

            cmd = parse_command(resp.text)
            if cmd is None:
                format_errors += 1
                history.append(Turn("user", "Reply with exactly one ```bash block.", "note", step, f"note-{step}"))
                if format_errors >= self.max_format_errors:
                    res.exit_reason = "format_errors"
                    break
                continue
            if cmd == "submit":
                res.exit_reason = "submitted"
                break

            special = self.strategy.handle_command(cmd, history)
            if special is not None:
                out = special
            else:
                r = env.execute(cmd, timeout=self.cmd_timeout)
                out = f"(exit code {r.returncode})\n{r.output}"
            history.append(Turn("user", truncate(out, self.obs_max_chars), "observation", step, f"obs-{step}"))

        res.patch = env.diff()
        res.wall_time_s = time.time() - t0
        res.history = [asdict(t) for t in history]
        res.recall_log = list(getattr(self.strategy, "recall_log", []))
        return res
