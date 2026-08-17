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


_UNSUPPORTED_SCHEMA_CONSTRAINTS = {
    "minimum": "Must be at least {value}.",
    "maximum": "Must be at most {value}.",
    "exclusiveMinimum": "Must be greater than {value}.",
    "exclusiveMaximum": "Must be less than {value}.",
    "multipleOf": "Must be a multiple of {value}.",
    "minLength": "Must contain at least {value} characters.",
    "maxLength": "Must contain at most {value} characters.",
    "minItems": "Must contain at least {value} items.",
    "maxItems": "Must contain at most {value} items.",
    "uniqueItems": "Items must be unique.",
    "minProperties": "Must contain at least {value} properties.",
    "maxProperties": "Must contain at most {value} properties.",
}


def _anthropic_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Return the strict-tool subset Anthropic accepts without losing intent."""

    transformed: dict[str, Any] = {}
    constraint_notes: list[str] = []
    for key, value in schema.items():
        template = _UNSUPPORTED_SCHEMA_CONSTRAINTS.get(key)
        if template is not None:
            if key == "uniqueItems":
                if value:
                    constraint_notes.append(template)
            else:
                constraint_notes.append(template.format(value=value))
            continue
        if isinstance(value, dict):
            transformed[key] = _anthropic_schema(value)
        elif isinstance(value, list):
            transformed[key] = [
                _anthropic_schema(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            transformed[key] = value

    if constraint_notes:
        description = str(transformed.get("description", "")).strip()
        transformed["description"] = " ".join(
            part for part in [description, *constraint_notes] if part
        )
    return transformed


def _anthropic_request_body(body: dict[str, Any]) -> dict[str, Any]:
    """Transform strict tool schemas while leaving the caller's body untouched."""

    transformed = dict(body)
    tools = body.get("tools")
    if not isinstance(tools, list):
        return transformed

    transformed_tools: list[Any] = []
    for tool in tools:
        if not isinstance(tool, dict):
            transformed_tools.append(tool)
            continue
        transformed_tool = dict(tool)
        input_schema = tool.get("input_schema")
        if isinstance(input_schema, dict):
            transformed_tool["input_schema"] = _anthropic_schema(input_schema)
        transformed_tools.append(transformed_tool)
    transformed["tools"] = transformed_tools
    return transformed


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
        provider_body = _anthropic_request_body(body)
        request = urllib.request.Request(
            f"https://api.anthropic.com{path}",
            data=json.dumps(provider_body, separators=(",", ":")).encode("utf-8"),
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
