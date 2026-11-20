"""Where the agent's commands run.

DockerEnv: one container per SWE-bench task, repo at /testbed. Used for real runs.
LocalEnv: a folder on your machine. Only for trying things on a throwaway toy repo.
"""

import subprocess
import uuid


def _run(args, cwd=None, timeout=120):
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return 124, f"[timed out after {timeout}s]"


class LocalEnv:
    def __init__(self, folder):
        self.folder = folder

    def run(self, command):
        return _run(["bash", "-lc", command], cwd=self.folder)

    def close(self):
        pass


class DockerEnv:
    # SWE-bench's prebuilt images on Docker Hub. Double check the name against the swebench version you install.
    IMAGE = "swebench/sweb.eval.x86_64.{}:latest"

    def __init__(self, instance_id):
        image = self.IMAGE.format(instance_id.lower().replace("__", "_1776_"))
        self.name = f"ctxbench-{uuid.uuid4().hex[:8]}"
        code, out = _run(["docker", "run", "-d", "--rm", "--name", self.name, "-w", "/testbed", image, "sleep", "infinity"], timeout=600)
        if code != 0:
            raise RuntimeError(f"couldn't start {image}: {out}")

    def run(self, command):
        return _run(["docker", "exec", "-w", "/testbed", self.name, "bash", "-lc", command])

    def close(self):
        _run(["docker", "rm", "-f", self.name])
