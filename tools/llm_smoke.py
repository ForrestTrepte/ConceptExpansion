#!/usr/bin/env python3
"""Smoke test for LLM calls through llmemo: one guess from each backend.

Asks a tiny guesser question (no prompt from the deck) through the Claude CLI
(`claude -p` on the Claude subscription) and through OpenRouter, both with
structured output. Calls are cached in sim-playtests/cache/ and paid calls are
recorded in the spending ledger llm-spend/. Commit both after recording.

    uv run python tools/llm_smoke.py           # replay from the cache (no calls, no cost)
    uv run python tools/llm_smoke.py --record  # call the backends for anything missing

Recording needs a Claude login for the CLI and OPENROUTER_API_KEY for OpenRouter.
See docs/simulated-playtesting.md.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

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


def guesses(value: object) -> list[str]:
    """Validate a structured reply: a list of up to 3 non-empty strings."""
    if not isinstance(value, dict) or not isinstance(value.get("guesses"), list):
        raise ValueError(f"reply has no guesses list: {value!r}")
    out: list[object] = value["guesses"]
    strings = [g for g in out if isinstance(g, str) and g.strip()]
    if not 1 <= len(out) <= 3 or len(strings) != len(out):
        raise ValueError(f"expected 1-3 guesses: {out!r}")
    return strings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--record", action="store_true", help="call backends on a cache miss")
    args = parser.parse_args()

    cache = Cache(
        CACHE_DIR,
        mode="record" if args.record else "replay",
        spend_limit=SPEND_LIMIT_USD,
        ledger=Ledger(ROOT / "llm-spend"),
        code_version=git_code_version(ROOT),
        tags={"run": "smoke"},
    )

    claude_request = ClaudeCli.request(CLAUDE_MODEL, PROMPT, system=SYSTEM, json_schema=SCHEMA)
    result = cache.call(claude_request, ClaudeCli(), label="smoke-claude")
    print(f"Claude CLI ({CLAUDE_MODEL}):", guesses(result.reply["structured_output"]))
    print("  cached:", result.cached, " served by:", result.meta.get("servedModel"))

    openrouter_request = OpenRouter.chat_request(
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
    result = cache.call(openrouter_request, OpenRouter(), label="smoke-openrouter")
    content = result.reply["choices"][0]["message"]["content"]
    print(f"OpenRouter ({OPENROUTER_MODEL}):", guesses(json.loads(content)))
    print("  cached:", result.cached, " served by:", result.meta.get("servedModel"))

    total = cache.stats.total
    print(
        f"Spent ${total.uncached_cost_usd:.6f} this run; "
        f"replayed calls originally cost ${total.cached_cost_usd:.6f}"
    )


if __name__ == "__main__":
    main()
