"""Structured data models used by CapAge."""

from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass(frozen=True)
class ProposedAction:
    """An action proposed by the strategic agent.

    A proposal is an expression of intent only.
    Creating one does not authorize or execute the action.
    """

    action_type: str
    tool_name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    action_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )
