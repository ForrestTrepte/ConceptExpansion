"""The board icons as data, read from the human reference docs.

docs/board-icons.md (meanings, two icons per table row, like the player aid) and
docs/pictured-elements.md (what each picture shows) stay laid out for people. These
functions read them by code, and `reference_list` turns them into one line per icon
for models, so no code has to be matched across columns or tables.
"""

from __future__ import annotations

from pathlib import Path

from notation import COLORS, CODES, ROWS

ROOT = Path(__file__).resolve().parent.parent
BOARD_ICONS = ROOT / "docs" / "board-icons.md"
PICTURED = ROOT / "docs" / "pictured-elements.md"


def _rows(doc: Path) -> list[list[str]]:
    rows = []
    for line in doc.read_text(encoding="utf-8").splitlines():
        if line.startswith("|"):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows


def icon_meanings(doc: Path = BOARD_ICONS) -> dict[str, str]:
    """Each icon's meanings, e.g. `A4` -> `Fauna / Animal`."""
    out = {}
    for cells in _rows(doc):
        for code, meaning in zip(cells[::2], cells[1::2]):
            if code in CODES:
                out[code] = meaning
    return out


def pictured(doc: Path = PICTURED) -> dict[str, tuple[str, str, str]]:
    """Each icon's elements, look-alikes, and small details (backgrounds left out)."""
    out = {}
    for cells in _rows(doc):
        if len(cells) >= 4 and cells[0] in CODES:
            out[cells[0]] = (cells[1], cells[2], cells[3])
    return out


def code_order() -> list[str]:
    """Icons column by column (A1–A14, B1–B14, …), then the colors."""
    return [f"{col}{row}" for col, rows in ROWS.items() for row in range(1, rows + 1)] + list(COLORS)


def reference_list() -> str:
    meanings, pics = icon_meanings(), pictured()
    lines = [
        "# Board reference",
        "",
        "One line per icon: its code, its meanings (separated by /), and what its picture"
        " shows. A code stands for the whole icon with all its meanings.",
        "",
    ]
    for code in code_order():
        line = f"{code}: {meanings[code]}."
        elements, looks, details = pics.get(code, ("", "", ""))
        if code not in COLORS and elements:
            line += f" Picture: {elements}."
            if looks:
                line += f" Looks like: {looks}."
            if details:
                line += f" Details: {details}."
        lines.append(line)
    return "\n".join(lines) + "\n"
