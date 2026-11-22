#!/usr/bin/env python3
"""Run every check and rebuild every generated file. Never makes live LLM calls.

    uv run python tools/run_all.py

Steps: mypy, pytest (LLM calls replay from the cache), the player aid, the prompt
check, and the card PDF. Each step runs even if an earlier one failed, except that the
PDF is skipped when the prompt check fails. Exits nonzero if any step failed.
`uv run` syncs the environment first, so there is no separate setup step.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

STEPS: list[tuple[str, list[str]]] = [
    ("mypy", [PY, "-m", "mypy"]),
    ("pytest", [PY, "-m", "pytest", "-q"]),
    ("player aid", [PY, "tools/player_aid.py"]),
    ("prompt check", [PY, "tools/cards.py", "check"]),
    ("card PDF", [PY, "tools/cards.py", "pdf"]),
]


def main() -> int:
    env = dict(os.environ)
    if env.get("LLMEMO_MODE", "replay") != "replay":
        print(f"note: ignoring LLMEMO_MODE={env['LLMEMO_MODE']}; run_all only replays")
    env["LLMEMO_MODE"] = "replay"

    results: list[tuple[str, str]] = []
    for name, cmd in STEPS:
        if name == "card PDF" and ("prompt check", "FAILED") in results:
            results.append((name, "skipped"))
            continue
        print(f"\n=== {name} ===", flush=True)
        code = subprocess.run(cmd, cwd=ROOT, env=env).returncode
        results.append((name, "ok" if code == 0 else "FAILED"))

    print("\n=== summary ===")
    for name, outcome in results:
        print(f"{outcome:>8}  {name}")
    return 1 if any(outcome != "ok" for _, outcome in results) else 0


if __name__ == "__main__":
    sys.exit(main())
