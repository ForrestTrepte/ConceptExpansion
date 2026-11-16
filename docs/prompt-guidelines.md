# Prompt guidelines

How to choose, grade, and select prompts for the expansion. Revise this file as
playtesting shows what works. Back to [README](../README.md).

## Every prompt must pass these tests

1. **Recognition.** Most American adults today would know right away what it is
   without needing it explained. Roughly: at least 4 of 5 typical players for
   Blue and Red, at least 3 of 5 for Black. Once guessed, nobody should need it
   explained.
2. **Clueability.** It fits under an obvious Main Concept icon (Object, Fauna,
   Food, Character, Title, Expression, and so on) **and** has at least two other
   features you can show with separate icons. Name the actual icons from
   [board-icons.md](board-icons.md).
3. **A working route through the hardest part.** For every part of the prompt, you
   can name icons that get a guesser there. For Red and Black, write the route for
   the hardest part (e.g. "ice = water + cold + cube"). If you can't name one, drop
   the prompt. (*Selfie* failed in play because no route to "self" landed.)
4. **Distinctness.** Name the one or two likeliest wrong guesses (its *neighbors*)
   and the icon that separates the prompt from them. Penguin vs. orca: a bird that
   doesn't fly. Glasses vs. monocle: the number of circles. If nothing on the board
   separates them, drop the prompt.
5. **Durability.** It should still be familiar in 5 to 10 years. Recent pop culture
   is welcome if it has already lasted or crossed into the mainstream (e.g. a
   franchise, an app everyone uses, a widely known star). Avoid memes, single-season
   hits, and short-lived celebrities.
6. **Family-friendly.** Nothing crude, sexual, hateful, or likely to upset people at
   a mixed table.
7. **Fits on the card.** Keep it short. The limit is about 24 characters.
8. **Not a base-game duplicate**, including obvious variants (singular/plural, small
   wording changes).

## Difficulty bands

All three bands use the same board. Difficulty comes from **how far the words are
from the icons**, not from how obscure the answer is. Break the prompt into its
parts (the words, or the key features of a thing), then rate each part:

- **Direct:** one obvious icon shows it (food, vehicle, fire, cold, money).
- **Built:** it takes a Sub-Concept or two or three icons combined (ice = water +
  cold + cube; drowning = person + water + death; "bird that doesn't fly").
- **Far:** no combination states it outright. It needs a metaphor, a pun, a chain of
  ideas, or a final hunt for exact words ("self", "snooze", the idiomatic meaning of
  a phrase).

The band follows from the **hardest part** and from how much the wording matters:

| Band | Standard | Examples |
|---|---|---|
| **Blue: easy** | Every part is direct. A person's first guess from the Main Concept plus the two or three most obvious icons is probably right. One near-miss neighbor is fine. | Pizza, Umbrella, Penguin, Volcano, Toothbrush, Food truck |
| **Red: difficult** | Exactly one part is built, **or** every part is direct but the obvious icons point first to a common neighbor (smartphone → tablet; lifeguard → navy). Specific characters, places, and titles with one signature feature go here. Idioms and titles whose words are all direct icons go here too, not in Black. | Lifeguard, Spider-Man, Smartphone, Roller coaster, Under the weather |
| **Black: most difficult** | At least one part is built **and** the guesser must land on the exact wording (idiom, title, set phrase), **or** two or more parts are built, **or** one part is far. | Break the ice, Snooze button, Selfie, Jurassic Park |

**The first-guess test.** Before assigning a band, ask what a *person* (not Claude)
would guess from the Main Concept plus the two or three most obvious icons. If that
guess is the answer, the prompt is Blue, whatever its form. Claude guessed every
human-clued prompt in one step in the card 2 playtest, so Claude's own sense of
difficulty runs easy. When in doubt, choose the easier band.

Lessons from playtesting behind these standards:

- **Direct compounds are Blue.** *Food truck* (vehicle + food) went in one step.
- **Literal idioms and signature titles are not Black.** *Under the weather* (below +
  weather) was solved from two bare pawns. *Spider-Man* (red + blue + web) and
  *Harry Potter* (wand) fell as soon as their signature feature was clued.
- **Neighbors make good difficulty.** The best moments were plausible wrong answers
  that one more clue fixed: orca for *Penguin*, admiral for *Lifeguard*, hail for
  "ice", tablet for *Smartphone*.
- **Hard to show is fine for Red and Black**, as long as there is a route and players
  know the prompt instantly once they get it.

## What makes a prompt fun

Use these to rank prompts that meet the same band standard:

- **Shape and picture play.** The clue-giver gets to use an icon's shape or picture
  cleverly: the cone of a *Volcano*, the up-down-wavy of a *Roller coaster*. The
  clue-giver's favorites from the card 2 playtest (Toothbrush, Volcano, Smartphone,
  Roller coaster, Black Friday) all had this.
- **More than one route.** Different clue-givers can take different paths (*Harry
  Potter*: wand, or glasses + lightning scar).
- **An "aha" when a neighbor gives way.** Orca → penguin, ice cube → *Break the ice*.
- **Instant recognition at the end.** The table should groan or laugh, not ask
  what it means.

## Good prompt types

- Everyday objects, animals, foods, places, jobs, activities.
- Modern compounds people actually say: *video call*, *delivery driver*, *escape room*.
- Enduring characters, people, films, books, games, and brands.
- Common idioms whose words suggest concrete icons but need building: *spill the
  beans*, *break the ice*, *elephant in the room*.
- Real people, used sparingly: only names known across generations, with a
  clueable signature (job, look, famous work). They are usually Black.

## Avoid

- Proverbs, literary quotations, and phrases where the exact wording is the whole
  challenge.
- Long wordings of a simple idea. Use a multi-word phrase only when it's a set
  phrase people always say exactly that way (*Break the ice*). Otherwise trim it to
  its core: *Snooze button*, not *Hit the snooze button*.
- Wordings whose last step is hunting for a verb or function word no icon shows.
- Words about "self", "personal", or "your" as the key part. They are very hard to
  show. Allow at most a rare Black prompt like this, and only with a written route.
- Archaic, regional, or specialist vocabulary.
- Things with only one clueable feature (purely abstract single words with no
  concrete angle).
- Near-synonyms of a prompt already on the same card.

## Recording a candidate

Use the `notes` column of `data/prompts.csv`, in this order:

```
Clue: <Main Concept + supporting icons>; Hard: <hardest part = route>; Neighbors: <likely wrong guesses → separating icon>
```

`Hard:` is required for Red and Black and optional for Blue. Playtest feedback goes
after these fields.

## Building cards from the pool

Cards are assembled from the whole pool: new drafts, earlier drafts, and approved
prompts alike. A prompt being approved or already on a card doesn't reserve it a
slot.

1. **Band every prompt** by the standards above, re-checking earlier ones too. Its
   `difficulty` is the band it meets, not the band it was drafted for.
2. **Fill slots band by band.** Within a band, prefer the more fun prompts (see
   above), then the ones that best meet the standard.
3. **Balance each card:**
   - The nine prompts come from different categories (no three animals in Blue).
   - Each band is about as hard as the same band on other cards.
   - At most one pop-culture prompt (title, character, person, brand) in each
     card's Black band, and at most two on the card overall.
   - No near-synonyms or shared key words on the same card.
4. **Balance the deck:**
   - Black leans toward idioms: roughly half idioms and set phrases, the rest split
     between titles/characters/people and compound concepts (*Bucket list*,
     *Breaking news*).
   - Red and Blue lean toward concrete things, with a few phrases and titles in Red.
   - Real people stay rare, roughly one per few cards.
5. **Leave the rest in the pool** (blank `card`). Mark prompts `rejected` only when
   they fail a test, so they aren't suggested again.
