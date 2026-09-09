from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


class RunEventBus:
    """Durable JSONL event stream for future FastAPI/SSE + Bolt.diy UI."""

    def __init__(self, event_path: Path, run_id: str) -> None:
        self.event_path = Path(event_path)
        self.run_id = run_id
        self.event_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._sequence = self._load_sequence()

    def _load_sequence(self) -> int:
        if not self.event_path.exists():
            return 0
        try:
            with self.event_path.open("r", encoding="utf-8") as handle:
                return sum(1 for line in handle if line.strip())
        except OSError:
            return 0

    def emit(
        self,
        event_type: str,
        *,
        stage: str | None = None,
        agent: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            self._sequence += 1
            event = {
                "seq": self._sequence,
                "type": event_type,
                "run_id": self.run_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "stage": stage,
                "agent": agent,
                "data": data or {},
            }

            with self.event_path.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(event, ensure_ascii=False) + "\n"
                )

            return event
