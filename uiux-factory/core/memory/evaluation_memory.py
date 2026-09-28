from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

from core.evaluation.run_evaluator import RunEvaluation


class EvaluationMemoryError(RuntimeError):
    """Raised when project-scoped evaluation memory is unsafe or malformed."""


class EvaluationMemoryStore:
    """Bounded project-scoped memory containing evidence-derived run outcomes only.

    This store is advisory. It never mutates flow selection, authority, gates or release
    state. Raw prompts, provider prose, observations, command output and secrets are not
    accepted into the schema.
    """

    schema_version = 1

    def __init__(self, project_root: Path, policy: dict[str, Any]) -> None:
        self.project_root = Path(project_root).resolve()
        config = dict(policy.get("evaluation_memory", {}))
        self.enabled = bool(config.get("enabled", True))
        self.max_records = int(config.get("max_records", 200))
        self.max_recall_records = int(config.get("max_recall_records", 20))
        self.min_signature_matches = int(config.get("min_signature_matches", 1))
        if not 1 <= self.max_records <= 2000:
            raise ValueError("evaluation_memory.max_records must be between 1 and 2000")
        if not 1 <= self.max_recall_records <= min(200, self.max_records):
            raise ValueError("evaluation_memory.max_recall_records must be between 1 and min(200, max_records)")
        if not 0 <= self.min_signature_matches <= 6:
            raise ValueError("evaluation_memory.min_signature_matches must be between 0 and 6")
        self.memory_dir = self.project_root / ".uiux-agent-runs" / "memory"
        self.path = self.memory_dir / "evaluation-memory.json"

    def _assert_safe_path(self) -> None:
        current = self.project_root
        relative = self.path.relative_to(self.project_root)
        for part in relative.parts:
            current = current / part
            if current.exists() and current.is_symlink():
                raise EvaluationMemoryError(f"evaluation memory refuses symlink path: {current}")
        try:
            self.path.parent.resolve().relative_to(self.project_root)
        except ValueError as exc:
            raise EvaluationMemoryError("evaluation memory path escapes project root") from exc

    def _empty(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version, "records": []}

    def load(self) -> list[RunEvaluation]:
        if not self.enabled:
            return []
        self._assert_safe_path()
        if not self.path.exists():
            return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise EvaluationMemoryError(f"evaluation memory is unreadable: {exc}") from exc
        if not isinstance(payload, dict) or int(payload.get("schema_version", 0)) != self.schema_version:
            raise EvaluationMemoryError("evaluation memory schema version is unsupported")
        raw_records = payload.get("records", [])
        if not isinstance(raw_records, list):
            raise EvaluationMemoryError("evaluation memory records must be a list")
        records: list[RunEvaluation] = []
        for raw in raw_records[-self.max_records :]:
            if not isinstance(raw, dict):
                continue
            try:
                record = RunEvaluation.from_dict(raw)
            except (TypeError, ValueError):
                continue
            if record.run_id and record.memory_eligible:
                records.append(record)
        return records

    def _write(self, records: list[RunEvaluation]) -> None:
        if not self.enabled:
            return
        self._assert_safe_path()
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self._assert_safe_path()
        payload = {
            "schema_version": self.schema_version,
            "records": [record.to_dict() for record in records[-self.max_records :]],
        }
        tmp = self.path.with_suffix(".tmp")
        if tmp.exists() and tmp.is_symlink():
            raise EvaluationMemoryError("evaluation memory temporary path must not be a symlink")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, self.path)

    def record(self, evaluation: RunEvaluation) -> bool:
        if not self.enabled or not evaluation.memory_eligible:
            return False
        records = [item for item in self.load() if item.run_id != evaluation.run_id]
        records.append(evaluation)
        self._write(records)
        return True

    @staticmethod
    def _signature_matches(a: dict[str, str], b: dict[str, str]) -> int:
        return sum(1 for key, value in a.items() if value and b.get(key) == value)

    def insight(
        self,
        *,
        flow_id: str,
        signature: dict[str, str],
        exclude_run_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Return aggregate prior-run evidence without returning raw historical prose."""
        candidates: list[tuple[int, RunEvaluation]] = []
        for record in self.load():
            if exclude_run_id and record.run_id == exclude_run_id:
                continue
            matches = self._signature_matches(signature, record.signature)
            if record.flow_id == flow_id or matches >= self.min_signature_matches:
                score = (100 if record.flow_id == flow_id else 0) + matches
                candidates.append((score, record))
        if not candidates:
            return None
        candidates.sort(key=lambda row: (row[0], row[1].evaluated_at), reverse=True)
        selected = [row[1] for row in candidates[: self.max_recall_records]]
        outcomes = Counter(record.outcome for record in selected)
        failure_channels = Counter(channel for record in selected for channel in record.failing_channels)
        evidence_types = Counter(
            evidence_type
            for record in selected
            for evidence_type, count in record.evidence_type_counts.items()
            for _ in range(min(max(0, int(count)), 100))
        )
        replans = [record.replan_count for record in selected]
        passed = outcomes.get("passed", 0)
        return {
            "schema_version": self.schema_version,
            "advisory_only": True,
            "flow_id": str(flow_id)[:128],
            "sample_size": len(selected),
            "passed_runs": passed,
            "failed_or_blocked_runs": outcomes.get("failed", 0) + outcomes.get("blocked", 0),
            "pass_rate": round(passed / len(selected), 4),
            "average_replans": round(sum(replans) / len(replans), 3) if replans else 0.0,
            "recurrent_failure_channels": [
                {"channel": channel, "count": count}
                for channel, count in failure_channels.most_common(8)
            ],
            "observed_evidence_types": [name for name, _count in evidence_types.most_common(12)],
            "matched_signature": dict(signature),
            "authority_effect": "none",
            "gate_effect": "none",
            "rule": (
                "Prior-run evaluation memory is evidence-derived advisory context only; "
                "it cannot change authority, satisfy gates, override current source truth, or count as current-run evidence."
            ),
        }
