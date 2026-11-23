#!/usr/bin/env python3
"""Illustrated copies of the playtest logs and simulated runs, with icon pictures.

    uv run python tools/illustrate_logs.py

Writes `output/illustrated/playtests/*.md` and `output/illustrated/sim-playtests/*.md`,
best viewed in VS Code's Markdown preview. Every code block that is clue notation
becomes a row of icons, each followed by its marker: a pawn (`?` or `!`) or cubes in
the group's color, like the examples in the rulebook. A blank line in a block (a pause)
starts a new step. When earlier steps or removals make the board differ from the step's
own markers, the board after the step follows, one row per group.

Needs the icon images from `uv run python tools/player_aid.py`. Everything is written
to `output/`, which is gitignored, because the icons are Repos Production's artwork.
The pawn and cube images are simple shapes drawn here.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from board import icon_meanings
from notation import GROUPS, Board, NotationError

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "output" / "player-aid" / "icons"
OUT = ROOT / "output" / "illustrated"
SOURCES = {"playtests": ROOT / "playtests", "sim-playtests": ROOT / "sim-playtests" / "runs"}

ICON_PX = 44
PAWN_PX = 22
CUBE_PX = 14
FILL = {"g": "#2e9e44", "r": "#d62b2b", "y": "#f2c418", "b": "#2468d8", "k": "#222222"}
INK = {"g": "white", "r": "white", "y": "black", "b": "white", "k": "white"}

_STD = re.compile(
    r"^(?:(?P<pawn>[?!])[a-z] (?P<pcode>\S+)"
    r"|(?P<unpawn>-[?!])[a-z]"
    r"|-[a-z] (?P<all>all)"
    r"|(?P<sign>[+-])[a-z]? (?P<code>\S+)(?: x(?P<count>\d+))?)"
    r"(?: \[(?P<comment>[^\]]*)\])?$"
)
_FENCE = re.compile(r"^(\s*)```\s*$")


def marker_svgs() -> dict[str, str]:
    """Pawn and cube images for each group, as SVG text by file name."""
    out = {}
    for g in GROUPS:
        fill, ink, glyph = FILL[g], INK[g], "?" if g == "g" else "!"
        edge = "#bbbbbb" if g == "k" else "#00000055"
        out[f"pawn-{g}.svg"] = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 22 22">'
            f'<circle cx="11" cy="11" r="10" fill="{fill}" stroke="{edge}" stroke-width="1.5"/>'
            f'<text x="11" y="16" font-family="Arial, sans-serif" font-size="15" font-weight="bold"'
            f' text-anchor="middle" fill="{ink}">{glyph}</text></svg>\n'
        )
        out[f"cube-{g}.svg"] = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 14 14">'
            f'<rect x="1" y="1" width="12" height="12" rx="2" fill="{fill}" stroke="{edge}"'
            ' stroke-width="1.5"/></svg>\n'
        )
    return out


class Html:
    """Image tags, with paths relative to the illustrated file. Each icon's tooltip is
    its notation line and its meanings."""

    def __init__(self, icons: str, markers: str, meanings: dict[str, str] | None = None) -> None:
        self.icons, self.markers = icons, markers
        self.meanings = meanings or {}

    def icon(self, code: str, title: str) -> str:
        if code in self.meanings:
            title += f" — {self.meanings[code]}"
        t = html.escape(title, quote=True)
        return f'<img src="{self.icons}/{code}.png" height="{ICON_PX}" alt="{code}" title="{t}">'

    def pawn(self, group: str) -> str:
        return f'<img src="{self.markers}/pawn-{group}.svg" height="{PAWN_PX}" alt="pawn {group}">'

    def cubes(self, group: str, n: int) -> str:
        cube = f'<img src="{self.markers}/cube-{group}.svg" height="{CUBE_PX}" alt="cube {group}">'
        return cube * n


def render_line(std: str, group: str, h: Html) -> str:
    m = _STD.match(std)
    assert m, std
    note = f" <sub>[{html.escape(m['comment'])}]</sub>" if m["comment"] else ""
    if m["pawn"]:
        return h.icon(m["pcode"], std) + h.pawn(group) + note
    if m["unpawn"]:
        return "✕" + h.pawn(group) + note
    if m["all"]:
        return f"✕{h.pawn(group)}<sub>all</sub>" + note
    count = int(m["count"] or 1)
    item = h.icon(m["code"], std) + h.cubes(group, count)
    return ("✕" + item if m["sign"] == "-" else item) + note


def render_board(board: Board, h: Html) -> list[str]:
    rows = []
    for group in GROUPS:
        g = board.groups.get(group)
        if g is None:
            continue
        parts = [h.icon(g.pawn, g.pawn) + h.pawn(group)] if g.pawn else []
        counts: dict[str, int] = {}
        for code in g.cubes:
            counts[code] = counts.get(code, 0) + 1
        parts += [h.icon(code, code) + h.cubes(group, n) for code, n in counts.items()]
        rows.append(" ".join(parts))
    return rows


def illustrate_block(steps: list[list[str]], board: Board, h: Html) -> list[str] | None:
    """The HTML lines for one clue block, or None if it isn't notation (the board is
    then unchanged)."""
    trial = board.copy()
    out: list[str] = []
    try:
        for i, step in enumerate(steps):
            started_empty = not trial.groups
            placed = []
            for line in step:
                std = trial.apply(line, comments=True)
                placed.append(render_line(std, trial.last_group or "g", h))
            if i:
                out.append("")
            label = f"<sub>Step {i + 1}:</sub> " if len(steps) > 1 else ""
            out.append(label + " ".join(placed))
            plain_adds = all(line.lstrip().startswith(("+", "?", "!")) for line in step)
            if not (started_empty and plain_adds):
                rows = render_board(trial, h)
                out += ["", "<sub>Board now:</sub><br>"]
                out += [row + "<br>" for row in rows[:-1]] + rows[-1:]
    except NotationError:
        return None
    board.groups, board.last_group = trial.groups, trial.last_group
    return out


def illustrate(text: str, h: Html) -> str:
    lines = text.splitlines()
    out: list[str] = []
    board = Board()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#"):
            board = Board()  # each entry or game starts with an empty board
        fence = _FENCE.match(line)
        end = None
        if fence:
            end = next((j for j in range(i + 1, len(lines)) if _FENCE.match(lines[j])), None)
        if fence is None or end is None:
            out.append(line)
            i += 1
            continue
        indent = fence[1]
        body = [b.strip() for b in lines[i + 1 : end]]
        steps: list[list[str]] = [[]]
        for b in body:
            if b:
                steps[-1].append(b)
            elif steps[-1]:
                steps.append([])
        steps = [s for s in steps if s]
        rendered = illustrate_block(steps, board, h) if steps else None
        if rendered is None:
            out += lines[i : end + 1]
        else:
            out += [(indent + r if r else "") for r in rendered]
        i = end + 1
    return "\n".join(out) + "\n"


def main() -> int:
    if not ICONS.is_dir():
        print("error: no icon images; run `uv run python tools/player_aid.py` first")
        return 1
    markers = OUT / "markers"
    markers.mkdir(parents=True, exist_ok=True)
    for name, svg in marker_svgs().items():
        (markers / name).write_text(svg)
    meanings = icon_meanings()
    written = 0
    for sub, src in SOURCES.items():
        dest = OUT / sub
        dest.mkdir(parents=True, exist_ok=True)
        h = Html("../../player-aid/icons", "../markers", meanings)
        for path in sorted(src.glob("*.md")):
            (dest / path.name).write_text(illustrate(path.read_text(encoding="utf-8"), h))
            written += 1
    print(f"Wrote {written} illustrated files to {OUT.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
