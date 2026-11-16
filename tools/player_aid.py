#!/usr/bin/env python3
"""Make a local copy of the official Concept player aid with grid coordinates on each icon.

Usage:
    python tools/player_aid.py

Downloads the official player aid PDF (once) and writes, under output/player-aid/:
    player-aid.pdf          the official PDF, unchanged (download cache)
    player-aid-coords.pdf   the same PDF with a code such as "A4" on every icon
    icons/<code>.png        one image per icon, e.g. icons/A4.png
    board-icons.md          docs/board-icons.md's tables with each icon's picture

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
    for p, code, x, y in icon_codes():
        box = tuple(round(v * scale) for v in (x - pad, y - pad, x + TILE + pad, y + TILE + pad))
        pages[p].crop(box).save(dest_dir / f"{code}.png")
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
        "",
        "**Colors** (named, not coded): Red, Orange, Yellow, Green, Blue, Purple, Pink, Brown, Black, "
        "Grey, White, Clear (Transparent / Invisible / Glass).",
    ]
    for title, left, right in [("Page 1, left (A, B)", "A", "B"), ("Page 1, right (C, D)", "C", "D"),
                               ("Page 2, left (E, F)", "E", "F"), ("Page 2, right (G, H)", "G", "H")]:
        lines += ["", f"## {title}", "", "| Icon | Code | Meanings | Icon | Code | Meanings |",
                  "|---|---|---|---|---|---|"]
        for row in range(1, ROWS_PER_COLUMN[left] + 1):
            lines.append(f"| {cell(f'{left}{row}')} | {cell(f'{right}{row}')} |")
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(codes)


def main() -> int:
    src = OUT_DIR / "player-aid.pdf"
    download(src)
    annotated = OUT_DIR / "player-aid-coords.pdf"
    annotate(src, annotated)
    print(f"Wrote {annotated}")
    n = extract_icons(src, OUT_DIR / "icons")
    print(f"Wrote {n} icon images to {OUT_DIR / 'icons'}")
    doc = OUT_DIR / "board-icons.md"
    write_illustrated_doc(ROOT / "docs" / "board-icons.md", doc)
    print(f"Wrote {doc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
