# How to do Assignment 1, step by step

This walks you through everything from the beginning: what the code does, how to get it on your laptop, how to implement your strategy, and how to get it merged. If you've never used git branches or opened a pull request, that's fine, it's all in here.

The actual assignment (what you're reproducing and what's due when) is in [`assignments/README.md`](assignments/README.md). This doc is the how.

## Part 1: What we're actually building

### The agent

A coding agent is just a loop. We give a model a GitHub issue and a repo. Each step, the model writes a shell command, we run it, and we paste the output back in. It keeps going until it thinks the bug is fixed.

```
task ──> model ──> command ──> run it ──> output ──┐
           ^                                       │
           └───────── everything so far ───────────┘
```

The problem is the "everything so far" part. Every command's output gets added to the conversation, and the model reads the whole thing again on every step. After 30 steps of `cat`-ing files and running tests, that's a lot of text. It costs more money each step, and models get worse at finding things in really long inputs.

### Where your code fits

A **context strategy** decides what the model actually sees on each step. It takes the full history and returns the messages to send:

```
full history (never changes)  ──>  your strategy  ──>  what the model sees this step
```

That's it. Your whole assignment is one function, `build_view(history)`. The agent loop, Docker, the model calls and the cost tracking are already written and shared by everyone. That's on purpose. If everyone used their own agent, we couldn't compare the numbers.

A few examples of what a strategy can do:

- **Full history** (already done): send everything. This is the baseline.
- **Masking** (A): replace old command outputs with a short note like "output hidden".
- **Summarization** (B): once things get long, have a model write a summary of the old stuff and send that instead.
- **Hybrid or paging** (C): mix the two, or let the agent pull hidden stuff back.

### The pieces you'll touch

| File | What it is | Do you edit it? |
|---|---|---|
| `src/ctxbench/agent.py` | The loop above | No |
| `src/ctxbench/messages.py` | `Turn` (one message in the history) and `ContextView` (what your strategy returns) | No |
| `src/ctxbench/strategies/base.py` | The `ContextStrategy` class you inherit from, plus helpers `pinned()` and `body()` | No |
| `src/ctxbench/strategies/full_history.py` | The simplest possible strategy. Read it first | No |
| `src/ctxbench/strategies/<yours>.py` | Your stub | **Yes** |
| `tests/test_assignments.py` | Tests for your strategy | **Yes**, add your own |
| `configs/experiment.yaml` | Settings for real runs | Yes, your strategy's params |
| `docs/assignments/<yours>.md` | Your write-up | **Yes** |

## Part 2: One-time setup

### Accounts and tools

1. Make a GitHub account if you don't have one, and send Ben your username so he can add you to the repo.
2. Accept the invite (it shows up in your email and on GitHub).
3. Install git, Python 3.10 or newer, and [uv](https://docs.astral.sh/uv/) (it makes Python environments fast and painless). On a Mac: `brew install git uv`.
4. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/). You won't need it until real runs, but it's a big download.

Tell git who you are. This goes on every commit you make:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@uw.edu"
```

### Get the code

```bash
git clone https://github.com/bbioren/AISC-research-project.git
cd AISC-research-project
uv venv
source .venv/bin/activate          # do this every time you open a new terminal
uv pip install -e ".[dev]"
pytest
```

The last line should end with something like `22 passed, 64 skipped`. The skipped ones are the strategies nobody has written yet, including yours. Post in the team channel once you get here.

### Look at the harness working

```bash
ctxbench show-view --strategy full_history --steps 4
```

This makes a fake history (no Docker, no API key) and prints exactly what a strategy would send the model. Each line is one message. Try `--steps 30` and look at how much text the model would be reading. That's the problem your strategy is solving.

Now try yours:

```bash
ctxbench show-view --strategy masking      # or summarization, or hybrid
```

It'll say it isn't implemented yet. Your job is to change that.

## Part 3: The git workflow

Nobody pushes straight to `main`. Everyone works on their own **branch**, a separate copy of the code where you can change whatever you want without breaking things for anyone else. When it's ready, you open a **pull request** (PR), which asks to merge your branch into `main`. Someone reviews it, and once it's approved it gets merged.

### Start your branch

```bash
git checkout main
git pull                                   # get the latest main
git checkout -b masking-strategy           # make your branch; use your own name for it
```

Good branch names say what's on them: `masking-strategy`, `summarization-strategy`, `hybrid-strategy`, `fix-docker-images`.

### Save your work as you go

A **commit** is a saved snapshot. Commit whenever you get something small working. Don't wait until the end.

```bash
git status                                 # see what you changed
git add src/ctxbench/strategies/masking.py tests/test_assignments.py
git commit -m "Hide observations outside the window"
git push -u origin masking-strategy        # first push; after that, just `git push`
```

Pushing puts your branch on GitHub, so it's backed up even if your laptop dies.

### Open a pull request

You can open a PR as soon as you have something, even if it's not done. Mark it as a draft, so people can see your progress and help.

1. Go to the repo on GitHub. There'll be a banner saying your branch had recent pushes, with a **Compare & pull request** button. Click it.
2. Base should be `main`, compare should be your branch.
3. Fill in the template (what it does, how you checked it, the paper settings).
4. Click **Create draft pull request**. When it's ready for review, click **Ready for review** and ask someone on the team to look at it.

Or from the terminal, if you have the GitHub CLI: `gh pr create --draft --fill`.

Every PR automatically runs `pytest` on GitHub. You'll see a green check or a red X at the bottom of the PR. Red means click **Details** to see what failed.

### Reviewing someone else's PR

You'll each review one other person's PR. Go to the **Files changed** tab, read the code, and leave comments by clicking the line number. Things to check:

- Does it follow the rules in `tests/test_contract.py`?
- Do the settings match what the paper says? Ask for the page number if it's missing.
- Is there anything you don't understand? Ask. If you can't follow it, the paper's reviewers won't either.

When you're happy, click **Review changes**, then **Approve**.

### When `main` changes under you

If someone else's PR gets merged while you're working, bring their changes into your branch:

```bash
git checkout main && git pull
git checkout masking-strategy
git merge main
```

If git says there's a **conflict**, it means you both changed the same lines. Open the file, find the `<<<<<<<` and `>>>>>>>` markers, keep the right version, delete the markers, then `git add` the file and `git commit`. If it gets confusing, stop and ask in the team channel. Don't force-push to fix it.

## Part 4: Implementing your strategy

Do these in order. Each step has a check, so you always know whether you're on track.

### Step 1: Read the code (about 30 min)

Read these files in this order:

1. `agent.py`: just the `run` method. Find the line where `build_view` gets called and the line where the model's output becomes a new `Turn`.
2. `messages.py`: what a `Turn` holds (`role`, `content`, `kind`, `step`, `id`) and what a `ContextView` holds.
3. `strategies/base.py`: the rules every strategy follows, and the `pinned()` and `body()` helpers.
4. `strategies/full_history.py`: three lines of code. Make sure you get why it works.
5. Your stub: the comment at the top lists what to look for in the paper.
6. `tests/test_contract.py` and the part of `tests/test_assignments.py` for your strategy.

**Check:** can you explain to someone what `history` looks like after 3 steps? (System prompt, task, then action, observation, action, observation, action, observation.)

### Step 2: Read the paper and fill in the settings (by Tue Nov 25)

Fill in the settings table in your write-up (`docs/assignments/<yours>.md`). For every setting, write down the page or section it came from. If the paper doesn't say, check their code. If it's not there either, pick something reasonable and write down that you picked it.

**Check:** you could implement it from your table alone without reopening the paper.

### Step 3: Write tests for the paper's settings first

Before writing your strategy, add at least 2 tests to `tests/test_assignments.py` that check the paper's specific behavior. For example, for masking: "with a window of 3, exactly the last 3 observations are visible." Copy the pattern of the existing tests in that file. Use the `view(...)` helper at the top, which skips the test while your strategy isn't written yet. `history_factory(n)` gives you a fake history with `n` steps.

**Check:** `pytest tests/test_assignments.py` shows your new tests as skipped (because the strategy doesn't exist yet), not erroring.

### Step 4: Implement `build_view`

Start simple and grow it. A good first version for almost any strategy:

```python
def build_view(self, history):
    msgs = [t.as_message() for t in pinned(history)]   # system prompt + task, always
    hidden = []
    for t in body(history):                            # everything after that
        # decide: send t as-is, change it, or leave it out
        msgs.append(t.as_message())
    return ContextView(messages=msgs, hidden_ids=hidden)
```

`t.as_message()` sends a turn unchanged. `t.as_message("some other text")` sends it with different content. That's how you'd replace an observation with a placeholder.

Things that trip people up:

- **Don't change `history`.** No `history.pop()`, no `t.content = ...`. Build a new list.
- **Record what you hid.** Any observation the model can't see in full goes in `hidden_ids`. The failure analysis relies on this.
- **Summarization only (B and maybe C):** call the model with `self.llm.complete(messages)` and add its `prompt_tokens`, `completion_tokens` and `cost` to the `ContextView`'s `extra_` fields. Otherwise summarization looks free, which is exactly the wrong conclusion. Also keep track of what you've already summarized so you don't redo it every step.

**Check:**

```bash
pytest                                              # nothing red
ctxbench show-view --strategy masking --steps 20   # does it look like what the paper describes?
```

Commit and push after this step.

### Step 5: Try it on 2 real tasks

Now you need Docker running and an API key in `.env` (Ben will tell you which model and key to use). A needs to finish getting Docker working first, so coordinate with them.

```bash
ctxbench run configs/experiment.yaml --limit 2 --strategy masking
```

Each task writes a JSON file to `results/`. Open one and read through `history`. That's the whole conversation the agent had. Look at `views` too: it tells you what was hidden at each step.

**Check:** both tasks finish (`exit_reason` is `submitted` or `step_limit`, not a crash), and the hidden observations are the ones you'd expect.

### Step 6: The full run, scoring and the write-up

Once everyone's strategy works on 2 tasks, B runs the full 50 (or you each run your own; we'll decide based on cost). Then:

```bash
ctxbench eval-cmd configs/experiment.yaml   # prints the scoring commands; run them
ctxbench report configs/experiment.yaml     # makes the results table
```

Finish your write-up: the results table, whether your trend matches the paper, and your 5 failure notes. For the failure notes, pick 5 tasks your strategy didn't solve, open their JSON, and read the `history` from start to end. Write down where it went wrong, and whether it needed something it couldn't see anymore.

Then mark your PR ready for review.

## Part 5: When you're stuck

- **`pytest` errors on import:** make sure your environment is active (`source .venv/bin/activate`) and you installed with `uv pip install -e ".[dev]"`.
- **`ctxbench: command not found`:** same fix.
- **Docker errors about images:** that's A's area. Post the exact error in the team channel.
- **A test fails and you don't get why:** run just that test with `pytest -x -k test_name -vv` to see the full output.
- **Git got weird:** stop, don't force anything, and post `git status` in the team channel.
- **Stuck for more than a day on anything:** post what you tried. Seriously, nobody is going to think less of you. Losing a week quietly is the only real mistake here.
