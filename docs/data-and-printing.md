# Prompt data and printing

How prompts are stored, checked, and turned into printable sheets. Back to
[README](../README.md).

## Setup

```sh
pip install -r requirements.txt
```

## Prompt data: `data/prompts.csv`

This is the single source of truth: one row per prompt, for both the candidate pool
and the cards.

| Column | Meaning |
|---|---|
| `card` | Card number (1, 2, …). Leave blank for prompts in the unassigned pool. |
| `difficulty` | `blue` (easy), `red` (difficult), or `black` (most difficult). |
| `prompt` | The text printed on the card. Follow the [capitalization convention](../README.md#conventions) and [prompt guidelines](prompt-guidelines.md). |
| `category` | Free-form tag (food, animal, expression, title, …), used to balance cards. |
| `source` | `original` for prompts we wrote. For borrowed prompts, the dataset name or URL. |
| `license` | `CC-BY-NC-SA-4.0` for originals. For borrowed prompts, the source's license. |
| `status` | `draft` (not yet reviewed by a person), `approved`, or `rejected`. |
| `notes` | Anything useful. Drafts start with `Clue:` and the icons a clue-giver could use. Add playtest feedback here. |

Rules enforced by `check`:
- Each card has exactly 3 prompts of each difficulty.
- No duplicates. Comparison ignores case, punctuation, leading "the/a/an", and
  trailing plural "s".
- `source` and `license` are required.
- Rejected prompts can't be on a card. Keep them in the file so we don't suggest them
  again.
- Warnings: a prompt longer than 24 characters, or one that doesn't start with a
  capital letter.

Within a card, prompts are numbered in band order (blue 1–3, red 4–6, black 7–9).
Within a band, they keep the order they have in the file.

## Commands

```sh
python tools/cards.py check                     # validate data/prompts.csv
python tools/cards.py pdf                       # all draft + approved cards -> output/cards.pdf
python tools/cards.py pdf --cards 1-9          # just cards 1-9
python tools/cards.py pdf --no-cut-lines       # margin cut marks only, no corner + marks
python tools/cards.py pdf --status approved     # only cards whose prompts are all approved
```

## Printing

- The PDF holds 9 cards per US Letter page with no gaps between them. Each card is
  61.5 × 88.9 mm: MTG height, but 2 mm narrower than MTG so that slightly uneven
  hand-cut cards still fit in sleeves. The size is set by `CARD_WIDTH_MM` and
  `CARD_HEIGHT_MM` in `tools/cards.py`.
- Print at **100% / Actual size**, not "Fit to page". Check one card with a ruler
  before cutting the rest.
- **Cutting:** a faint "+" marks every card corner, so after you cut the columns,
  each strip still shows where to make the cross cuts. The marks in the margins line
  up with the same edges.
- Use cardstock or ordinary paper. In a sleeve, ordinary paper usually feels fine,
  and a spare card behind it stiffens it.

## Player aid with icon codes

```sh
python tools/player_aid.py
```

This downloads the official player aid once and writes the following to
`output/player-aid/`:

- `player-aid-coords.pdf`: the player aid with each icon's code (A1–H14) printed on
  it. Use it when giving or reading clues in text-based playtests.
- `icons/<code>.png`: one image per icon, e.g. `icons/A4.png`.

These files are **not committed**. The player aid is Repos Production's copyrighted
artwork, so everyone generates their own copy for personal use. The code-to-meanings
table is in [board-icons.md](board-icons.md).
