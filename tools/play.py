"""Interactive games: the clue-giver model gives clues, and you guess in the terminal.

    LLMEMO_MODE=record uv run python tools/simplay.py play play

Run through `simplay.py play <spec>`; the spec (a `model-clues` spec, e.g.
`sim-playtests/specs/play.toml`) sets the clue-giver model, round cap, and spend limit.
Each game uses a random unassigned draft prompt from data/prompts.csv that isn't in any
playtest log, so you can't have seen it there. The answer stays hidden until the game
ends. Correct guesses are decided by the judge, as in simulated games.

Each finished game is appended to `playtests/<today>-claude-clues.md` as a `### Pool:`
entry, with a pause wherever you guessed, so later `human-clues` runs can replay your
games to model guessers. While you play, `output/illustrated/play/current.md` shows the
board with icon pictures (open it in VS Code's Markdown preview).

Every call is live (each one includes your guesses), so this needs LLMEMO_MODE=record.
"""

from __future__ import annotations

import asyncio
import csv
import datetime
import os
import random
from collections.abc import Callable
from pathlib import Path
from typing import Any

import illustrate_logs
import playtest_logs
import simplay
from simplay import Game, Spec

LIVE = illustrate_logs.OUT / "play" / "current.md"
VERDICTS = ("keep", "too easy", "too hard", "unclear", "reword")

Input = Callable[[str], str]


def pool_prompts(path: Path = simplay.PROMPTS_CSV) -> list[tuple[str, str]]:
    """Unassigned draft prompts not in any playtest log, as (prompt, band)."""
    played = {g.prompt for g in playtest_logs.load_logs()}
    with path.open(newline="", encoding="utf-8") as f:
        return [
            (r["prompt"], r["difficulty"])
            for r in csv.DictReader(f)
            if not r["card"] and r["status"] == "draft" and r["prompt"] not in played
        ]


def describe(lines: list[str], meanings: dict[str, str]) -> list[str]:
    """Notation lines with the icon's meanings beside them."""
    out = []
    for line in lines:
        codes = [w for w in line.split() if w in meanings]
        out.append(f"  {line:<14} {meanings[codes[0]] if codes else ''}".rstrip())
    return out


def write_live(game: Game, meanings: dict[str, str]) -> None:
    if not illustrate_logs.ICONS.is_dir():
        return
    LIVE.parent.mkdir(parents=True, exist_ok=True)
    markers = illustrate_logs.OUT / "markers"
    markers.mkdir(parents=True, exist_ok=True)
    for name, svg in illustrate_logs.marker_svgs().items():
        (markers / name).write_text(svg)
    steps = "\n\n".join("\n".join(t.lines) for t in game.turns if t.lines)
    text = f"# Current game\n\n```\n{steps}\n```\n"
    h = illustrate_logs.Html("../../player-aid/icons", "../markers", meanings)
    LIVE.write_text(illustrate_logs.illustrate(text, h))


def human_guesser(game: Game, meanings: dict[str, str], read: Input) -> simplay.Ask:
    """An Ask whose guesser is you. Other roles go to `model`."""
    shown = 0
    last_verdict = 0

    async def ask(role: str, request: dict[str, Any], attempt: int) -> object:
        nonlocal shown, last_verdict
        assert role == "guesser"
        # The clue-giver's answer to your last guesses, then the new markers.
        if last_verdict < len(game.turns) - 1:
            prev = game.turns[-2]
            print(f"\nClue-giver: {simplay.feedback(prev)}")
            last_verdict = len(game.turns) - 1
        turn = game.turns[-1]
        print(f"\nStep {len(game.turns)}:")
        print("\n".join(describe(turn.lines, meanings)) or "  (no new markers)")
        if shown < len(game.turns):
            write_live(game, meanings)
            shown = len(game.turns)
        while True:
            text = read('Guesses (comma-separated), "board?", or "pass": ').strip()
            if text.lower() == "board?":
                print(game.turns[-1].board)
                continue
            if text.lower() == "pass":
                return {"guesses": [], "pass": True}
            guesses = [g.strip() for g in text.split(",") if g.strip()]
            most = request["jsonSchema"]["properties"]["guesses"]["maxItems"]
            if len(guesses) > most:
                print(f"At most {most} guesses at a time.")
            elif guesses:
                return {"guesses": guesses, "pass": False}

    return ask


async def play_one(spec: Spec, answer: str, read: Input, model: simplay.Ask) -> Game:
    meanings = illustrate_logs.icon_meanings()
    game = Game(answer, "model-clues", 1)
    you = human_guesser(game, meanings, read)

    async def ask(role: str, request: dict[str, Any], attempt: int) -> object:
        return await (you if role == "guesser" else model)(role, request, attempt)

    return await simplay.play_model_clues(ask, spec, answer, 1, game)


def game_key(answer: str) -> str:
    """The ID that tags a game's cache entries (`game` tag) and appears in its log entry."""
    return f"{datetime.date.today().isoformat()}/{answer}"


def log_game(
    game: Game, band: str, spec: Spec, verdict: str, comment: str, game_id: str = ""
) -> Path:
    today = datetime.date.today().isoformat()
    path = playtest_logs.LOGS / f"{today}-claude-clues.md"
    result: playtest_logs.Result = {
        "solved": "solved",
        "skipped": "skipped",
    }.get(game.outcome or "", "failed")  # type: ignore[assignment]
    guesses = [
        (g, t.verdict == "yes" and g == t.yes_to)
        for t in game.turns
        for g in t.guesses
        if not (t.verdict == "correct" and g == t.correct_guess)
    ]
    assert spec.clue_giver is not None
    extra = [
        f"Band: {band} (draft) · Outcome: {(game.outcome or '').replace('_', ' ')}"
        + (f" · Clue-giver confidence: {game.confidence}/5" if game.confidence else ""),
        "Clue-giver plans: " + " / ".join(t.plan for t in game.turns if t.plan),
    ]
    if game_id:
        extra.append(f"Game ID (the `game` tag on its cache entries): {game_id}")
    if comment:
        extra.append(f"Comments: {comment}")
    entry = playtest_logs.format_entry(
        game.prompt,
        clue_giver=f"Claude ({spec.clue_giver.model})",
        result=result,
        steps=[t.lines for t in game.turns if t.lines] if result != "skipped" else [],
        solved_step=game.solved_at,
        verdict=verdict,
        guesses=guesses,
        extra=extra,
    )
    if not path.exists():
        path.write_text(
            f"# Text playtest {today} (Claude gives clues, interactive)\n\n"
            "- Clue-giver: Claude, via `simplay.py play` · Guesser: human\n"
            "- Prompts: unassigned drafts from the pool\n"
        )
    with path.open("a", encoding="utf-8") as f:
        f.write("\n" + entry)
    playtest_logs.parse_log(path)  # the new entry must read back
    return path


def cmd_play(spec_id: str, read: Input = input) -> int:
    from llmemo import Cache, ClaudeCli, Ledger, UsageLimitReached, git_code_version

    spec = simplay.load_spec(spec_id)
    if spec.mode != "model-clues":
        print(f"{spec_id}: play needs a model-clues spec")
        return 2
    if os.environ.get("LLMEMO_MODE") != "record":
        print("play makes live calls (each one includes your guesses). Run it with")
        print(f"  LLMEMO_MODE=record uv run python tools/simplay.py play {spec_id}")
        return 2
    cache = Cache(
        simplay.CACHE_DIR,
        mode="replay",  # LLMEMO_MODE=record, checked above, makes this record
        spend_limit=spec.spend_limit_usd,
        ledger=Ledger(simplay.ROOT / "llm-spend"),
        code_version=git_code_version(simplay.ROOT),
        tags={"run": f"play-{spec_id}"},
    )
    claude = ClaudeCli()

    game_id = ""

    async def model(role: str, request: dict[str, Any], attempt: int) -> object:
        variant = None if role == "judge" else "play"
        result = await cache.acall(
            request,
            claude.acall,
            label=role,
            variant=variant,
            attempt=attempt,
            tags={"game": game_id},  # metadata only, outside the key
        )
        reply = result.reply
        return reply.get("structured_output") if isinstance(reply, dict) else None

    while True:
        pool = pool_prompts()
        if not pool:
            print("No unplayed draft prompts left in the pool.")
            return 0
        answer, band = random.choice(pool)
        game_id = game_key(answer)
        print("\nNew prompt. The clue-giver is thinking…")
        try:
            game = asyncio.run(play_one(spec, answer, read, model))
        except UsageLimitReached as e:
            when = e.resets_at.astimezone().strftime("%Y-%m-%d %H:%M %Z") if e.resets_at else "unknown"
            print(f"\nStopped: the Claude usage limit was reached. It resets at {when}.")
            print("This game wasn't logged.")
            return 2
        last = game.turns[-1] if game.turns else None
        if game.outcome == "solved" and last is not None:
            print(f"\nCorrect: {last.correct_guess}")
        elif game.outcome == "skipped":
            print("\nThe clue-giver skipped this prompt.")
        else:
            print(f"\nGame over ({(game.outcome or '').replace('_', ' ')}).")
        print(f"The answer was: {answer}  (band: {band})")
        if game.error:
            print(f"Error: {game.error}")
        verdict = ""
        while game.outcome != "skipped":
            verdict = read(f"Verdict ({', '.join(VERDICTS)}; Enter to skip): ").strip().lower()
            if verdict in ("", *VERDICTS):
                break
        comment = read("Comment (Enter to skip): ").strip()
        if game.outcome == "error":
            print("Not logged, because of the error.")
        else:
            path = log_game(game, band, spec, verdict, comment, game_id)
            print(f"Logged to {path.relative_to(simplay.ROOT)}")
        if read("Play another? [y/N]: ").strip().lower() != "y":
            return 0
