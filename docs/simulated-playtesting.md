# Simulated playtesting with LLMs

Plan for playtests where one model gives clues and another guesses. Back to
[README](../README.md).

**Status (2026-11-22): phase 1 done.** LLM calls go through
[llmemo](https://github.com/ForrestTrepte/llmemo) v0.2.0, pinned in `pyproject.toml`.
`tools/simplay.py` plays both modes. The dry run (`sim-playtests/runs/dry-run-*.md`)
cost $0.13 API-equivalent for 6 games, about 8k tokens and 3–5 s per call, nearly all
of it the shared system prompt. Haiku as guesser solved every prompt, including ones
humans failed, so calibration (phase 2) has a real gap to close.

## Why

Reading a prompt doesn't show how hard it is to clue. The 2026-11-16 tabletop playtest
found many prompts harder than expected: clue-givers couldn't see how to start (Taco,
Déjà vu), and guessers missed associations (Popcorn, Snail, Statue of Liberty). A
simulation could screen many prompts cheaply, but only if it agrees with human results.
Simulated results are weaker evidence than human playtests and are used only after
calibration.

## How a simulated game works

A Python script (`tools/simplay.py`) runs the game. The models never talk to each
other directly. The rules and notation are those in [playtesting.md](playtesting.md).

- **Clue-giver (Claude):** gets the prompt, [board-icons.md](board-icons.md),
  [pictured-elements.md](pictured-elements.md) (as a text stand-in for the pictures),
  and the notation rules. It does **not** get the routes recorded in `notes`: the
  tabletop showed human clue-givers don't follow them. Before a game it rates its
  confidence and may skip, like the tabletop skips. It replies in a structured format:
  placements, a verdict on the last guesses (`Correct` / `Yes: <guess>` / `No`), or
  give up. No picture-detail placements. It answers only Yes or No; whether a guess is
  correct is the judge's call.
- **Guesser:** gets only the board reference and the clues so far. llmemo runs each
  `claude -p` call in an empty temporary folder with no tools, so it can't read answers.
  It gives 1–3 guesses per turn, or passes.
- **Both roles get the same board reference:** the icon tables from
  [board-icons.md](board-icons.md) and the picture tables from
  [pictured-elements.md](pictured-elements.md), cut out by heading so the docs' intros
  and worklists (which name prompts) are never sent. The rules summary and role
  instructions are in `tools/sim_prompts/`.
- **The script** validates every placement code and allows nothing but notation, so
  no label words or hints leak. Lines are checked against the board (`tools/notation.py`),
  and an invalid reply is retried with the error. A "Yes" must name one of the guesses.
- **Judge:** a guess that matches the answer (ignoring case, punctuation, accents, and
  a leading article) wins without a call. Otherwise a separate judge call decides,
  using a fixed model (Sonnet, low effort, set in code as `JUDGE`) and
  `tools/sim_prompts/judge.md`. It sees only the answer and the guesses, never the
  clues, and is strict: wording variants a human would accept count, but parts of a
  phrase, broader or narrower things, and neighbors don't. Its request has no variant,
  so every trial and spec shares one verdict for the same answer and guesses. Both modes
  use it, so changing the clue-giver model can't change the scoring. It caps the number of rounds and writes each game in
  the standard notation. It must not use unseeded randomness, so reruns make exactly
  the same calls.
- **Each call is a single prompt.** The Claude CLI request has a system prompt and a
  prompt, not a message history, so the script writes the game so far into the prompt.
  Pass the long reference docs as separate parts of `system` (a list of strings), so
  llmemo stores each one once.
- **Two modes:**
  - **Human clues** (`human-clues`): feed the exact clue sequences from human playtest logs to the model
    guesser. This measures guesser bias directly (does it get Popcorn from the clues
    the human missed?). The clues are read straight from the logs in `playtests/` whose
    guessers were people (tabletop and `claude-clues`), by `tools/playtest_logs.py`;
    the answer is the prompt as it was played. Text logs mark where the guesser
    replied with blank lines (the 2026-11-16 one had them filled in by assumption).
    Tabletop logs have no such pauses, so the script starts a new step at each change
    of group. After the last step the guesser gets
    `extra_rounds` more turns with no new markers, like a human staring at the
    board. Correct guesses are decided by the judge, as in model-clue games; "Yes" answers come
    from the guesses the log marks Yes.
  - **Model clues** (`model-clues`): model clue-giver against model guesser.
- **Repeats:** each prompt is played about 3 times, as llmemo variants (`trial-1`,
  `trial-2`, …). Retries after an invalid reply use llmemo's `attempt`. Per-prompt
  summary: solve rate, average steps, skips, and the most common wrong guesses (the
  likely neighbors).

## Calibration

About 22 prompts have human guessers: card 1 (Claude clues,
`playtests/2026-11-16-claude-clues.md`) and cards 5–6
(`playtests/2026-11-16-tabletop.md`). Card 2 had Claude guessing, so it isn't human
ground truth. The test: does the simulation rank the known failures (Taco, Popcorn,
Snail, Statue of Liberty, Elvis Presley, Rain check, Déjà vu, Selfie) below the known
successes (Pizza, Lighthouse, Drone, Couch potato, Lego, Once in a blue moon, ...)?

Levers against the known bias (Claude guesses more easily than people):

- Cap guesses per turn; people don't list 20 candidates.
- Little or no extended thinking for the guesser. llmemo's Claude CLI request offers
  `effort` (`low` … `max`) but no way to turn thinking off; even a tiny Haiku smoke
  call thought for 63 tokens.
- A weaker guesser model.
- Later, guessers that aren't Claude (via OpenRouter).

Pick the configuration whose results best match the humans. Record it here.

## Backends

Both are llmemo's built-in backends. Requests need full model IDs (llmemo rejects
aliases such as `sonnet`).

- **Now: the owner's Claude subscription** through `claude -p` (llmemo's `ClaudeCli`).
  The plan is Pro, which has the smallest usage limits, shared with interactive use.
  The CLI reports an API-equivalent cost, which counts toward llmemo's spending limit
  and ledger, so it's the measure of usage. Estimate: about 100k input tokens per game,
  mostly cached; measure it in the phase 1 dry run. Use Sonnet as clue-giver and Haiku
  or Sonnet as guesser; Opus drains the limits fast. The CLI can't set temperature, so
  variety comes from repeats.
  - **Usage limit:** when the limit refuses a call, llmemo raises `UsageLimitReached`
    (never cached). `simplay.py run` stops, writes nothing for that spec, and prints when
    the limit resets. Rerun the same command after that; calls already recorded replay.
  - **Speed:** the smoke call (Haiku, structured output) took 14 s. Structured output
    costs the CLI an extra turn. A game of about 12 calls may take a few minutes, so run
    games in parallel with `Cache.acall`, and compare plain-text replies if that's too
    slow.
- **Later, if needed: OpenRouter** (llmemo's `OpenRouter`), for non-Claude guessers and
  more volume. Add it only if Claude-only calibration still shows too much bias. The key
  is in `OPENROUTER_API_KEY`, a Codespaces secret. The smoke test uses
  `openai/gpt-6-luna`, which is cheap and supports structured output
  (`response_format` with a JSON schema).

## Storing results

Results are committed to the repo as llmemo's cache of LLM calls: each raw reply is
stored under a hash of everything sent. Logs and summaries are generated from the
cache. Reruns after a bug fix or a tweak are free wherever a call's inputs haven't
changed.

- `sim-playtests/cache/`: the llmemo cache. Commit it.
- `llm-spend/<branch>/<developer>.jsonl`: llmemo's spending ledger, one row per paid
  call (subscription calls at their API-equivalent cost). Commit it with the entries it
  paid for.
- `sim-playtests/specs/<id>.toml`: a run's settings (mode, prompts, trials, models,
  effort, caps, spend limit). Write one per run; change settings by making a new spec,
  so recorded runs stay reproducible.
- `sim-playtests/runs/<id>.json` and `<id>.md`: written by
  `uv run python tools/simplay.py run <id>`. The JSON has the settings, every game, usage
  per game, and the cache entries used (collected with llmemo's `on_entry_used` hook,
  for pruning). The Markdown has a summary table, usage, and each game in playtest
  notation with the clue-giver's private plans. `simplay.py all` (part of
  `tools/run_all.py`) replays every spec that has a recorded run.
  `uv run python tools/illustrate_logs.py` (also in `run_all.py`) writes a copy with
  icon pictures to `output/illustrated/sim-playtests/`.
- `uv run python tools/simplay.py preview <id> <prompt>` prints the requests a game
  starts with, without calling a model.

Notes:

- Every script and test that calls a model sets `mode="replay"` in code, so a cache
  miss raises `CacheMiss` instead of calling the model. To record, set
  `LLMEMO_MODE=record` on that one command (e.g. `LLMEMO_MODE=record uv run pytest -m llm`);
  never export it in a shell profile. Always set a `spend_limit`. Tests that use the
  cache are marked `@pytest.mark.llm`.
- Editing [board-icons.md](board-icons.md) or [pictured-elements.md](pictured-elements.md)
  changes every call's input, so it invalidates the whole cache. Finish the
  pictured-elements re-banding before calibrating.
- `sim-playtests/` contains answers. A guessing agent must not read it (see CLAUDE.md and
  [playtesting.md](playtesting.md)).

## Phases

1. **Build the harness** on llmemo with the subscription backend and both modes.
   Dry-run 2–3 prompts to measure usage and speed.
2. **Calibrate** on the ~22 human-tested prompts, 3 runs each. Tune the guess cap,
   models, effort, and round cap. Record the findings here.
3. **(Optional) Add OpenRouter guessers** and compare.
4. **If calibrated, use it in card reassembly** (README Next steps): re-rank a
   shortlist per band. The whole pool (about 2,300 games) is too much for Pro.
5. **Record decisions** in the README and update Next steps.
