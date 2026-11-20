# What does a coding agent forget?

Our AISC research project on context management for coding agents.

A coding agent's context fills up fast, mostly with output from the commands it runs. There are a few known ways to cut it down: hide old outputs (masking), summarize old turns with a model, or mix the two. *The Complexity Trap* (Lindenbauer et al. 2025) compared these and found masking is about half the cost and works as well. We're reproducing those strategies first, and then picking our own method based on where they fail.

**Start with [`docs/GUIDE.md`](docs/GUIDE.md).** It covers the assignment, setup, git, and how to implement your strategy.

## Setup

```bash
git clone https://github.com/bbioren/AISC-research-project.git && cd AISC-research-project
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
```

## Commands

```bash
ctxbench show-view --strategy masking            # what a strategy sends the model, on a fake history
ctxbench run --strategy masking --limit 2        # real SWE-bench tasks (needs Docker + an API key in .env)
```

## What's in here

```
src/ctxbench/
  agent.py          the agent loop (same for every strategy)
  messages.py       Turn (one message) and ContextView (what a strategy returns)
  strategies/       full_history (done), masking (A), summarization (B), hybrid (C)
  env.py            runs commands in Docker, or in a local folder for tests
  llm.py            calls the model and counts tokens and cost
  data.py           loads our 50 tasks (configs/subset_50.txt)
  cli.py            the ctxbench command
tests/              pytest
docs/               the guide and the write-up template
```
