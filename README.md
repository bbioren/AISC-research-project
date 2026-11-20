# What does a coding agent forget? Context management on SWE-bench

AISC Research Program project. This repo is a controlled testbed: one agent loop,
one model, one fixed task subset. The **only** thing that changes between
experimental conditions is the context-management strategy.

> **Start here:** [`docs/WORKPLAN.md`](docs/WORKPLAN.md) has the plan to CP2: who owns what, and what's due when.
> [`docs/assignments/README.md`](docs/assignments/README.md) has the full spec for the current assignment
> (each person reproduces one strategy from the literature, due Dec 3).

## The question

Coding agents pile up context quickly, and most of it is tool output.
Prior work compares ways of cutting it:

- **Observation masking** (hide old tool outputs)
- **LLM summarization** (compress old turns with a model)
- **Hybrids** of the two

The Complexity Trap (Lindenbauer et al., 2025) found that masking roughly halves cost
while matching or beating summarization on SWE-bench Verified. So re-running that comparison
is our **benchmark, not our contribution**.

**Novelty: decided Mon Dec 1.** We'll choose it from what the reproduced strategies
get wrong: which information they lose and which failures that causes. Current working
direction (from the Project Summary Doc): *recover the information masking throws away,
and attribute each failure to the specific information that was lost.*
`src/ctxbench/attribution.py` already does a first pass at that failure analysis.

## Benchmark plan

| Condition | What it is | Source | Owner |
|---|---|---|---|
| `full_history` | No context management; upper bound on cost | — | done |
| `masking` | Hide all but recent tool outputs | SWE-agent; *The Complexity Trap* | A |
| `summarization` | LLM summary of older turns | OpenHands condenser; *The Complexity Trap* | B |
| `hybrid` (or `paging`) | Masking + summarization, or MemGPT-style paging | *The Complexity Trap*; MemGPT | C |
| *ours* | Decided Dec 1 | — | team |

**Metrics:**
- **Primary:** resolve rate and **cost per resolved task**.
- **Secondary:**
  - total and peak prompt tokens, steps
  - failure-attribution labels (`never_seen` / `seen_then_hidden` / `seen_visible`) and rediscovery counts

We report tokens and $ rather than wall-clock time, because API latency makes time too noisy to compare.

**Sanity check:** our masking-vs-full-history gap should go in the same direction as the
Complexity Trap's. If it doesn't, fix the harness before trusting anything else.

## Scope and budget

- **Tasks:** a fixed random 50-instance subset of SWE-bench Verified (`ctxbench subset --n 50 --seed 0`).
- **Model:** one inexpensive model for every condition (`configs/experiment.yaml`).
- **Budget:** `agent.cost_limit` caps each task at $1. Ask Ben before any run expected to cost over $10.
- **Dataset caveat:** SWE-bench Verified has contamination and test-quality concerns. We compare
  conditions *relative to each other* on the same tasks, which is robust to that. It goes in Limitations.

## Setup

```bash
git clone https://github.com/bbioren/AISC-research-project && cd AISC-research-project
uv venv && source .venv/bin/activate        # or: python -m venv .venv && source .venv/bin/activate
uv pip install -e ".[dev,eval,analysis]"     # or: pip install -e ".[dev,eval,analysis]"
cp .env.example .env                         # add your API key; never commit .env
pytest                                       # offline; unimplemented strategies show as "skipped"
```

Real runs need **Docker** running, with enough disk for SWE-bench images (budget about 100 GB).

## Workflow

```bash
ctxbench subset --n 50 --seed 0                          # once; commit configs/subset_50_seed0.txt
ctxbench run configs/experiment.yaml --limit 2 --strategy masking   # smoke test first!
ctxbench run configs/experiment.yaml --strategy masking  # full run for one condition (resumable)
ctxbench eval-cmd configs/experiment.yaml                # prints SWE-bench scoring commands; run them
ctxbench report configs/experiment.yaml                  # -> results/<run>/summary.md
ctxbench attribute configs/experiment.yaml               # -> results/<run>/attribution.json
```

## Layout

```
src/ctxbench/
  agent.py            bash-only agent loop (identical across conditions; don't edit without asking)
  messages.py         Turn / ContextView: full history is kept; strategies only choose the view
  strategies/         full_history (done), masking (A), summarization (B), hybrid (C)
  env.py              DockerEnv (SWE-bench images) and LocalEnv (toy smoke tests only)
  llm.py              LiteLLM wrapper with token/cost accounting; ScriptedLLM for tests
  data.py             SWE-bench loading, fixed subsets, patch parsing
  metrics.py          results table
  attribution.py      failure attribution
  cli.py              `ctxbench` command
docs/assignments/     current assignment + each person's write-up
configs/              experiment config + committed task subset
results/              run outputs (raw trajectories gitignored; summaries committed)
tests/                test_contract.py (rules for every strategy), test_assignments.py, test_harness.py
```

## Adding a strategy

1. Subclass `ContextStrategy` and implement `build_view(history) -> ContextView`.
2. Register it in `strategies/__init__.py` and add it to `configs/experiment.yaml`.
3. `tests/test_contract.py` automatically checks it against the rules every strategy must follow.
   Add tests for its specific behavior.

## Before the first real run

- Check `image_template` in `configs/experiment.yaml` against the installed `swebench` version.
- Pick the model (B), and agree on a total budget with Ben.

## Milestones

| Checkpoint | Date | Done looks like |
|---|---|---|
| CP1 | Nov 13 (overdue) | Project Summary Doc submitted and approved |
| Assignment 1 | Dec 3 | 3 strategies reproduced, run on 50 tasks, written up |
| Novelty decision | Dec 1 | One novel method chosen from the failure notes |
| CP2 | Dec 4 | Baselines exist with numbers; novel method in development |
| CP3 | Jan 22 target / Jan 29 | All conditions run, failure analysis checked by hand, charts |
| CP4 | Feb 12 target / Feb 19 | 6-page IEEE paper |

## Key references

- Lindenbauer et al., 2025: *The Complexity Trap*. Masking vs summarization on SWE-bench Verified.
- Yang et al., 2024: *SWE-agent*.
- Wang et al., ICLR 2025: *OpenHands*.
- Packer et al., 2023: *MemGPT*.
- Liu et al., 2024: *Lost in the Middle*.
- Jimenez et al., 2024: *SWE-bench*. SWE-bench Verified (OpenAI, 2024).

The rest of the literature review lives in the team's Project Ideation Doc.
Every citation needs a link before it goes in the paper.
