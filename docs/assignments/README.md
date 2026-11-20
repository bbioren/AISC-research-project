# Assignment 1: Reproduce a strategy from the literature

Due **Wednesday Dec 3**. CP2 is the next day.

## Why

We can't claim we did something new until the existing methods are running in our own setup, with the same agent, model and tasks. So each of you is reproducing one published strategy. Put together, your three results are our benchmark table.

The other reason is that you'll see where these strategies fail. We're going to use that to pick our own method on Monday Dec 1, so pay attention to it.

## Assignments

| | Strategy | Papers | File | Also in charge of |
|---|---|---|---|---|
| **A** | Observation masking | SWE-agent (Yang et al. 2024), *The Complexity Trap* (Lindenbauer et al. 2025) | `src/ctxbench/strategies/masking.py` | Docker + SWE-bench setup |
| **B** | LLM summarization | OpenHands condenser (Wang et al., ICLR 2025), *The Complexity Trap* | `src/ctxbench/strategies/summarization.py` | Picking the model, cost estimate |
| **C** | Masking + summarization hybrid **or** MemGPT-style paging | *The Complexity Trap*, MemGPT (Packer et al. 2023) | `src/ctxbench/strategies/hybrid.py` | Task subset, failure analysis |

The comment at the top of each file has a list of what to look for in the paper. For how to actually do it (setup, branches, PRs, testing), follow [`../GUIDE.md`](../GUIDE.md).

## What to turn in

1. **Paper summary**, about a page, in `docs/assignments/<yours>.md` (use the template). Explain how the method works, list every setting the paper used with the page or section it's from, and note anything the paper doesn't specify plus what you went with instead.
2. **Your implementation.** All the tests in `tests/test_contract.py` and `tests/test_assignments.py` should pass for your strategy. Add at least 2 of your own that check the paper-specific settings.
3. **Results** on the 50-task subset, using the same model as everyone else, scored with SWE-bench. `ctxbench report` puts them in the shared table.
4. **How it compares to the paper.** We're using a different model and a smaller set of tasks, so the numbers won't match. The direction should, though. For example, masking should come out cheaper than full history without resolving a lot fewer tasks. If yours doesn't line up, give your best guess why.
5. **Failure notes.** Pick 5 runs where your strategy failed and read the whole trajectory. For each one write a line about what went wrong and whether the agent had lost information it needed (which observation, and what was in it). These are what we'll be looking at on Dec 1.

## Dates

| When | What |
|---|---|
| Sun Nov 23 | Repo set up, tests pass. Summary doc section drafted by Sat |
| Tue Nov 25 | Paper read, settings table done. A: 2 tasks running in Docker. C: picked hybrid or paging |
| Nov 26-28 | Thanksgiving |
| Sun Nov 30 | Implementation done, tests pass, tried on 2 real tasks |
| **Mon Dec 1** | **Meeting to choose our method.** Bring your failure notes (3+ if you can) |
| Wed Dec 3 | 50-task run scored, write-up done |

## Ground rules

- Don't change the shared code (`agent.py`, `env.py`, `llm.py`, `messages.py`) to get your strategy working. If you think it needs a change, bring it up in the team channel first, since it changes everyone's numbers.
- Everyone uses the same model, task subset and agent settings. They're in `configs/experiment.yaml`.
- One branch and one PR per person, and someone else reviews it before it gets merged.
- Keep API keys in `.env`. Ask Ben before running anything over $10.
- If you've been stuck for a day, post in the team channel with what you tried.
- You can use AI tools to help write code. You still have to be able to explain every line when someone reviews it, and the paper settings have to come from the actual paper with a page number.
