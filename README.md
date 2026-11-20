# What does a coding agent forget?

This is our AISC research project on context management for coding agents. The repo is a test setup where the agent loop, the model and the tasks stay the same, and the only thing we swap out is how the agent's context gets managed.

**New here?** Read [`docs/WORKPLAN.md`](docs/WORKPLAN.md) first for who's doing what and when. The current assignment is in [`docs/assignments/README.md`](docs/assignments/README.md).

## The question

Coding agents build up a lot of context as they work, and most of it is output from the commands they run. People have tried a few ways of cutting it down:

- **Observation masking:** hide older command outputs
- **LLM summarization:** have a model summarize older turns
- some mix of the two

*The Complexity Trap* (Lindenbauer et al. 2025) compared these on SWE-bench Verified. They found masking costs about half as much and does as well as summarization, sometimes better. So just running that comparison again isn't a contribution. It's our baseline.

We're picking our actual novel method on **Monday Dec 1**, based on what goes wrong with the strategies we reproduce. The working idea right now (from the summary doc) is to recover the information masking throws away, and to work out which lost information caused each failure. `src/ctxbench/attribution.py` has a first attempt at that second part.

## What we're comparing

| Condition | What it does | From | Who |
|---|---|---|---|
| `full_history` | Nothing, the agent sees everything. Most expensive | n/a | done |
| `masking` | Hides all but the most recent command outputs | SWE-agent, *The Complexity Trap* | A |
| `summarization` | An LLM summarizes older turns | OpenHands condenser, *The Complexity Trap* | B |
| `hybrid` / `paging` | Masking + summarization, or MemGPT-style paging | *The Complexity Trap*, MemGPT | C |
| ours | TBD Dec 1 | | everyone |

The main things we care about are **resolve rate** and **cost per resolved task**. We also track total and peak prompt tokens, number of steps, and the failure labels from the attribution script. We're not using wall-clock time because API latency makes it too noisy.

One sanity check before trusting any results: masking vs full history should come out the same way it did in *The Complexity Trap*. If it doesn't, something is probably wrong with our setup.

## Scope

- **Tasks:** 50 random instances from SWE-bench Verified, picked once with a fixed seed (`ctxbench subset --n 50 --seed 0`) and committed so we all use the same ones.
- **Model:** one cheap model for every condition, set in `configs/experiment.yaml`.
- **Cost:** each task stops at $1 (`agent.cost_limit`). Ask Ben before anything that'll cost over $10 total.
- SWE-bench Verified has known problems with contamination and test quality. Since we compare conditions against each other on the same tasks, that matters less for us, but it should go in the limitations section.

## Setup

```bash
git clone https://github.com/bbioren/AISC-research-project && cd AISC-research-project
uv venv && source .venv/bin/activate        # or: python -m venv .venv && source .venv/bin/activate
uv pip install -e ".[dev,eval,analysis]"     # or: pip install -e ".[dev,eval,analysis]"
cp .env.example .env                         # put your API key in here, don't commit it
pytest                                       # runs offline; strategies nobody's written yet show up as skipped
```

For real runs you'll need Docker running and a lot of free disk for the SWE-bench images. Figure on around 100 GB.

## Running things

```bash
ctxbench subset --n 50 --seed 0                          # only once, then commit configs/subset_50_seed0.txt
ctxbench run configs/experiment.yaml --limit 2 --strategy masking   # always try 2 tasks first
ctxbench run configs/experiment.yaml --strategy masking  # full run for one strategy (picks up where it left off)
ctxbench eval-cmd configs/experiment.yaml                # prints the SWE-bench scoring commands to run
ctxbench report configs/experiment.yaml                  # writes results/<run>/summary.md
ctxbench attribute configs/experiment.yaml               # writes results/<run>/attribution.json
```

## What's where

```
src/ctxbench/
  agent.py            the agent loop, same for every condition (ask before changing)
  messages.py         Turn and ContextView. The full history is always kept, strategies just pick what the model sees
  strategies/         full_history (done), masking (A), summarization (B), hybrid (C)
  env.py              DockerEnv for SWE-bench, LocalEnv for quick tests on a toy repo
  llm.py              wrapper around LiteLLM that tracks tokens and cost; ScriptedLLM for tests
  data.py             loading SWE-bench, the task subset, reading patches
  metrics.py          builds the results table
  attribution.py      failure analysis
  cli.py              the ctxbench command
docs/                 work plan, assignment, everyone's write-ups
configs/              experiment settings and the task subset
results/              run outputs (raw trajectories aren't committed, summaries are)
tests/                test_contract.py (rules every strategy follows), test_assignments.py, test_harness.py
```

## Adding a strategy

Subclass `ContextStrategy` and write `build_view(history) -> ContextView`. Then add it to the registry in `strategies/__init__.py` and to `configs/experiment.yaml`. `tests/test_contract.py` will automatically check it against the rules every strategy has to follow. You should still add tests for whatever's specific to yours.

## Before the first real run

- Check that `image_template` in `configs/experiment.yaml` matches the image names for the `swebench` version you installed.
- B picks the model, and we agree on a total budget.

## Timeline

| | When | Done means |
|---|---|---|
| CP1 | Nov 13 (late) | Summary doc submitted and approved |
| Method decision | Mon Dec 1 | We've picked our method based on the failure notes |
| Assignment 1 | Wed Dec 3 | 3 strategies reproduced, run on 50 tasks, written up |
| CP2 | Thu Dec 4 | Baseline numbers exist, our method is underway |
| CP3 | Jan 22 (hard deadline Jan 29) | Everything run, failure analysis checked by hand, charts done |
| CP4 | Feb 12 (hard deadline Feb 19) | 6-page paper in IEEE format |

## Papers

- Lindenbauer et al. 2025, *The Complexity Trap*: masking vs summarization on SWE-bench Verified
- Yang et al. 2024, *SWE-agent*
- Wang et al., ICLR 2025, *OpenHands*
- Packer et al. 2023, *MemGPT*
- Liu et al. 2024, *Lost in the Middle*
- Jimenez et al. 2024, *SWE-bench*. SWE-bench Verified is from OpenAI (2024)

The full lit review is in our Project Ideation Doc. Everything we cite in the paper needs a link.
