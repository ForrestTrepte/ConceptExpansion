# Simulated playtesting with LLMs

Plan for playtests where one model gives clues and another guesses. Back to
[README](../README.md).

**Status (2026-11-19): planned, not built.** The harness is waiting for a reusable
LLM-call cache package that the owner is finding or building (see
[Cache requirements](#cache-requirements)). Don't build the harness, or a stand-in cache,
until that package is ready.

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
  give up. No picture-detail placements.
- **Guesser:** gets only the board reference and the clues so far. It runs with no
  tools from a folder outside the repo, so it can't read answers. It gives 1–3
  guesses per turn, or passes.
- **The script** validates every placement code and allows nothing but notation, so
  no label words or hints leak. It caps the number of rounds and writes each game in
  the standard notation. It must not use unseeded randomness, so reruns make exactly
  the same calls.
- **Two modes:**
  - **Replay:** feed the exact clue sequences from human playtest logs to the model
    guesser. This measures guesser bias directly (does it get Popcorn from the clues
    the human missed?).
  - **Full game:** model clue-giver against model guesser.
- **Repeats:** each prompt is played about 3 times. Per-prompt summary: solve rate,
  average steps, skips, and the most common wrong guesses (the likely neighbors).

## Calibration

About 22 prompts have human guessers: card 1 (Claude clues,
`playtests/2026-11-16-claude-clues.md`) and cards 5–6
(`playtests/2026-11-16-tabletop.md`). Card 2 had Claude guessing, so it isn't human
ground truth. The test: does the simulation rank the known failures (Taco, Popcorn,
Snail, Statue of Liberty, Elvis Presley, Rain check, Déjà vu, Selfie) below the known
successes (Pizza, Lighthouse, Drone, Couch potato, Lego, Once in a blue moon, ...)?

Levers against the known bias (Claude guesses more easily than people):

- Cap guesses per turn; people don't list 20 candidates.
- No extended thinking for the guesser.
- A weaker guesser model.
- Later, guessers that aren't Claude (via OpenRouter).

Pick the configuration whose results best match the humans. Record it here.

## Backends

- **Now: the owner's Claude subscription** through the official CLI run headless
  (`claude -p --model <id> --tools "" --strict-mcp-config --setting-sources ""
  --no-session-persistence --system-prompt ... --output-format json`), from a working
  directory outside the repo. A test call on Haiku worked (about 1 s). The plan is Pro,
  which has the smallest usage limits, shared with interactive use. Estimate: about
  100k input tokens per game, mostly cached. Measure real usage in the dry run. Use
  Sonnet as clue-giver and Haiku or Sonnet as guesser; Opus drains the limits fast.
  The CLI can't set temperature, so variety comes from repeats.
- **Later, if needed: OpenRouter**, for non-Claude guessers (GPT, Gemini) and more
  volume. Add it only if Claude-only calibration still shows too much bias. The key
  goes in an environment variable from a gitignored `.env`, never in chat or git.

## Storing results

Results are committed to the repo as a **cache of LLM calls**: each raw reply is
stored under a hash of everything sent. Logs and summaries are generated from the
cache. Reruns after a bug fix or a tweak are free wherever a call's inputs haven't
changed. Planned layout (adjust to the package):

- `sim/cache/`: the cache entries, one JSON file per call.
- `sim/runs/<run-id>.json`: the run's settings and list of games.
- Generated summaries in the playtest notation (committing them is optional).

Notes:

- Editing [board-icons.md](board-icons.md) or [pictured-elements.md](pictured-elements.md)
  changes every call's input, so it invalidates the whole cache. Finish the
  pictured-elements re-banding before calibrating.
- `sim/` contains answers. When it's created, add it to the guesser's no-read list in
  CLAUDE.md and [playtesting.md](playtesting.md).
- Use full model IDs (e.g. `claude-sonnet-5-5`), not aliases, which move to new models.

## Cache requirements

Requirements for the reusable package. Check the package against them before using it.

**Key**
1. Stable hash (e.g. SHA-256) of a canonical form of the request: sorted keys, fixed
   JSON encoding, no Python `hash()` or pickle.
2. The caller supplies the key contents: backend, exact model ID, system prompt,
   messages, tools, all settings, and attached files or images (hashed by content).
3. A variant string in the key (e.g. `trial-2`), for independent samples of the same
   request. (Changed 2026-11-20 from a replicate number: a free-form string also covers
   rerolls.)
4. An attempt number in the key, so retries replay too.
5. Fields left out of the key are declared explicitly (timeouts, API keys, CLI
   version) and recorded only as metadata.
6. A versioned key format.

**Stored data**
7. The raw reply, unchanged. Parsing is the caller's job.
8. Metadata: timestamp, latency, token usage, cost, the model that answered, tool or
   CLI version, caller-defined tags (run, game, role).
9. Never store secrets.
10. Configurable caching of failed calls. Invalid but delivered replies are cached.

**Storage**
11. Git-friendly text: one pretty-printed JSON file per entry, stable key order, UTF-8,
    LF, trailing newline, in hash-prefix folders. Not SQLite or pickle.
12. Large repeated inputs (system prompts, reference docs) stored once by hash.
13. Writes done in one step (temp file + rename), safe for parallel threads and
    processes.
14. No silent overwrites; replacing an entry takes an explicit refresh.

**Modes**
15. Read-write. There's no default mode: the harness must choose read-write or
    cache-only. (Changed 2026-11-20: neither default is safe for every caller.)
16. Cache-only: a miss is an error.
17. Refresh for selected entries.
18. ~~Dry run: count misses and estimate their cost without calling.~~ Dropped (2026-11-20):
    in a multi-turn game, every call after the first miss depends on the missing reply,
    so misses can't be counted ahead. [llmemo](https://github.com/ForrestTrepte/llmemo)
    offers a `contains(key)` check instead.

**Backends and API**
19. Wraps any `request -> response` callable: HTTP SDKs (Anthropic, OpenAI-compatible
    endpoints such as OpenRouter) and subprocess calls (`claude -p`). This project
    needs the subprocess case.
20. Small API, e.g. `cache.call(request, fn, replicate=0, tags={...})`. Sync required,
    async a plus, safe for parallel calls.
21. Few dependencies, Python 3.12+, MIT-compatible license. (Changed 2026-11-20 from
    3.10+: every project that will use the package runs 3.12.)

**Analysis and maintenance**
22. ~~Query entries by tag or metadata without calling a model.~~ Dropped (2026-11-20):
    iterating over the entries is enough.
23. ~~Run manifests listing the keys a run used.~~ Dropped (2026-11-20): llmemo reports
    each entry a run uses through a hook, so the harness can save that list itself.
24. Prune entries no recent run used.
25. Nice to have: explain a miss by showing which field differs from the nearest entry.
26. Nice to have: a command-line tool for stats, showing entries, misses, and pruning.

## Phases

1. **Build the harness** on the cache package with the subscription backend and both
   modes. Dry-run 2–3 prompts to measure usage.
2. **Calibrate** on the ~22 human-tested prompts, 3 runs each. Tune the guess cap,
   models, and round cap. Record the findings here.
3. **(Optional) Add OpenRouter guessers** and compare.
4. **If calibrated, use it in card reassembly** (README Next steps): re-rank a
   shortlist per band. The whole pool (about 2,300 games) is too much for Pro.
5. **Record decisions** in the README and update Next steps.
