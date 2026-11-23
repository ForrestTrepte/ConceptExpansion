#!/usr/bin/env python3
"""Make a local copy of the official Concept player aid with grid coordinates on each icon.

Usage:
    uv run python tools/player_aid.py

Downloads the official player aid PDF (once) and writes, under output/player-aid/:
    player-aid.pdf          the official PDF, unchanged (download cache)
    player-aid-coords.pdf   the same PDF with a code such as "A4" on every icon
    icons/<code>.png        one image per icon, e.g. icons/A4.png, and per color, e.g. icons/Red.png
    board-icons.md          docs/board-icons.md's tables with each icon's picture
    pictured-elements.md    docs/pictured-elements.md with each icon's picture

Everything is written to output/, which is gitignored: the player aid is Repos Production's
copyrighted material, so we generate these files locally instead of committing them.
See docs/board-icons.md for the code -> meanings table.
"""
from __future__ import annotations

import io
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "player-aid"
URL = ("https://cdn.svc.asmodee.net/production-rprod/storage/games/concept/new-box/"
       "helpsheets2026/con-en01-player-aid-mkt-1767696650pHOQV.pdf")

# Icon tile geometry in PDF points (page is 680.3 pt square, origin top-left as measured).
TILE = 39.0
COL_X = [128.0, 174.0, 469.0, 514.0]
ROW_Y = [28.0, 73.0, 118.0, 163.0, 208.0, 253.0, 298.0, 342.0, 387.0, 432.0, 477.0, 522.0, 567.0, 611.0]
PAGE_COLUMNS = ["ABCD", "EFGH"]
# Page 2's left pair (E, F) has 11 rows; the colors box sits below it.
ROWS_PER_COLUMN = {c: 14 for c in "ABCDGH"} | {"E": 11, "F": 11}

# Color swatches in the dashed box at the bottom left of page 2 (named, not coded).
SWATCH = 35.0
SWATCH_X = [88.0, 128.0, 262.0, 302.0]
SWATCH_Y = [537.0, 577.0, 617.0]
COLOR_GRID = [["Red", "Orange", "Pink", "Brown"],
              ["Yellow", "Green", "Black", "Grey"],
              ["Blue", "Purple", "White", "Clear"]]
COLOR_MEANINGS = {"Clear": "Transparent / Invisible / Glass"}


def color_swatches() -> list[tuple[int, str, float, float]]:
    """(page index, color name, x, y-from-top) for every color swatch."""
    return [(1, name, x, y) for names, y in zip(COLOR_GRID, SWATCH_Y) for name, x in zip(names, SWATCH_X)]


def icon_codes() -> list[tuple[int, str, float, float]]:
    """(page index, code, x, y-from-top) for every icon tile."""
    out = []
    for page, letters in enumerate(PAGE_COLUMNS):
        for letter, x in zip(letters, COL_X):
            for row in range(ROWS_PER_COLUMN[letter]):
                out.append((page, f"{letter}{row + 1}", x, ROW_Y[row]))
    return out


def download(dest: Path) -> None:
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading player aid to {dest}")
    req = urllib.request.Request(URL, headers={"User-Agent": "concept-expansion-tools"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    if not data.startswith(b"%PDF"):
        raise SystemExit("error: download did not return a PDF")
    dest.write_bytes(data)


def annotate(src: Path, dest: Path) -> None:
    from pypdf import PdfReader, PdfWriter
    from reportlab.lib.colors import Color, HexColor, white
    from reportlab.pdfgen.canvas import Canvas

    writer = PdfWriter(clone_from=str(src))
    codes = icon_codes()
    for index, page in enumerate(writer.pages):
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        buf = io.BytesIO()
        c = Canvas(buf, pagesize=(w, h))
        for p, code, x, y in codes:
            if p != index:
                continue
            # label badge straddling the tile's top-left corner
            bw, bh = 15.0 if len(code) == 2 else 18.5, 9.0
            bx, by = x - 4, h - y - bh + 4
            c.setFillColor(white)
            c.setStrokeColor(HexColor("#c00000"))
            c.setLineWidth(0.8)
            c.roundRect(bx, by, bw, bh, 2.5, stroke=1, fill=1)
            c.setFillColor(HexColor("#c00000"))
            c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(bx + bw / 2, by + 2.3, code)
        # column letters above the grid
        c.setFillColor(Color(0.75, 0, 0))
        c.setFont("Helvetica-Bold", 9)
        for letter, x in zip(PAGE_COLUMNS[index], COL_X):
            c.drawCentredString(x + TILE / 2, h - 18, letter)
        c.save()
        overlay = PdfReader(io.BytesIO(buf.getvalue())).pages[0]
        page.merge_page(overlay)
    writer.add_metadata({"/Title": "Concept player aid with icon coordinates (personal use)"})
    with dest.open("wb") as f:
        writer.write(f)


def extract_icons(src: Path, dest_dir: Path, scale: float = 4.0) -> int:
    import pypdfium2 as pdfium

    dest_dir.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(src))
    pages = [pdf[i].render(scale=scale).to_pil() for i in range(len(pdf))]
    pad = 1.0
    n = 0
    tiles = [(p, code, x, y, TILE) for p, code, x, y in icon_codes()]
    tiles += [(p, name, x, y, SWATCH) for p, name, x, y in color_swatches()]
    for p, name, x, y, size in tiles:
        box = tuple(round(v * scale) for v in (x - pad, y - pad, x + size + pad, y + size + pad))
        pages[p].crop(box).save(dest_dir / f"{name}.png")
        n += 1
    return n


def write_illustrated_doc(icons_doc: Path, dest: Path) -> int:
    """Rebuild docs/board-icons.md's code tables with each icon's picture beside it."""
    import re

    meanings: dict[str, str] = {}
    for line in icons_doc.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 4 and re.fullmatch(r"[A-H]\d{1,2}", cells[0]):
            meanings[cells[0]] = cells[1]
            meanings[cells[2]] = cells[3]
    codes = [code for _, code, _, _ in icon_codes()]
    missing = [c for c in codes if c not in meanings]
    if missing:
        raise SystemExit(f"error: {icons_doc.name} has no meanings for {', '.join(missing)}")

    def cell(code: str) -> str:
        return f'<img src="icons/{code}.png" width="56" alt="{code}"> | **{code}** | {meanings[code]}'

    lines = [
        "# Board icons (illustrated, local copy)",
        "",
        "Generated by `tools/player_aid.py` from `docs/board-icons.md` and the official player aid. "
        "Not committed: the icon artwork is Repos Production's. Edit `docs/board-icons.md`, not this file.",
    ]
    for title, left, right in [("Page 1, left (A, B)", "A", "B"), ("Page 1, right (C, D)", "C", "D"),
                               ("Page 2, left (E, F)", "E", "F"), ("Page 2, right (G, H)", "G", "H")]:
        lines += ["", f"## {title}", "", "| Icon | Code | Meanings | Icon | Code | Meanings |",
                  "|---|---|---|---|---|---|"]
        for row in range(1, ROWS_PER_COLUMN[left] + 1):
            lines.append(f"| {cell(f'{left}{row}')} | {cell(f'{right}{row}')} |")

    def color_cell(name: str) -> str:
        meaning = COLOR_MEANINGS.get(name, name)
        return f'<img src="icons/{name}.png" width="50" alt="{name}"> | **{name}** | {meaning}'

    lines += ["", "## Colors (page 2, bottom left)", "",
              "Colors are written by name, not by code.", "",
              "| Icon | Name | Meanings | Icon | Name | Meanings |", "|---|---|---|---|---|---|"]
    for names in COLOR_GRID:
        for left, right in (names[0:2], names[2:4]):
            lines.append(f"| {color_cell(left)} | {color_cell(right)} |")
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(codes)


def write_illustrated_elements(elements_doc: Path, dest: Path) -> None:
    """Copy docs/pictured-elements.md with each icon's picture in a new first column."""
    import re

    names = {code for _, code, _, _ in icon_codes()} | {name for row in COLOR_GRID for name in row}
    docs_rel = "../../docs/"  # from output/player-aid/ back to docs/
    lines = [
        "# Pictured elements (illustrated, local copy)",
        "",
        "Generated by `tools/player_aid.py` from `docs/pictured-elements.md` and the official player aid. "
        "Not committed: the icon artwork is Repos Production's. Edit `docs/pictured-elements.md`, not this file.",
    ]
    text = elements_doc.read_text(encoding="utf-8")
    in_code_table = False  # only tables headed "| Code |" get the picture column
    for line in text.splitlines()[1:]:  # drop the original title
        # keep relative links working from output/player-aid/
        line = re.sub(r"\]\((?!https?:|#)([^)]+)\)", lambda m: f"]({docs_rel}{m.group(1)})", line)
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.startswith("|") else []
        if not cells:
            in_code_table = False
        elif cells[0] == "Code":
            in_code_table = True
            line = "| Icon " + line
        elif in_code_table and set(line.replace("|", "").strip()) <= set("-: "):
            line = "|---" + line
        elif in_code_table and cells[0] in names:
            line = f'| <img src="icons/{cells[0]}.png" width="96" alt="{cells[0]}"> ' + line
        lines.append(line)
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    src = OUT_DIR / "player-aid.pdf"
    download(src)
    annotated = OUT_DIR / "player-aid-coords.pdf"
    annotate(src, annotated)
    print(f"Wrote {annotated}")
    n = extract_icons(src, OUT_DIR / "icons")
    print(f"Wrote {n} icon and color images to {OUT_DIR / 'icons'}")
    doc = OUT_DIR / "board-icons.md"
    write_illustrated_doc(ROOT / "docs" / "board-icons.md", doc)
    print(f"Wrote {doc}")
    elements = OUT_DIR / "pictured-elements.md"
    write_illustrated_elements(ROOT / "docs" / "pictured-elements.md", elements)
    print(f"Wrote {elements}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
