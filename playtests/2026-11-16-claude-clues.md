# Text playtest 2026-11-16 (Claude gives clues)

- Clue-giver: Claude · Guesser: human
- Cards: starting with card 1

### Card 1, #1: Pizza
- Clue-giver: Claude · Guessed: yes (step 1) · Verdict: keep
- Clues:
  ```
  ?g A14
  + H4
  + F8
  ```
- Notable guesses: (none before correct)
- Comments: guessed immediately from the first three icons; fine for a Blue prompt

### Card 1, #2: Umbrella
- Clue-giver: Claude · Guessed: yes (step 1) · Verdict: keep
- Clues:
  ```
  ?g A1
  + C4
  + E1
  ```
- Notable guesses: Shelter, Jacket (in the same message as the correct guess)
- Comments: guessed on the first clue set

### Card 1, #3: Penguin
- Clue-giver: Claude · Guessed: yes (step 3) · Verdict: keep
- Clues:
  ```
  ?g A4
  + Black
  + White
  + E1
  + A11
  !r B11
  + E11
  ```
- Notable guesses: Zebra, Orca
- Comments: orca fits black/white/cold/swimming equally well; the "bird that doesn't fly" Sub-Concept (B11 + E11) resolved it. A good fit for Blue.

### Card 1, #4: Food truck
- Clue-giver: Claude · Guessed: yes (step 1) · Verdict: too easy
- Clues:
  ```
  ?g A12
  + A14
  ```
- Notable guesses: (none before correct)
- Comments: two icons were enough. The prompt is just the two icons' meanings put together, which is too direct for Red. Consider moving it to Blue.

### Card 1, #5: Selfie
- Clue-giver: Claude · Guessed: no (passed after step 4) · Verdict: unclear (clue problem, not a recognition problem)
- Clues:
  ```
  ?g H14
  + C14
  + C11
  !r A1
  + C7
  + C14
  + D11
  + F11
  + E8
  ```
- Notable guesses: Looking, Blinking, Virtual reality, Hand-eye coordination
- Comments: the red Sub-Concept (object + electronic + eye) read as VR, not as a phone camera. F11 did not come across as "yourself", and E8 (reversed, i.e. front camera) was too subtle. Next time try clueing "photo" more directly, or start with the phone. The prompt is still a good one; the trouble is that "self" is hard to show with the icons.
- Guesser comment: "Seemed difficult, but an interesting challenge. Not necessarily a bad prompt."

### Card 1, #6: Lifeguard
- Clue-giver: Claude · Guessed: yes (step 4) · Verdict: keep
- Clues:
  ```
  ?g A3
  + C4
  + A11
  + D10
  !r B13
  + Red
  !y F1
  + F4
  !b A2
  + F3
  + D5
  ```
- Notable guesses: Admiral, Seaman, British naval officer, Environmentalist
- Comments: A11 (seacraft/naval) pulled toward the navy, and the red clothing made it sound like a British officer. The beach (hot + ground) read as environmentalism. The drowning swimmer (person + water + death) gave it away. A good difficulty for Red.

### Card 1, #7: Break the ice
- Clue-giver: Claude · Guessed: yes (step 9) · Verdict: keep (the clueing was the problem)
- Clues:
  ```
  ?g B8
  + F8
  + E1
  !r E5
  + Clear
  + E1
  !y B1
  + C1
  + B8
  + G13
  +r G7
  -r all
  !r F3
  + E1
  + E5
  + G7
  ```
- Notable guesses: A break in the clouds (Yes), Diamond, Hail (Yes), Babies/Toddlers/Children, Go out and play when there's a break in the clouds, Ruby, Acid rain, Ice cube (Yes)
- Comments: "break" came across right away; "ice" was the hard part. Stone + clear + cold read as gems or hail. Water + cold + hard read as acid rain. Adding G7 (cube) finally got "ice cube", and the phrase followed right after. The yellow "meeting new people" Sub-Concept (group + new) read as children, and G13 read as "the past" rather than "beginning". Better clue: put the ice Sub-Concept as water + cold + cube from the start.

### Card 1, #8: Spider-Man
- Clue-giver: Claude · Guessed: yes (step 1) · Verdict: too easy
- Clues:
  ```
  ?g B2
  + Red
  + Blue
  + F10
  ```
- Notable guesses: (none before correct; guesser briefly thought "a superhero I'm not thinking of")
- Comments: one clue set was enough. Fictional + red + blue + web gives it away. Too easy for Black; it fits Blue (or maybe Red).

### Card 1, #9: Hit the snooze button
- Clue-giver: Claude · Guessed: yes (step 5) · Verdict: keep
- Clues:
  ```
  ?g H14
  !r A1
  + D8
  + C13
  !y E2
  + B14
  + G14
  + C3
  + D4
  ```
- Notable guesses: Start the clock, Stopwatch, On your marks!, Alarm clock (Yes), Snooze button (Yes), Reset/set/change the alarm, Snooze, Snooze the alarm, Alarm button
- Comments: "snooze button" came at step 3. The last step was finding the verb "hit", and D4 (attack) gave it. The long wording makes the last step fiddly. Consider shortening it to "Snooze button" (Red), or keep it as a Black prompt because the verb is part of the challenge.

## Session summary (card 1)

Human decisions after discussion:
- **Food truck:** too easy for Red. Moved to the unassigned pool as Blue.
- **Spider-Man:** moved from Black to Red. Grid → web is not instant, so it's not Blue.
- **Hit the snooze button:** shortened to *Snooze button*.
- **Selfie** and **Break the ice:** keep. Hard to show, but that's the fun of Red and
  Black. The guesser thought "ice" had plenty of associations.
- Card 1 needed a new Black prompt. *Jurassic Park* was drafted (unreviewed).

Guideline lessons (added to docs/prompt-guidelines.md): direct two-icon compounds are
Blue; hard-to-show ideas suit Red and Black; trim long wordings unless they're set
phrases said word for word.
