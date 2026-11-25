"""Tests for tools/scoresheet.py."""

from __future__ import annotations

from pathlib import Path

import pytest
import scoresheet


def test_rows_list_prompts_by_number_and_band() -> None:
    rows = scoresheet.rows_for([1])
    assert [(c, n) for c, n, _ in rows] == [(1, i) for i in range(1, 10)]
    assert [b for _, _, b in rows] == ["blue"] * 3 + ["red"] * 3 + ["black"] * 3


def test_pdf_has_no_prompt_text(tmp_path: Path) -> None:
    from pypdf import PdfReader

    out = tmp_path / "sheet.pdf"
    assert scoresheet.main(["1", "--out", str(out)]) == 0
    text = "".join(page.extract_text() for page in PdfReader(out).pages)
    assert "1 #9" in text and "solved" in text
    assert "Pizza" not in text  # card 1's first prompt


def test_unknown_card() -> None:
    with pytest.raises(ValueError, match="no such cards"):
        scoresheet.rows_for([999])
