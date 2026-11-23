"""Tests for tools/play.py with a scripted clue-giver and scripted typing."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import play
import playtest_logs
import pytest
import simplay
from simplay import Role, Spec

SPEC = Spec(
    id="play",
    mode="model-clues",
    prompts=(),
    guesser=Role("claude-haiku-5-5"),
    clue_giver=Role("claude-sonnet-5-5"),
    max_guesses=5,
)


def scripted(replies: dict[str, list[object]]) -> simplay.Ask:
    async def ask(role: str, request: dict[str, Any], attempt: int) -> object:
        return replies[role].pop(0)

    return ask


def typing(*lines: str) -> play.Input:
    queue = list(lines)
    return lambda _prompt: queue.pop(0)


def test_human_game_with_yes_then_judge(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(play, "write_live", lambda *_: None)
    model = scripted(
        {
            "clue-giver": [
                {"confidence": 4, "action": "clue", "plan": "food", "lines": ["?g A14", "+ H4"]},
                {"verdict": "yes", "yes_to": "pie", "action": "clue", "plan": "p", "lines": ["+ Red"]},
            ],
            "judge": [{"correct": [False, False]}, {"correct": [True]}],
        }
    )
    read = typing("board?", "Pie, Cake, A, B, C, D", "Pie, Cake", "Pizza pie")
    game = asyncio.run(play.play_one(SPEC, "Pizza", read, model))
    assert (game.outcome, game.solved_at) == ("solved", 2)
    out = capsys.readouterr().out
    assert "?g A14" in out and "Food / Eating / Edible" in out
    assert "?g A14 | H4" in out  # board?
    assert "At most 5 guesses" in out
    assert "Clue-giver: Yes: Pie" in out
    assert "Pizza" not in out.replace("Pizza pie", "")  # the answer stays hidden


def test_logged_game_reads_back(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(playtest_logs, "LOGS", tmp_path)
    game = simplay.Game("Fire drill", "model-clues", 1, outcome="solved", solved_at=2, confidence=3)
    game.turns = [
        simplay.Turn(["?g A10", "+ E3"], "", "plan a", ["Bonfire", "Campfire"], verdict="yes", yes_to="Campfire"),
        simplay.Turn(["!r G14"], "", "plan b", ["Fire drill"], verdict="correct", correct_guess="Fire drill"),
    ]
    path = play.log_game(game, "red", SPEC, "keep", "fun")
    (entry,) = playtest_logs.parse_log(path)
    assert (entry.prompt, entry.card, entry.result, entry.solved_step) == ("Fire drill", None, "solved", 2)
    assert entry.steps == (("?g A10", "+ E3"), ("!r G14",))
    assert entry.yes == ("Campfire",)
    assert entry.source.endswith("claude-clues.md, pool")
    text = path.read_text()
    assert "Comments: fun" in text and "Band: red" in text and "Bonfire" in text


def test_pool_excludes_logged_and_assigned_prompts() -> None:
    pool = dict(play.pool_prompts())
    assert pool and "Pizza" not in pool and "Popcorn" not in pool
    assert set(pool.values()) <= {"blue", "red", "black"}


def test_play_requires_record_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLMEMO_MODE", raising=False)
    assert play.cmd_play("play", typing()) == 2
