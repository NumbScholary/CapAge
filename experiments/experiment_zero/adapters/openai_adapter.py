#!/usr/bin/env python3
"""Provider-neutral stdin/stdout adapter for the OpenAI Responses API."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: openai_adapter.py MODEL")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        fail("OPENAI_API_KEY is not set")

    request = json.load(sys.stdin)
    context = request.get("context", "")
    prompt = request.get("prompt", "")
    body = {
        "model": sys.argv[1],
        "input": [
            {"role": "developer", "content": context},
            {"role": "user", "content": prompt},
        ],
    }
    parameters = request.get("parameters", {})
    if "max_output_tokens" in parameters:
        body["max_output_tokens"] = parameters["max_output_tokens"]

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
        fail(f"OpenAI API HTTP {exc.code}")
    except urllib.error.URLError as exc:
        fail(f"OpenAI API transport error: {exc.reason}")

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
                "cached_input_tokens": usage.get("input_tokens_details", {}).get("cached_tokens"),
            },
            "provider_status": payload.get("status"),
        },
        sys.stdout,
        separators=(",", ":"),
    )


if __name__ == "__main__":
    main()
