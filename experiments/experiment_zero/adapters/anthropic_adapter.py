#!/usr/bin/env python3
"""Provider-neutral stdin/stdout adapter for the Anthropic Messages API."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def fail(message: str, exit_code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(exit_code)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: anthropic_adapter.py MODEL")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        fail("ANTHROPIC_API_KEY is not set")

    request = json.load(sys.stdin)
    parameters = request.get("parameters", {})
    body = {
        "model": sys.argv[1],
        "max_tokens": parameters.get("max_output_tokens", 4096),
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": parameters.get("effort", "medium")},
        "system": request.get("context", ""),
        "messages": [{"role": "user", "content": request.get("prompt", "")}],
    }

    http_request = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(http_request, timeout=150) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        retryable = exc.code in (408, 409, 429) or exc.code >= 500
        fail(f"Anthropic API HTTP {exc.code}", 75 if retryable else 1)
    except urllib.error.URLError as exc:
        fail(f"Anthropic API transport error: {exc.reason}", 75)

    output = "".join(
        block.get("text", "")
        for block in payload.get("content", [])
        if block.get("type") == "text"
    )
    usage = payload.get("usage", {})
    json.dump(
        {
            "output": output,
            "usage": {
                "input_tokens": usage.get("input_tokens"),
                "output_tokens": usage.get("output_tokens"),
                "cache_creation_input_tokens": usage.get("cache_creation_input_tokens"),
                "cache_read_input_tokens": usage.get("cache_read_input_tokens"),
            },
            "provider_status": payload.get("stop_reason"),
        },
        sys.stdout,
        separators=(",", ":"),
    )


if __name__ == "__main__":
    main()
