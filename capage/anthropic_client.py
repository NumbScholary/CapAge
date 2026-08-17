"""Minimal Anthropic Messages API client for the economic sandbox runner.

The client deliberately has no retry loop.  A transport failure can leave the
host uncertain about whether a request was processed, so a paid sandbox run
must stop instead of risking a duplicate model charge or duplicate action.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any


class AnthropicAPIError(RuntimeError):
    """Raised when a request cannot be completed or validated."""


class AnthropicMessagesClient:
    """Small dependency-free client for token counting and Messages calls."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        timeout_seconds: int = 180,
        urlopen: Callable[..., Any] | None = None,
    ) -> None:
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not self._api_key:
            raise AnthropicAPIError("ANTHROPIC_API_KEY is not set")
        self._timeout_seconds = timeout_seconds
        self._urlopen = urlopen or urllib.request.urlopen

    def count_tokens(self, request_body: dict[str, Any]) -> int:
        """Return Anthropic's preflight count for the complete model input."""

        count_body = {
            key: value
            for key, value in request_body.items()
            if key not in {"max_tokens"}
        }
        payload = self._post("/v1/messages/count_tokens", count_body)
        input_tokens = payload.get("input_tokens")
        if isinstance(input_tokens, bool) or not isinstance(input_tokens, int):
            raise AnthropicAPIError("token-count response omitted input_tokens")
        if input_tokens < 0:
            raise AnthropicAPIError("token-count response contained a negative count")
        return input_tokens

    def create_message(self, request_body: dict[str, Any]) -> dict[str, Any]:
        """Create exactly one paid Messages API response."""

        return self._post("/v1/messages", request_body)

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            f"https://api.anthropic.com{path}",
            data=json.dumps(body, separators=(",", ":")).encode("utf-8"),
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            method="POST",
        )
        try:
            with self._urlopen(request, timeout=self._timeout_seconds) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as exc:
            raise AnthropicAPIError(f"Anthropic API returned HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise AnthropicAPIError(
                f"Anthropic API transport failure: {exc.reason}"
            ) from exc
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AnthropicAPIError("Anthropic API returned invalid JSON") from exc

        if not isinstance(payload, dict):
            raise AnthropicAPIError("Anthropic API returned a non-object payload")
        return payload
