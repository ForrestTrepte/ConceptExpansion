#!/usr/bin/env python3
"""Printable score sheet for a tabletop playtest round.

    uv run python tools/scoresheet.py 19-21          # writes output/scoresheet-19-21.pdf

One row per prompt on the given cards, with boxes for who clued and guessed, the
result, time, difficulty, and interest, and whether the final board was photographed.
The fields match the tabletop log format in docs/playtesting.md (Recording results).
Prompts are listed by card and number only, never by text, so guessers can see the
sheet. Each row shows its band color.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cards import DEFAULT_DATA, cards_from, load, parse_ranges, read_version

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output"

# Columns: (heading, width in inches, box labels or None for a blank to write in).
COLUMNS: list[tuple[str, float, tuple[str, ...] | None]] = [
    ("Prompt", 0.7, None),
    ("Clue-giver", 0.7, None),
    ("Guessers", 0.95, None),
    ("Result", 1.65, ("solved", "gave up", "skipped")),
    ("Time (min)", 1.1, ("<1", "1–3", "3+")),
    ("Difficulty", 2.6, ("too easy", "easy", "difficult", "hard", "too hard")),
    ("Interest", 2.0, ("low", "medium", "high", "fantastic")),
    ("Photo", 0.45, ("",)),
]
BAND_COLORS = {"blue": "#1f78c8", "red": "#d0312d", "black": "#222222"}


def rows_for(card_numbers: list[int], data: Path = DEFAULT_DATA) -> list[tuple[int, int, str]]:
    """(card, prompt number 1-9, band) for each prompt, in card order."""
    prompts, errors = load(data)
    if errors:
        raise ValueError("; ".join(errors))
    cards = cards_from(prompts)
    missing = [n for n in card_numbers if n not in cards]
    if missing:
        raise ValueError(f"no such cards in {data.name}: {', '.join(map(str, missing))}")
    rows = []
    for n in card_numbers:
        prompts_on_card = cards[n]
        if len(prompts_on_card) != 9:
            print(f"warning: card {n} has {len(prompts_on_card)} prompts, not 9", file=sys.stderr)
        rows += [(n, i, p.difficulty) for i, p in enumerate(prompts_on_card, 1)]
    return rows


def build(rows: list[tuple[int, int, str]], title: str, out: Path, version: str) -> None:
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen.canvas import Canvas

    width, height = landscape(letter)
    margin, row_h, box = 0.4 * inch, 0.34 * inch, 0.12 * inch
    c = Canvas(str(out), pagesize=(width, height))
    c.setTitle(f"New Notions score sheet: {title}")

    def page_header() -> float:
        y = height - margin
        c.setFont("Helvetica-Bold", 13)
        c.drawString(margin, y - 12, f"New Notions playtest · {title} · v{version}")
        c.setFont("Helvetica", 9)
        c.drawString(margin + 4.6 * inch, y - 12, "Date ____________   Players ______________________________")
        c.setFillColor(HexColor("#555555"))
        c.drawString(
            margin,
            y - 26,
            "Prompts are listed by card and number only. Photograph the final board of each"
            " played prompt (show the card number). Write comments on the back.",
        )
        c.setFillColor(HexColor("#000000"))
        y -= 46
        x = margin
        c.setFont("Helvetica-Bold", 8.5)
        for heading, w, _ in COLUMNS:
            c.drawString(x + 3, y + 4, heading)
            x += w * inch
        c.setStrokeColor(HexColor("#888888"))
        c.line(margin, y, x, y)
        return y

    y = page_header()
    previous_card = None
    for card, number, band in rows:
        if y - row_h < margin + 0.2 * inch:
            c.showPage()
            y = page_header()
            previous_card = None
        top, y = y, y - row_h
        if previous_card is not None and card != previous_card:
            c.setStrokeColor(HexColor("#444444"))
            c.setLineWidth(1.2)
            c.line(margin, top, margin + sum(w for _, w, _ in COLUMNS) * inch, top)
            c.setLineWidth(1)
        previous_card = card
        c.setFillColor(HexColor(BAND_COLORS.get(band, "#888888")))
        c.rect(margin, y + 3, 0.09 * inch, row_h - 6, stroke=0, fill=1)
        c.setFillColor(HexColor("#000000"))
        x = margin
        for i, (_, w, labels) in enumerate(COLUMNS):
            if i == 0:
                c.setFont("Helvetica-Bold", 10)
                c.drawString(x + 0.15 * inch, y + 0.11 * inch, f"{card} #{number}")
            elif labels is None:
                c.setStrokeColor(HexColor("#bbbbbb"))
                c.line(x + 4, y + 6, x + w * inch - 8, y + 6)
            else:
                c.setFont("Helvetica", 7)
                bx = x + 4
                for label in labels:
                    c.setStrokeColor(HexColor("#333333"))
                    c.rect(bx, y + 0.1 * inch, box, box, stroke=1, fill=0)
                    c.drawString(bx + box + 2, y + 0.11 * inch, label)
                    bx += box + 6 + c.stringWidth(label, "Helvetica", 7)
            x += w * inch
        c.setStrokeColor(HexColor("#dddddd"))
        c.line(margin, y, x, y)
    c.save()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("cards", help="card numbers, e.g. 19-21 or 5,6")
    ap.add_argument("--out", type=Path, help="output PDF (default output/scoresheet-<cards>.pdf)")
    args = ap.parse_args(argv)
    numbers = sorted(parse_ranges(args.cards))
    try:
        rows = rows_for(numbers)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    label = args.cards.replace(",", "_")
    out = args.out or OUT_DIR / f"scoresheet-{label}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    title = f"card{'s' if len(numbers) > 1 else ''} {args.cards}"
    build(rows, title, out, read_version())
    print(f"Wrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out} ({len(rows)} prompts)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
