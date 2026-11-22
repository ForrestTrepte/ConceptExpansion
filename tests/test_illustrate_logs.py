"""Tests for tools/illustrate_logs.py: clue blocks become icons and markers."""

from __future__ import annotations

from illustrate_logs import Html, icon_meanings, illustrate, marker_svgs

H = Html("icons", "markers")


def test_single_step_block() -> None:
    out = illustrate("### Card 1, #1: X\n- Clues:\n  ```\n  ?g A4\n  + Yellow x2\n  ```\n", H)
    assert "```" not in out
    assert '  <img src="icons/A4.png"' in out
    assert out.count('src="markers/cube-g.svg"') == 2
    assert 'src="markers/pawn-g.svg"' in out
    assert "Board now" not in out  # the step's markers are the whole board


def test_pauses_show_steps_and_board() -> None:
    text = "### X\n```\n?g A4\n\n!r B11\n+ G14\n\n- G14\n```\n"
    out = illustrate(text, H)
    assert "<sub>Step 3:</sub> ✕" in out
    assert out.count("Board now") == 2


def test_board_carries_over_blocks_until_a_heading() -> None:
    out = illustrate("### A\n```\n?g A4\n```\n```\n+ B4\n```\n### B\n```\n+ C4\n```\n", H)
    assert out.count("Board now") == 1  # only for "+ B4"; "+ C4" starts a new entry


def test_other_code_blocks_are_kept() -> None:
    text = "```\nuv run pytest\n```\n```\n- A4\n```\n"
    assert illustrate(text, H) == text


def test_picture_detail_comment() -> None:
    out = illustrate("```\n+g A8 [on the bulb]\n```\n", H)
    assert "<sub>[on the bulb]</sub>" in out


def test_markers_for_every_group() -> None:
    names = marker_svgs()
    assert len(names) == 10 and all(svg.startswith("<svg") for svg in names.values())


def test_tooltips_include_meanings() -> None:
    meanings = icon_meanings()
    assert meanings["A4"] == "Fauna / Animal"
    assert meanings["Clear"] == "Transparent / Invisible / Glass"
    assert len(meanings) == 118  # 106 icons and 12 colors
    out = illustrate("```\n?g A4\n```\n", Html("i", "m", meanings))
    assert 'title="?g A4 — Fauna / Animal"' in out
