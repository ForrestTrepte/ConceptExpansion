# Text playtesting

How to playtest prompts in a chat conversation (for example, a person with Claude)
without the physical board. Back to [README](../README.md).

Tabletop playtests with printed cards are the strongest evidence. Log them in
`playtests/YYYY-MM-DD-tabletop.md` in the same per-prompt format as below. Also record
the number of players, which prompts were skipped, and any house rules. Three or more
players (two or more guessers) is typical and gets stuck less often than two.

There are two text-playtest modes, each run in a fresh conversation:

- **Claude gives clues, the human guesses.** Tests whether the prompt can be clued and
  whether people recognize it. This is the main evidence.
- **The human gives clues, Claude guesses.** A useful second check, but weaker
  evidence: Claude drafted the prompts and thinks in similar patterns, so it may find
  them easier than people do.

## Setup

- Generate the coded player aid with `python tools/player_aid.py` and keep
  `output/player-aid/player-aid-coords.pdf` open. Icon codes and meanings are in
  [board-icons.md](board-icons.md). There's an illustrated version at
  `output/player-aid/board-icons.md`.
- The clue-giver chooses the prompts. We test **every** prompt, working through a card
  in order (1–9). Only the clue-giver knows the card number and the prompt.
- **When Claude is the guesser,** it must not read `data/prompts.csv`, `playtests/`,
  `sim-playtests/` (simulated playtests), the generated card PDFs, or git history,
  since all of them contain the answers.
- If you play both modes, use different cards in each. Once you've seen an answer,
  you can't guess it fairly.

## Starting a session

Open a new conversation and start with one of these:

- **Claude gives clues, the human guesses:**
  > Let's run a text playtest per docs/playtesting.md. You give clues, starting with card 1.
- **The human gives clues, Claude guesses:**
  > You are the guesser in a text playtest (docs/playtesting.md). Do not read any prompt or playtest files.

Change the card number to continue where an earlier session stopped.

## Notation

Icons are written as grid codes (`A4`, `G14`, …). The color swatches are written by
name: `Red`, `Orange`, `Yellow`, `Green`, `Blue`, `Purple`, `Pink`, `Brown`, `Black`,
`Grey`, `White`, `Clear`. A code means the whole icon with all its meanings. Never
write an icon's label words in clues.

A clue is a series of placements, one per line, in the order they were made.

### Groups

Each pawn and its matching cubes form a group, written with one letter:

| Letter | Group |
|---|---|
| `g` | Main Concept (green `?` pawn) |
| `r`, `y`, `b`, `k` | Sub-Concepts (red, yellow, blue, black `!` pawns) |

Group colors carry no meaning; they only show which markers belong together. To make
a color part of a clue, put a cube on a color swatch. If the clue-giver picked a pawn
color on purpose, say so in a comment.

### Lines

| Line | Meaning |
|---|---|
| `?g A4` | Place the Main Concept pawn on A4 |
| `!r B11` | Place the red Sub-Concept pawn on B11 |
| `+ B11` | Cube on B11, in the same group as the line before |
| `+g G14` | Green cube on G14 (name the group when it differs from the line before) |
| `+ G4 x2` | Two cubes on G4 |
| `- G4` | Remove a cube from G4 (same group rule as `+`) |
| `-?g`, `-!r` | Remove a pawn (to move it, remove it and place it again) |
| `-r all` | Clear the whole red group, pawn and cubes |
| `[...]` | Comment at the end of a line: where on a picture a marker went, or anything else the notation can't show |

**Group rule:** a cube line (`+` or `-`) leaves out the group letter when the
previous line is in the same group, and names it otherwise. The first line of a
clue always names its group.

**Order is free.** The rules describe placing the Main Concept first, then
Sub-Concepts, each pawn before its cubes. That is a good way to plan, not a
requirement: cubes can come before their pawn or have no pawn at all, and
Sub-Concepts can come before the Main Concept. The notation is the same either way.

**Picture details:** some groups place a marker on one detail inside an icon's
picture (the octopus in A4). Write it as a comment: `+ A8 [on the bulb]`. This house
rule is fine in play, but prompts must not depend on it (see
[prompt-guidelines.md](prompt-guidelines.md)).

**Example** (Bee, from the rules: an animal that flies and is yellow and black, flies
around flowers, and is connected to an edible yellow liquid):

```
?g A4
+ B11
+ Yellow
+ Black
!r B11
+ G14
+ B4
!y A14
+ F3
+ Yellow
```

### Shorthand in chat

When typing clues in chat, these shortcuts are fine. Logs and other committed files
use only the standard form above, so convert shorthand when writing the log.

| Shorthand | Standard form |
|---|---|
| `? A4` | `?g A4` |
| `!red B11`, `!blu B11`, `?green A4` (full or partial color names) | `!r B11`, `!b B11`, `?g A4` |
| `+r G14` right after a red line (repeating the group) | `+ G14` |
| `+E2` (no space) | `+ E2` |
| `!b E8 D3`, `+ C11 H9` (several codes on one line) | one line per marker: `!b E8`, `+ D3`; `+ C11`, `+ H9` |

## Turn flow

1. The clue-giver chooses a prompt and says **"New prompt."** Nothing else: no card
   number, no difficulty band, no word count.
2. The clue-giver sends **any number of notation lines** per message.
3. The guesser replies with **any number of guesses**, e.g. `Cat, Dog, Mouse`. At any
   time they can also send:
   - `board?`: the clue-giver replies with the current board grouped by color, in
     placement order, for example:
     ```
     ?g A4  | B11, Yellow, Black
     !r B11 | G14, B4
     ```
   - `pass`: give up on this prompt.
4. The clue-giver answers with exactly one of:
   - `Correct: <answer>`: the turn ends.
   - `Yes: <one of the guesses>`: that guess is on the right track.
   - `No`
   - Then, optionally, more notation lines.
   No other hints: no "warmer", "almost", or explanations.
5. A turn ends with `Correct`, with the guesser's `pass`, or when the clue-giver gives
   up. On a pass or give-up, the clue-giver reveals the answer.
6. After each turn, both players may comment briefly (e.g. "never heard of it",
   "clue C13 was misleading"). The comments go in the log.

## Recording results

The AI session (whichever role it plays) keeps a log as it goes, in
`playtests/YYYY-MM-DD-<mode>.md`, where mode is `claude-clues` or `human-clues`. One
entry per prompt:

~~~markdown
### Card 3, #7: Piece of cake
- Clue-giver: Claude · Guessed: yes (step 4) · Verdict: keep
- Clues:
  ```
  ?g B8
  + F9
  + A14
  ...
  ```
- Notable guesses: Birthday party, Slice
- Comments: guesser first thought it was a food, not an expression
~~~

**Verdicts:** `keep`, `too easy`, `too hard`, `unclear` (players didn't recognize it),
`reword`.

At the end of the session, the AI adds a one-line summary to each tested prompt's
`notes` in `data/prompts.csv` (e.g. `Playtest 2026-11-17: guessed in 4 steps, keep`).
It then proposes `status` changes (`approved` / `rejected`), which a human confirms.
When Claude was the guesser, the session updates `data/prompts.csv` only after all
guessing is finished.
