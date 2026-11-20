# Assignment 1: Reproduce a context-management strategy from the literature

**Due:** write-up + code by **Wed Dec 3** (checkpoints below). **CP2:** Thu Dec 4.

## Why we're doing this

Before we can claim anything new, we need the methods we're comparing against
working in *our* setup: same agent, same model, same 50 tasks. Each of you
reproduces one published strategy. Together, your three results become our
benchmark table. And while you implement them, you'll see where each one breaks.
That evidence is what we'll use to choose our novel method on **Mon Dec 1**.

## Who does what

| | Strategy | Paper(s) | Code goes in | Also owns |
|---|---|---|---|---|
| **A** | Observation masking | SWE-agent (Yang et al., 2024); *The Complexity Trap* (Lindenbauer et al., 2025) | `src/ctxbench/strategies/masking.py` | Docker + SWE-bench setup |
| **B** | LLM summarization | OpenHands condenser (Wang et al., ICLR 2025); *The Complexity Trap* | `src/ctxbench/strategies/summarization.py` | Choosing the model + cost estimate |
| **C** | Hybrid masking + summarization **or** MemGPT-style paging | *The Complexity Trap*; MemGPT (Packer et al., 2023) | `src/ctxbench/strategies/hybrid.py` | The task subset + failure-analysis tooling |

Each strategy file's docstring tells you exactly what to find in the paper.

## What you hand in

1. **Paper summary** (about 1 page), in `docs/assignments/<you>.md` using the template there:
   - what the method does and why
   - the exact settings the paper used, with the page or section for each
   - anything the paper leaves unspecified, and what you chose instead
2. **Implementation:** your strategy in its file, with every test in `tests/test_contract.py` and
   `tests/test_assignments.py` passing for it. Add at least 2 tests of your own for the
   paper-specific settings.
3. **Results:** your strategy run on the 50-task subset (same model as everyone),
   scored with SWE-bench, in the shared results table (`ctxbench report`).
4. **Comparison to the paper:** does the trend match? For example, is masking cheaper than full
   history at a similar resolve rate? We don't expect the same absolute numbers (different model,
   subset and agent); we do expect the same *direction*. If it doesn't match, say why you think so.
5. **Failure notes:** read **5 failed runs** of your strategy end to end. For each, write one line
   on what went wrong, and whether it lost information it needed later (which observation, and what
   was in it). These notes are the input to the Dec 1 novelty decision.

## Checkpoints

| Date | Checkpoint |
|---|---|
| Sun Nov 23 | Repo set up, `pytest` passes; your Project Summary Doc section drafted (Sat) |
| Tue Nov 25 | Paper read; settings table filled in your write-up. **C:** choice of hybrid vs paging made. **A:** 2 tasks run end to end in Docker |
| Nov 26–28 | Thanksgiving: no expectations |
| Sun Nov 30 | Implementation done and tests pass; smoke-tested on 2 real tasks |
| **Mon Dec 1** | **Novelty decision meeting:** each person brings their failure notes so far (aim for 3+) |
| Wed Dec 3 | Full 50-task run scored; write-up complete |

## Rules

- **Don't modify the shared harness** (`agent.py`, `env.py`, `llm.py`, `messages.py`) to make your
  strategy work. If you need a change, post in the team channel first, since it affects everyone's numbers.
- Same model, same subset, same agent settings for every condition. Those are in `configs/experiment.yaml`.
- One branch and pull request per person. Someone else on the team reviews it before merge.
- No API keys in git (`.env` only). Ask Ben before any run expected to cost over $10.
- Stuck for 24 hours? Post in the team channel with what you tried.
- Use AI tools to help you code if you want, but you must be able to explain every line in review,
  and every paper setting must come from the paper itself, with a page number.
