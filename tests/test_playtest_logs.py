"""Tests for tools/playtest_logs.py: reading and checking playtest logs."""

from __future__ import annotations

from pathlib import Path

import playtest_logs
import pytest
from playtest_logs import LogFormatError, parse_log

ENTRY = """# Log

### Card 3, #7: Piece of cake
- Clue-giver: Claude · Guessed: yes (step 2) · Verdict: keep
- Clues:
  ```
  ?g B8
  + F9

  !r A14 [on the plate]
  ```
- Notable guesses: Birthday party (Yes), Slice, Cake (in the same message, Yes)

### Card 3 observations

### Card 3, #8: Rain check
- Clue-giver: human · Guessed: skipped · Verdict: too hard
- Comments: a route that wasn't played:
  ```
  ?g B8
  ```

### Card 3, #9: Plot twist
- Clue-giver: human · Guessed: not played (ran out of time)
"""


def write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_parse_text_log(tmp_path: Path) -> None:
    games = parse_log(write(tmp_path, "2026-01-01-claude-clues.md", ENTRY))
    cake, rain, plot = games
    assert (cake.prompt, cake.card, cake.number, cake.result, cake.solved_step) == (
        "Piece of cake", 3, 7, "solved", 2
    )
    assert cake.steps == (("?g B8", "+ F9"), ("!r A14 [on the plate]",))
    assert cake.yes == ("Birthday party",)
    assert cake.source.endswith("2026-01-01-claude-clues.md, card 3 #7")
    assert (rain.result, rain.clues) == ("skipped", ())
    assert plot.result == "not played"


def test_tabletop_steps_split_at_group_changes(tmp_path: Path) -> None:
    text = ENTRY.replace("  + F9\n\n", "  + F9\n  +g C6\n").replace("Card 3, #7", "Card 3, #7")
    text = text.replace("  !r A14 [on the plate]\n", "  !r A14 [on the plate]\n  + E3\n  +g H4\n")
    cake = parse_log(write(tmp_path, "2026-01-01-tabletop.md", text))[0]
    assert len(cake.clues) == 1
    assert cake.steps == (
        ("?g B8", "+ F9", "+g C6"),
        ("!r A14 [on the plate]", "+ E3"),
        ("+g H4",),
    )


@pytest.mark.parametrize(
    ("name", "old", "new"),
    [
        ("2026-01-01-tabletop.md", "", ""),  # tabletop logs have no pauses
        ("2026-01-01-claude-clues.md", "Guessed: yes", "Guessed: maybe"),
        ("2026-01-01-claude-clues.md", "  + F9\n", "  + Z99\n"),
        ("2026-01-01-claude-clues.md", "  + F9\n\n", "  + F9\n\n\n"),
        ("2026-01-01-claude-clues.md", "### Card 3, #8: Rain check", "### Card 3 #8 Rain check"),
        ("2026-01-01-claude-clues.md", "Guessed: skipped", "Guessed: no"),  # played, no clues
        ("notes.md", "", ""),
    ],
)
def test_format_errors(tmp_path: Path, name: str, old: str, new: str) -> None:
    text = ENTRY.replace(old, new) if old else ENTRY
    with pytest.raises(LogFormatError):
        parse_log(write(tmp_path, name, text))


def test_repo_logs_are_valid() -> None:
    games = playtest_logs.load_logs()
    human = playtest_logs.human_guessed()
    assert len(games) >= 30
    assert human["Popcorn"][0].kind == "tabletop"
    assert len(human["Break the ice"][0].steps) == 9
    assert "Toothbrush" not in human  # Claude guessed in that session
    assert all(g.kind != "tabletop" or len(g.clues) <= 1 for g in games)


def test_ratings_line(tmp_path: Path) -> None:
    text = ENTRY.replace(
        "- Clue-giver: human · Guessed: skipped · Verdict: too hard\n",
        "- Clue-giver: human · Guessed: skipped (no idea how to start) · Verdict: too hard\n"
        "- Players: clue-giver B; guessers Forrest, C · Time: 1–3 min · Difficulty: too hard"
        " · Interest: low\n",
    )
    rain = parse_log(write(tmp_path, "2026-01-01-tabletop.md", text.replace("  + F9\n\n", "  + F9\n")))[1]
    assert (rain.clue_giver_name, rain.guessers) == ("B", ("Forrest", "C"))
    assert (rain.time, rain.difficulty, rain.interest) == ("1–3 min", "too hard", "low")
    with pytest.raises(LogFormatError, match="interest must be one of"):
        parse_log(write(tmp_path, "2026-01-02-tabletop.md", text.replace("Interest: low", "Interest: meh").replace("  + F9\n\n", "  + F9\n")))
