#!/usr/bin/env python3
"""Simulated playtests: a model clue-giver and a model guesser play Concept prompts.

    uv run python tools/simplay.py run dry-run-model-clues   # play a spec's games (from the cache)
    uv run python tools/simplay.py all                       # replay every recorded run
    uv run python tools/simplay.py preview dry-run-model-clues Pizza   # print the first requests

A spec (`sim-playtests/specs/<id>.toml`) says which prompts to play, in which mode, with
which models. `run` writes `sim-playtests/runs/<id>.json` (settings, games, usage, and
the cache entries used) and `<id>.md` (the games in playtest notation).

Modes:
- `model-clues`: the clue-giver model clues the prompt, and the guesser model guesses.
- `human-clues`: clue sequences from playtest logs with human guessers (`playtests/`,
  read by `tools/playtest_logs.py`) go to the guesser model, to compare it with them.

Every call goes through llmemo and replays from `sim-playtests/cache/`, so a missing
call fails. To record, set `LLMEMO_MODE=record` on the one command; it spends the Claude
subscription up to the spec's `spend_limit_usd`. See docs/simulated-playtesting.md.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import re
import statistics
import string
import sys
import tomllib
import unicodedata
from collections import Counter
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from notation import Board, NotationError
from playtest_logs import LogGame, human_guessed

ROOT = Path(__file__).resolve().parent.parent
SIM = ROOT / "sim-playtests"
CACHE_DIR = SIM / "cache"
SPECS_DIR = SIM / "specs"
RUNS_DIR = SIM / "runs"
PROMPTS_CSV = ROOT / "data" / "prompts.csv"
TEXTS = Path(__file__).resolve().parent / "sim_prompts"
DOCS = ROOT / "docs"

MAX_ATTEMPTS = 3  # tries per call when a reply is invalid

Mode = Literal["model-clues", "human-clues"]


@dataclass(frozen=True)
class Role:
    model: str
    effort: str | None = None  # claude-cli: --effort; openrouter: reasoning effort
    backend: str = "claude-cli"  # or "openrouter" (guesser only), with an OpenRouter model ID
    max_tokens: int | None = None  # openrouter only; leave room for reasoning models


# Fixed for every run, so changing the clue-giver or guesser can't change the scoring.
JUDGE = Role("claude-sonnet-5-5", "low")
Outcome = Literal["solved", "passed", "gave_up", "out_of_rounds", "skipped", "error"]


# Reference texts ----------------------------------------------------------------------


def section(text: str, start: str, stop: str | None) -> str:
    """The part of a Markdown doc from heading `start` up to the heading that begins with
    `stop`. Raises ValueError if either is missing, so a renamed heading can't silently
    change what the models see."""
    i = text.index(f"\n{start}\n")
    j = text.index(f"\n{stop}", i) if stop else len(text)
    return text[i:j].strip() + "\n"


def board_reference() -> str:
    """Icon meanings and pictured elements, without the docs' intros and worklists, which
    name prompts. Both roles get the same text."""
    icons = section((DOCS / "board-icons.md").read_text(), "## Page 1", "## Clue mechanics")
    pictured = section(
        (DOCS / "pictured-elements.md").read_text(),
        "## Page 1, left (A, B)",
        "## Audit",
    )

    def demote(s: str) -> str:
        return re.sub(r"^## ", "### ", s, flags=re.MULTILINE)

    return (
        "# Board reference\n\n## Icon meanings\n\n"
        + demote(icons)
        + "\n## What each icon's picture shows\n\n"
        "Elements are the main drawings. Look-alikes are drawings that resemble a specific"
        " real thing. Small details are parts of a drawing. Background is the pattern"
        " behind it.\n\n" + demote(pictured)
    )


def text(name: str, **values: object) -> str:
    return string.Template((TEXTS / f"{name}.md").read_text()).substitute(values)


def reference(kind: str) -> str:
    """The board reference models get: `tables` (the docs' tables as they are, the
    original format) or `list` (one line per icon: meanings and picture together)."""
    if kind == "tables":
        return board_reference()
    if kind == "list":
        from board import reference_list

        return reference_list()
    raise ValueError(f"reference must be tables or list, not {kind!r}")


def system(role_text: str, kind: str = "tables") -> list[str]:
    """The system prompt as parts, so llmemo stores the long shared ones once. llmemo
    joins parts with nothing between them, so each ends with a blank line."""
    parts = [text("rules"), reference(kind), role_text]
    return [p.rstrip("\n") + "\n\n" for p in parts]


# Specs and data -----------------------------------------------------------------------


@dataclass(frozen=True)
class Spec:
    id: str
    mode: Mode
    prompts: tuple[str, ...]
    guesser: Role
    clue_giver: Role | None = None
    trials: int = 1
    max_rounds: int = 8
    max_guesses: int = 3
    guesser_prompt: str = "guesser"  # tools/sim_prompts/<name>.md
    reference: str = "tables"  # board reference format: tables or list (see `reference`)
    extra_rounds: int = 2
    concurrency: int = 3
    spend_limit_usd: float = 0.0


def load_spec(spec_id: str, specs_dir: Path = SPECS_DIR) -> Spec:
    data = tomllib.loads((specs_dir / f"{spec_id}.toml").read_text())
    known = {f for f in Spec.__dataclass_fields__} - {"id"}
    unknown = set(data) - known
    if unknown:
        raise ValueError(f"spec {spec_id}: unknown settings {sorted(unknown)}")

    def role(name: str) -> Role | None:
        if name not in data:
            return None
        return Role(**data[name])

    mode = data["mode"]
    if mode not in ("model-clues", "human-clues"):
        raise ValueError(f"spec {spec_id}: mode must be model-clues or human-clues")
    guesser = role("guesser")
    if guesser is None:
        raise ValueError(f"spec {spec_id}: [guesser] is required")
    clue_giver = role("clue_giver")
    for name, r in (("guesser", guesser), ("clue_giver", clue_giver)):
        if r is not None and r.backend not in ("claude-cli", "openrouter"):
            raise ValueError(f"spec {spec_id}: [{name}] backend must be claude-cli or openrouter")
        if r is not None and r.effort == "none" and r.backend != "openrouter":
            raise ValueError(f"spec {spec_id}: [{name}] effort none is for OpenRouter models")
    if clue_giver is not None and clue_giver.backend != "claude-cli":
        raise ValueError(f"spec {spec_id}: only the guesser can use OpenRouter")
    if mode == "model-clues" and clue_giver is None:
        raise ValueError(f"spec {spec_id}: a model-clues spec needs [clue_giver]")
    rest = {k: v for k, v in data.items() if k not in ("mode", "prompts", "guesser", "clue_giver")}
    return Spec(
        id=spec_id,
        mode=mode,
        prompts=tuple(data["prompts"]),
        guesser=guesser,
        clue_giver=clue_giver,
        **rest,
    )


def deck_prompts(path: Path = PROMPTS_CSV) -> set[str]:
    with path.open(newline="", encoding="utf-8") as f:
        return {r["prompt"] for r in csv.DictReader(f) if r["status"] != "rejected"}


# Matching guesses ---------------------------------------------------------------------


def match_key(s: str) -> str:
    """Letters and digits only, lowercase, no accents, no leading article: so "The
    Spider-man" matches "Spider-Man" and "Deja vu" matches "Déjà vu"."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()
    s = re.sub(r"^(the|a|an)\s+", "", s)
    return re.sub(r"[^a-z0-9]", "", s)


def matches(guess: str, answers: Sequence[str]) -> bool:
    return match_key(guess) in {match_key(a) for a in answers}


# Requests -----------------------------------------------------------------------------

GUESS_SCHEMA_BASE: dict[str, Any] = {
    "type": "object",
    "properties": {
        "guesses": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["guesses"],
    "additionalProperties": False,
}

_LINES = {"type": "array", "items": {"type": "string"}}
_PLAN = {"type": "string"}
_VERDICT = {"type": "string", "enum": ["yes", "no"]}
_YES_TO = {"type": "string"}

FIRST_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "confidence": {"type": "integer", "minimum": 1, "maximum": 5},
        "action": {"type": "string", "enum": ["clue", "skip"]},
        "plan": _PLAN,
        "lines": _LINES,
    },
    "required": ["confidence", "action", "plan", "lines"],
    "additionalProperties": False,
}
NEXT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "verdict": _VERDICT,
        "yes_to": _YES_TO,
        "action": {"type": "string", "enum": ["clue", "give_up"]},
        "plan": _PLAN,
        "lines": _LINES,
    },
    "required": ["verdict", "yes_to", "action", "plan", "lines"],
    "additionalProperties": False,
}
JUDGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"correct": {"type": "array", "items": {"type": "boolean"}}},
    "required": ["correct"],
    "additionalProperties": False,
}


def guesses(n: int) -> str:
    return f"{n} guess" if n == 1 else f"{n} guesses"


def guess_schema(max_guesses: int) -> dict[str, Any]:
    schema: dict[str, Any] = json.loads(json.dumps(GUESS_SCHEMA_BASE))
    schema["properties"]["guesses"]["maxItems"] = max_guesses
    return schema


@dataclass
class Turn:
    """One step: markers placed, then the guesser's reply and the clue-giver's verdict."""

    lines: list[str]
    board: str
    plan: str = ""
    guesses: list[str] = field(default_factory=list)
    passed: bool = False
    verdict: str = ""  # correct / yes / no; empty until judged
    yes_to: str = ""
    correct_by: str = ""  # "match" (the script) or "judge", when verdict is correct
    correct_guess: str = ""


def feedback(turn: Turn) -> str:
    if turn.verdict == "yes":
        return f"Yes: {turn.yes_to}"
    return turn.verdict.capitalize()


def history(turns: Sequence[Turn], *, for_clue_giver: bool) -> str:
    out = []
    for i, t in enumerate(turns, 1):
        placed = "\n".join(t.lines) if t.lines else "(no new markers)"
        part = f"Step {i}, markers placed:\n{placed}\n"
        if for_clue_giver and t.plan:
            part += f"Your private plan: {t.plan}\n"
        part += f"Board now:\n{t.board}\n"
        if t.passed:
            part += "Guesser: pass\n"
        elif t.guesses:
            part += f"Guesses: {', '.join(t.guesses)}\n"
        if t.verdict:
            part += f"Clue-giver: {feedback(t)}\n"
        out.append(part)
    return "\n".join(out)


def guesser_request(spec: Spec, turns: Sequence[Turn]) -> dict[str, Any]:
    from llmemo import ClaudeCli

    prompt = (
        "New prompt.\n\n"
        + history(turns, for_clue_giver=False)
        + f"\nGive up to {guesses(spec.max_guesses)}, best first, or none to pass."
    )
    parts = system(text(spec.guesser_prompt, guesses=guesses(spec.max_guesses)), spec.reference)
    if spec.guesser.backend == "openrouter":
        return openrouter_request(spec.guesser, parts, prompt, guess_schema(spec.max_guesses))
    return ClaudeCli.request(
        spec.guesser.model,
        prompt,
        system=parts,
        json_schema=guess_schema(spec.max_guesses),
        effort=spec.guesser.effort,
    )


def openrouter_request(
    role: Role, parts: Sequence[str], prompt: str, schema: dict[str, Any]
) -> dict[str, Any]:
    """The same system text and prompt as a Claude request, as an OpenRouter chat
    request with a JSON-schema reply. `maxItems` is dropped from the schema (strict mode
    doesn't support it everywhere); replies with too many guesses are rejected and retried
    like any invalid reply."""
    from llmemo import OpenRouter

    loose = json.loads(json.dumps(schema))
    for prop in loose["properties"].values():
        prop.pop("maxItems", None)
    body: dict[str, Any] = {
        "model": role.model,
        "messages": [
            {"role": "system", "content": "".join(parts)},
            {"role": "user", "content": prompt},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "reply", "strict": True, "schema": loose},
        },
    }
    if role.effort == "none":
        body["reasoning"] = {"enabled": False}
    elif role.effort:
        body["reasoning"] = {"effort": role.effort}
    if role.max_tokens:
        body["max_tokens"] = role.max_tokens
    return OpenRouter.chat_request(body)


def structured(reply: object) -> object:
    """The JSON object a reply carries: `structured_output` from the Claude CLI, or the
    message content from OpenRouter (parsed, allowing a ```json fence). None if absent."""
    if not isinstance(reply, dict):
        return None
    if "structured_output" in reply or "choices" not in reply:
        return reply.get("structured_output")
    try:
        content = reply["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None
    if not isinstance(content, str):
        return None
    content = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", content)
    try:
        value: object = json.loads(content)
    except ValueError:
        return None
    return value


def clue_giver_request(
    spec: Spec, answer: str, turns: Sequence[Turn], *, error: str = ""
) -> dict[str, Any]:
    from llmemo import ClaudeCli

    assert spec.clue_giver is not None
    prompt = f"The answer is: {answer}\n\n"
    if not turns:
        prompt += (
            "This is the start of the game. Rate your confidence, then give your first"
            " markers, or skip."
        )
        schema = FIRST_SCHEMA
    else:
        prompt += (
            "The game so far:\n\n"
            + history(turns, for_clue_giver=True)
            + "\nThe judge found none of the last guesses correct. Answer Yes or No to them,"
            f" then add markers or give up. The guesser has {spec.max_rounds - len(turns)}"
            " turns left."
        )
        schema = NEXT_SCHEMA
    if error:
        prompt += f"\n\nYour last reply was rejected: {error}. Reply again."
    return ClaudeCli.request(
        spec.clue_giver.model,
        prompt,
        system=system(text("clue-giver"), spec.reference),
        json_schema=schema,
        effort=spec.clue_giver.effort,
    )


def judge_request(answer: str, guesses: Sequence[str], *, error: str = "") -> dict[str, Any]:
    """Whether each guess names the answer. The judge sees no clues, and its model is fixed
    here rather than in the spec, so every run scores guesses the same way. It is the same
    request for the same answer and guesses, so all trials and specs share one verdict."""
    from llmemo import ClaudeCli

    listed = "\n".join(f"{i}. {g}" for i, g in enumerate(guesses, 1))
    prompt = (
        f"Answer: {answer}\n\nGuesses:\n{listed}\n\nReply with one true or false per guess,"
        " in order."
    )
    if error:
        prompt += f"\n\nYour last reply was rejected: {error}. Reply again."
    return ClaudeCli.request(
        JUDGE.model, prompt, system=text("judge"), json_schema=JUDGE_SCHEMA, effort=JUDGE.effort
    )


# Games --------------------------------------------------------------------------------

# (role, request, attempt) -> the structured reply, or None if the backend gave none.
Ask = Callable[[str, dict[str, Any], int], Awaitable[object]]


class Invalid(ValueError):
    pass


@dataclass
class Game:
    prompt: str
    mode: Mode
    trial: int
    source: str = ""  # the playtest log entry, for human-clues games
    human_result: str = ""  # solved / failed, for human-clues games
    human_step: int | None = None
    clue_comments: bool = False  # the logged clues have [...] comments
    outcome: Outcome | None = None
    solved_at: int | None = None
    confidence: int | None = None
    turns: list[Turn] = field(default_factory=list)
    invalid: list[dict[str, str]] = field(default_factory=list)
    error: str = ""
    usage: dict[str, Any] = field(default_factory=dict)


def _obj(reply: object) -> dict[str, Any]:
    if not isinstance(reply, dict):
        raise Invalid(f"expected a JSON object, got {reply!r}")
    return reply


def parse_guesses(reply: object, max_guesses: int) -> tuple[list[str], bool]:
    """The guesses, and whether the guesser passed (an empty list)."""
    raw = _obj(reply).get("guesses")
    if not isinstance(raw, list):
        raise Invalid("guesses must be a list")
    guesses: list[str] = []
    for g in raw:
        if not isinstance(g, str):
            raise Invalid("each guess must be a string")
        g = g.strip()
        if g and all(match_key(g) != match_key(x) for x in guesses):
            guesses.append(g)
    if len(guesses) > max_guesses:
        raise Invalid(f"at most {max_guesses} guesses")
    return guesses, not guesses


def parse_verdict(r: dict[str, Any], guesses: Sequence[str]) -> tuple[str, str]:
    verdict, yes_to = r.get("verdict"), r.get("yes_to", "")
    if verdict not in ("yes", "no") or not isinstance(yes_to, str):
        raise Invalid("verdict must be yes or no")
    if verdict == "yes":
        named = [g for g in guesses if match_key(g) == match_key(yes_to)]
        if not named:
            raise Invalid(f"yes_to must be one of the guesses: {', '.join(guesses)}")
        return verdict, named[0]
    return verdict, ""


async def ask_valid(
    ask: Ask,
    role: str,
    build: Callable[[str], dict[str, Any]],
    parse: Callable[[object], Any],
    game: Game,
) -> Any:
    """Ask until the reply parses, at most MAX_ATTEMPTS times. Each retry tells the model
    why its last reply was rejected."""
    error = ""
    for attempt in range(MAX_ATTEMPTS):
        reply = await ask(role, build(error), attempt)
        try:
            return parse(reply)
        except (Invalid, NotationError) as e:
            error = str(e)
            game.invalid.append({"role": role, "attempt": str(attempt), "error": error})
    raise Invalid(f"{role}: no valid reply after {MAX_ATTEMPTS} tries ({error})")


async def guess_turn(ask: Ask, spec: Spec, game: Game) -> None:
    turn = game.turns[-1]
    turn.guesses, turn.passed = await ask_valid(
        ask,
        "guesser",
        lambda _err: guesser_request(spec, game.turns),
        lambda r: parse_guesses(r, spec.max_guesses),
        game,
    )


def parse_judge(reply: object, guesses: Sequence[str]) -> list[bool]:
    correct = _obj(reply).get("correct")
    if not isinstance(correct, list) or not all(isinstance(c, bool) for c in correct):
        raise Invalid("correct must be a list of true/false values")
    if len(correct) != len(guesses):
        raise Invalid(f"give one value per guess ({len(guesses)})")
    return correct


async def check_correct(ask: Ask, game: Game, answers: Sequence[str]) -> bool:
    """Whether the last turn's guesses include the answer: an exact match (ignoring case,
    punctuation, accents, and a leading article) first, then the judge. Marks the turn."""
    turn = game.turns[-1]
    guesses = turn.guesses
    if exact := [g for g in guesses if matches(g, answers)]:
        turn.verdict, turn.correct_by, turn.correct_guess = "correct", "match", exact[0]
    else:
        correct = await ask_valid(
            ask,
            "judge",
            lambda err: judge_request(answers[0], guesses, error=err),
            lambda r: parse_judge(r, guesses),
            game,
        )
        if not any(correct):
            return False
        turn.verdict, turn.correct_by = "correct", "judge"
        turn.correct_guess = guesses[correct.index(True)]
    game.outcome, game.solved_at = "solved", len(game.turns)
    return True


async def play_model_clues(
    ask: Ask, spec: Spec, answer: str, trial: int, game: Game | None = None
) -> Game:
    """A model clue-giver against `ask`'s guesser. Pass `game` to watch it as it's played
    (the interactive human guesser does)."""
    game = game or Game(answer, "model-clues", trial)
    board = Board()

    def first(reply: object) -> tuple[int, str, str, list[str], Board]:
        r = _obj(reply)
        conf, action, plan, lines = r.get("confidence"), r.get("action"), r.get("plan"), r.get("lines")
        if not isinstance(conf, int) or action not in ("clue", "skip"):
            raise Invalid("confidence must be 1-5 and action clue or skip")
        if not isinstance(plan, str) or not isinstance(lines, list):
            raise Invalid("plan must be a string and lines a list")
        trial_board = board.copy()
        std = trial_board.apply_all([str(x) for x in lines]) if action == "clue" else []
        if action == "clue" and not std:
            raise Invalid("place at least one marker, or skip")
        return conf, action, plan, std, trial_board

    try:
        conf, action, plan, lines, board = await ask_valid(
            ask,
            "clue-giver",
            lambda err: clue_giver_request(spec, answer, [], error=err),
            first,
            game,
        )
        game.confidence = conf
        if action == "skip":
            game.outcome = "skipped"
            return game
        game.turns.append(Turn(lines, board.summary(), plan))

        while True:
            await guess_turn(ask, spec, game)
            turn = game.turns[-1]
            if turn.passed:
                game.outcome = "passed"
                return game
            if await check_correct(ask, game, [answer]):
                return game
            if len(game.turns) >= spec.max_rounds:
                game.outcome = "out_of_rounds"
                return game
            guesses = turn.guesses

            def respond(reply: object) -> tuple[str, str, str, str, list[str], Board]:
                r = _obj(reply)
                verdict, yes_to = parse_verdict(r, guesses)
                action, plan, lines = r.get("action"), r.get("plan"), r.get("lines")
                if action not in ("clue", "give_up") or not isinstance(plan, str) or not isinstance(lines, list):
                    raise Invalid("action must be clue or give_up, plan a string, lines a list")
                trial_board = board.copy()
                std = trial_board.apply_all([str(x) for x in lines]) if action == "clue" else []
                return verdict, yes_to, action, plan, std, trial_board

            verdict, yes_to, action, plan, lines, board = await ask_valid(
                ask,
                "clue-giver",
                lambda err: clue_giver_request(spec, answer, game.turns, error=err),
                respond,
                game,
            )
            turn.verdict, turn.yes_to = verdict, yes_to
            if action == "give_up":
                game.outcome = "gave_up"
                return game
            game.turns.append(Turn(lines, board.summary(), plan))
    except Invalid as e:
        game.outcome, game.error = "error", str(e)
        return game


async def play_human_clues(ask: Ask, spec: Spec, human: LogGame, trial: int) -> Game:
    """The logged clues, a step at a time (see LogGame.steps), then `extra_rounds` turns
    with no new markers. The answer is the prompt as it was played."""
    game = Game(
        human.prompt,
        "human-clues",
        trial,
        source=human.source,
        human_result=human.result,
        human_step=human.solved_step,
        clue_comments=any("[" in line for line in human.lines),
    )
    if human.result == "skipped":
        game.outcome = "skipped"
        return game
    board = Board()
    answers = [human.prompt]
    steps = [*human.steps, *([()] * spec.extra_rounds)]
    try:
        for i, step in enumerate(steps, 1):
            lines = board.apply_all(list(step), comments=True)
            game.turns.append(Turn(lines, board.summary()))
            await guess_turn(ask, spec, game)
            turn = game.turns[-1]
            if turn.passed:
                game.outcome = "passed"
                return game
            if await check_correct(ask, game, answers):
                return game
            yes = [g for g in turn.guesses if matches(g, human.yes)]
            turn.verdict, turn.yes_to = ("yes", yes[0]) if yes else ("no", "")
        game.outcome = "out_of_rounds"
    except Invalid as e:
        game.outcome, game.error = "error", str(e)
    return game


# Running a spec -----------------------------------------------------------------------


def _add_usage(u: dict[str, Any], meta: dict[str, Any]) -> None:
    u["calls"] = u.get("calls", 0) + 1
    if isinstance(meta.get("costUsd"), (int, float)):
        u["cost_usd"] = round(u.get("cost_usd", 0.0) + meta["costUsd"], 6)
    if isinstance(meta.get("latencyMs"), int):
        u["latency_s"] = round(u.get("latency_s", 0.0) + meta["latencyMs"] / 1000, 1)
    tokens = u.setdefault("tokens", {})
    for k, v in (meta.get("usage") or {}).items():
        if isinstance(v, int):
            tokens[k] = tokens.get(k, 0) + v


async def run_spec(spec: Spec) -> dict[str, Any]:
    from llmemo import Cache, ClaudeCli, Ledger, OpenRouter, Result, git_code_version

    entries: set[str] = set()

    def used(result: Result) -> None:
        entries.add(result.entry_id)

    cache = Cache(
        CACHE_DIR,
        mode="replay",  # LLMEMO_MODE=record overrides this for one command
        spend_limit=spec.spend_limit_usd,
        ledger=Ledger(ROOT / "llm-spend"),
        code_version=git_code_version(ROOT),
        tags={"run": spec.id},
        on_entry_used=used,
        log_calls=True,
    )
    claude = ClaudeCli()
    openrouter = OpenRouter()
    sem = asyncio.Semaphore(spec.concurrency)

    def asker(usage: dict[str, Any], trial: int) -> Ask:
        async def ask(role: str, request: dict[str, Any], attempt: int) -> object:
            # The judge's verdict depends only on the answer and guesses, so it is shared
            # by every trial.
            variant = None if role == "judge" else f"trial-{trial}"
            backend = openrouter.acall if request.get("backend") == "openrouter" else claude.acall
            result = await cache.acall(
                request, backend, label=role, variant=variant, attempt=attempt
            )
            _add_usage(usage, result.meta)
            return structured(result.reply)

        return ask

    # Human-clues prompts are named as they were played, so they're checked against the
    # logs; model-clues prompts against the deck.
    humans = human_guessed() if spec.mode == "human-clues" else {}
    deck = deck_prompts()
    for p in spec.prompts:
        if spec.mode == "human-clues" and p not in humans:
            raise ValueError(f"{spec.id}: no game with human guessers for {p!r} in playtests/")
        if spec.mode == "model-clues" and p not in deck:
            raise ValueError(f"{spec.id}: {p!r} isn't an active prompt in data/prompts.csv")

    async def one(prompt: str, human: LogGame | None, trial: int) -> Game:
        async with sem:
            usage: dict[str, Any] = {}
            ask = asker(usage, trial)
            if human is None:
                game = await play_model_clues(ask, spec, prompt, trial)
            else:
                game = await play_human_clues(ask, spec, human, trial)
            game.usage = usage
            return game

    # Every logged game of a human-clues prompt is played.
    jobs: list[tuple[str, LogGame | None]] = [
        (p, h) for p in spec.prompts for h in (humans[p] if humans else [None])
    ]
    games = await asyncio.gather(
        *(one(p, h, t) for p, h in jobs for t in range(1, spec.trials + 1))
    )
    return {
        "spec": asdict(spec),
        "games": [asdict(g) for g in games],
        "entries": sorted(entries),
    }


# Reports ------------------------------------------------------------------------------


def summarize(run: dict[str, Any]) -> list[dict[str, Any]]:
    by_prompt: dict[str, list[dict[str, Any]]] = {}
    for g in run["games"]:
        by_prompt.setdefault(g["prompt"], []).append(g)
    rows = []
    for prompt, games in by_prompt.items():
        solved = [g["solved_at"] for g in games if g["outcome"] == "solved"]
        wrong: Counter[str] = Counter()
        for g in games:
            for t in g["turns"]:
                if t["verdict"] != "correct":
                    wrong.update(t["guesses"])
        rows.append(
            {
                "prompt": prompt,
                "human": _human(games[0]),
                "comments": any(g["clue_comments"] for g in games),
                "games": len(games),
                "solved": len(solved),
                "avg_steps": round(statistics.mean(solved), 1) if solved else None,
                "skipped": sum(g["outcome"] == "skipped" for g in games),
                "errors": sum(g["outcome"] == "error" for g in games),
                "common_wrong": [w for w, _ in wrong.most_common(5)],
            }
        )
    return rows


def _human(game: dict[str, Any]) -> str:
    result: str = game["human_result"]
    if result == "solved" and game["human_step"]:
        return f"solved (step {game['human_step']})"
    return result


def agreement(games: Sequence[dict[str, Any]]) -> list[str]:
    """How the model's results compare with the humans' on the same clues: how often it
    solved games humans solved and games they failed, and how often its outcome (solved
    or not) matched theirs. Also without games whose clues have comments, which a model
    reads as words while people saw a marker on a picture."""
    out = []
    for name, subset in (
        ("All games", [g for g in games if g["human_result"] in ("solved", "failed")]),
        ("Without clue comments", [g for g in games if g["human_result"] in ("solved", "failed") and not g["clue_comments"]]),
    ):
        if not subset:
            continue
        hs = [g for g in subset if g["human_result"] == "solved"]
        hf = [g for g in subset if g["human_result"] == "failed"]
        ms = sum(g["outcome"] == "solved" for g in hs)
        mf = sum(g["outcome"] == "solved" for g in hf)
        same = sum((g["outcome"] == "solved") == (g["human_result"] == "solved") for g in subset)
        out.append(
            f"| {name} | {ms}/{len(hs)} | {mf}/{len(hf)} |"
            f" {same}/{len(subset)} ({100 * same / len(subset):.0f}%) |"
        )
    if not out:
        return []
    return [
        "## Agreement with human guessers",
        "",
        "Model games solved, by what the humans did with the same clues.",
        "",
        "| Games | Humans solved: model solved | Humans failed: model solved | Same outcome |",
        "|---|---|---|---|",
        *out,
        "",
    ]


def markdown(run: dict[str, Any]) -> str:
    spec = run["spec"]
    roles = f"guesser {spec['guesser']['model']} (effort {spec['guesser']['effort'] or 'default'})"
    if spec["clue_giver"]:
        cg = spec["clue_giver"]
        roles = f"clue-giver {cg['model']} (effort {cg['effort'] or 'default'}), " + roles
    out = [
        f"# Simulated run: {spec['id']}",
        "",
        "Generated by `tools/simplay.py` from the llmemo cache. Contains answers: guessers"
        " must not read it.",
        "",
        f"- Mode: {spec['mode']} · {roles}",
        f"- Trials: {spec['trials']} · max rounds {spec['max_rounds']} · max guesses"
        f" {spec['max_guesses']} · guesser prompt {spec.get('guesser_prompt', 'guesser')}"
        f" · reference {spec.get('reference', 'tables')}",
        "",
    ]
    human = spec["mode"] == "human-clues"
    if human:
        out += agreement(run["games"])
    out += ["## Summary", ""]
    if human:
        out += [
            "| Prompt | Humans | Clue comments | Model solved | Avg steps | Common wrong guesses |",
            "|---|---|---|---|---|---|",
        ]
    else:
        out += [
            "| Prompt | Solved | Avg steps | Skipped | Errors | Common wrong guesses |",
            "|---|---|---|---|---|---|",
        ]
    for r in summarize(run):
        if human:
            out.append(
                f"| {r['prompt']} | {r['human']} | {'yes' if r['comments'] else ''} |"
                f" {r['solved']}/{r['games']} | {r['avg_steps'] or '–'} |"
                f" {', '.join(r['common_wrong'])} |"
            )
        else:
            out.append(
                f"| {r['prompt']} | {r['solved']}/{r['games']} | {r['avg_steps'] or '–'} |"
                f" {r['skipped']} | {r['errors']} | {', '.join(r['common_wrong'])} |"
            )
    out += ["", "## Usage", "", "| Game | Calls | Cost (USD, API-equivalent) | Model time (s) | Input tokens | Cache-read tokens | Output tokens |", "|---|---|---|---|---|---|---|"]
    for g in run["games"]:
        u, t = g["usage"], g["usage"].get("tokens", {})
        out.append(
            f"| {g['prompt']} #{g['trial']} | {u.get('calls', 0)} | {u.get('cost_usd', 0):.4f} |"
            f" {u.get('latency_s', 0)} | {t.get('inputTokens', 0)} | {t.get('cacheReadTokens', 0)} |"
            f" {t.get('outputTokens', 0)} |"
        )
    out += ["", "## Games"]
    for g in run["games"]:
        result = g["outcome"].replace("_", " ")
        if g["outcome"] == "solved":
            result += f" (step {g['solved_at']})"
        head = f"- Outcome: {result}"
        if g["confidence"] is not None:
            head += f" · Clue-giver confidence: {g['confidence']}/5"
        out += ["", f"### {g['prompt']} (trial {g['trial']})", head]
        if g["source"]:
            out.append(f"- Human clues from: {g['source']}")
        if g["error"]:
            out.append(f"- Error: {g['error']}")
        for i, t in enumerate(g["turns"], 1):
            out += [f"- Step {i}:", "  ```"]
            out += [f"  {line}" for line in t["lines"]] or ["  (no new markers)"]
            out.append("  ```")
            if t["plan"]:
                out.append(f"  Plan: {t['plan']}")
            reply = "pass" if t["passed"] else ", ".join(t["guesses"])
            verdict = {
                "yes": f"Yes: {t['yes_to']}",
                "": "–",
                "correct": "Correct" + (f" (judge: {t['correct_guess']})" if t["correct_by"] == "judge" else ""),
            }.get(t["verdict"], t["verdict"].capitalize())
            out.append(f"  Guesses: {reply} → {verdict}")
        if g["invalid"]:
            out.append(f"- Invalid replies retried: {len(g['invalid'])}")
    return "\n".join(out) + "\n"


def write_run(run: dict[str, Any], runs_dir: Path = RUNS_DIR) -> None:
    runs_dir.mkdir(parents=True, exist_ok=True)
    spec_id = run["spec"]["id"]
    (runs_dir / f"{spec_id}.json").write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n")
    (runs_dir / f"{spec_id}.md").write_text(markdown(run))


# CLI ----------------------------------------------------------------------------------


def cmd_run(spec_ids: Sequence[str]) -> int:
    from llmemo import UsageLimitReached

    for spec_id in spec_ids:
        try:
            run = asyncio.run(run_spec(load_spec(spec_id)))
        except UsageLimitReached as e:
            # Nothing is written for this spec. Calls recorded so far are in the cache,
            # so a rerun after the reset replays them and records only the rest.
            when = e.resets_at.astimezone().strftime("%Y-%m-%d %H:%M %Z") if e.resets_at else "unknown"
            print(f"{spec_id}: stopped, the Claude usage limit was reached ({e})")
            print(f"Limit resets at: {when}. Rerun the same command after that.")
            return 2
        write_run(run)
        print(f"{spec_id}: wrote {RUNS_DIR.relative_to(ROOT)}/{spec_id}.json and .md")
    return 0


def cmd_all() -> int:
    """Replay every spec that has a recorded run. Specs never recorded are listed."""
    specs = sorted(p.stem for p in SPECS_DIR.glob("*.toml"))
    recorded = [s for s in specs if (RUNS_DIR / f"{s}.json").exists()]
    for s in specs:
        if s not in recorded:
            print(f"{s}: not recorded yet, skipped")
    if not recorded:
        print("no recorded runs")
        return 0
    return cmd_run(recorded)


def cmd_preview(spec_id: str, prompt: str) -> int:
    spec = load_spec(spec_id)
    turns = [Turn(["?g A1", "+ C4"], "?g A1 | C4")]
    if spec.clue_giver:
        req = clue_giver_request(spec, prompt, [])
        print("=== clue-giver: first request (system parts are separated by ---) ===")
        print("\n---\n".join(req["system"]))
        print("=== prompt ===")
        print(req["prompt"])
        print("=== schema ===")
        print(json.dumps(req["jsonSchema"], indent=2))
    req = judge_request(prompt, ["Pizza pie", "Pie"])
    print("\n=== judge: system ===")
    print(req["system"])
    print("=== prompt ===")
    print(req["prompt"])
    req = guesser_request(spec, turns)
    print("\n=== guesser: prompt after an example step (system: rules, board, then this) ===")
    print(req["system"][-1])
    print("=== prompt ===")
    print(req["prompt"])
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_run = sub.add_parser("run", help="play the games in one or more specs")
    p_run.add_argument("spec", nargs="+")
    sub.add_parser("all", help="replay every recorded run")
    p_play = sub.add_parser("play", help="guess yourself against the clue-giver model (live)")
    p_play.add_argument("spec")
    p_prev = sub.add_parser("preview", help="print the requests a game starts with")
    p_prev.add_argument("spec")
    p_prev.add_argument("prompt")
    args = parser.parse_args(argv)
    if args.cmd == "run":
        return cmd_run(args.spec)
    if args.cmd == "all":
        return cmd_all()
    if args.cmd == "play":
        from play import cmd_play

        return cmd_play(args.spec)
    return cmd_preview(args.spec, args.prompt)


if __name__ == "__main__":
    sys.exit(main())
