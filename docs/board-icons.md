# Board icons (text reference)

A text transcription of the icon meanings in the official
[Concept player aid (PDF)](https://cdn.svc.asmodee.net/production-rprod/storage/games/concept/new-box/helpsheets2026/con-en01-player-aid-mkt-1767696650pHOQV.pdf),
keyed by grid code. The player aid says these meanings are not exhaustive, and players
can use icons creatively. Back to [README](../README.md).

## Icon codes

Each icon has a code made of a column letter and a row number, read off the player
aid like a spreadsheet:

- **Page 1:** columns **A B** (left half) and **C D** (right half), rows 1–14.
- **Page 2:** columns **E F** (left half, rows 1–11) and **G H** (right half, rows 1–14).
- **Colors** (the dashed box at the bottom left of page 2) are named by color: `Red`,
  `Orange`, `Yellow`, `Green`, `Blue`, `Purple`, `Pink`, `Brown`, `Black`, `Grey`,
  `White`, and `Clear` (the Transparent / Invisible / Glass swatch).

A code stands for the **whole icon, with all its meanings**. When you give clues, use
codes rather than label words, so you don't tell the guesser which meaning you intend.

Run `python tools/player_aid.py` to generate local copies of: the player aid with
every code printed on its icon, one image per icon, and an **illustrated version of this
page** (`output/player-aid/board-icons.md`, best viewed in VS Code's Markdown preview). See
[data-and-printing.md](data-and-printing.md#player-aid-with-icon-codes).

## Page 1

| Code | Meanings | Code | Meanings |
|---|---|---|---|
| A1 | Object / Box | B1 | Human / Society / Group |
| A2 | Human / Real / Historical | B2 | Character / Fictional / Imaginary |
| A3 | Work / Occupation | B3 | Hobby / Sport |
| A4 | Fauna / Animal | B4 | Flora / Plant / Nature |
| A5 | Literature / Writing / Book | B5 | Music / Song |
| A6 | Cinema / Movie | B6 | Art / Sculpture – Painting / Drawing – Cartoon |
| A7 | Television / Program / Show | B7 | Title / Brand / Name |
| A8 | Idea / Intelligence / Concept | B8 | Expression – Quote / Talking / Words |
| A9 | Place – Country / World / Flag | B9 | Building / Monument / City |
| A10 | Date / Event / Day | B10 | Celebration / Anniversary / Holiday |
| A11 | Seacraft / Naval / Swimming | B11 | Aircraft / Aerial / Flying |
| A12 | Ground transportation / Road | B12 | Tool / Construction |
| A13 | Game / Toy | B13 | Clothing / Accessory / Costume |
| A14 | Food / Eating / Edible | B14 | House – Dwelling / Room / Domestic |

| Code | Meanings | Code | Meanings |
|---|---|---|---|
| C1 | Baby – Child / Young / New | D1 | Adult – Elderly / Old / Past |
| C2 | Feminine / Female | D2 | Masculine / Male |
| C3 | Slow / Slow motion | D3 | Fast / Race |
| C4 | Defense / Protection / Wall | D4 | Attack / Conflict – Combat / Weapon |
| C5 | Life / Heart / Love | D5 | Death / Bad / Illness |
| C6 | Happy / Positive | D6 | Sad / Negative |
| C7 | Electronic / Computing | D7 | Mechanical / Industrial |
| C8 | Money / Rich / Expensive | D8 | Time / Duration |
| C9 | Religion / Myth / Spirituality | D9 | Power / Politics |
| C10 | Science / Math | D10 | Medical / Medicine / Health |
| C11 | Head / Face / Neck | D11 | Arm / Hand / Finger |
| C12 | Torso – Back / Stomach / Body | D12 | Leg / Foot |
| C13 | Ear / Sound / Hearing | D13 | Nose / Scent / Smelling |
| C14 | Eye / Sight | D14 | Mouth / Taste |

## Page 2

| Code | Meanings | Code | Meanings |
|---|---|---|---|
| E1 | Cold / Snow – Rain / Cloud | F1 | Hot / Day – Light / Sun |
| E2 | Night – Evening / Space / Moon – Star | F2 | Lightning – Storm / Electricity / Anger |
| E3 | Fire / Burn / Cooking | F3 | Water / Liquid / Aquatic |
| E4 | Air / Wind / Blowing | F4 | Earth / Ground |
| E5 | Stone / Mineral / Hard | F5 | Wood |
| E6 | Metal | F6 | Fabric |
| E7 | Plastic / Rubber | F7 | Paper / Sheet |
| E8 | Opposite / Reverse | F8 | Cut – Break / Separation / Half |
| E9 | Fragment / Multitude / Cluster | F9 | Part / Fragment / Assembly |
| E10 | Inside / Internal | F10 | Grill – Wire / Network / Grid |
| E11 | Zero / None / Absence | F11 | One / Unit / Number |

| Code | Meanings | Code | Meanings |
|---|---|---|---|
| G1 | Line – Straight / Diagonal / Stiff | H1 | Arch – Curve / Rounded / Flexible |
| G2 | Cross / Crossing / Addition | H2 | Angles / Sharp / Jagged |
| G3 | Spiral / Drunkenness / Coil | H3 | Wavy / Ripple / Hair |
| G4 | Circle / Ring | H4 | Round |
| G5 | Triangle | H5 | Star |
| G6 | Rectangle / Square | H6 | Flat |
| G7 | Cube | H7 | Sphere |
| G8 | Pyramid | H8 | Cylinder |
| G9 | Cone | H9 | Hollow / Hole / Pierced |
| G10 | Big / High | H10 | Small / Low |
| G11 | Fat / Large / Long | H11 | Thin – Fine / Narrow / Short |
| G12 | High / Climb / Above | H12 | Low / Descend / Below |
| G13 | Left / Beginning / Before – Past | H13 | Right / End / After – Future |
| G14 | Turn / Around / Cycle – Repetition | H14 | Use – Action / Do – Verb / Button |

## Clue mechanics (from the rules)

- **Main Concept:** the green `?` pawn shows what kind of thing the answer is. Green
  cubes add details about it.
- **Sub-Concepts:** red, yellow, blue, and black `!` pawns, each with matching cubes,
  describe related ideas (e.g. Bee → a Sub-Concept for honey).
- **Icon order matters.** "House + job + fire" (fire station) is a different clue from
  "job + fire + house" (firefighters).
- **Cube count matters.** Eye + one circle gives monocle. Eye + two circles gives glasses.
