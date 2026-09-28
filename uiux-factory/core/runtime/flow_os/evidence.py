from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


TRUSTED_EVIDENCE_TYPES = frozenset({
    "file_read",
    "file_change",
    "search_result",
    "command_result",
    "validator_result",
    "artifact",
    "tool_observation",
    "browser_render",
    "deployment_result",
})


@dataclass(frozen=True)
class EvidenceRecord:
    id: str
    type: str
    stage_id: str
    tool: str
    status: str
    summary: str
    data: dict[str, Any] = field(default_factory=dict)
    origin: str = "runtime"
    trusted: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EvidenceRecord":
        record = cls(
            id=str(payload["id"]),
            type=str(payload["type"]),
            stage_id=str(payload["stage_id"]),
            tool=str(payload["tool"]),
            status=str(payload["status"]),
            summary=str(payload.get("summary", "")),
            data=dict(payload.get("data", {})),
            origin=str(payload.get("origin", "runtime")),
            trusted=bool(payload.get("trusted", True)),
            created_at=str(payload.get("created_at", "")) or datetime.now(timezone.utc).isoformat(),
        )
        if record.trusted and (record.origin != "runtime" or record.type not in TRUSTED_EVIDENCE_TYPES):
            raise ValueError("trusted evidence must be emitted by the runtime with a recognized evidence type")
        return record


def _record_type(tool: str, result: Any) -> str:
    if tool in {"write_project_file", "write_artifact", "replace_text"}:
        return "file_change"
    if tool in {"search_text", "list_files_recursive"}:
        return "search_result"
    if tool in {"read_text", "list_files"}:
        return "file_read"
    if tool == "run_target_command":
        return "command_result"
    if tool == "run_validator":
        return "validator_result"
    if tool == "release_action":
        return "tool_observation"
    if isinstance(result, dict) and result.get("path"):
        return "artifact"
    return "tool_observation"


def evidence_from_tool(stage_id: str, tool: str, result: Any) -> EvidenceRecord:
    evidence_type = _record_type(tool, result)
    data = dict(result) if isinstance(result, dict) else {"value": result}
    if evidence_type in {"command_result", "validator_result"}:
        returncode = int(data.get("returncode", 0))
        status = "PASS" if returncode == 0 else "FAIL"
        summary = f"{tool} exited with code {returncode}"
    elif evidence_type == "file_change":
        status = "PASS"
        summary = f"runtime changed {data.get('path', 'a workspace file')}"
    elif evidence_type == "search_result":
        status = "OBSERVED"
        count = len(data.get("matches", data.get("items", []))) if isinstance(data, dict) else 0
        summary = f"runtime observed {count} search/list result(s)"
    elif evidence_type == "file_read":
        status = "OBSERVED"
        summary = f"runtime read {data.get('path', 'project evidence')}"
    else:
        status = "OBSERVED"
        summary = f"runtime observed {tool} result"
    return EvidenceRecord(
        id=f"ev_{uuid.uuid4().hex[:16]}",
        type=evidence_type,
        stage_id=str(stage_id),
        tool=str(tool),
        status=status,
        summary=summary,
        data=data,
    )


def provider_claim_records(stage_id: str, claims: list[str]) -> list[dict[str, Any]]:
    """Preserve provider claims for traceability without upgrading them to evidence."""
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "id": f"claim_{uuid.uuid4().hex[:16]}",
            "type": "provider_claim",
            "stage_id": str(stage_id),
            "tool": "provider",
            "status": "CLAIMED",
            "summary": str(claim),
            "data": {},
            "origin": "provider",
            "trusted": False,
            "created_at": now,
        }
        for claim in claims
    ]


def _trusted_records(records: list[dict[str, Any]]) -> list[EvidenceRecord]:
    trusted: list[EvidenceRecord] = []
    for payload in records:
        try:
            record = EvidenceRecord.from_dict(dict(payload))
        except (KeyError, TypeError, ValueError):
            continue
        if record.trusted and record.origin == "runtime":
            trusted.append(record)
    return trusted


def trusted_stage_evidence(records: list[dict[str, Any]], stage_id: str) -> list[EvidenceRecord]:
    return [record for record in _trusted_records(records) if record.stage_id == stage_id]


def _evidence_channel(record: EvidenceRecord) -> tuple[Any, ...]:
    """Identify observations where a later retry supersedes an earlier result."""
    if record.type == "validator_result":
        return (record.type, record.tool, str(record.data.get("name", "")))
    if record.type == "command_result":
        argv = tuple(str(item) for item in record.data.get("argv", []))
        return (record.type, record.tool, argv, str(record.data.get("cwd", ".")))
    if record.type == "browser_render":
        viewport = record.data.get("viewport", {})
        if isinstance(viewport, dict):
            viewport_key = tuple(sorted((str(key), str(value)) for key, value in viewport.items()))
        else:
            viewport_key = str(viewport)
        return (record.type, str(record.data.get("route", "")), viewport_key)
    path = str(record.data.get("path", ""))
    if path:
        return (record.type, record.tool, path)
    return (record.type, record.tool)


def effective_evidence(records: list[dict[str, Any]]) -> list[EvidenceRecord]:
    """Return the latest trusted record per stage + evidence channel.

    Release readiness must evaluate the repaired current state, not permanently block
    because an earlier attempt failed. A later retry only supersedes evidence from the
    same stage and channel; unrelated evidence can never hide a failure.
    """
    latest: dict[tuple[Any, ...], EvidenceRecord] = {}
    for record in _trusted_records(records):
        latest[(record.stage_id, *_evidence_channel(record))] = record
    return list(latest.values())


def effective_stage_evidence(records: list[dict[str, Any]], stage_id: str) -> list[EvidenceRecord]:
    """Return the latest trusted record per evidence channel for one stage."""
    return [record for record in effective_evidence(records) if record.stage_id == stage_id]


def gate_evidence_errors(
    gates: list[dict[str, Any]],
    stage_id: str,
    records: list[dict[str, Any]],
    agent: str = "",
) -> list[str]:
    """Evaluate typed evidence requirements without treating model prose as proof."""
    effective = effective_stage_evidence(records, stage_id)
    available = {record.type for record in effective if record.status != "FAIL"}
    errors: list[str] = []
    for record in effective:
        if record.status == "FAIL":
            errors.append(f"runtime evidence failed: {record.type} via {record.tool} ({record.summary})")

    role_defaults = {
        "research": {"file_read", "search_result", "validator_result", "command_result"},
        "implementation": {"file_change", "validator_result", "command_result"},
        "qa": {"validator_result", "command_result", "file_read", "search_result", "browser_render"},
        "development": set(TRUSTED_EVIDENCE_TYPES),
    }
    for gate in gates:
        if gate.get("approval") == "human":
            continue
        gate_id = str(gate.get("id", "unnamed"))
        declared = gate.get("evidence_types")
        if declared is not None:
            required = {str(item) for item in declared}
            missing = sorted(required.difference(available))
            if missing:
                errors.append(f"gate {gate_id} missing typed evidence: {', '.join(missing)}")
            continue
        acceptable = role_defaults.get(agent, set(TRUSTED_EVIDENCE_TYPES))
        if not available.intersection(acceptable):
            errors.append(f"gate {gate_id} has no trusted runtime evidence for stage role {agent or '(unknown)'}")
    return errors
