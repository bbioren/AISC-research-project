# Guide

## The assignment

Each of you reproduces one context management strategy from a paper, in this repo, and runs it on our 50 SWE-bench tasks.

| | Strategy | Papers | Your file |
|---|---|---|---|
| A | Observation masking | SWE-agent (Yang et al. 2024), *The Complexity Trap* (Lindenbauer et al. 2025) | `strategies/masking.py` |
| B | LLM summarization | OpenHands (Wang et al., ICLR 2025), *The Complexity Trap* | `strategies/summarization.py` |
| C | Masking + summarization hybrid | *The Complexity Trap* | `strategies/hybrid.py` |

The comment at the top of your file says what to look for in the paper.

By **Wed Dec 3**, hand in:
1. Your strategy, with `pytest` passing and at least 2 tests of your own.
2. A write-up (copy `docs/TEMPLATE.md`): the paper's settings with page numbers, your results, and notes on 5 runs that failed.

On **Mon Dec 1** we meet to pick our own method, so bring whatever failure notes you have by then.

| When | What |
|---|---|
| Sun Nov 23 | Setup done, `pytest` passes |
| Tue Nov 25 | Paper read, settings table filled in |
| Nov 26-28 | Thanksgiving, nothing due |
| Sun Nov 30 | Strategy written, tests pass, tried on 2 real tasks |
| Mon Dec 1 | Meeting to pick our method |
| Wed Dec 3 | 50-task run done, write-up finished |

## How it works

An agent is a loop. The model gets a GitHub issue, writes a shell command, we run it and paste the output back, and it keeps going until it says it's done. Every output gets added to the history, and the model rereads the whole history every step. After 30 steps that's a lot of text, which costs money and makes the model worse.

Your strategy decides what the model actually gets to see each step:

```
full history  ──>  your build_view()  ──>  the messages sent to the model
```

That one function is the whole assignment. Everything else (the loop, Docker, the model calls) is shared, so everyone's numbers can be compared.

Read these in order before you start, it's under 250 lines total:

1. `messages.py`: a `Turn` is one message, a `ContextView` is what you return
2. `strategies/base.py`: the rules, plus `pinned()` and `body()`
3. `strategies/full_history.py`: the simplest strategy, 3 lines
4. `agent.py`: find where `build_view` gets called
5. your stub, and your tests in `tests/test_strategies.py`

## Setup (once)

1. Send Ben your GitHub username so he can add you to the repo, then accept the invite.
2. Install git and [uv](https://docs.astral.sh/uv/). On a Mac: `brew install git uv`.
3. Tell git who you are: `git config --global user.name "Your Name"` and `git config --global user.email "you@uw.edu"`
4. Then:

```bash
git clone https://github.com/bbioren/AISC-research-project.git && cd AISC-research-project
uv venv && source .venv/bin/activate     # the activate part again in every new terminal
uv pip install -e ".[dev]"
pytest                                   # should say "4 passed, 13 skipped"
ctxbench show-view --steps 30            # look at how much the model has to read
```

## Branches and pull requests

Nobody pushes to `main` directly. You work on your own branch and open a pull request (PR) when it's ready.

```bash
git checkout main && git pull
git checkout -b masking                  # your branch, named after your strategy
```

Commit every time you get something small working, and push so it's backed up:

```bash
git add src/ctxbench/strategies/masking.py tests/test_strategies.py
git commit -m "Hide observations outside the window"
git push -u origin masking               # after the first time, just `git push`
```

To open a PR, go to the repo on GitHub and click **Compare & pull request**. Open it as a draft early so people can see your progress, then click **Ready for review** when it's done. GitHub runs `pytest` on every PR, and a red X means click **Details** to see what failed.

Each of you reviews one other person's PR. Read it in **Files changed**, comment on anything you don't follow or anything that doesn't match the paper, then **Approve**.

If `main` changes while you're working: `git checkout main && git pull && git checkout masking && git merge main`. If git says there's a conflict and you're not sure what to do, stop and ask in the team channel.

## Writing your strategy

1. **Read the paper** and fill in the settings table in your write-up, with page numbers.
2. **Write 2 tests** for the paper's settings in `tests/test_strategies.py`, copying the ones already there. They'll show as skipped until your strategy works.
3. **Write `build_view`.** A starting point that works for all three:

```python
def build_view(self, history):
    msgs = [t.as_message() for t in pinned(history)]   # system prompt + task, always first
    hidden = []
    for t in body(history):
        msgs.append(t.as_message())                     # or t.as_message("other text"), or skip it
    return ContextView(msgs, hidden)
```

   Don't change `history` itself, and put the id of every observation you hide or summarize in `hidden`.
4. **Check it:** `pytest`, then `ctxbench show-view --strategy masking --steps 30` and see if it looks like what the paper describes.
5. **Try 2 real tasks.** You need Docker running and an API key in `.env` (Ben will send it). Run `ctxbench run --strategy masking --limit 2`. Each task saves a JSON file in `results/masking/`. Open one and read the `history` to see what the agent did.
6. **Full run:** drop `--limit`, then run the scoring command it prints at the end.
7. **Write-up:** fill in your results, then pick 5 tasks that failed, read their history, and write down what went wrong.

## Stuck?

- `ctxbench: command not found` or import errors: run `source .venv/bin/activate`.
- A test fails and you don't know why: `pytest -x -vv`.
- Stuck for more than a day on anything: post in the team channel with what you tried.
