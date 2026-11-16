# Concept Expansion (unofficial)

A free, printable, fan-made expansion deck of new prompts for the party game
[*Concept*](https://boardgamegeek.com/boardgame/147151/concept) by Repos Production.
This project is not affiliated with or endorsed by Repos Production or Asmodee.

## Goals

- **Modern, familiar prompts.** The base deck has dated references and obscure
  phrases (e.g. "What's bred in the bone comes out the flesh"). Every prompt here
  should be something a typical American adult today would recognize right away.
- **Clueable with the board.** Each prompt must be guessable using the icons on the
  Concept board (see the player aid below and [docs/board-icons.md](docs/board-icons.md)).
  Hard prompts should be hard because they need clever clues, not because nobody
  knows what they mean.
- **Drop-in compatible.** Cards use the same 3×3 layout as the base game, so they
  can be swapped with the base deck and play by the normal rules.
- **Easy to print at home.** The cards are Magic: The Gathering size, printed on
  ordinary US Letter paper, cut out, and slid into standard MTG sleeves.
- **Free to share.** Every prompt is original or taken from an openly licensed source,
  and we record where each one came from.

## Resources

- [deep-research-report.md](deep-research-report.md): a ChatGPT deep research report
  on existing expansions, fan content, and open word sources. Use it for ideas only.
  It is not a plan.
- [Concept player aid (PDF)](https://cdn.svc.asmodee.net/production-rprod/storage/games/concept/new-box/helpsheets2026/con-en01-player-aid-mkt-1767696650pHOQV.pdf):
  every board icon and what it can mean. Use it to check whether players can clue a
  word or phrase with the game's concepts. There is a text version in
  [docs/board-icons.md](docs/board-icons.md).
- [Concept rules (PDF)](https://cdn.svc.asmodee.net/production-rprod/storage/games/concept/new-box/rules2026/con-us01-rules-mkt-1767695504Rco5p.pdf):
  the official rules of the game.

## Card format

Each card follows the base game's layout: **9 numbered prompts in three bands of 3**.

| Prompts | Band color | Difficulty |
|---|---|---|
| 1–3 | Blue | Easy |
| 4–6 | Red | Difficult |
| 7–9 | Black | Most difficult |

- **Size:** 2.5 × 3.5 in (63 × 88 mm), the same as MTG cards. Portrait orientation.
- **Sheet:** 9 cards per US Letter page (3 × 3), with cut marks.
- **Fronts only.** Opaque-backed sleeves hide the back.
- Cards get a small set mark and card number so expansion cards can be told apart
  from base cards. The set mark is a placeholder, "CX", until the expansion is named.
- **No official art.** Do not use Concept artwork, logos, or trade dress. Use plain
  text and the three band colors only.

## Conventions

- **Language:** American English spelling and usage.
- **Capitalization:** capitalize the first letter of each prompt. Write the rest the
  way it is normally written (proper nouns and titles capitalized, common words
  lowercase). Examples: "Bee", "Fire station", "Break the ice", "The Lion King".
- **Prompt content:** follow the rules in [docs/prompt-guidelines.md](docs/prompt-guidelines.md).
- **Prompt data and printing:** all prompts are stored in `data/prompts.csv`, and
  `tools/cards.py` checks them and builds the PDF. See
  [docs/data-and-printing.md](docs/data-and-printing.md).
- **Provenance:** for every prompt, record where it came from (original, or which
  dataset and license). We need this for attribution and licensing.
- **Private material** (such as a transcribed base-game prompt list for duplicate
  checks) goes in `private/`, which is gitignored. Never commit it.
  Generated PDFs go in `output/`, which is also gitignored.
- **Borrowed prompts:** keep prompts from third-party sources to a small share of
  the deck, and prefer original ones. Material from someone else stays under their
  terms, so every borrowed prompt makes it harder to license the deck commercially later.

## Licenses

- **Code** (scripts in `tools/` and so on): MIT. See [LICENSE](LICENSE).
- **Card content** (prompts, card layouts, generated PDFs):
  [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
  See [LICENSE-CONTENT.md](LICENSE-CONTENT.md). Third-party prompts keep their
  original licenses, which are recorded per prompt and credited.
- The project owner may also license their own content under other terms, including
  commercially. The CC license is non-exclusive.

## Contributing

By contributing prompts or other content, you agree that it is released under the
licenses above, and that the project owner may also license your contributions under
other terms, including commercially.

## Decisions

Newest at the bottom. Include the date and a one-line reason.

| Date | Decision | Why |
|---|---|---|
| 2026-11-16 | English-language (American English) expansion | Our players' language |
| 2026-11-16 | MTG-size cards (2.5 × 3.5 in), 9 per US Letter page, fronts only | Prints on ordinary paper and fits standard MTG sleeves |
| 2026-11-16 | Same 3×3 layout as the base game (3 Blue, 3 Red, 3 Black) | Mixes into the base deck with no rule changes |
| 2026-11-16 | Deck will be shared publicly for free | Others have the same problem with the base deck |
| 2026-11-16 | Only original or openly licensed prompts. Never copy base-game prompts or other commercial games' cards | Required to share publicly |
| 2026-11-16 | No official Concept artwork or logos | Avoid trademark and copyright issues |
| 2026-11-16 | Prompts come from a mix: AI-drafted candidates plus filtered open datasets, reviewed by humans and playtested | Combines speed with judgment about what players actually know |
| 2026-11-16 | Target 100 cards (900 prompts). Playtest about 25 cards first | Matches the base game's size |
| 2026-11-16 | Include some recent pop culture in the main deck, but only items likely to stay recognizable for years. No separate swappable module | Keeps the deck fresh without dating fast |
| 2026-11-16 | Card content license: CC BY-NC-SA 4.0. Code stays MIT. Contributors agree to let the owner relicense | Prevents others from selling the deck, keeps the owner able to license it commercially, and allows NC-SA sources such as Monikers |
| 2026-11-16 | Keep borrowed third-party prompts to a minimum and prefer original ones | Third-party prompts can't be relicensed without their creators' permission |
| 2026-11-16 | Prompts are stored in one CSV (`data/prompts.csv`), one row per prompt, with a blank card number for the unassigned pool | Simple to edit by hand or in a spreadsheet, and git diffs stay readable |
| 2026-11-16 | Python + reportlab generate the PDF. No gaps between cards; cut marks in the margins, with an optional outline | 3×3 MTG cards only fit on Letter paper with no gaps |

## Next steps

1. **Test print.** Print `output/cards.pdf` (run `python tools/cards.py pdf`) at
   100% scale, cut out one card, and check that it fits an MTG sleeve and the text is
   easy to read. Adjust the layout in `tools/cards.py` if needed.
2. **Review the 9 draft cards** (cards 1–9 in `data/prompts.csv`). Set each prompt to
   `approved` or `rejected`, and update the guidelines with anything you learn.
3. **Draft cards 10–25** to complete the playtest set of about 25 cards.
4. **Playtest.** Record failures and why in the `notes` column, revise the
   guidelines, then scale up toward 100 cards.
5. **Evaluate open sources** from the research report (Open Party Game Word Lists,
   OpenWord Lexicon, idiom corpora) as pools of candidate prompts, keeping borrowed
   prompts to a minimum.

### Future tasks

- **Base-game prompt list for duplicate checks.** Planned for after the first playtest.
  Put it in `private/` and never commit it. Status of the search (2026-11-16):
  - No official list or PDF of the base-game cards from Asmodee or Repos was found.
  - The [IneG/concept](https://huggingface.co/datasets/IneG/concept) dataset on
    Hugging Face contains English targets with card numbers and difficulty, taken from
    Board Game Arena game logs. It is gated: you need a Hugging Face account and must
    accept its terms (CC BY-NC 4.0, research use only). It only contains prompts that
    came up in logged games, so it may not cover all 990. Using it for duplicate
    checks is outside its stated research-only purpose.
  - BoardGameGeek threads to check by hand (they block automated access):
    [List of English cards?](https://boardgamegeek.com/thread/1564788/list-of-english-cards)
    and [Spreadsheet of all cards](https://boardgamegeek.com/thread/1564116/spreadsheet-of-all-cards).
    The second may not be about Concept.
  - Fallback: transcribe a physical deck.
- **Expansion name and set mark** to print on each card.
