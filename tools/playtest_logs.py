#!/usr/bin/env python3
"""Read the playtest logs in `playtests/` and check their format.

    uv run python tools/playtest_logs.py check

The format is in docs/playtesting.md (Recording results). Each prompt is an entry:

    ### Card 3, #7: Piece of cake
    - Clue-giver: Claude · Guessed: yes (step 4) · Verdict: keep
    - Clues:
      ```
      ?g B8
      + F9

      + A14
      ```
    - Notable guesses: Birthday party (Yes), Slice

Tabletop entries may add a ratings line right after the first line (see
docs/playtesting.md):

    - Players: clue-giver B; guessers Forrest, C · Time: 1–3 min · Difficulty: hard · Interest: high

A blank line in a clue block is a pause: the guesser replied there. Only text playtests
have pauses. At the table the clue-giver keeps placing markers while people guess, so
tabletop logs never have them; `steps` splits a tabletop game at each change of group
instead, as an assumption for simulated guessers. Other `###` headings (such as "Card 5
observations") are not entries.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from notation import Board, NotationError

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "playtests"

Kind = Literal["tabletop", "claude-clues", "human-clues"]
Result = Literal["solved", "failed", "skipped", "not played"]
# Logs whose guessers were people, so their games are evidence about human guessing.
HUMAN_GUESSERS: tuple[Kind, ...] = ("tabletop", "claude-clues")

_FILE = re.compile(r"^\d{4}-\d{2}-\d{2}-(tabletop|claude-clues|human-clues)\.md$")
_ENTRY = re.compile(r"^### (?:Card (\d+), #(\d)|Pool): (.+)$")
_STATUS = re.compile(
    r"^- Clue-giver: (Claude|human)(?: \([^)]*\))? · Guessed: (yes|no|skipped|not played)"
    r"(?: \(([^)]*)\))?(?: · Verdict: .+)?$"
)
_RATINGS = re.compile(
    r"^- Players: clue-giver (?P<giver>[^;·]+); guessers (?P<guessers>[^·]+)"
    r"(?: · Time: (?P<time>[^·]+))?(?: · Difficulty: (?P<difficulty>[^·]+))?"
    r"(?: · Interest: (?P<interest>[^·]+))?$"
)
TIMES = ("under 1 min", "1–3 min", "over 3 min")
DIFFICULTIES = ("too easy", "easy", "difficult", "hard", "too hard")
INTERESTS = ("low", "medium", "high", "fantastic")
_CLUES = re.compile(r"^- Clues(?: \([^)]*\))?:$")
_RESULTS: dict[str, Result] = {
    "yes": "solved",
    "no": "failed",
    "skipped": "skipped",
    "not played": "not played",
}


class LogFormatError(ValueError):
    pass


@dataclass(frozen=True)
class LogGame:
    prompt: str  # as it was played, which may differ from data/prompts.csv today
    card: int | None  # None for a prompt from the unassigned pool
    number: int | None
    source: str  # path and entry, e.g. "playtests/x.md, card 1 #7" or "playtests/x.md, pool"
    kind: Kind
    result: Result
    solved_step: int | None  # from "Guessed: yes (step N)", if given
    clues: tuple[tuple[str, ...], ...]  # the logged pauses; one part if there were none
    yes: tuple[str, ...]  # notable guesses marked (Yes)
    clue_giver_name: str = ""  # from the Players line (tabletop), e.g. "B"
    guessers: tuple[str, ...] = ()
    time: str = ""  # one of TIMES, if rated
    difficulty: str = ""  # one of DIFFICULTIES
    interest: str = ""  # one of INTERESTS

    @property
    def lines(self) -> tuple[str, ...]:
        return tuple(line for part in self.clues for line in part)

    @property
    def steps(self) -> tuple[tuple[str, ...], ...]:
        """The clues split where a guesser takes a turn: the logged pauses, or for a
        tabletop game (which has none) a new step at each change of group."""
        if self.kind != "tabletop":
            return self.clues
        return split_at_group_changes(self.lines)


def split_at_group_changes(lines: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    board = Board()
    steps: list[list[str]] = []
    for line in lines:
        before = board.last_group
        board.apply(line, comments=True)
        if not steps or board.last_group != before:
            steps.append([])
        steps[-1].append(line)
    return tuple(tuple(s) for s in steps)


def _split_guesses(text: str) -> list[str]:
    """Split on commas that aren't inside parentheses."""
    parts, depth, cur = [], 0, ""
    for ch in text:
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    parts.append(cur.strip())
    return [p for p in parts if p]


def parse_log(path: Path) -> list[LogGame]:
    m = _FILE.match(path.name)
    if not m:
        raise LogFormatError(f"{path.name}: name must be YYYY-MM-DD-<tabletop|claude-clues|human-clues>.md")
    kind: Kind = m[1]  # type: ignore[assignment]
    rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    lines = path.read_text(encoding="utf-8").splitlines()
    games: list[LogGame] = []
    i = 0

    def fail(n: int, msg: str) -> LogFormatError:
        return LogFormatError(f"{rel}:{n + 1}: {msg}")

    while i < len(lines):
        if not lines[i].startswith("### "):
            i += 1
            continue
        head = _ENTRY.match(lines[i])
        if not head:
            if lines[i].startswith(("### Card", "### Pool")) and "observations" not in lines[i]:
                raise fail(
                    i, f"entry heading must be '### Card N, #K: Prompt' or '### Pool: Prompt': {lines[i]!r}"
                )
            i += 1
            continue
        start = i
        end = next((j for j in range(i + 1, len(lines)) if lines[j].startswith("#")), len(lines))
        body = lines[i + 1 : end]
        i = end
        if not body or not (status := _STATUS.match(body[0])):
            raise fail(start + 1, "the line after the heading must be '- Clue-giver: … · Guessed: …'")
        result = _RESULTS[status[2]]
        step = re.search(r"\bstep (\d+)\b", status[3] or "")
        ratings = _RATINGS.match(body[1]) if len(body) > 1 else None
        if len(body) > 1 and body[1].startswith("- Players:") and not ratings:
            raise fail(
                start + 2,
                "ratings line must be '- Players: clue-giver X; guessers Y, Z"
                " · Time: … · Difficulty: … · Interest: …'",
            )
        rated: dict[str, str] = {}
        for field, allowed in (("time", TIMES), ("difficulty", DIFFICULTIES), ("interest", INTERESTS)):
            value = (ratings[field] or "").strip() if ratings else ""
            if value and value not in allowed:
                raise fail(start + 2, f"{field} must be one of: {', '.join(allowed)}")
            rated[field] = value
        clue_at = [k for k, b in enumerate(body) if _CLUES.match(b)]
        clues: list[list[str]] = []
        if clue_at:
            k = clue_at[0] + 1
            if k >= len(body) or body[k].strip() != "```":
                raise fail(start + 1 + k, "a code block must follow '- Clues:'")
            indent = body[k][: len(body[k]) - len(body[k].lstrip())]
            k += 1
            clues = [[]]
            while k < len(body) and body[k].strip() != "```":
                text = body[k].removeprefix(indent).rstrip()
                if text:
                    clues[-1].append(text)
                elif clues[-1]:
                    clues.append([])
                else:
                    raise fail(start + 1 + k, "a pause must come after a clue line, once")
                k += 1
            if k >= len(body):
                raise fail(start + 1 + k, "clue block isn't closed")
            if not clues[-1]:
                raise fail(start + k, "a clue block can't end with a pause")
        if len(clue_at) > 1:
            raise fail(start + 1 + clue_at[1], "one '- Clues:' block per entry")
        played = result in ("solved", "failed")
        if played != bool(clues):
            raise fail(start + 1, "played games need a clue block, and skipped ones none")
        if kind == "tabletop" and len(clues) > 1:
            raise fail(start + 1, "tabletop logs have no pauses (blank lines in clue blocks)")
        board = Board()
        for part in clues:
            try:
                board.apply_all(part, comments=True)
            except NotationError as e:
                raise fail(start, f"{head[3]}: {e}") from None
        yes: list[str] = []
        for b in body:
            if b.startswith("- Notable guesses: "):
                for g in _split_guesses(b.removeprefix("- Notable guesses: ")):
                    if g.endswith(" (Yes)"):
                        yes.append(g.removesuffix(" (Yes)"))
        games.append(
            LogGame(
                prompt=head[3],
                card=int(head[1]) if head[1] else None,
                number=int(head[2]) if head[2] else None,
                source=f"{rel}, card {head[1]} #{head[2]}" if head[1] else f"{rel}, pool",
                kind=kind,
                result=result,
                solved_step=int(step[1]) if step and result == "solved" else None,
                clues=tuple(tuple(p) for p in clues),
                yes=tuple(yes),
                clue_giver_name=ratings["giver"].strip() if ratings else "",
                guessers=tuple(g.strip() for g in ratings["guessers"].split(",")) if ratings else (),
                **rated,
            )
        )
    return games


def format_entry(
    prompt: str,
    *,
    clue_giver: str,
    result: Result,
    steps: Sequence[Sequence[str]],
    solved_step: int | None = None,
    verdict: str = "",
    guesses: Sequence[tuple[str, bool]] = (),
    extra: Sequence[str] = (),
) -> str:
    """A log entry for a pool prompt in the format `parse_log` reads: steps separated by
    pauses, notable guesses with `(Yes)` marks, and extra bullets (e.g. comments)."""
    word = {"solved": "yes", "failed": "no", "skipped": "skipped", "not played": "not played"}[result]
    if solved_step is not None:
        word += f" (step {solved_step})"
    status = f"- Clue-giver: {clue_giver} · Guessed: {word}"
    if verdict:
        status += f" · Verdict: {verdict}"
    out = [f"### Pool: {prompt}", status]
    if steps:
        out += ["- Clues:", "  ```"]
        out += "\n\n".join("\n".join(f"  {line}" for line in step) for step in steps).split("\n")
        out = [line if line.strip() else "" for line in out]
        out.append("  ```")
    if guesses:
        out.append(
            "- Notable guesses: " + ", ".join(g + (" (Yes)" if yes else "") for g, yes in guesses)
        )
    out += [f"- {e}" for e in extra]
    return "\n".join(out) + "\n"


def load_logs(logs_dir: Path = LOGS) -> list[LogGame]:
    return [g for p in sorted(logs_dir.glob("*.md")) for g in parse_log(p)]


def human_guessed(logs_dir: Path = LOGS) -> dict[str, list[LogGame]]:
    """Games with human guessers, by prompt as played, in log order."""
    out: dict[str, list[LogGame]] = {}
    for g in load_logs(logs_dir):
        if g.kind in HUMAN_GUESSERS and g.result != "not played":
            out.setdefault(g.prompt, []).append(g)
    return out


def main(argv: list[str]) -> int:
    if argv != ["check"]:
        print(__doc__.split("\n\n")[1])
        return 2
    try:
        games = load_logs()
    except LogFormatError as e:
        print(f"error: {e}")
        return 1
    files = sorted({g.source.split(",")[0] for g in games})
    human = sum(g.kind in HUMAN_GUESSERS and g.result in ("solved", "failed") for g in games)
    print(f"ok: {len(games)} entries in {len(files)} logs; {human} played with human guessers")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
