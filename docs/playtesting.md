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
  the generated card PDFs, or git history, since all of them contain the answers.
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

Icons are written as grid codes (`A4`, `G14`, …). Colors are written by name: `Red`,
`Orange`, `Yellow`, `Green`, `Blue`, `Purple`, `Pink`, `Brown`, `Black`, `Grey`,
`White`, `Clear`. A code means the whole icon with all its meanings. Never write an
icon's label words in clues.

| Line | Meaning |
|---|---|
| `? A4` | Place the green Main Concept pawn on A4 (`? green A4` also works) |
| `+ B11` | Cube on B11, in the current color (see below) |
| `+ G4 x2` | Two cubes on G4 |
| `!red B11` | Place the red Sub-Concept pawn on B11 (also `!yellow`, `!blue`, `!black`; `! red B11` also works) |
| `+red G14` | Red cube on G14 (naming a color is optional) |
| `- G4` | Remove one cube from G4, in the current color (`-red G4` for a red cube) |
| `-red` | Clear the whole red Sub-Concept, both pawn and cubes |
| `-?` | Remove the Main Concept pawn (then place it again with `? <code>`) |

**Current color:** a cube line without a color uses the color of the most recently
placed pawn or colored cube. So after `!red E10`, a plain `+ C11` is a red cube. To go
back to adding green cubes after a Sub-Concept, write `+green <code>`.

Order matters: lines are read in the order they were placed.

**Example** (Bee, from the rules: an animal that flies and is yellow and black, flies
around flowers, and is connected to an edible yellow liquid):

```
? A4
+ B11
+ Yellow
+ Black
!red B11
+ G14
+ B4
!yellow A14
+ F3
+ Yellow
```

## Turn flow

1. The clue-giver chooses a prompt and says **"New prompt."** Nothing else: no card
   number, no difficulty band, no word count.
2. The clue-giver sends **any number of notation lines** per message.
3. The guesser replies with **any number of guesses**, e.g. `Cat, Dog, Mouse`. At any
   time they can also send:
   - `board?`: the clue-giver replies with the current board grouped by color, in
     placement order, for example:
     ```
     GREEN   ? A4   | B11, Yellow, Black
     RED     ! B11  | G14, B4
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
  ? B8
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
