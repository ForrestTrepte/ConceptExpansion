"""Tests for tools/notation.py: parsing clue lines and tracking the board."""

from __future__ import annotations

import pytest
from notation import Board, NotationError, normalize_code


def test_bee_example() -> None:
    board = Board()
    lines = board.apply_all(
        ["?g A4", "+ B11", "+ yellow", "+ Black", "!r B11", "+ G14", "+ B4", "!y A14", "+ F3", "+ Yellow"]
    )
    assert lines[2] == "+ Yellow"
    assert board.summary() == (
        "?g A4 | B11, Yellow, Black\n!r B11 | G14, B4\n!y A14 | F3, Yellow"
    )


def test_group_rule_in_standard_form() -> None:
    board = Board()
    assert board.apply_all(["?g A4", "+g B11", "!r C3", "+g G14", "+g D3"]) == [
        "?g A4",
        "+ B11",
        "!r C3",
        "+g G14",
        "+ D3",
    ]


def test_each_step_names_its_first_group() -> None:
    board = Board()
    board.apply_all(["?g A4"])
    assert board.apply_all(["+ B11"]) == ["+g B11"]


def test_counts_and_removal() -> None:
    board = Board()
    board.apply_all(["?g A13", "+ G7 x3", "- G7"])
    assert board.summary() == "?g A13 | G7, G7"
    board.apply_all(["-g all"])
    assert board.summary() == "(empty)"


def test_cubes_without_pawn() -> None:
    board = Board()
    board.apply_all(["+g E2", "+ D4"])
    assert board.summary() == "g (no pawn) | E2, D4"


def test_move_pawn() -> None:
    board = Board()
    board.apply_all(["!r A1", "+ C7", "-!r", "!r B1"])
    assert board.summary() == "!r B1 | C7"


@pytest.mark.parametrize(
    "lines",
    [
        ["+ A4"],  # first line has no group
        ["?g Z9"],  # unknown code
        ["?g E12"],  # column E stops at row 11
        ["?r A4"],  # ? pawn is only for g
        ["!g A4"],  # g has the ? pawn
        ["?g A4", "?g B4"],  # second pawn in a group
        ["?g A4", "- B4"],  # removing a cube that isn't there
        ["?g A4 hint: it flies"],  # words
        ["?g A4 [on the octopus]"],  # comments need comments=True
        ["+g A4 x0"],
    ],
)
def test_rejected(lines: list[str]) -> None:
    board = Board()
    with pytest.raises(NotationError):
        board.apply_all(lines)


def test_rejected_step_leaves_board_unchanged() -> None:
    board = Board()
    board.apply_all(["?g A4"])
    with pytest.raises(NotationError):
        board.apply_all(["+ B11", "+ nonsense"])
    assert board.summary() == "?g A4"


def test_comments_allowed_for_human_games() -> None:
    board = Board()
    assert board.apply_all(["+g A8 [on the bulb]"], comments=True) == ["+g A8 [on the bulb]"]


def test_normalize_code() -> None:
    assert normalize_code("h14") == "H14"
    assert normalize_code("clear") == "Clear"
    with pytest.raises(NotationError):
        normalize_code("Gray")
