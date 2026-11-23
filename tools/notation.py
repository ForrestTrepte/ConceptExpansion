"""Clue notation from docs/playtesting.md: parse and check lines, and track the board.

    board = Board()
    lines = board.apply_all(["?g A4", "+ B11", "+ Yellow", "!r B11", "+ G14"])
    board.summary()   # "?g A4 | B11, Yellow\\n!r B11 | G14"

`Board.apply` checks each line against the board (no second pawn in a group, no removing
a marker that isn't there) and returns it in standard form. Comments (`[...]`) are only
accepted when `comments=True`, for transcribed human games: a model clue-giver may not
use them, so nothing but icon codes can reach the guesser.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

COLORS = (
    "Red",
    "Orange",
    "Yellow",
    "Green",
    "Blue",
    "Purple",
    "Pink",
    "Brown",
    "Black",
    "Grey",
    "White",
    "Clear",
)
ROWS = {"A": 14, "B": 14, "C": 14, "D": 14, "E": 11, "F": 11, "G": 14, "H": 14}
CODES = frozenset(
    [f"{col}{row}" for col, rows in ROWS.items() for row in range(1, rows + 1)] + list(COLORS)
)
GROUPS = ("g", "r", "y", "b", "k")
MAX_COUNT = 9

_COLOR_BY_LOWER = {c.lower(): c for c in COLORS}
_LINE = re.compile(
    r"""^(?:
        (?P<pawn>[?!])(?P<pgroup>[a-z])\s+(?P<pcode>\S+)          # ?g A4, !r B11
      | (?P<unpawn>-[?!])(?P<ugroup>[a-z])                         # -?g, -!r
      | -(?P<cgroup>[a-z])\s+all                                   # -r all
      | (?P<sign>[+-])(?P<group>[a-z])?\s+(?P<code>\S+)(?:\s+x(?P<count>\d+))?  # + B11 x2
    )\s*(?:\[(?P<comment>[^\[\]]*)\])?$""",
    re.VERBOSE,
)


class NotationError(ValueError):
    """A line that isn't valid notation, or that doesn't fit the board."""


def normalize_code(text: str) -> str:
    """`a4` -> `A4`, `yellow` -> `Yellow`. Raises NotationError for anything else."""
    if text.lower() in _COLOR_BY_LOWER:
        return _COLOR_BY_LOWER[text.lower()]
    code = text.upper()
    if code not in CODES:
        raise NotationError(f"unknown icon code {text!r}")
    return code


@dataclass
class Group:
    pawn: str | None = None
    cubes: list[str] = field(default_factory=list)


@dataclass
class Board:
    """The markers on the board, by group, in placement order."""

    groups: dict[str, Group] = field(default_factory=dict)
    last_group: str | None = None

    def copy(self) -> Board:
        return Board(
            {g: Group(v.pawn, list(v.cubes)) for g, v in self.groups.items()}, self.last_group
        )

    def apply(self, line: str, *, comments: bool = False, name_group: bool = False) -> str:
        """Apply one line and return it in standard form, naming the group on a cube line
        if `name_group`. The board is unchanged if the line is rejected."""
        m = _LINE.match(line.strip())
        if not m:
            raise NotationError(f"not a notation line: {line!r}")
        comment = m["comment"]
        if comment is not None and not comments:
            raise NotationError(f"comments are not allowed: {line!r}")
        tail = f" [{comment.strip()}]" if comment is not None else ""

        if m["pawn"]:
            group = self._group(m["pgroup"], pawn=m["pawn"])
            code = normalize_code(m["pcode"])
            g = self.groups.setdefault(group, Group())
            if g.pawn is not None:
                raise NotationError(f"group {group} already has a pawn on {g.pawn}: {line!r}")
            g.pawn = code
            self.last_group = group
            return f"{m['pawn']}{group} {code}{tail}"

        if m["unpawn"]:
            group = self._group(m["ugroup"], pawn=m["unpawn"][1])
            had = self.groups.get(group)
            if had is None or had.pawn is None:
                raise NotationError(f"group {group} has no pawn to remove: {line!r}")
            had.pawn = None
            self._drop_if_empty(group)
            self.last_group = group
            return f"{m['unpawn']}{group}{tail}"

        if m["cgroup"]:
            group = self._group(m["cgroup"])
            if group not in self.groups:
                raise NotationError(f"group {group} has nothing to clear: {line!r}")
            del self.groups[group]
            self.last_group = group
            return f"-{group} all{tail}"

        given: str | None = m["group"] or self.last_group
        if given is None:
            raise NotationError(f"the first line must name its group: {line!r}")
        group = self._group(given)
        code = normalize_code(m["code"])
        count = int(m["count"]) if m["count"] else 1
        if not 1 <= count <= MAX_COUNT:
            raise NotationError(f"count must be 1 to {MAX_COUNT}: {line!r}")
        if m["sign"] == "+":
            self.groups.setdefault(group, Group()).cubes.extend([code] * count)
        else:
            if count != 1:
                raise NotationError(f"remove one cube per line: {line!r}")
            cubes = self.groups[group].cubes if group in self.groups else []
            if code not in cubes:
                raise NotationError(f"group {group} has no cube on {code} to remove: {line!r}")
            del cubes[len(cubes) - 1 - cubes[::-1].index(code)]
            self._drop_if_empty(group)
        named = group if name_group or group != self.last_group else ""
        self.last_group = group
        return f"{m['sign']}{named} {code}" + (f" x{count}" if count > 1 else "") + tail

    def apply_all(self, lines: list[str], *, comments: bool = False) -> list[str]:
        """Apply several lines, all or nothing. The first line of the result always names
        its group, so a step can be read on its own."""
        trial = self.copy()
        out = [
            trial.apply(line, comments=comments, name_group=i == 0) for i, line in enumerate(lines)
        ]
        self.groups, self.last_group = trial.groups, trial.last_group
        return out

    def summary(self) -> str:
        """The board grouped by color, as in the `board?` reply of docs/playtesting.md."""
        rows = []
        for group in GROUPS:
            g = self.groups.get(group)
            if g is None:
                continue
            head = f"{'?' if group == 'g' else '!'}{group} {g.pawn}" if g.pawn else f"{group} (no pawn)"
            rows.append(f"{head} | {', '.join(g.cubes)}" if g.cubes else head)
        return "\n".join(rows) if rows else "(empty)"

    @staticmethod
    def _group(group: str, *, pawn: str | None = None) -> str:
        if group not in GROUPS:
            raise NotationError(f"unknown group {group!r}; use one of {', '.join(GROUPS)}")
        if pawn == "?" and group != "g":
            raise NotationError("only the Main Concept group g has the ? pawn")
        if pawn == "!" and group == "g":
            raise NotationError("Sub-Concept pawns are !r, !y, !b, or !k")
        return group

    def _drop_if_empty(self, group: str) -> None:
        g = self.groups[group]
        if g.pawn is None and not g.cubes:
            del self.groups[group]
