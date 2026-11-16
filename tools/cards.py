#!/usr/bin/env python3
"""Validate the prompt data and build printable card sheets.

Usage:
    python tools/cards.py check [--data data/prompts.csv]
    python tools/cards.py pdf   [--data data/prompts.csv] [--out output/cards.pdf]
                                [--cards 1-25] [--status draft,approved] [--no-cut-lines]

See docs/data-and-printing.md for the file format and print settings.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = ROOT / "data" / "prompts.csv"
DEFAULT_OUT = ROOT / "output" / "cards.pdf"

COLUMNS = ["card", "difficulty", "prompt", "category", "source", "license", "status", "notes"]
DIFFICULTIES = ["blue", "red", "black"]  # band order on the card, top to bottom
STATUSES = {"draft", "approved", "rejected"}
MAX_PROMPT_CHARS = 24
SET_MARK = "NN"  # New Notions
CARD_WIDTH_MM = 61.5
CARD_HEIGHT_MM = 88.9

# --- Data -------------------------------------------------------------------


@dataclass
class Prompt:
    line: int
    card: int | None
    difficulty: str
    prompt: str
    category: str
    source: str
    license: str
    status: str
    notes: str


def normalize(text: str) -> str:
    """Lowercase, strip punctuation/articles and a trailing plural 's' for duplicate checks."""
    t = re.sub(r"[^a-z0-9 ]", "", text.lower())
    t = re.sub(r"^(the|a|an) ", "", t)
    words = [w[:-1] if len(w) > 3 and w.endswith("s") else w for w in t.split()]
    return " ".join(words)


def load(path: Path) -> tuple[list[Prompt], list[str]]:
    errors: list[str] = []
    prompts: list[Prompt] = []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != COLUMNS:
            errors.append(f"{path.name}: header must be exactly: {','.join(COLUMNS)}")
            return prompts, errors
        for i, row in enumerate(reader, start=2):
            row = {k: (v or "").strip() for k, v in row.items()}
            card = None
            if row["card"]:
                if not row["card"].isdigit() or int(row["card"]) < 1:
                    errors.append(f"line {i}: card must be a positive integer or blank")
                    continue
                card = int(row["card"])
            prompts.append(Prompt(i, card, row["difficulty"].lower(), row["prompt"], row["category"],
                                  row["source"], row["license"], row["status"].lower(), row["notes"]))
    return prompts, errors


def check(prompts: list[Prompt]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    seen: dict[str, Prompt] = {}
    by_card: dict[int, list[Prompt]] = defaultdict(list)
    for p in prompts:
        where = f"line {p.line} ({p.prompt!r})"
        if not p.prompt:
            errors.append(f"line {p.line}: prompt is empty")
        if p.difficulty not in DIFFICULTIES:
            errors.append(f"{where}: difficulty must be one of {', '.join(DIFFICULTIES)}")
        if p.status not in STATUSES:
            errors.append(f"{where}: status must be one of {', '.join(sorted(STATUSES))}")
        if not p.source or not p.license:
            errors.append(f"{where}: source and license are required")
        if p.prompt and not p.prompt[0].isupper() and not p.prompt[0].isdigit():
            warnings.append(f"{where}: should start with a capital letter")
        if len(p.prompt) > MAX_PROMPT_CHARS:
            warnings.append(f"{where}: longer than {MAX_PROMPT_CHARS} characters")
        if p.status == "rejected":
            if p.card is not None:
                errors.append(f"{where}: rejected prompts must not be assigned to a card")
            continue
        key = normalize(p.prompt)
        if key in seen:
            errors.append(f"{where}: duplicate of line {seen[key].line} ({seen[key].prompt!r})")
        else:
            seen[key] = p
        if p.card is not None:
            by_card[p.card].append(p)
    for card, items in sorted(by_card.items()):
        for d in DIFFICULTIES:
            n = sum(1 for p in items if p.difficulty == d)
            if n != 3:
                errors.append(f"card {card}: has {n} {d} prompts, needs exactly 3")
    return errors, warnings


def cards_from(prompts: list[Prompt]) -> dict[int, list[Prompt]]:
    """Card number -> its 9 prompts in print order (blue, red, black; file order within a band)."""
    by_card: dict[int, list[Prompt]] = defaultdict(list)
    for p in prompts:
        if p.card is not None and p.status != "rejected":
            by_card[p.card].append(p)
    return {c: sorted(items, key=lambda p: (DIFFICULTIES.index(p.difficulty), p.line))
            for c, items in sorted(by_card.items())}


def parse_ranges(spec: str) -> set[int]:
    out: set[int] = set()
    for part in spec.split(","):
        a, _, b = part.strip().partition("-")
        out.update(range(int(a), int(b or a) + 1))
    return out


# --- PDF --------------------------------------------------------------------

def build_pdf(cards: dict[int, list[Prompt]], out: Path, cut_lines: bool) -> int:
    from reportlab.lib.colors import HexColor, white
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch, mm
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen.canvas import Canvas

    # MTG size is 63.5 x 88.9 mm; 2 mm narrower so hand-cut cards slide into sleeves easily
    card_w, card_h = CARD_WIDTH_MM * mm, CARD_HEIGHT_MM * mm
    cols, rows = 3, 3
    page_w, page_h = letter
    x0 = (page_w - cols * card_w) / 2            # side margins
    y0 = (page_h - rows * card_h) / 2            # 0.25 in top/bottom margins

    band_colors = {"blue": HexColor("#1f78c8"), "red": HexColor("#d0312d"), "black": HexColor("#222222")}
    band_fills = {"blue": HexColor("#eaf3fb"), "red": HexColor("#fcebea"), "black": HexColor("#e4e4e4")}
    font, bold = "Helvetica", "Helvetica-Bold"

    def fit_size(text: str, max_w: float, size: float, min_size: float = 6.5) -> float:
        while size > min_size and stringWidth(text, font, size) > max_w:
            size -= 0.25
        return size

    def draw_card(c: Canvas, x: float, y: float, number: int, prompts: list[Prompt]) -> None:
        pad = 0.13 * inch
        header_h = 0.24 * inch
        gap = 0.06 * inch
        # header: set mark and card number
        c.setFillColor(HexColor("#666666"))
        c.setFont(bold, 7)
        c.drawString(x + pad, y + card_h - pad - 7, SET_MARK)
        c.setFont(font, 7)
        c.drawRightString(x + card_w - pad, y + card_h - pad - 7, f"#{number:03d}")
        # bands
        top = y + card_h - pad - header_h
        band_h = (top - (y + pad) - 2 * gap) / 3
        for b, diff in enumerate(DIFFICULTIES):
            by = top - (b + 1) * band_h - b * gap
            bx, bw = x + pad, card_w - 2 * pad
            c.setStrokeColor(band_colors[diff])
            c.setFillColor(band_fills[diff])
            c.setLineWidth(1.2)
            c.roundRect(bx, by, bw, band_h, 6, stroke=1, fill=1)
            items = [p for p in prompts if p.difficulty == diff]
            line_h = band_h / 3
            for i, p in enumerate(items):
                n = b * 3 + i + 1
                cy = by + band_h - (i + 0.5) * line_h
                r = 0.075 * inch
                cx = bx + 0.06 * inch + r
                c.setFillColor(band_colors[diff])
                c.circle(cx, cy, r, stroke=0, fill=1)
                c.setFillColor(white)
                c.setFont(bold, 7)
                c.drawCentredString(cx, cy - 2.5, str(n))
                tx = cx + r + 0.06 * inch
                max_w = bx + bw - 0.06 * inch - tx
                size = fit_size(p.prompt, max_w, 10.5)
                c.setFillColor(HexColor("#111111"))
                c.setFont(font, size)
                c.drawString(tx, cy - size * 0.35, p.prompt)

    def draw_cut_marks(c: Canvas) -> None:
        c.setStrokeColor(HexColor("#888888"))
        c.setLineWidth(0.4)
        off, ln = 0.04 * inch, 0.18 * inch
        xs = [x0 + i * card_w for i in range(cols + 1)]
        ys = [y0 + j * card_h for j in range(rows + 1)]
        for xv in xs:
            c.line(xv, y0 - off, xv, y0 - off - ln)
            c.line(xv, y0 + rows * card_h + off, xv, y0 + rows * card_h + off + ln)
        for yv in ys:
            c.line(x0 - off, yv, x0 - off - ln, yv)
            c.line(x0 + cols * card_w + off, yv, x0 + cols * card_w + off + ln, yv)

    out.parent.mkdir(parents=True, exist_ok=True)
    c = Canvas(str(out), pagesize=letter)
    c.setTitle("New Notions: an unofficial fan expansion for Concept")
    items = list(cards.items())
    per_page = cols * rows
    pages = 0
    corners: set[tuple[float, float]] = set()
    for start in range(0, len(items), per_page):
        for k, (number, prompts) in enumerate(items[start:start + per_page]):
            col, row = k % cols, k // cols
            x = x0 + col * card_w
            y = y0 + (rows - 1 - row) * card_h
            if cut_lines:  # faint "+" at each card corner, so marks survive the first round of cuts
                corners.update({(x, y), (x + card_w, y), (x, y + card_h), (x + card_w, y + card_h)})
            draw_card(c, x, y, number, prompts)
        c.setStrokeColor(HexColor("#d4d4d4"))
        c.setLineWidth(0.3)
        arm = 1.5 * mm
        for cx, cy in corners:
            c.line(cx - arm, cy, cx + arm, cy)
            c.line(cx, cy - arm, cx, cy + arm)
        corners.clear()
        draw_cut_marks(c)
        c.setFillColor(HexColor("#999999"))
        c.setFont(font, 6)
        # rotated into the left margin, alongside the middle row, clear of the cut marks
        c.saveState()
        c.translate(x0 / 2 + 2, page_h / 2)
        c.rotate(90)
        c.drawCentredString(0, 0, "Print at 100% / Actual size. Unofficial fan expansion for Concept. CC BY-NC-SA 4.0")
        c.restoreState()
        c.showPage()
        pages += 1
    c.save()
    return pages


# --- CLI --------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "pdf"):
        sp = sub.add_parser(name)
        sp.add_argument("--data", type=Path, default=DEFAULT_DATA)
        if name == "pdf":
            sp.add_argument("--out", type=Path, default=DEFAULT_OUT)
            sp.add_argument("--cards", help="card numbers to print, e.g. 1-9,12")
            sp.add_argument("--status", default="draft,approved",
                            help="only print cards whose prompts all have one of these statuses")
            sp.add_argument("--no-cut-lines", dest="cut_lines", action="store_false",
                            help="omit the faint + marks at card corners (margin cut marks only)")
    args = ap.parse_args(argv)

    prompts, errors = load(args.data)
    if not errors:
        e, warnings = check(prompts)
        errors += e
        for w in warnings:
            print(f"warning: {w}", file=sys.stderr)
    for e in errors:
        print(f"error: {e}", file=sys.stderr)
    if errors:
        return 1

    cards = cards_from(prompts)
    if args.cmd == "check":
        pool = sum(1 for p in prompts if p.card is None and p.status != "rejected")
        print(f"OK: {len(prompts)} prompts, {len(cards)} cards, {pool} unassigned")
        return 0

    allowed = {s.strip() for s in args.status.split(",")}
    cards = {n: ps for n, ps in cards.items() if all(p.status in allowed for p in ps)}
    if args.cards:
        wanted = parse_ranges(args.cards)
        cards = {n: ps for n, ps in cards.items() if n in wanted}
    if not cards:
        print("error: no cards match the filters", file=sys.stderr)
        return 1
    pages = build_pdf(cards, args.out, args.cut_lines)
    print(f"Wrote {args.out} ({len(cards)} cards, {pages} pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
