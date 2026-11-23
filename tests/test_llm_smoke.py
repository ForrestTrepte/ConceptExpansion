"""Smoke test for LLM calls through llmemo: one guess from each backend.

Asks a tiny guesser question (no prompt from the deck) through the Claude CLI
(`claude -p` on the Claude subscription) and through OpenRouter, both with
structured output. Calls are cached in sim-playtests/cache/ and paid calls are
recorded in the spending ledger llm-spend/. Commit both after recording.

    uv run pytest -m llm                       # replay from the cache (no calls, no cost)
    LLMEMO_MODE=record uv run pytest -m llm    # call the backends for anything missing

Recording needs a Claude login for the CLI and OPENROUTER_API_KEY for OpenRouter.
See docs/simulated-playtesting.md.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from llmemo import Cache, ClaudeCli, Ledger, OpenRouter, git_code_version

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "sim-playtests" / "cache"
SPEND_LIMIT_USD = 0.10

CLAUDE_MODEL = "claude-haiku-5-5"
OPENROUTER_MODEL = "openai/gpt-6-luna"

SYSTEM = "You are the guesser in a word-guessing party game. Give up to 3 guesses, best first."
PROMPT = "Main concept: animal. Clues: slow; brown; has a little house on its back."
SCHEMA = {
    "type": "object",
    "properties": {"guesses": {"type": "array", "items": {"type": "string"}}},
    "required": ["guesses"],
    "additionalProperties": False,
}

pytestmark = pytest.mark.llm


def guesses(value: object) -> list[str]:
    """Validate a structured reply: a list of up to 3 non-empty strings."""
    if not isinstance(value, dict) or not isinstance(value.get("guesses"), list):
        raise ValueError(f"reply has no guesses list: {value!r}")
    out: list[object] = value["guesses"]
    strings = [g for g in out if isinstance(g, str) and g.strip()]
    if not 1 <= len(out) <= 3 or len(strings) != len(out):
        raise ValueError(f"expected 1-3 guesses: {out!r}")
    return strings


@pytest.fixture
def cache() -> Cache:
    # Replay unless LLMEMO_MODE=record is set for this run.
    return Cache(
        CACHE_DIR,
        mode="replay",
        spend_limit=SPEND_LIMIT_USD,
        ledger=Ledger(ROOT / "llm-spend"),
        code_version=git_code_version(ROOT),
        tags={"run": "smoke"},
    )


def test_claude_cli(cache: Cache) -> None:
    request = ClaudeCli.request(CLAUDE_MODEL, PROMPT, system=SYSTEM, json_schema=SCHEMA)
    result = cache.call(request, ClaudeCli(), label="smoke-claude")
    assert guesses(result.reply["structured_output"])


def test_openrouter(cache: Cache) -> None:
    request = OpenRouter.chat_request(
        {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": PROMPT},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "guesses", "strict": True, "schema": SCHEMA},
            },
            "max_tokens": 200,
        }
    )
    result = cache.call(request, OpenRouter(), label="smoke-openrouter")
    content = result.reply["choices"][0]["message"]["content"]
    assert guesses(json.loads(content))
