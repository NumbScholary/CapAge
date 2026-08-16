#!/usr/bin/env python3
"""Provider-neutral stdin/stdout adapter for the OpenAI Responses API."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request


def fail(message: str, exit_code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(exit_code)


def safe_error_label(value: object) -> str:
    """Return a log-safe provider error label without account or request data."""
    if not isinstance(value, str):
        return "unknown"
    cleaned = re.sub(r"[^A-Za-z0-9_.-]", "_", value)
    return cleaned[:80] or "unknown"


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: openai_adapter.py MODEL")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        fail("OPENAI_API_KEY is not set")

    request = json.load(sys.stdin)
    parameters = request.get("parameters", {})
    body = {
        "model": sys.argv[1],
        "input": [
            {"role": "developer", "content": request.get("context", "")},
            {"role": "user", "content": request.get("prompt", "")},
        ],
        "reasoning": {"effort": parameters.get("effort", "medium")},
        "max_output_tokens": parameters.get("max_output_tokens", 4096),
    }

    http_request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(http_request, timeout=150) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        error_code = "unknown"
        error_type = "unknown"
        try:
            error_payload = json.loads(exc.read().decode("utf-8", errors="replace"))
            error = error_payload.get("error", {})
            error_code = safe_error_label(error.get("code"))
            error_type = safe_error_label(error.get("type"))
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass
        retryable = exc.code in (408, 409, 429) or exc.code >= 500
        fail(
            f"OpenAI API HTTP {exc.code} code={error_code} type={error_type}",
            75 if retryable else 1,
        )
    except urllib.error.URLError as exc:
        fail(f"OpenAI API transport error: {exc.reason}", 75)

    text_parts = []
    for item in payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text_parts.append(content.get("text", ""))

    usage = payload.get("usage", {})
    json.dump(
        {
            "output": "".join(text_parts),
            "usage": {
                "input_tokens": usage.get("input_tokens"),
                "output_tokens": usage.get("output_tokens"),
                "reasoning_tokens": usage.get("output_tokens_details", {}).get("reasoning_tokens"),
                "cached_input_tokens": usage.get("input_tokens_details", {}).get("cached_tokens"),
            },
            "provider_status": payload.get("status"),
        },
        sys.stdout,
        separators=(",", ":"),
    )


if __name__ == "__main__":
    main()
