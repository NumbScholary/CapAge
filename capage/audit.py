"""Append-only audit logging for CapAge."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditLog:
    """Records CapAge events as append-only JSON lines."""

    def __init__(self, path: str = "data/audit.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event_type: str, data: dict[str, Any]) -> None:
        """Append one event to the audit log."""

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "data": data,
        }

        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event) + "\n")
