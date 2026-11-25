# Prompt guidelines

How to choose, grade, and select prompts for the expansion. Revise this file as
playtesting shows what works. Back to [README](../README.md).

Every candidate goes through one rubric: **gates** decide whether it qualifies,
**difficulty** measures put it on a level (and catch prompts that can't be clued), and
**quality** measures rank prompts at the same level. The sections after the rubric
give examples, prompt types, how to record a candidate, and how to build cards.

## Clueability rubric

**Not yet checked against playtest data;
the weights are a starting guess.** Each measure is scored separately so it can be
checked against playtest results (see [prompt-pipeline.md](prompt-pipeline.md)). Score each prompt as
a typical American adult player would experience it, looking at the icon pictures, not
as a model that knows every icon's label words. Name the actual icons from
[board-icons.md](board-icons.md).

Older logs and decisions refer to numbered tests: test 1 is G1, tests 5–9 are G2–G6
(test 9, pictured on the board, is G6), and tests 2–4 are now D1, D2, and D4.

### Levels

Predictions use the same five levels as the group's difficulty rating, so the two can
be compared directly:

| Level | Meaning | Card band |
|---|---|---|
| **too easy** | One icon gives it away, usually because it's pictured (G6) | none |
| **easy** | | Blue |
| **medium** | | Red |
| **hard** | | Black |
| **too hard** | Can't be clued, or not reliably | none |

Band colors are used only for card slots: a prompt rated *medium* goes in a Red slot.

### Gates

Yes/no each. A prompt that fails a gate is marked `rejected`, with the gate as the
reason.

| # | Gate | Fails when | Examples |
|---|---|---|---|
| G1 | **Recognition** | Of 5 typical American adults, fewer than 3 would know it instantly once guessed, or fewer than 4 for Blue and Red. Score the count (0–5). Nobody should need it explained | Rain check 4, Elbow room 3 |
| G2 | **Durability** | It's unlikely to be familiar in 5–10 years. Recent pop culture is welcome if it has already lasted or crossed into the mainstream (a franchise, an app everyone uses, a widely known star) | memes, single-season hits, short-lived celebrities |
| G3 | **Family-friendly** | It's crude, sexual, hateful, or likely to upset people at a mixed table | |
| G4 | **Length** | It's longer than about 24 characters | |
| G5 | **Base-game duplicate** | It matches a base-game prompt, including obvious variants (singular/plural, small wording changes). Checked against the private list, not scored by a model | |
| G6 | **Pictured on the board** | It's drawn as its own element inside an icon (see below) | Octopus (drawn in A4), Light bulb (drawn in A8) |

**G6 in detail.** Some groups place a cube right on a picture detail, which makes
pictured prompts trivial. Look at the icon images, not just the labels; the elements
drawn in each icon are listed in [pictured-elements.md](pictured-elements.md).

- **These count as pictured:** small details and parts of a larger drawing (*Window*:
  the windows on B14's house; *Anchor*: the emblem on A11's yacht); another form of a
  pictured thing (*Full moon*: E2's crescent moon); and drawings of a specific thing
  the icon doesn't name (*Abraham Lincoln* in A2, *Coca-Cola* in B7, *April Fools'
  Day* from A10's "1 APRIL" page).
- **These are fine:** compounds built from a pictured element (*Lighthouse* = the A8
  lightbulb + B14), and things a pictured element only symbolizes (*Halloween*: B10
  shows a jack-o'-lantern, not Halloween). Score such prompts with the pictured part
  counted as direct.
- A broader category that includes a pictured element is fine when players read the
  picture as its own meaning: *Emoji* stays even though C6 shows a smiley face,
  because players read it as "happy". Reconsider such a prompt if playtesters name it
  from a cube placed on the picture.

### Difficulty

Difficulty comes from **how far the words are from the icons**, not from how obscure
the answer is. Find the **best route**: the clue plan a good clue-giver would use,
from a Main Concept to the answer. Routes must work by placing markers on whole
icons, not on one detail inside an icon's picture; some groups do that, but it isn't
standard play. Then break the answer into its **parts** (each word a guesser must say,
for phrases and titles; each key feature, for things) and rate how the route reaches
each one:

- **Direct:** one obvious icon shows it by its main meaning or an obvious picture
  (food, vehicle, fire, cold, money).
- **Built:** it takes a Sub-Concept or two or three icons combined (ice = water + cold
  + cube; drowning = person + water + death; "bird that doesn't fly").
- **Far:** no combination states it outright. It needs a secondary label, a metaphor,
  a pun, a chain of ideas, or a final hunt for exact words ("self", "snooze", "check"
  in *Rain check*).
- **None:** no icons get a guesser there at all. One such part makes the prompt too
  hard.

Sometimes the best route clues what an idiom means instead of its words. Then score
the meaning as a single part, not each word. In play, *Couch potato* was clued as "a
lazy person at home watching TV": person (C2/D2) + opposite (E8) of fast (D3) + home
(B14) + TV (A7). Nobody built "couch" or "potato". That meaning is one built part
(several icons combined). The guesser's jump from the meaning to the exact phrase is
scored by D3, exact wording.

| # | Measure | Scale | Anchors from play |
|---|---|---|---|
| D1 | **Foothold**: how well the clue-giver can start | 0: no Main Concept fits and no first association comes to mind, or there are fewer than two other features to show · 1: a Main Concept fits, but the first markers point to many things · 2: Main Concept plus one strong feature narrows it to a small family · 3: Main Concept plus one or two icons is enough for most people | 0: Déjà vu, Taco (skipped). 1: Snail (animal + slow → turtle). 2: Penguin. 3: Pizza, Food truck |
| D2 | **Parts** along the best route | Each part direct, built, far, or none, with its icons. Count built and far parts | Ice = built (water + cold + cube). "Self" = far |
| D3 | **Exact wording**: can guessers have the right idea and still say something else? | 0: no; once they have the idea, they say the answer (one common name) · 1: yes: a set phrase or title whose exact words must be found, or a thing with a more common name that comes out first | 0: Umbrella, Penguin. 1: Once in a blue moon ("rarely" isn't enough), Couch potato ("lazy person"), Automobile (they say "car") |
| D4 | **Neighbors**: the 1–3 likeliest wrong answers from the obvious clue | For each, the icon that separates it, or *none*. Count the ones with none | Penguin vs. orca: B11 + E11. Glasses vs. monocle: the number of circles. Umbrella vs. cooler: rain vs. cold, both in E1 |

### Quality

For ranking prompts at the same level: what makes a prompt fun to clue and guess.

| # | Measure | Scale | Examples |
|---|---|---|---|
| Q1 | **Routes**: distinct clue plans that reach the answer, the best route included. Routes are distinct when they rest on a different idea, not different icons for the same idea. Different clue-givers can take different paths | count | Harry Potter: wand, or glasses + lightning scar. Popcorn: cinema, or the popping process |
| Q2 | **Aha neighbor**: a plausible wrong guess that one more clue turns into the answer | yes/no | orca → Penguin, ice cube → Break the ice, admiral → Lifeguard, tablet → Smartphone |
| Q3 | **Picture play**: the clue-giver uses an icon's shape or picture cleverly | yes/no | Volcano (cone), Roller coaster (up-down-wavy). The card 2 favorites (Toothbrush, Volcano, Smartphone, Roller coaster, Black Friday) all had this |
| Q4 | **New angle**: the best route sees the thing from an unexpected side | yes/no | Couch potato (clued as "the opposite of fast") |

The table should groan or laugh at the end, not ask what it means; that's G1.

### Scores

**Difficulty points** = (3 − foothold) + built parts + 3 × far parts + exact wording +
neighbors with no separating icon.

| Points | Level |
|---|---|
| (one icon gives it away) | too easy |
| 0–1 | easy |
| 2–3 | medium |
| 4–5 | hard |
| 6 or more, **or** foothold 0, **or** a part with no route | too hard |

**Quality** = min(Q1, 3) + Q2 + Q3 + Q4, from 0 to 6. Within a level, prefer higher
quality.

These weights are a starting guess, set by hand to match the examples below. They
will be checked against the playtested prompts and refit when there's enough data
(see [prompt-pipeline.md](prompt-pipeline.md#5-evaluate-and-revise)).

**Two phases** (see [prompt-pipeline.md](prompt-pipeline.md#1-analyze)): the screen
scores the gates, D1, D3, and the number of far and none parts; the full ranking
scores everything for the prompts that pass.

## Levels in practice

| Level | What it usually looks like | Examples |
|---|---|---|
| **easy** (Blue) | Every part is direct. A person's first guess from the Main Concept plus the two or three most obvious icons is probably right. One near-miss neighbor is fine | Pizza 0, Penguin 1, Umbrella, Volcano, Toothbrush, Food truck 0 |
| **medium** (Red) | Exactly one part is built, **or** every part is direct but the obvious icons point first to a common neighbor (smartphone → tablet; lifeguard → navy). Specific characters, places, and titles with one signature feature. Idioms and titles whose words are all direct icons | Lifeguard, Spider-Man, Smartphone, Roller coaster, Under the weather |
| **hard** (Black) | A built part **and** exact wording (idiom, title, set phrase), **or** two or more built parts, **or** one far part | Break the ice, Snooze button, Selfie 4, Jurassic Park |

Worked scores: Star Wars 1 (foothold 3, both words direct, exact wording 1): easy, and
it went in one step on a Red slot. Selfie 4 (foothold 2, "self" far): hard. Déjà vu
(foothold 0): too hard, and it was skipped.

**A full example: *Black sheep*** (an AI-scored illustration; not yet playtested).

- **Gates:** pass. G1: about 5 of 5 know it. G2: lasting idiom. G3: fine. G4: 11
  characters. G5: not yet checked (needs the private list). G6: no sheep is drawn on
  the board.
- **Best route:** Expression (B8) as the Main Concept, then the words: Black (the
  color) and sheep = animal (A4) + White + wavy (H3, for wool). The meaning, one (F11)
  set against the group (B1) by opposite (E8), confirms the idiom.
- **D1 Foothold 2:** Expression + Black + animal narrows it to a small family (black
  cat, black sheep, black widow).
- **D2 Parts:** "Black" direct, "sheep" built. 1 built, 0 far.
- **D3 Exact wording 1:** a set phrase; a guesser with the idea may say "outcast" or
  "odd one out".
- **D4 Neighbors:** black cat (separated by H3 wool), odd one out (separated by the
  animal), black widow (separated by White + wool). 0 with no separating icon.
- **Difficulty points:** (3 − 2) + 1 + 0 + 1 + 0 = 3, so **medium** (Red).
- **Q1 Routes 2:** the words (black + sheep) and the meaning (the one who doesn't fit
  the group). **Q2 Aha neighbor:** yes, black cat → wool → black sheep. **Q3 Picture
  play:** yes, H3's wavy lines for wool. **Q4 New angle:** no.
- **Quality:** min(2, 3) + 1 + 1 + 0 = 4 of 6.

**The first-guess test.** As a check on the score, ask what a *person* (not Claude)
would guess from the Main Concept plus the two or three most obvious icons. If that
guess is the answer, the prompt is easy, whatever its form. Claude guessed every
human-clued prompt in one step in the card 2 playtest, so Claude's own sense of
difficulty runs easy. When in doubt, choose the easier level.

**Grading by reading a prompt runs easy.** In the first tabletop playtest (two humans,
printed cards), many prompts were harder than expected, and some were skipped or
failed. A prompt that looks easy can still be hard to build from icons, or the guesser
may not make the association the clue-giver needs. A written route is necessary but
not enough. Levels assigned without play are provisional until playtested. Working
through actual clues, not just naming icons, gives a better estimate.

Lessons from playtesting behind these levels:

- **Direct compounds are easy.** *Food truck* (vehicle + food) went in one step.
- **Literal idioms and signature titles are not hard.** *Under the weather* (below +
  weather) was solved from two bare pawns. *Spider-Man* (red + blue + web) and *Harry
  Potter* (wand) fell as soon as their signature feature was clued.
- **One easy built noun doesn't make an idiom hard.** *Black sheep*, *Third wheel*, and
  *Top dog* are medium: once the animal or object is built, the direct word next to it
  gives the phrase. Hard idioms also need a verb or meaning the icons don't hand over
  (*Break the ice*, *Hit the hay*). (From the pool re-banding, not yet playtested.)
- **No route, no solve.** *Selfie* failed in play because no route to "self" landed.
- **Neighbors make good difficulty.** The best moments were plausible wrong answers
  that one more clue fixed (Q2).
- **Hard to show is fine for medium and hard**, as long as there is a route and
  players know the prompt instantly once they get it.
- **Prompts are harder at the table than on paper.** See the tabletop playtest of
  2026-11-16 in `playtests/`.

## Good prompt types

- Everyday objects, animals, foods, places, jobs, activities.
- Modern compounds people actually say: *video call*, *delivery driver*, *escape room*.
- Enduring characters, people, films, books, games, and brands.
- Common idioms whose words suggest concrete icons but need building: *spill the
  beans*, *break the ice*, *elephant in the room*.
- Real people, used sparingly: only names known across generations, with a clueable
  signature (job, look, famous work). They are usually hard.

## Avoid

Each of these scores badly on the rubric; the list is a reminder when drafting.

- Proverbs, literary quotations, and phrases where the exact wording is the whole
  challenge (D3, far parts).
- Long wordings of a simple idea (G4, D3). Use a multi-word phrase only when it's a
  set phrase people always say exactly that way (*Break the ice*). Otherwise trim it
  to its core: *Snooze button*, not *Hit the snooze button*.
- Wordings whose last step is hunting for a verb or function word no icon shows (a far
  part).
- Words about "self", "personal", or "your" as the key part (far or none). Allow at
  most a rare hard prompt like this, and only with a written route.
- Archaic, regional, or specialist vocabulary (G1).
- Things with only one clueable feature: purely abstract single words with no concrete
  angle (D1).
- Near-synonyms of a prompt already on the same card (see building cards, below).

## Recording a candidate

Use the `notes` column of `data/prompts.csv`, in this order:

```
Clue: <Main Concept + supporting icons>; Hard: <hardest part = route>; Neighbors: <likely wrong guesses → separating icon>
```

These are the rubric's foothold (D1), hardest part (D2), and neighbors (D4), written
out. `Hard:` is required for Red and Black and optional for Blue. Playtest feedback
goes after these fields.

## Building cards from the pool

Cards are assembled from the whole pool: new drafts, earlier drafts, and approved
prompts alike. A prompt being approved or already on a card doesn't reserve it a
slot.

1. **Score every prompt** with the rubric, re-checking earlier ones too. Its
   `difficulty` is the band for the level it scores, not the band it was drafted for.
2. **Fill slots band by band.** Within a band, prefer higher quality, then the prompts
   that sit most clearly in the level.
3. **Balance each card:**
   - The nine prompts come from different categories (no three animals in Blue).
   - Each band is about as hard as the same band on other cards.
   - At most one pop-culture prompt (title, character, person, brand) in each card's
     Black band, and at most two on the card overall.
   - No near-synonyms or shared key words on the same card.
4. **Balance the deck:**
   - Black leans toward idioms: roughly half idioms and set phrases, the rest split
     between titles/characters/people and compound concepts (*Bucket list*, *Breaking
     news*).
   - Red and Blue lean toward concrete things, with a few phrases and titles in Red.
   - Real people stay rare, roughly one per few cards.
5. **Leave the rest in the pool** (blank `card`). Mark prompts `rejected` only when
   they fail a gate, so they aren't suggested again.
