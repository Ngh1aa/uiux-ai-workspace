from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Callable, Iterable, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class RunSessionEvent:
    seq: int
    type: str
    run_id: str
    timestamp: str
    stage: str | None
    agent: str | None
    data: dict[str, Any]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RunSessionEvent":
        return cls(
            seq=int(payload["seq"]),
            type=str(payload["type"]),
            run_id=str(payload["run_id"]),
            timestamp=str(payload["timestamp"]),
            stage=str(payload["stage"]) if payload.get("stage") is not None else None,
            agent=str(payload["agent"]) if payload.get("agent") is not None else None,
            data=deepcopy(dict(payload.get("data") or {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "seq": self.seq,
            "type": self.type,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "stage": self.stage,
            "agent": self.agent,
            "data": deepcopy(self.data),
        }


class RunSessionLog:
    """Append-only typed JSONL event record for one Factory run.

    The log is the durable chronology. `run.json` remains a convenient snapshot,
    while replay/projection/fork behavior derives from this record. Writes are
    serialized and sequence numbers are verified contiguous when the log is read.
    """

    def __init__(self, event_path: Path, run_id: str) -> None:
        self.event_path = Path(event_path).resolve()
        self.run_id = run_id
        self.event_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._sequence = self._load_and_validate_sequence()

    def _load_and_validate_sequence(self) -> int:
        if not self.event_path.exists():
            return 0
        expected = 1
        with self.event_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                payload = json.loads(line)
                event = RunSessionEvent.from_dict(payload)
                if event.seq != expected:
                    raise RuntimeError(
                        f"Non-contiguous run event log at {self.event_path}: "
                        f"expected seq {expected}, got {event.seq}."
                    )
                if event.run_id != self.run_id:
                    raise RuntimeError(
                        f"Run event belongs to {event.run_id}, expected {self.run_id}."
                    )
                expected += 1
        return expected - 1

    @property
    def seq(self) -> int:
        return self._sequence

    def append(
        self,
        event_type: str,
        *,
        stage: str | None = None,
        agent: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not event_type.strip():
            raise ValueError("Event type cannot be empty.")
        payload_data = deepcopy(data or {})
        # Validate data can round-trip as ordinary JSON before touching the log.
        json.dumps(payload_data, ensure_ascii=False, allow_nan=False)

        with self._lock:
            next_seq = self._sequence + 1
            event = RunSessionEvent(
                seq=next_seq,
                type=event_type,
                run_id=self.run_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                stage=stage,
                agent=agent,
                data=payload_data,
            )
            encoded = json.dumps(
                event.to_dict(),
                ensure_ascii=False,
                allow_nan=False,
            )
            with self.event_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(encoded + "\n")
                handle.flush()
            self._sequence = next_seq
            return event.to_dict()

    def snapshot(
        self,
        from_seq: int = 1,
        to_seq_inclusive: int | None = None,
    ) -> tuple[RunSessionEvent, ...]:
        if from_seq < 1:
            raise ValueError("from_seq must be >= 1.")
        upper = self.seq if to_seq_inclusive is None else to_seq_inclusive
        if upper < from_seq - 1:
            raise ValueError("Invalid event snapshot range.")

        events: list[RunSessionEvent] = []
        if not self.event_path.exists():
            return ()
        with self.event_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                event = RunSessionEvent.from_dict(json.loads(line))
                if event.seq < from_seq:
                    continue
                if event.seq > upper:
                    break
                events.append(event)
        return tuple(events)

    def event_at(self, seq: int) -> RunSessionEvent:
        if seq < 1 or seq > self.seq:
            raise IndexError(f"Event sequence out of range: {seq}")
        for event in self.snapshot(seq, seq):
            return event
        raise IndexError(f"Event sequence not found: {seq}")

    def replay(self, consumer: Callable[[RunSessionEvent], None]) -> None:
        for event in self.snapshot():
            consumer(event)

    def project(self, initial: T, reducer: Callable[[T, RunSessionEvent], T]) -> T:
        state = initial
        for event in self.snapshot():
            state = reducer(state, event)
        return state

    def project_run_state(self) -> dict[str, Any]:
        def reduce(state: dict[str, Any], event: RunSessionEvent) -> dict[str, Any]:
            if event.type == "run.created":
                state["status"] = "running"
                state["runtime_preset"] = event.data.get("runtime_preset", "standard")
            elif event.type == "stage.started":
                state["active_stage"] = event.stage
            elif event.type == "stage.completed":
                if event.stage and event.stage not in state["completed_stages"]:
                    state["completed_stages"].append(event.stage)
                state["active_stage"] = None
            elif event.type == "artifact.registered":
                name = event.data.get("name")
                path = event.data.get("path")
                if name and path:
                    state["artifacts"][str(name)] = str(path)
            elif event.type == "run.failed":
                state["status"] = "failed"
                state["active_stage"] = None
                if event.data.get("error"):
                    state["errors"].append(str(event.data["error"]))
            elif event.type == "run.completed":
                state["status"] = "completed"
                state["active_stage"] = None
            return state

        return self.project(
            {
                "run_id": self.run_id,
                "status": "created",
                "runtime_preset": "standard",
                "active_stage": None,
                "completed_stages": [],
                "artifacts": {},
                "errors": [],
            },
            reduce,
        )

    def fork(
        self,
        target_path: Path,
        child_run_id: str,
        *,
        boundary: int | None = None,
    ) -> "RunSessionLog":
        cut = self.seq if boundary is None else boundary
        if cut < 0 or cut > self.seq:
            raise ValueError(f"Fork boundary out of range: {cut}")
        target = Path(target_path).resolve()
        if target.exists() and target.stat().st_size:
            raise FileExistsError(f"Fork target already contains events: {target}")

        child = RunSessionLog(target, child_run_id)
        for event in self.snapshot(1, cut):
            data = deepcopy(event.data)
            data["inherited_from"] = {
                "run_id": self.run_id,
                "seq": event.seq,
            }
            child.append(
                event.type,
                stage=event.stage,
                agent=event.agent,
                data=data,
            )
        child.append(
            "session.forked",
            data={
                "source_run_id": self.run_id,
                "source_boundary": cut,
                "inherited_event_count": cut,
            },
        )
        return child
