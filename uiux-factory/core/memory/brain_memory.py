from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

from pydantic import ValidationError

from core.brain_os.memory_contracts import (
    BrainMemoryKind,
    BrainMemoryRecord,
    DecisionMemoryRecord,
    HypothesisMemoryRecord,
    RationaleMemoryRecord,
)
from core.runtime.run_lock import RunLock, RunLockTimeout


class BrainMemoryError(RuntimeError):
    """Raised when project-scoped Brain memory is unsafe or malformed."""


_KIND_MODELS = {
    BrainMemoryKind.RATIONALE.value: RationaleMemoryRecord,
    BrainMemoryKind.HYPOTHESIS.value: HypothesisMemoryRecord,
    BrainMemoryKind.DECISION.value: DecisionMemoryRecord,
}


class BrainMemoryStore:
    """Bounded project-scoped semantic memory for Brain reasoning contracts.

    Records are advisory historical context only. Recall cannot select flow, change
    authority, satisfy gates, become current-run evidence or approve release.
    """

    schema_version = 1

    def __init__(self, project_root: Path, policy: dict[str, Any] | None = None) -> None:
        self.project_root = Path(project_root).resolve()
        config = dict((policy or {}).get("brain_memory", {}))
        self.enabled = bool(config.get("enabled", True))
        self.max_records = int(config.get("max_records", 500))
        self.max_recall_records = int(
            config.get("max_recall_records", min(50, self.max_records))
        )
        self.lock_timeout_seconds = float(config.get("lock_timeout_seconds", 10.0))
        self.lock_stale_seconds = float(config.get("lock_stale_seconds", 60.0))
        if not 1 <= self.max_records <= 5000:
            raise ValueError("brain_memory.max_records must be between 1 and 5000")
        if not 1 <= self.max_recall_records <= min(500, self.max_records):
            raise ValueError("brain_memory.max_recall_records must be between 1 and min(500, max_records)")
        if not 0.1 <= self.lock_timeout_seconds <= 120:
            raise ValueError("brain_memory.lock_timeout_seconds must be between 0.1 and 120")
        if not 1 <= self.lock_stale_seconds <= 3600:
            raise ValueError("brain_memory.lock_stale_seconds must be between 1 and 3600")
        self.memory_dir = self.project_root / ".uiux-agent-runs" / "memory"
        self.path = self.memory_dir / "brain-memory.json"

    def _assert_safe_path(self) -> None:
        current = self.project_root
        relative = self.path.relative_to(self.project_root)
        for part in relative.parts:
            current = current / part
            if current.exists() and current.is_symlink():
                raise BrainMemoryError(f"brain memory refuses symlink path: {current}")
        try:
            self.path.parent.resolve().relative_to(self.project_root)
        except ValueError as exc:
            raise BrainMemoryError("brain memory path escapes project root") from exc

    def _prepare_memory_dir(self) -> None:
        self._assert_safe_path()
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self._assert_safe_path()

    def _lock(self) -> RunLock:
        self._prepare_memory_dir()
        lock_parent = self.memory_dir / ".runtime"
        if lock_parent.exists() and lock_parent.is_symlink():
            raise BrainMemoryError("brain memory lock directory must not be a symlink")
        lock_parent.mkdir(exist_ok=True)
        if lock_parent.is_symlink():
            raise BrainMemoryError("brain memory lock directory must not be a symlink")
        try:
            lock_parent.resolve().relative_to(self.memory_dir.resolve())
        except ValueError as exc:
            raise BrainMemoryError("brain memory lock directory escapes memory root") from exc
        return RunLock(
            self.memory_dir,
            timeout_seconds=self.lock_timeout_seconds,
            stale_seconds=self.lock_stale_seconds,
            poll_seconds=0.05,
        )

    def _read_payload(self) -> dict[str, Any]:
        if not self.enabled:
            return {"schema_version": self.schema_version, "records": []}
        self._assert_safe_path()
        if not self.path.exists():
            return {"schema_version": self.schema_version, "records": []}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise BrainMemoryError(f"brain memory is unreadable: {exc}") from exc
        if not isinstance(payload, dict):
            raise BrainMemoryError("brain memory root must be an object")
        if set(payload).difference({"schema_version", "records"}):
            raise BrainMemoryError("brain memory contains unknown top-level fields")
        try:
            version = int(payload.get("schema_version", 0))
        except (TypeError, ValueError, OverflowError) as exc:
            raise BrainMemoryError("brain memory schema version is malformed") from exc
        if version != self.schema_version:
            raise BrainMemoryError("brain memory schema version is unsupported")
        if not isinstance(payload.get("records"), list):
            raise BrainMemoryError("brain memory records must be a list")
        return payload

    @staticmethod
    def _parse_record(raw: Any) -> BrainMemoryRecord:
        if not isinstance(raw, dict):
            raise BrainMemoryError("brain memory record must be an object")
        kind = str(raw.get("kind", ""))
        model = _KIND_MODELS.get(kind)
        if model is None:
            raise BrainMemoryError(f"unsupported brain memory kind: {kind or '<missing>'}")
        try:
            return model.model_validate(raw)
        except ValidationError as exc:
            raise BrainMemoryError(f"brain memory record is malformed: {exc}") from exc

    def load(self) -> list[BrainMemoryRecord]:
        payload = self._read_payload()
        return [self._parse_record(raw) for raw in payload["records"][-self.max_records:]]

    def _write(self, records: Iterable[BrainMemoryRecord]) -> None:
        if not self.enabled:
            return
        self._prepare_memory_dir()
        bounded = list(records)[-self.max_records:]
        payload = {
            "schema_version": self.schema_version,
            "records": [record.model_dump(mode="json") for record in bounded],
        }
        encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        fd, temporary = tempfile.mkstemp(prefix=".brain-memory-", suffix=".tmp", dir=str(self.memory_dir))
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(encoded)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def record(self, record: BrainMemoryRecord) -> bool:
        if not self.enabled:
            return False
        expected_scope = str(self.project_root)
        if record.project_scope != expected_scope:
            raise BrainMemoryError(
                "brain memory project_scope must equal the resolved target project root"
            )
        try:
            with self._lock():
                records = [item for item in self.load() if item.id != record.id]
                records.append(record)
                self._write(records)
        except RunLockTimeout as exc:
            raise BrainMemoryError("timed out waiting for brain memory transaction lock") from exc
        except OSError as exc:
            raise BrainMemoryError(f"brain memory transaction failed: {exc}") from exc
        return True

    def recall(
        self,
        *,
        kinds: Iterable[BrainMemoryKind | str] = (),
        tags: Iterable[str] = (),
        source_refs: Iterable[str] = (),
        exclude_run_id: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return bounded advisory projections, never records usable as current evidence."""

        requested_kinds = {
            item.value if isinstance(item, BrainMemoryKind) else str(item).strip()
            for item in kinds
            if (item.value if isinstance(item, BrainMemoryKind) else str(item).strip())
        }
        requested_tags = {str(item).strip() for item in tags if str(item).strip()}
        requested_refs = {str(item).strip() for item in source_refs if str(item).strip()}
        max_items = self.max_recall_records if limit is None else int(limit)
        if not 1 <= max_items <= self.max_recall_records:
            raise ValueError("brain memory recall limit exceeds policy max_recall_records")

        selected: list[BrainMemoryRecord] = []
        for record in reversed(self.load()):
            if exclude_run_id and record.source_run_id == exclude_run_id:
                continue
            if requested_kinds and record.kind.value not in requested_kinds:
                continue
            if requested_tags and not requested_tags.intersection(record.tags):
                continue
            if requested_refs and record.source_ref not in requested_refs:
                continue
            selected.append(record)
            if len(selected) >= max_items:
                break

        return [
            {
                "memory_ref": record.id,
                "kind": record.kind.value,
                "source_run_id": record.source_run_id,
                "source_ref": record.source_ref,
                "evidence_refs": list(record.evidence_refs),
                "tags": list(record.tags),
                "created_at": record.created_at,
                "payload": self._recall_payload(record),
                "advisory_only": True,
                "authority_effect": "none",
                "gate_effect": "none",
                "evidence_effect": "none",
                "current_run_evidence": False,
            }
            for record in selected
        ]

    @staticmethod
    def _recall_payload(record: BrainMemoryRecord) -> dict[str, Any]:
        if isinstance(record, HypothesisMemoryRecord):
            return {"hypothesis": record.hypothesis.model_dump(mode="json")}
        if isinstance(record, DecisionMemoryRecord):
            return {"decision": record.decision.model_dump(mode="json")}
        if isinstance(record, RationaleMemoryRecord):
            return {
                "subject": record.subject,
                "rationale": record.rationale,
                "hypothesis_refs": list(record.hypothesis_refs),
                "decision_refs": list(record.decision_refs),
            }
        raise BrainMemoryError("unsupported brain memory record type")
