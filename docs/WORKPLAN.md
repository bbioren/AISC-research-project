# Plan through CP2 (Dec 4)

Last updated Nov 20.

## Where we're headed

CP2 is due Thursday Dec 4. By then we need our baseline numbers and we need to have started on our own method.

Here's how we get there. Each of you is going to reproduce one context management strategy from a paper we've already read, inside this repo, and run it on our 50 SWE-bench Verified tasks. That gives us the baselines. Then on Monday Dec 1 we meet and pick our novel method based on where those strategies broke.

For now the working idea is still the one from the summary doc: get back the information that masking throws away, and figure out which lost information actually caused each failure. What you find while reproducing these papers might change that, and that's fine. That's kind of the point.

Thanksgiving is Nov 26-28 so realistically we have about a week of work time. Don't plan on doing anything over the break.

## This weekend (everyone)

The Project Summary Doc is late for CP1, so that comes first. The director has to approve it before we can really start building.

- [ ] Write your section of the summary doc in the team Drive folder by **Saturday Nov 22**. I'll clean it up and submit Sunday.
  - A: methods + datasets, technical milestones
  - B: benchmark plan, expected outcome, who the audience is
  - C: prior work and where it falls short. You can pull a lot from the lit review in the ideation doc, but every citation needs a link.
- [ ] Clone the repo, install it, and get `pytest` to pass. Steps are in the main README. Message the team channel once it works.
- [ ] Read the README and [`assignments/README.md`](assignments/README.md).
- [ ] Read *The Complexity Trap* (Lindenbauer et al. 2025). It's the closest paper to ours. Be ready to explain what they found in a couple sentences at check-in.

## Who's doing what

Everyone uses the same model, tasks and agent loop so the numbers are actually comparable. Details for the assignment are in [`assignments/README.md`](assignments/README.md).

| | A | B | C |
|---|---|---|---|
| **Name** | | | |
| **Strategy** | Observation masking | LLM summarization | Masking + summarization hybrid, or MemGPT-style paging (your call, decide by Nov 25) |
| **Read** | SWE-agent (Yang et al. 2024), *The Complexity Trap* | OpenHands condenser (Wang et al., ICLR 2025), *The Complexity Trap* | *The Complexity Trap*, MemGPT (Packer et al. 2023) |
| **Code** | `strategies/masking.py` | `strategies/summarization.py` | `strategies/hybrid.py` |
| **Write-up** | `assignments/A_masking.md` | `assignments/B_summarization.md` | `assignments/C_third_strategy.md` |
| **Also in charge of** | Getting Docker + SWE-bench working | Picking the model, estimating cost | The task subset, failure analysis script |

## What's due

By **Wednesday Dec 3** each of you should have:

- [ ] A short summary of your paper (~1 page) with the exact settings they used and where in the paper you found each one
- [ ] Your strategy implemented, all the tests passing, plus at least 2 tests you wrote yourself
- [ ] Results from running it on the 50 tasks, scored with SWE-bench
- [ ] A comparison with the paper. We won't match their numbers exactly (different model, fewer tasks) but the trend should go the same way. If it doesn't, say why you think that is.
- [ ] Notes on 5 runs that failed. Read the whole trajectory and write down what went wrong and whether the agent lost something it needed later.

Dates along the way:

| When | What |
|---|---|
| Sat Nov 22 | Summary doc section drafted |
| Sun Nov 23 | Repo set up and tests passing |
| Tue Nov 25 | Paper read, settings table filled in. A has 2 tasks running in Docker, B has a shortlist of models, C has picked hybrid or paging |
| Nov 26-28 | Thanksgiving, nothing due |
| Sun Nov 30 | Strategy implemented, tests passing, tried on 2 real tasks |
| **Mon Dec 1** | **Meeting to pick our method.** Bring whatever failure notes you have (3+ ideally) |
| Wed Dec 3 | Full run done and scored, write-up finished |

## How we're working

- At check-in I'll ask everyone the same three things: what you got done (show me the file or the number), what's next, and what's blocking you.
- If you're stuck for more than a day, post in the team channel and say what you've tried. Setup issues especially can eat a whole week if nobody hears about them.
- Code, results and write-ups go in this repo. Make a branch and a PR for each task and have someone else on the team review it. Summary doc drafts go in Drive.
- Please don't edit `agent.py`, `env.py`, `llm.py` or `messages.py` without asking first. Changes there affect everyone's results.
- API keys go in `.env` and never get committed.
- Check with me before starting anything that'll cost more than $10.
- When the baseline table is done, post it in #wins.
