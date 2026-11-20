import pytest

from ctxbench.messages import Turn


def make_history(n_steps: int, obs_lines: int = 2) -> list[Turn]:
    """Makes a fake trajectory: system prompt, task, then an action and an observation for each step."""
    h = [Turn("system", "SYSTEM PROMPT", "system", 0, "system"), Turn("user", "TASK: fix the bug", "task", 0, "task")]
    for s in range(1, n_steps + 1):
        h.append(Turn("assistant", f"step {s}\n```bash\ncat file{s}.py\n```", "action", s, f"act-{s}"))
        body = "\n".join(f"file{s}.py line {i}" for i in range(obs_lines))
        h.append(Turn("user", f"(exit code 0)\n{body}", "observation", s, f"obs-{s}"))
    return h


@pytest.fixture
def history_factory():
    return make_history
