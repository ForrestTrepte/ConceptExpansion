"""Tests for tools/simplay.py with scripted models: no LLM calls, no cache."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import pytest
import simplay
from notation import Board
from playtest_logs import LogGame
from simplay import Role, Spec


def spec(mode: simplay.Mode = "model-clues", **kw: Any) -> Spec:
    return Spec(
        id="test",
        mode=mode,
        prompts=("Pizza",),
        guesser=Role("claude-haiku-5-5", "low"),
        clue_giver=Role("claude-sonnet-5-5") if mode == "model-clues" else None,
        **kw,
    )


class Script:
    """A fake model: replies come from per-role queues, and requests are kept."""

    def __init__(self, **replies: Sequence[object]) -> None:
        self.replies = {role.replace("_", "-"): list(r) for role, r in replies.items()}
        self.requests: list[tuple[str, dict[str, Any], int]] = []

    async def __call__(self, role: str, request: dict[str, Any], attempt: int) -> object:
        self.requests.append((role, request, attempt))
        return self.replies[role].pop(0)

    def prompts(self, role: str) -> list[str]:
        return ["".join(r["prompt"]) for ro, r, _ in self.requests if ro == role]


def first(lines: list[str], action: str = "clue", confidence: int = 4) -> dict[str, Any]:
    return {"confidence": confidence, "action": action, "plan": "food first", "lines": lines}


def nxt(verdict: str, lines: list[str], yes_to: str = "", action: str = "clue") -> dict[str, Any]:
    return {"verdict": verdict, "yes_to": yes_to, "action": action, "plan": "p", "lines": lines}


def guess(*g: str) -> dict[str, Any]:
    return {"guesses": list(g), "pass": False}


def judged(*correct: bool) -> dict[str, Any]:
    return {"correct": list(correct)}


def run_full(script: Script, answer: str = "Pizza", **kw: Any) -> simplay.Game:
    return asyncio.run(simplay.play_model_clues(script, spec(**kw), answer, 1))


def test_solved_by_exact_guess_without_judging() -> None:
    script = Script(clue_giver=[first(["?g A14", "+ H4"])], guesser=[guess("Pie", "pizza")])
    game = run_full(script)
    assert (game.outcome, game.solved_at, game.confidence) == ("solved", 1, 4)
    assert [r for r, _, _ in script.requests] == ["clue-giver", "guesser"]


def test_yes_then_solved_by_judge() -> None:
    script = Script(
        clue_giver=[first(["?g A14"]), nxt("yes", ["+ H4"], yes_to="pie")],
        guesser=[guess("Pie", "Cake"), guess("Pizza pie")],
        judge=[judged(False, False), judged(True)],
    )
    game = run_full(script)
    assert (game.outcome, game.solved_at) == ("solved", 2)
    assert game.turns[0].yes_to == "Pie"
    assert (game.turns[1].correct_by, game.turns[1].correct_guess) == ("judge", "Pizza pie")
    assert [r for r, _, _ in script.requests] == [
        "clue-giver", "guesser", "judge", "clue-giver", "guesser", "judge"
    ]
    guesser_view = script.prompts("guesser")[1]
    assert "Clue-giver: Yes: Pie" in guesser_view
    assert "food first" not in guesser_view  # the plan is private
    assert "Pizza" not in "".join(script.requests[1][1]["system"]) + guesser_view


def test_invalid_lines_are_retried_with_the_error() -> None:
    script = Script(
        clue_giver=[first(["?g A14 it is round"]), first(["?g A14"])],
        guesser=[guess("Pizza")],
    )
    game = run_full(script)
    assert game.outcome == "solved"
    assert [a for _, _, a in script.requests] == [0, 1, 0]
    assert "rejected" in script.prompts("clue-giver")[1]
    assert len(game.invalid) == 1


def test_error_after_max_attempts() -> None:
    script = Script(clue_giver=[first(["nope"])] * simplay.MAX_ATTEMPTS)
    game = run_full(script)
    assert game.outcome == "error"


def test_judge_sees_only_answer_and_guesses() -> None:
    script = Script(
        clue_giver=[first(["?g A14"])], guesser=[guess("Pizza pie", "Pie")], judge=[judged(True, False)]
    )
    run_full(script)
    _, req, _ = script.requests[-1]
    assert req["model"] == simplay.JUDGE.model
    assert req["prompt"].startswith("Answer: Pizza\n\nGuesses:\n1. Pizza pie\n2. Pie")
    assert "A14" not in req["prompt"] + req["system"]


def test_judge_reply_must_cover_every_guess() -> None:
    script = Script(
        clue_giver=[first(["?g A14"])],
        guesser=[guess("Pizza pie", "Pie")],
        judge=[judged(True), judged(True, False)],
    )
    game = run_full(script)
    assert game.outcome == "solved"
    assert game.invalid[0]["role"] == "judge"


def test_yes_to_must_be_a_guess() -> None:
    script = Script(
        clue_giver=[first(["?g A14"]), nxt("yes", [], yes_to="Pizza"), nxt("no", ["+ H4"])],
        guesser=[guess("Cake"), guess("Pizza")],
        judge=[judged(False)],
    )
    game = run_full(script)
    assert game.outcome == "solved"
    assert game.invalid[0]["role"] == "clue-giver"


def test_skip_and_give_up_and_pass() -> None:
    assert run_full(Script(clue_giver=[first([], action="skip", confidence=1)])).outcome == "skipped"
    gave_up = Script(
        clue_giver=[first(["?g A14"]), nxt("no", [], action="give_up")],
        guesser=[guess("Cake")],
        judge=[judged(False)],
    )
    assert run_full(gave_up).outcome == "gave_up"
    passed = Script(clue_giver=[first(["?g A14"])], guesser=[{"guesses": [], "pass": True}])
    assert run_full(passed).outcome == "passed"


def test_out_of_rounds_after_last_judging() -> None:
    script = Script(
        clue_giver=[first(["?g A14"]), nxt("no", ["+ H4"])],
        guesser=[guess("Cake"), guess("Pie")],
        judge=[judged(False), judged(False)],
    )
    game = run_full(script, max_rounds=2)
    assert game.outcome == "out_of_rounds"
    assert script.requests[-1][0] == "judge"


def test_clue_giver_cannot_say_correct() -> None:
    script = Script(
        clue_giver=[first(["?g A14"]), nxt("correct", []), nxt("no", [], action="give_up")],
        guesser=[guess("Cake")],
        judge=[judged(False)],
    )
    game = run_full(script)
    assert game.outcome == "gave_up"
    assert game.invalid[0]["role"] == "clue-giver"


def test_human_clues_use_logged_steps_then_extra_rounds() -> None:
    human = LogGame(
        prompt="Break the ice",
        card=1,
        number=7,
        source="playtests/x.md:9",
        kind="claude-clues",
        result="solved",
        solved_step=9,
        clues=(("?g B8", "+ F8"), ("!r E5 [on the rock]",)),
        yes=("Hail",),
    )
    script = Script(
        guesser=[guess("Breakup"), guess("hail"), guess("Ice"), guess("Break the ice!")],
        judge=[judged(False), judged(False), judged(False)],
    )
    game = asyncio.run(simplay.play_human_clues(script, spec("human-clues", extra_rounds=2), human, 1))
    assert (game.outcome, game.solved_at, game.source) == ("solved", 4, "playtests/x.md:9")
    assert game.turns[1].verdict == "yes" and game.turns[1].yes_to == "hail"
    assert game.turns[2].lines == []
    assert "[on the rock]" in script.prompts("guesser")[1]


def test_too_many_guesses_rejected() -> None:
    with pytest.raises(simplay.Invalid):
        simplay.parse_guesses(guess("a", "b", "c", "d"), 3)
    assert simplay.parse_guesses(guess("Cat", "cat", "Dog"), 3) == (["Cat", "Dog"], False)


def test_match_key() -> None:
    assert simplay.matches("the spiderman", ["Spider-Man"])
    assert simplay.matches("Deja vu", ["Déjà vu"])
    assert not simplay.matches("Ice", ["Break the ice"])


def test_board_reference_leaves_out_worklists() -> None:
    ref = simplay.board_reference()
    assert "| A4 | Fauna / Animal |" in ref and "| A4 | Octopus;" in ref
    for word in ("Audit", "Compounds to re-band", "Lighthouse", "Clue mechanics"):
        assert word not in ref


def test_system_parts_are_separated() -> None:
    parts = simplay.system("role")
    assert all(p.endswith("\n\n") for p in parts)


def test_specs_load() -> None:
    for path in simplay.SPECS_DIR.glob("*.toml"):
        s = simplay.load_spec(path.stem)
        assert s.spend_limit_usd > 0


def test_markdown_report() -> None:
    script = Script(clue_giver=[first(["?g A14"])], guesser=[guess("Pizza pie")], judge=[judged(True)])
    game = run_full(script)
    run = {"spec": asdict(spec()), "games": [asdict(game)], "entries": []}
    md = simplay.markdown(run)
    assert "| Pizza | 1/1 | 1 |" in md
    assert "Guesses: Pizza pie → Correct (judge: Pizza pie)" in md


def test_usage_limit_stops_the_run(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    from datetime import UTC, datetime

    from llmemo import UsageLimitReached

    async def refused(_spec: Spec) -> dict[str, Any]:
        raise UsageLimitReached("limit", resets_at=datetime(2026, 11, 23, 4, 0, tzinfo=UTC))

    monkeypatch.setattr(simplay, "run_spec", refused)
    monkeypatch.setattr(simplay, "write_run", lambda _run: pytest.fail("wrote a partial run"))
    assert simplay.cmd_run(["dry-run-model-clues"]) == 2
    out = capsys.readouterr().out
    assert "usage limit" in out and "2026-11-2" in out


def test_agreement_with_humans() -> None:
    def g(human: str, outcome: str, comments: bool = False) -> dict[str, Any]:
        return {"human_result": human, "outcome": outcome, "clue_comments": comments}

    games = [g("solved", "solved"), g("failed", "solved"), g("failed", "out_of_rounds", True)]
    rows = simplay.agreement(games)
    assert "| All games | 1/1 | 1/2 | 2/3 (67%) |" in rows
    assert "| Without clue comments | 1/1 | 1/1 | 1/2 (50%) |" in rows


def test_one_guess_wording() -> None:
    req = simplay.guesser_request(spec(max_guesses=1, guesser_prompt="guesser-instinct"), [])
    assert "Give up to 1 guess, best first" in req["prompt"]
    assert "say up to 1 guess:" in req["system"][-1]
    assert req["jsonSchema"]["properties"]["guesses"]["maxItems"] == 1


def test_list_reference() -> None:
    req = simplay.clue_giver_request(spec(reference="list"), "Pizza", [])
    ref = req["system"][1]
    assert "A4: Fauna / Animal. Picture: Octopus;" in ref
    assert "Sky, grass" not in ref  # backgrounds are left out
    assert "Clear: Transparent / Invisible / Glass." in ref
    assert len([line for line in ref.splitlines() if ":" in line[:7]]) == 118
    default = simplay.clue_giver_request(spec(), "Pizza", [])
    assert "| A4 | Fauna / Animal |" in default["system"][1]  # existing runs unchanged


def test_openrouter_guesser_request() -> None:
    s = replace(spec("human-clues"), guesser=Role("openai/gpt-6-luna", "low", "openrouter", 2000))
    req = simplay.guesser_request(s, [simplay.Turn(["?g A1"], "?g A1")])
    assert req["backend"] == "openrouter" and req["endpoint"] == "chat/completions"
    body = req["body"]
    assert body["model"] == "openai/gpt-6-luna"
    assert body["reasoning"] == {"effort": "low"} and body["max_tokens"] == 2000
    system, user = body["messages"]
    claude = simplay.guesser_request(spec("human-clues"), [simplay.Turn(["?g A1"], "?g A1")])
    assert system["content"] == "".join(claude["system"]) and user["content"] == claude["prompt"]
    schema = body["response_format"]["json_schema"]["schema"]
    assert "maxItems" not in schema["properties"]["guesses"]


def test_structured_reply_from_either_backend() -> None:
    assert simplay.structured({"structured_output": {"pass": True}}) == {"pass": True}
    fenced = {"choices": [{"message": {"content": '```json\n{"guesses": ["Cat"], "pass": false}\n```'}}]}
    assert simplay.structured(fenced) == {"guesses": ["Cat"], "pass": False}
    assert simplay.structured({"choices": [{"message": {"content": "Cat!"}}]}) is None
    assert simplay.structured("nope") is None


def test_only_the_guesser_uses_openrouter(tmp_path: Path) -> None:
    (tmp_path / "x.toml").write_text(
        'mode = "model-clues"\nprompts = []\nspend_limit_usd = 1.0\n'
        '[clue_giver]\nmodel = "openai/gpt-6-luna"\nbackend = "openrouter"\n'
        '[guesser]\nmodel = "openai/gpt-6-luna"\nbackend = "openrouter"\n'
    )
    with pytest.raises(ValueError, match="only the guesser"):
        simplay.load_spec("x", tmp_path)
