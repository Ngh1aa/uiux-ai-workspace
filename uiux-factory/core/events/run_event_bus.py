from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, TypeVar

from core.events.run_session_log import RunSessionEvent, RunSessionLog


T = TypeVar("T")


class RunEventBus:
    """Durable append-only event stream for one Factory run.

    This remains the small API used by orchestration code, while RunSessionLog
    owns validation, replay, projection and fork semantics.
    """

    def __init__(self, event_path: Path, run_id: str) -> None:
        self.log = RunSessionLog(event_path=event_path, run_id=run_id)
        self.event_path = self.log.event_path
        self.run_id = run_id

    @property
    def seq(self) -> int:
        return self.log.seq

    def emit(
        self,
        event_type: str,
        *,
        stage: str | None = None,
        agent: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.log.append(
            event_type,
            stage=stage,
            agent=agent,
            data=data,
        )

    def snapshot(
        self,
        from_seq: int = 1,
        to_seq_inclusive: int | None = None,
    ) -> tuple[RunSessionEvent, ...]:
        return self.log.snapshot(from_seq, to_seq_inclusive)

    def replay(self, consumer: Callable[[RunSessionEvent], None]) -> None:
        self.log.replay(consumer)

    def project(self, initial: T, reducer: Callable[[T, RunSessionEvent], T]) -> T:
        return self.log.project(initial, reducer)

    def project_run_state(self) -> dict[str, Any]:
        return self.log.project_run_state()
