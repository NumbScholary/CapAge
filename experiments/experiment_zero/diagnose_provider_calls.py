#!/usr/bin/env python3
"""Run one non-scored call per provider and report only adapter health."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
request = json.dumps({
    "scenario_id": "DIAGNOSTIC",
    "prompt": "Reply with the single word OK.",
    "context": "This is an unscored provider connectivity diagnostic.",
    "tools": [],
    "parameters": {"effort": "medium", "max_output_tokens": 256},
}).encode()

candidates = [
    ("OpenAI", [sys.executable, str(ROOT / "adapters/openai_adapter.py"), "gpt-5.6-terra"]),
    ("Anthropic", [sys.executable, str(ROOT / "adapters/anthropic_adapter.py"), "claude-sonnet-5"]),
]

failed = False
for provider, command in candidates:
    result = subprocess.run(command, input=request, capture_output=True, check=False, timeout=180)
    if result.returncode == 0:
        print(f"{provider}: adapter call succeeded")
    else:
        failed = True
        error = result.stderr.decode("utf-8", errors="replace").strip()
        print(f"{provider}: adapter call failed (exit {result.returncode}): {error}")

if failed:
    raise SystemExit(1)
