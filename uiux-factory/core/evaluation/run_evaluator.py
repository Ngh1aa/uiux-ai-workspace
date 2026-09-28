from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit

from core.runtime.flow_os.evidence import EvidenceRecord, effective_evidence


SIGNATURE_KEYS = (
    "intent",
    "website_type",
    "business_domain",
    "product_archetype",
    "change_surface",
    "validation_lane",
)
TERMINAL_STATES = frozenset({"COMPLETED", "FAILED", "BLOCKED"})


def _bounded(value: Any, limit: int = 96) -> str:
    return str(value or "").strip()[:limit]


def _bounded_int(value: Any, upper: int = 10000) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return 0
    return min(max(0, parsed), upper)


def _route_path(raw: Any) -> str:
    text = _bounded(raw, 512)
    if not text:
        return ""
    parsed = urlsplit(text)
    if parsed.scheme or parsed.netloc:
        return (parsed.path or "/")[:128]
    return text.split("?", 1)[0].split("#", 1)[0][:128]


@dataclass(frozen=True)
class RunEvaluation:
    schema_version: int
    run_id: str
    flow_id: str
    flow_revision: int
    managed_state: str
    outcome: str
    evaluated_at: str
    signature: dict[str, str] = field(default_factory=dict)
    completed_stage_count: int = 0
    stage_count: int = 0
    replan_count: int = 0
    effective_evidence_count: int = 0
    status_counts: dict[str, int] = field(default_factory=dict)
    evidence_type_counts: dict[str, int] = field(default_factory=dict)
    passing_evidence_types: list[str] = field(default_factory=list)
    failing_channels: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    memory_eligible: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RunEvaluation":
        return cls(
            schema_version=_bounded_int(payload.get("schema_version", 1), 100),
            run_id=_bounded(payload.get("run_id"), 128),
            flow_id=_bounded(payload.get("flow_id"), 128),
            flow_revision=_bounded_int(payload.get("flow_revision", 0), 10000),
            managed_state=_bounded(payload.get("managed_state"), 32),
            outcome=_bounded(payload.get("outcome"), 32),
            evaluated_at=_bounded(payload.get("evaluated_at"), 64),
            signature={
                _bounded(key, 64): _bounded(value, 128)
                for key, value in dict(payload.get("signature", {})).items()
                if _bounded(key, 64) and _bounded(value, 128)
            },
            completed_stage_count=_bounded_int(payload.get("completed_stage_count", 0)),
            stage_count=_bounded_int(payload.get("stage_count", 0)),
            replan_count=_bounded_int(payload.get("replan_count", 0)),
            effective_evidence_count=_bounded_int(payload.get("effective_evidence_count", 0), 100000),
            status_counts={
                _bounded(key, 32): _bounded_int(value, 100000)
                for key, value in dict(payload.get("status_counts", {})).items()
            },
            evidence_type_counts={
                _bounded(key, 64): _bounded_int(value, 100000)
                for key, value in dict(payload.get("evidence_type_counts", {})).items()
            },
            passing_evidence_types=sorted(
                {_bounded(item, 64) for item in payload.get("passing_evidence_types", []) if _bounded(item, 64)}
            ),
            failing_channels=sorted(
                {_bounded(item, 256) for item in payload.get("failing_channels", []) if _bounded(item, 256)}
            ),
            reasons=[_bounded(item, 256) for item in payload.get("reasons", []) if _bounded(item, 256)][:16],
            memory_eligible=bool(payload.get("memory_eligible", False)),
        )


class RunEvaluator:
    """Evaluate one managed Flow OS run from trusted runtime evidence only.

    Provider summaries, provider evidence claims, prompts and arbitrary model prose never
    participate in the outcome. The record intentionally contains only bounded metadata
    suitable for project-scoped learning memory.
    """

    schema_version = 1

    @staticmethod
    def signature(task_context: dict[str, Any]) -> dict[str, str]:
        result: dict[str, str] = {}
        for key in SIGNATURE_KEYS:
            value = task_context.get(key)
            if isinstance(value, (str, int, float, bool)):
                text = _bounded(value, 128)
                if text and text.lower() not in {"unknown", "unspecified", "none"}:
                    result[key] = text
        return result

    @staticmethod
    def collect_evidence(managed: Any, harness: Any) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for run_ids in dict(getattr(managed, "stage_runs", {})).values():
            for run_id in list(run_ids):
                try:
                    state = harness.resume(str(run_id))
                except (FileNotFoundError, TypeError, ValueError):
                    continue
                records.extend(list(state.context.get("evidence_records", [])))
        try:
            manager_state = harness.resume(str(managed.manager_run_id))
        except (FileNotFoundError, TypeError, ValueError):
            manager_state = None
        if manager_state is not None:
            records.extend(list(manager_state.context.get("release_evidence", [])))
        return records

    @staticmethod
    def failure_channel(record: EvidenceRecord) -> str:
        detail = ""
        if record.type == "validator_result":
            detail = _bounded(record.data.get("name"), 96)
        elif record.type == "command_result":
            argv = record.data.get("argv", [])
            if isinstance(argv, list) and argv:
                detail = _bounded(argv[0], 64)
        elif record.type == "browser_render":
            detail = _route_path(record.data.get("route") or record.data.get("url"))
        elif record.type == "deployment_result":
            detail = _bounded(record.data.get("adapter"), 64)
        base = f"{_bounded(record.stage_id, 64)}:{_bounded(record.type, 64)}:{_bounded(record.tool, 64)}"
        return f"{base}:{detail}" if detail else base

    def evaluate(self, managed: Any, harness: Any) -> RunEvaluation:
        effective = effective_evidence(self.collect_evidence(managed, harness))
        status_counts = Counter(_bounded(record.status, 32) or "UNKNOWN" for record in effective)
        type_counts = Counter(_bounded(record.type, 64) or "unknown" for record in effective)
        passing_types = sorted({record.type for record in effective if record.status == "PASS"})
        failures = [record for record in effective if record.status == "FAIL"]
        failing_channels = sorted({self.failure_channel(record) for record in failures})
        has_pass = any(record.status == "PASS" for record in effective)

        state = _bounded(getattr(managed, "state", ""), 32) or "UNKNOWN"
        if failures:
            outcome = "failed"
            reasons = ["latest effective trusted runtime evidence contains failure"]
        elif state == "FAILED":
            outcome = "failed"
            reasons = ["managed lifecycle ended FAILED"]
        elif state == "BLOCKED":
            outcome = "blocked"
            reasons = ["managed lifecycle ended BLOCKED"]
        elif state == "COMPLETED" and not has_pass:
            outcome = "insufficient_evidence"
            reasons = ["managed lifecycle completed without trusted PASS evidence"]
        elif state == "COMPLETED":
            outcome = "passed"
            reasons = ["managed lifecycle completed with trusted PASS evidence and no effective failure"]
        else:
            outcome = "incomplete"
            reasons = [f"managed lifecycle is not terminal: {state}"]

        evidence_backed = bool(effective)
        memory_eligible = state in TERMINAL_STATES and evidence_backed and outcome in {"passed", "failed", "blocked"}
        return RunEvaluation(
            schema_version=self.schema_version,
            run_id=_bounded(getattr(managed, "manager_run_id", ""), 128),
            flow_id=_bounded(getattr(getattr(managed, "flow", None), "id", ""), 128),
            flow_revision=_bounded_int(getattr(getattr(managed, "flow", None), "revision", 0), 10000),
            managed_state=state,
            outcome=outcome,
            evaluated_at=datetime.now(timezone.utc).isoformat(),
            signature=self.signature(dict(getattr(managed, "task_context", {}))),
            completed_stage_count=_bounded_int(len(list(getattr(managed, "completed_stages", [])))),
            stage_count=_bounded_int(len(list(getattr(getattr(managed, "flow", None), "stages", [])))),
            replan_count=_bounded_int(getattr(managed, "replan_count", 0)),
            effective_evidence_count=len(effective),
            status_counts=dict(sorted(status_counts.items())),
            evidence_type_counts=dict(sorted(type_counts.items())),
            passing_evidence_types=passing_types,
            failing_channels=failing_channels,
            reasons=reasons,
            memory_eligible=memory_eligible,
        )
