# New Notions

*An unofficial fan expansion for Concept.*

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

- **Size:** 60.5 × 85.9 mm, portrait. That's MTG size (63.5 × 88.9 mm, 2.5 × 3.5 in)
  made 3 mm smaller each way, so slightly uneven hand-cut cards still slide into MTG sleeves.
- **Sheet:** 9 cards per US Letter page (3 × 3), with cut marks.
- **Fronts only.** Opaque-backed sleeves hide the back.
- Cards get a small set mark and card number so expansion cards can be told apart
  from base cards. The set mark is "NN" (*New Notions*), followed by the version
  (e.g. "NN v0.1").
- **Version:** the content version in `data/VERSION`. Bump it when the prompts on the
  cards change (prompts added, removed, reworded, or moved between cards or bands),
  not for layout or other cosmetic tweaks. 0.x versions are playtest decks; the
  first release will be 1.0.
- **No official art.** Do not use Concept artwork, logos, or trade dress. Use plain
  text and the three band colors only.

## Conventions

- **Language:** American English spelling and usage.
- **Capitalization:** capitalize the first letter of each prompt. Write the rest the
  way it is normally written (proper nouns and titles capitalized, common words
  lowercase). Examples: "Bee", "Fire station", "Break the ice", "The Lion King".
- **Prompt content:** follow the rules in [docs/prompt-guidelines.md](docs/prompt-guidelines.md).
- **Playtesting:** text playtests by chat follow
  [docs/playtesting.md](docs/playtesting.md). Logs go in `playtests/`.
- **LLM calls** (simulated playtests) go through llmemo, which caches them in
  `sim-playtests/cache/` and records spending in `llm-spend/`. Both are committed. See
  [docs/simulated-playtesting.md](docs/simulated-playtesting.md).
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
| 2026-11-16 | Print a small, faint "+" at every card corner, in addition to the margin marks | Margin marks are lost after the first round of cuts. Full cut lines showed on the finished cards |
| 2026-11-16 | Board icons are referred to by grid codes (A1–H14) from the player aid, and colors by name. `tools/player_aid.py` makes a local annotated copy of the player aid and icon images. Neither is committed | Naming an icon by one of its labels would tell the guesser which meaning is intended. The artwork is copyrighted |
| 2026-11-16 | Text playtests in chat, in both directions, using code-based clue notation, with a log per session in `playtests/` | Lets us test prompts without the physical game. The logs keep the clue sequences |
| 2026-11-16 | Prompts whose parts each map directly to an obvious icon go in Blue. Hard-to-show ideas are welcome in Red and Black | Card 1 playtest: Food truck went in one step. Selfie and Break the ice were hard but fun |
| 2026-11-16 | Use multi-word phrases only when they're set phrases said word for word; otherwise trim to the core ("Snooze button", not "Hit the snooze button") | Card 1 playtest: the guesser had the idea quickly but got stuck on the exact words |
| 2026-11-16 | In playtest notation, a cube line with no color uses the color of the last pawn or colored cube | Clue-giver's request: less typing during play |
| 2026-11-16 | Name: *New Notions: an unofficial fan expansion for Concept*. Set mark "NN" | "Notion" is a synonym for concept and "new" says more prompts. "Concept" stays out of the name itself so it isn't mistaken for an official product |
| 2026-11-16 | Bands are set by how far a prompt's hardest part is from the icons (direct / built / far), plus a first-guess test. See [docs/prompt-guidelines.md](docs/prompt-guidelines.md) | Explained every playtest result better than the earlier band descriptions. Literal idioms and signature-feature titles went in one step |
| 2026-11-16 | Red and Black prompts must record a clue route for their hardest part and their likely neighbors, in `notes` | *Selfie* failed for lack of a route. Near-miss neighbors made the best moments |
| 2026-11-16 | The first 18 cards are assembled from one pool: all existing prompts (approved included) plus new drafts. Choose by band standard, then by fun | Approved prompts earn their place by comparison, not by having been first |
| 2026-11-16 | Black leans toward idioms (about half); real people are allowed but rare | Idioms are the most reliable kind of hard; real people are hard to clue and can date |
| 2026-11-16 | Idioms and compounds with one easily built noun and otherwise direct words (*Black sheep*, *Third wheel*, *Top dog*) are Red. Black idioms need a built part plus a verb or meaning the icons don't hand over (*Break the ice*, *Hit the hay*) | Re-banding the pool: the first-guess test put these in Red, and "when in doubt, choose the easier band" |
| 2026-11-16 | Each of the first 18 cards has one pop-culture prompt in Red and at most one in Black. Black on each card is two idioms plus one other, or one idiom, one compound concept, and one title or person | Meets the per-card pop-culture limits and the half-idiom Black target |
| 2026-11-16 | Cards 1–18 approved as assembled, including the re-banding behind them | Owner reviewed the selection |
| 2026-11-16 | Cards are 3 mm narrower and 3 mm shorter than MTG (60.5 × 85.9 mm) | Second test print: 61.5 × 88.9 mm was still too big for the sleeves |
| 2026-11-16 | Track a content version in `data/VERSION` (now 0.1; release will be 1.0) and print it after the set mark. Bump it only when the prompts on the cards change | Tells printed decks apart by content; cosmetic changes don't make a new deck |
| 2026-11-17 | No prompt may be something drawn as its own element inside an icon (e.g. the octopus in A4, the lightbulb in A8). Compounds built from one are fine (*Lighthouse*). Routes must not depend on cubes placed on picture details | Tabletop playtest: some groups place cubes on picture details, which makes such prompts trivial |
| 2026-11-17 | Bands assigned by reading a prompt are provisional until playtested | First tabletop playtest: many prompts were harder than expected, and some were skipped or failed |
| 2026-11-17 | Playtest notation has one standard form for committed logs: one line per marker, one-letter groups (`?g`, `!r`/`y`/`b`/`k`), the group letter on a cube line only when it changes, `[...]` for comments. Chat shorthand is allowed but converted in logs. Group colors carry no meaning, and markers may be placed in any order | Clue-givers used several shortcuts at the table. One form keeps logs consistent and doesn't imply a pawn-then-cubes order |
| 2026-11-17 | Test 9 allows a broader category that includes a pictured element when players read the picture as its own meaning (*Emoji* vs. C6's smiley face). Reconsider if playtesters name it from a cube on the picture | Owner's call after the card 6 playtest: C6 reads as "happy", not as emojis in general |
| 2026-11-17 | Cards can be left unbalanced between rounds of card assembly. `check` keeps treating a band without exactly 3 prompts as an error, so no PDF can be built until the cards are rebalanced | Avoids temporary filler that the next round would redo, and keeps half-finished cards from being printed |
| 2026-11-19 | The elements drawn in every icon are listed in [docs/pictured-elements.md](docs/pictured-elements.md), and `tools/player_aid.py` makes an illustrated local copy. 38 pictured prompts are rejected, 8 of them taken off cards | Owner reviewed the labels; test 9 needs a list to check prompts against |
| 2026-11-19 | Test 9 counts small details and parts of a drawing (*Window*), other forms of a pictured thing (*Full moon*), and look-alikes (*Abraham Lincoln*, *Coca-Cola*) as pictured. Things a pictured element only symbolizes stay (*Halloween* vs. B10's jack-o'-lantern) | Owner: a cube can sit right on a small detail and give the prompt away, but a symbol isn't a picture of the thing itself |
| 2026-11-19 | Simulated playtests run first on the owner's Claude subscription through the headless CLI (`claude -p`). OpenRouter (guessers that aren't Claude, more volume) comes later, only if calibration shows it's needed | No extra cost; a blind, tool-less test call worked. Claude-only calibration will show whether other models are needed |
| 2026-11-19 | Simulation results are committed as a cache of LLM calls (raw replies keyed by a hash of every input). Logs and summaries are generated from the cache | A permanent record to study without rerunning; after a fix or tweak, calls whose inputs didn't change replay for free |
| 2026-11-19 | The cache comes from a reusable package the owner will find or build. Harness work waits for it | The owner uses this caching approach across projects |
| 2026-11-22 | LLM calls use [llmemo](https://github.com/ForrestTrepte/llmemo) v0.1.0, pinned by git tag in `requirements.txt`. Cache in `sim-playtests/cache/`, spending ledger in `llm-spend/`, both committed | The owner's package meets the cache requirements; the ledger keeps a record of spending, subscription calls included |
| 2026-11-22 | General caching, backend, spending, and cache-maintenance features go into llmemo, not this repo | Keeps this repo about the game and makes the features reusable in the owner's other projects |

## Next steps

1. **Simulated playtesting with LLMs: build the harness (phase 1).** The plan is in
   [docs/simulated-playtesting.md](docs/simulated-playtesting.md): one model gives
   clues, another guesses, calibrated against the human playtests. llmemo is set up,
   and `python tools/llm_smoke.py` replays one small call through each backend. Next,
   write `tools/simplay.py` and dry-run 2–3 prompts to measure usage and speed (record
   only when the owner asks). The pictured-elements re-banding in step 2 can go ahead
   in parallel. Finish it before calibrating, since edits to the icon docs invalidate
   the cache.
2. **Reassemble cards 1–18 (expected check errors until then).** Rebuild every card
   from the whole pool, using:
   - **Tabletop re-banding:** after the 2026-11-16 playtest, the owner moved Taco,
     Popcorn, and Snail from Blue to Red and Statue of Liberty from Red to Black (see
     `playtests/2026-11-16-tabletop.md`). That and the pictured-elements rejections
     leave several cards unbalanced, so `tools/cards.py check` fails and no PDF can be
     built. This is on purpose: don't fill the gaps ad hoc before this step.
   - **Pictured-elements audit (done 2026-11-19):** the rejected prompts are already off their
     cards (cards 5, 8, 10, 11, 13, 15, 17 now have gaps). Re-band the compounds listed
     under "Compounds to re-band" in [docs/pictured-elements.md](docs/pictured-elements.md),
     then delete that doc's audit section.
   - **Simulated playtesting (step 1):** re-rank the best prompts in each band using
     its results, alongside the band standards and the fun criteria in
     [docs/prompt-guidelines.md](docs/prompt-guidelines.md).
   The owner approves the new cards, then bump `data/VERSION` to 0.2.
3. **Test print at the new size.** Once the cards are rebalanced, print
   `output/cards.pdf` (run `python tools/cards.py pdf`) at 100% scale. The cards are
   now 60.5 × 85.9 mm, which hasn't been printed yet. Cut out a few cards and check
   that they slide into MTG sleeves and the text is easy to read. Adjust the layout in
   `tools/cards.py` if needed.
4. **Keep playtesting the 18 cards** (cards 1–18 in `data/prompts.csv`, approved by
   the owner on 2026-11-16; 628 prompts remain unassigned (not counting 38 rejected), and nothing has been
   checked against the base game). Tabletop play with 3+ players is the best
   evidence. Text playtests follow [docs/playtesting.md](docs/playtesting.md); logs
   are in `playtests/`. Apply lessons to the guidelines after each session.
5. **Scale up** toward 25 playtest cards, then 100.
6. **Evaluate open sources** from the research report (Open Party Game Word Lists,
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
- **Publish the printable PDF for others to download.** Plan: publish it as a GitHub
  Release asset (e.g. `v0.1-playtest`, `v1.0`), ideally built automatically by a
  GitHub Action when a version tag is pushed, rather than committing the PDF to the
  repo. A release gives each version a stable download link without adding a new
  binary to git history every time the PDF is rebuilt.
