# Work plan to CP2 (Dec 4)

*As of Nov 20, 2026*

## Goal: reproduced baselines and a chosen novel method by Dec 4

CP2 (First Prototype) is due **Thursday, Dec 4**. To pass it we need two things:
our benchmark exists with real numbers, and our novel method is in development.

- **Baselines:** each person reproduces one published context-management strategy in this repo.
  You run it on our fixed 50-task SWE-bench Verified subset and get its resolve rate, tokens and cost.
- **Novel method chosen and started:** on **Mon Dec 1** we pick our novel method, based on where
  the reproduced strategies failed, and start building it.

Working novelty until Dec 1: *recover the information that masking throws away, and attribute
each failure to the specific information that was lost.* Your failure notes decide whether we
keep it, sharpen it or replace it.

Thanksgiving is Nov 26–28, so plan on about 7 working days.

## Everyone, by Sunday, Nov 23

The Project Summary Doc is overdue for CP1. The director has to approve it before we build, so it comes first.

- [ ] **Project Summary Doc, one section each.** Draft your part in our team Drive folder by
  **Sat Nov 22** so Ben can edit and submit Sunday.
  - Person A: methods and datasets, technical milestones
  - Person B: benchmark plan, outcome, audience
  - Person C: prior work and its weak points (adapt the lit review from the Ideation Doc; add a link for every citation)
- [ ] **Repo setup.** Clone, install, and get `pytest` passing (see the main README). Post in the team channel when you're green.
- [ ] **Read the README** and [`assignments/README.md`](assignments/README.md).
- [ ] **Read *The Complexity Trap*** (Lindenbauer et al., 2025). It's the result we're reproducing.
  Come to the next check-in able to say what it found in two sentences.

## Who owns what

Each person reproduces one strategy from the literature, using the same model, tasks and agent.
Together the three results form our benchmark table. Full spec: [`assignments/README.md`](assignments/README.md).

| | Person A | Person B | Person C |
|---|---|---|---|
| **Name** | | | |
| **Reproduces** | Observation masking | LLM summarization | Hybrid masking + summarization, or MemGPT-style paging (pick by Nov 25) |
| **Papers** | SWE-agent (Yang et al., 2024); *The Complexity Trap* (Lindenbauer et al., 2025) | OpenHands condenser (Wang et al., ICLR 2025); *The Complexity Trap* | *The Complexity Trap*; MemGPT (Packer et al., 2023) |
| **Code** | `strategies/masking.py` | `strategies/summarization.py` | `strategies/hybrid.py` |
| **Write-up** | `assignments/A_masking.md` | `assignments/B_summarization.md` | `assignments/C_third_strategy.md` |
| **Also owns** | Docker + SWE-bench setup | Choosing the model + cost estimate | Task subset + failure-analysis tooling |

## What you hand in, and when

Everyone hands in the same five things by **Wed Dec 3**:

- [ ] **Paper summary (about 1 page):** what the method does and the exact settings the paper
  used, each with a page or section number.
- [ ] **Implementation:** your strategy in its file, with all the contract and assignment tests
  passing, plus at least 2 tests of your own.
- [ ] **Results:** your strategy run on the 50-task subset and scored with SWE-bench.
- [ ] **Comparison to the paper:** does your trend go the same direction as theirs? If not, why do you think it doesn't?
- [ ] **Failure notes:** 5 failed runs read end to end. For each, what went wrong, and whether it
  lost information it needed later.

| Date | Checkpoint |
|---|---|
| Sat Nov 22 | Your Project Summary Doc section drafted |
| Sun Nov 23 | Repo set up, `pytest` passes |
| Tue Nov 25 | Paper read and settings table filled in. **A:** 2 tasks run in Docker. **C:** hybrid vs. paging decided. **B:** model shortlist |
| Nov 26–28 | Thanksgiving: no expectations |
| Sun Nov 30 | Implementation done, tests pass, smoke-tested on 2 real tasks |
| **Mon Dec 1** | **Novelty decision meeting:** bring your failure notes so far (aim for 3+) |
| Wed Dec 3 | Full 50-task run scored; write-up complete |

## How we work

- **Weekly check-in:** each person answers three things: what you finished (with the number or file),
  what's next, and what's blocking you.
- **24-hour rule:** stuck for more than a day? Post in the team channel with what you tried.
  Setup problems are the easiest way to lose a week quietly.
- **Where things go:** code, results and write-ups in this repo, one branch and pull request per
  task, reviewed by a teammate. Drafts for the Project Summary Doc go in the team Drive folder.
- **Don't change the shared harness** (`agent.py`, `env.py`, `llm.py`, `messages.py`) without asking
  in the team channel. It affects everyone's numbers.
- **Never commit API keys.** They go in `.env`, which git ignores.
- **Spend:** don't start a run expected to cost over $10 without checking with Ben first.
- **#wins:** post the baseline table there when it lands.
