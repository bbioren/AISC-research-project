"""Where the agent's bash commands actually run.

DockerEnv starts one container per SWE-bench task, with the repo at /testbed.
This is what the real experiments use. The image names are supposed to follow
SWE-bench's naming, but double check `image_template` against whatever swebench
version you installed. `python -m swebench.harness.prepare_images` can build or
pull them.

LocalEnv just runs commands in a folder on your machine. Only use it to try the
loop out on a throwaway toy repo. Don't point it at anything you care about.
"""

from __future__ import annotations

import subprocess
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ExecResult:
    output: str
    returncode: int
    timed_out: bool = False


class Environment(ABC):
    @abstractmethod
    def execute(self, command: str, timeout: int = 120) -> ExecResult: ...

    def diff(self) -> str:
        return self.execute("git -c core.fileMode=false diff", timeout=60).output

    def close(self) -> None: ...

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def _run(argv: list[str], timeout: int, cwd: str | None = None) -> ExecResult:
    try:
        p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return ExecResult(output=p.stdout + p.stderr, returncode=p.returncode)
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        return ExecResult(output=out + f"\n[command timed out after {timeout}s]", returncode=124, timed_out=True)


class LocalEnv(Environment):
    def __init__(self, workdir: str):
        self.workdir = workdir

    def execute(self, command: str, timeout: int = 120) -> ExecResult:
        return _run(["bash", "-lc", command], timeout, cwd=self.workdir)


class DockerEnv(Environment):
    def __init__(self, instance_id: str, image_template: str, workdir: str = "/testbed"):
        self.image = image_template.format(
            instance_id=instance_id,
            instance_id_lower=instance_id.lower(),
            # The SWE-bench images on Docker Hub write "__" as "_1776_" in their names.
            instance_id_1776=instance_id.lower().replace("__", "_1776_"),
        )
        self.workdir = workdir
        self.name = f"ctxbench-{instance_id.lower().replace('/', '_')}-{uuid.uuid4().hex[:6]}"
        r = _run(["docker", "run", "-d", "--rm", "--name", self.name, "-w", workdir, self.image, "sleep", "infinity"], 600)
        if r.returncode != 0:
            raise RuntimeError(f"failed to start {self.image}: {r.output}")

    def execute(self, command: str, timeout: int = 120) -> ExecResult:
        return _run(["docker", "exec", "-w", self.workdir, self.name, "bash", "-lc", command], timeout)

    def close(self) -> None:
        _run(["docker", "rm", "-f", self.name], 60)
