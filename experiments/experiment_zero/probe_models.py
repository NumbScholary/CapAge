#!/usr/bin/env python3
"""Verify that the preregistered model aliases are available without inference."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


def model_ids(url: str, headers: dict[str, str]) -> set[str]:
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"model availability probe failed with HTTP {exc.code}") from exc
    return {item["id"] for item in payload.get("data", []) if isinstance(item, dict) and "id" in item}


openai_key = os.environ["OPENAI_API_KEY"]
anthropic_key = os.environ["ANTHROPIC_API_KEY"]

openai_models = model_ids(
    "https://api.openai.com/v1/models",
    {"Authorization": f"Bearer {openai_key}"},
)
anthropic_models = model_ids(
    "https://api.anthropic.com/v1/models",
    {"x-api-key": anthropic_key, "anthropic-version": "2023-06-01"},
)

required = {
    "OpenAI": ("gpt-5.6-terra", openai_models),
    "Anthropic": ("claude-sonnet-5", anthropic_models),
}
missing = [f"{provider} model {model}" for provider, (model, available) in required.items() if model not in available]
if missing:
    raise SystemExit("unavailable candidate: " + ", ".join(missing))

print("Both preregistered candidate model aliases are available.")
