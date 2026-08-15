"""Controlled tools available to CapAge."""

from typing import Any


def echo(arguments: dict[str, Any]) -> dict[str, Any]:
    """Return the supplied arguments without external side effects."""

    return {
        "success": True,
        "tool": "echo",
        "result": arguments,
    }


TOOLS = {
    "echo": echo,
}
