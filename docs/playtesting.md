# Text playtesting

How to playtest prompts in a chat conversation (for example, a person with Claude)
without the physical board. Back to [README](../README.md).

Tabletop playtests with printed cards are the strongest evidence. Log them in
`playtests/YYYY-MM-DD-tabletop.md` in the same per-prompt format as below, with the
ratings described under [Tabletop sessions](#tabletop-sessions). Also record any house
rules. Three or more players (two or more guessers) is typical and gets stuck less
often than two. How tabletop rounds fit into choosing prompts is in
[prompt-pipeline.md](prompt-pipeline.md).

There are two text-playtest modes, each run in a fresh conversation:

- **Claude gives clues, the human guesses.** Tests whether the prompt can be clued and
  whether people recognize it. This is the main evidence.
- **The human gives clues, Claude guesses.** A useful second check, but weaker
  evidence: Claude drafted the prompts and thinks in similar patterns, so it may find
  them easier than people do.

## Playing against the clue-giver model

To guess against a model clue-giver in the terminal, with no chat session:

```
LLMEMO_MODE=record uv run python tools/simplay.py play play
```

Each game uses a random unassigned draft prompt that isn't in any log, the judge
decides correct guesses, and the finished game is added to today's `claude-clues` log
as a `### Pool:` entry with real pauses. Keep `output/illustrated/play/current.md` open
in the Markdown preview to see the board with pictures. The spec
`sim-playtests/specs/play.toml` sets the model and the spend limit (calls are live).
Each game's cache entries carry a `game` tag (`<date>/<prompt>`), which the log entry
also lists. Games logged before the tag existed (2026-11-23) can be found by the
answer in their requests ("The answer is: …", "Answer: …").
Don't read `data/prompts.csv` or the logs between games, since they contain the
answers to come.

## Setup

- Generate the coded player aid with `uv run python tools/player_aid.py` and keep
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
- Clue-giver: Claude · Guessed: yes (step 3) · Verdict: keep
- Clues:
  ```
  ?g B8
  + F9

  !r A14
  + B10

  + C6
  ```
- Notable guesses: Birthday party (Yes), Slice
- Comments: guesser first thought it was a food, not an expression
~~~

Simulated playtests read these logs (`tools/playtest_logs.py`), so keep to this form.
`uv run python tools/playtest_logs.py check` checks it, and `tools/run_all.py` runs it.
To read the logs with icon pictures instead of codes, run
`uv run python tools/illustrate_logs.py` and open `output/illustrated/playtests/` in
VS Code's Markdown preview.

- **Heading:** `### Card N, #K: Prompt`, with the prompt as it was played, or
  `### Pool: Prompt` for an unassigned prompt. Other `###` headings (such as
  `### Card 5 observations`) are fine, but not ones starting `### Card` or `### Pool`
  that look like a broken entry.
- **First line:** `- Clue-giver: <Claude|human> · Guessed: <result> · Verdict: <verdict>`.
  The clue-giver may name a model in parentheses: `Claude (claude-sonnet-5-5)`.
  The result is `yes`, `no`, `skipped`, or `not played`, optionally followed by a note
  in parentheses, such as `yes (step 4)` or `no (passed after step 2)`. The verdict can
  be left out for `not played`.
- **Clues:** played prompts (`yes` or `no`) have one `- Clues:` line (it may say more
  in parentheses, e.g. `- Clues (main attempt of several):`) followed by a code block
  in the standard notation. Skipped and unplayed prompts have none. Other code blocks,
  such as an untried route in the comments, are ignored.
- **Pauses (text playtests only):** a blank line in the clue block marks where the
  guesser replied, so each part is one step. No blank line means everything was sent
  at once. **Tabletop logs never have pauses:** the clue-giver keeps placing markers
  while people guess. For simulated guessers, the script splits a tabletop game into
  steps itself, at each change of group.
- **Notable guesses:** comma-separated. Mark guesses the clue-giver answered `Yes` to
  with ` (Yes)` right after them.
- **Players and ratings (tabletop):** lines right after the first line, each optional:
  ```
  - Players: clue-giver B; guessers Forrest, C
  - Time: 3 min
  - Difficulty: hard (we nearly had it)
  - Interest: high
  ```
  Time is whole minutes. Difficulty and interest must be one of the values under
  [Tabletop sessions](#tabletop-sessions), optionally followed by a short comment in
  parentheses. Skipped prompts usually have only the Players line.

### Tabletop sessions

Before a round, print a score sheet for its cards:
`uv run python tools/scoresheet.py 19-21` writes `output/scoresheet-19-21.pdf`. It
lists prompts by card and number only (never the text), so anyone at the table can
fill it in. For each prompt, tick:

- **Result:** solved, gave up, or skipped. Skipping is allowed: the clue-giver may skip
  after about a minute of planning if they can't see how to start, and should say why
  in a few words. A skip is useful data (no foothold), so don't force an attempt.
- **Time:** roughly how many minutes it took, rounded to a whole number.
- **Difficulty**, agreed by the group: too easy, easy, medium, hard, too hard.
- **Interest**, agreed by the group: low, medium, high, fantastic.
- **Who** gave the clues and who guessed. Use a first name or an initial (B).

Photograph the final board of each played prompt with its card number visible. The
order of moves isn't recorded; the final board is enough. Comments (why it was fun,
where people got stuck) go on the back of the sheet.

Afterwards, give the sheet and photos to an AI session, which writes the log entries
(clues converted to notation, the players and ratings lines, comments). In the log, the ratings
become `Time: <N> min`, `Difficulty: too easy | easy |
medium | hard | too hard`, and `Interest: low | medium | high | fantastic`. A skip
is `Guessed: skipped (<reason>)`; gave up is `Guessed: no`.

**Verdicts:** `keep`, `too easy`, `too hard`, `unclear` (players didn't recognize it),
`reword`.

At the end of the session, the AI adds a one-line summary to each tested prompt's
`notes` in `data/prompts.csv` (e.g. `Playtest 2026-11-17: guessed in 4 steps, keep`).
It then proposes `status` changes (`approved` / `rejected`), which a human confirms.
When Claude was the guesser, the session updates `data/prompts.csv` only after all
guessing is finished.
