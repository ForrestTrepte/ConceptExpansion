# Prompt pipeline

How prompts go from candidates to cards: analyze them with a rubric, playtest the most
promising ones with the owner's group, check the rubric against what happened, and
repeat. Back to [README](../README.md).

Simulated playtesting (models giving clues and guessing) doesn't predict what people
solve, so it isn't part of this loop. See
[simulated-playtesting.md](simulated-playtesting.md#findings-so-far-2026-11-23).

## The loop

```
  candidate pool (data/prompts.csv)
        │
        ▼
  1. analyze ── rubric scores for each prompt (screen, then rank)
        │
        ▼
  2. select ─── 3 cards (27 prompts) the group hasn't seen
        │
        ▼
  3. playtest ─ the group plays them; score sheet + board photos
        │
        ▼
  4. log ────── playtests/YYYY-MM-DD-tabletop.md, with ratings
        │
        ▼
  5. evaluate ─ which rubric measures predicted the results?
        │
        └──▶ revise the rubric and guidelines, re-score, next round
```

One round is about the size the group plays in two weekly sessions.

## 1. Analyze

The rubric is in [prompt-guidelines.md](prompt-guidelines.md#clueability-rubric). It
breaks clueability into separate measurements (foothold, parts and their distance from
the icons, exact wording, neighbors, routes, fun) rather than a single opinion, so each
measurement can be checked against playtest results.

A script will apply the rubric to every candidate through llmemo (cached, so a rubric
change re-scores at a known cost and unchanged prompts replay free). It runs in two
phases to keep the cost down on the ~650-prompt pool:

- **Screen** (a cheaper model and a short prompt): the measures that rule prompts out:
  familiarity, foothold, far parts, exact-wording traps, pictured on the board,
  family-friendly. Clear failures are marked `rejected` with the reason.
- **Rank** (a stronger model, the full rubric, 2–3 samples per prompt): routes,
  neighbors, and fun for the prompts that pass. Disagreement between samples is
  itself a signal that a prompt is borderline.

An AI session reviews the results, especially borderline prompts, and assembles cards.
The script's output is evidence, not the final word.

## 2. Select a round

- **27 prompts on 3 cards**, balanced as in
  [prompt-guidelines.md](prompt-guidelines.md#building-cards-from-the-pool).
- **Only prompts the guessers haven't seen.** A player has seen a prompt if they
  clued or guessed it in a logged game. So far that's cards 5 and 6 for the group
  (tabletop 2026-11-16), plus, for Forrest, the text playtests and every `play` game.
  Merely glancing at a printed card doesn't count. The logs record who played.
- **About 2/3 best candidates, 1/3 to learn from.** If only top-scoring prompts are
  played, nobody finds out whether the rubric wrongly marks some prompts down. The
  "learn" third are prompts where the measures disagree, the samples disagree, or the
  score is near a level boundary. No label is needed: the evaluation re-scores the
  round with the rubric version used for selection (llmemo replays it free), so it
  can see which prompts were borderline.

## 3–4. Playtest and log

See [playtesting.md](playtesting.md#tabletop-sessions): print a score sheet with
`tools/scoresheet.py`, tick result, time, difficulty, and interest for each prompt,
note who clued and guessed, and photograph the final board. An AI session turns the
sheet and photos into log entries.

## 5. Evaluate and revise

Compare each rubric measure with the playtest results: solved / gave up / skipped,
time, and the group's difficulty and interest ratings. Questions to answer each round:

- Which measures separate solved from failed or skipped prompts? Which predict nothing?
- Does the predicted band match the group's difficulty rating?
- Do "fun" measures (routes, picture play, neighbors) match the interest rating?

**How to combine the measures.** The difficulty and quality scores in the rubric are
weighted sums with hand-set weights. With about 45 played prompts, fitting the weights
by regression would overfit: an ordinal logistic regression (the levels are ordered)
needs roughly 10 outcomes per measure, and there are 5 difficulty measures. So, for
now:

1. Check the hand-set score against the results: rank correlation with the group's
   difficulty rating, and how well it separates solved from failed or skipped.
2. Check each measure on its own the same way. Drop or rewrite the ones that predict
   nothing, and adjust weights only where the data clearly point one way.
3. Fit the weights (ordinal logistic regression, few predictors, checked by
   leave-one-out) once there's enough data: after several rounds, or sooner on the
   IneG/concept dataset, which has thousands of games with base-game difficulty bands.
   Weights fit on the base game would then be checked on our own playtests.

Record what changed in prompt-guidelines.md, and re-score the pool.

## Backlog

- **More candidates.** There are about 630 unplayed drafts, enough for many rounds. If
  analysis shows gaps (too few strong prompts in a band or category): an LLM
  brainstorming command using several models, and the CC BY 4.0
  [Open Party Game Word Lists](https://github.com/ylwl1997/party-game-word-lists).
  See [deep-research-report.md](../deep-research-report.md) for other sources.
- **The IneG/concept dataset** (Board Game Arena games of base-game prompts) could
  check the rubric against thousands of human games. It is gated and research-only;
  the owner will discuss asking its author for permission separately.
- **Testers outside the group.** After a couple of rounds, an alpha release on BGG to
  ask for feedback and recruit playtesters. A web page where people guess from
  recorded clue sequences could add several guessers per prompt.
- **Simulation, revisited.** Only if much more human data (several guessers per
  prompt) suggests a model could match people after all.
