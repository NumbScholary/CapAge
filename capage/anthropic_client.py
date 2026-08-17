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
            raise AnthropicAPIError(self._http_error_message(exc)) from exc
        except urllib.error.URLError as exc:
            raise AnthropicAPIError(
                f"Anthropic API transport failure: {exc.reason}"
            ) from exc
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise AnthropicAPIError("Anthropic API returned invalid JSON") from exc

        if not isinstance(payload, dict):
            raise AnthropicAPIError("Anthropic API returned a non-object payload")
        return payload

    def _http_error_message(self, exc: urllib.error.HTTPError) -> str:
        """Extract bounded provider diagnostics without exposing credentials."""

        error_type = ""
        error_message = ""
        request_id = ""
        try:
            raw = exc.read(4096).decode("utf-8", errors="replace")
            payload = json.loads(raw)
            if isinstance(payload, dict):
                error = payload.get("error")
                if isinstance(error, dict):
                    error_type = str(error.get("type", "")).strip()
                    error_message = str(error.get("message", "")).strip()
                request_id = str(payload.get("request_id", "")).strip()
        except (AttributeError, json.JSONDecodeError, OSError):
            pass
        if not request_id and exc.headers is not None:
            request_id = str(exc.headers.get("request-id", "")).strip()

        pieces = [f"Anthropic API returned HTTP {exc.code}"]
        if error_type:
            pieces.append(error_type[:120])
        if error_message:
            pieces.append(error_message[:1000])
        if request_id:
            pieces.append(f"request_id={request_id[:160]}")
        sanitized = ": ".join(pieces)
        return sanitized.replace(self._api_key, "[redacted]")
