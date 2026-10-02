from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Literal, Mapping

from core.events.run_session_log import RunSessionEvent
from core.runtime.lifecycle_projection import FACTORY_STAGE_PHASE, PHASES, project_managed_lifecycle
from core.runtime.lifecycle_reconciliation import LifecyclePhase


LifecycleEventKind = Literal[
    "run_started",
    "stage_started",
    "stage_completed",
    "run_completed",
    "run_failed",
    "run_blocked",
    "replan_applied",
    "approval_required",
    "approval_granted",
    "run_forked",
    "native_event_observed",
]
ChronologyStrength = Literal["durable_append_only", "derived_checkpoint_delta"]
SurfaceId = Literal["factory_product", "managed_flow"]


@dataclass(frozen=True)
class LifecycleEventReceipt:
    schema_version: Literal["lifecycle-event-receipt.v1"]
    surface_id: SurfaceId
    chronology_strength: ChronologyStrength
    kind: LifecycleEventKind
    run_id: str
    phase: LifecyclePhase | None
    native_type: str
    native_stage: str | None
    source_seq: int | None
    source_timestamp: str | None
    previous_checkpoint_hash: str | None
    checkpoint_hash: str | None
    lineage_refs: tuple[str, ...]
    details: dict[str, Any]
    observation_only: Literal[True] = True
    execution_effect: Literal["none"] = "none"
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"
    release_effect: Literal["none"] = "none"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _stable_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def _factory_phase(stage: str | None) -> LifecyclePhase | None:
    if not stage:
        return None
    normalized = str(stage).strip().lower()
    if normalized in FACTORY_STAGE_PHASE:
        return FACTORY_STAGE_PHASE[normalized]
    if normalized.startswith("qa_") or normalized.endswith("_qa"):
        return "QA"
    return None


def _managed_phase(payload: Mapping[str, Any], stage: str | None) -> LifecyclePhase | None:
    if not stage:
        return None
    synthetic = deepcopy(dict(payload))
    synthetic["active_stage"] = stage
    synthetic["completed_stages"] = []
    projection = project_managed_lifecycle(synthetic)
    for phase in ("RESEARCH", "DESIGN", "IMPLEMENT", "QA"):
        if projection.phase(phase).status == "active":
            return phase
    return None


def _factory_kind(native_type: str) -> tuple[LifecycleEventKind, LifecyclePhase | None]:
    mapping: dict[str, tuple[LifecycleEventKind, LifecyclePhase | None]] = {
        "run.created": ("run_started", "INTAKE"),
        "stage.started": ("stage_started", None),
        "stage.completed": ("stage_completed", None),
        "run.completed": ("run_completed", "FINALIZE"),
        "run.failed": ("run_failed", None),
        "session.forked": ("run_forked", None),
    }
    return mapping.get(native_type, ("native_event_observed", None))


def project_factory_event_receipts(
    events: Iterable[RunSessionEvent | Mapping[str, Any]],
) -> tuple[LifecycleEventReceipt, ...]:
    """Normalize Factory append-only events without mutating or replaying the run.

    Factory chronology remains authoritative only as chronology. These receipts do not
    inherit execution, gate, evidence or release authority from the native event log.
    """

    receipts: list[LifecycleEventReceipt] = []
    for raw in events:
        event = raw if isinstance(raw, RunSessionEvent) else RunSessionEvent.from_dict(dict(raw))
        kind, fixed_phase = _factory_kind(event.type)
        phase = fixed_phase
        if kind in {"stage_started", "stage_completed"}:
            phase = _factory_phase(event.stage)
        lineage: list[str] = [f"factory_event_seq:{event.seq}"]
        inherited = event.data.get("inherited_from")
        if isinstance(inherited, Mapping):
            source_run = inherited.get("run_id")
            source_seq = inherited.get("seq")
            if source_run is not None and source_seq is not None:
                lineage.append(f"inherited_from:{source_run}:{source_seq}")

        receipts.append(
            LifecycleEventReceipt(
                schema_version="lifecycle-event-receipt.v1",
                surface_id="factory_product",
                chronology_strength="durable_append_only",
                kind=kind,
                run_id=event.run_id,
                phase=phase,
                native_type=event.type,
                native_stage=event.stage,
                source_seq=event.seq,
                source_timestamp=event.timestamp,
                previous_checkpoint_hash=None,
                checkpoint_hash=None,
                lineage_refs=tuple(lineage),
                details=deepcopy(event.data),
            )
        )
    return tuple(receipts)


def _flow_revision(payload: Mapping[str, Any]) -> int:
    flow = payload.get("flow")
    if not isinstance(flow, Mapping):
        return 0
    raw = flow.get("revision", 0)
    if isinstance(raw, bool):
        return 0
    try:
        return int(raw or 0)
    except (TypeError, ValueError):
        return 0


def _flow_stage_order(payload: Mapping[str, Any]) -> tuple[str, ...]:
    flow = payload.get("flow")
    if not isinstance(flow, Mapping):
        return ()
    stages = flow.get("stages", [])
    ordered: list[str] = []
    if isinstance(stages, list):
        for item in stages:
            if isinstance(item, Mapping):
                stage_id = str(item.get("id", "")).strip()
                if stage_id:
                    ordered.append(stage_id)
    return tuple(ordered)


def _pending_human_gates(payload: Mapping[str, Any]) -> tuple[str, ...]:
    active_stage = str(payload.get("active_stage", "")).strip()
    flow = payload.get("flow")
    approved = {str(item) for item in list(payload.get("approved_gates", []))}
    if not active_stage or not isinstance(flow, Mapping):
        return ()
    for item in list(flow.get("stages", [])):
        if not isinstance(item, Mapping) or str(item.get("id", "")).strip() != active_stage:
            continue
        pending: list[str] = []
        for gate in list(item.get("gates", [])):
            if not isinstance(gate, Mapping) or gate.get("approval") != "human":
                continue
            gate_id = str(gate.get("id", "")).strip()
            if gate_id and gate_id not in approved:
                pending.append(gate_id)
        return tuple(pending)
    return ()


def project_managed_transition_receipts(
    previous: Mapping[str, Any] | None,
    current: Mapping[str, Any],
) -> tuple[LifecycleEventReceipt, ...]:
    """Derive observation receipts from two ManagedWebsiteRun checkpoints.

    A Managed checkpoint is not an append-only event stream. The returned order is a
    deterministic projection order only and must never be interpreted as native event
    chronology. No checkpoint is written and no managed transition method is called.
    """

    current_payload = deepcopy(dict(current))
    previous_payload = deepcopy(dict(previous)) if previous is not None else None
    run_id = str(current_payload.get("manager_run_id", "")).strip()
    if not run_id:
        raise ValueError("managed checkpoint requires manager_run_id")
    if previous_payload is not None:
        previous_run_id = str(previous_payload.get("manager_run_id", "")).strip()
        if previous_run_id != run_id:
            raise ValueError("managed checkpoint delta must refer to the same manager_run_id")

    current_hash = _stable_hash(current_payload)
    previous_hash = _stable_hash(previous_payload) if previous_payload is not None else None
    revision = _flow_revision(current_payload)
    state_before = str(previous_payload.get("state", "")) if previous_payload is not None else None
    state_after = str(current_payload.get("state", ""))
    receipts: list[LifecycleEventReceipt] = []

    def emit(
        kind: LifecycleEventKind,
        native_type: str,
        *,
        stage: str | None = None,
        phase: LifecyclePhase | None = None,
        lineage_refs: Iterable[str] = (),
        details: Mapping[str, Any] | None = None,
    ) -> None:
        payload_details = {
            "state_before": state_before,
            "state_after": state_after,
            "flow_revision": revision,
            "projection_order_only": True,
        }
        payload_details.update(deepcopy(dict(details or {})))
        receipts.append(
            LifecycleEventReceipt(
                schema_version="lifecycle-event-receipt.v1",
                surface_id="managed_flow",
                chronology_strength="derived_checkpoint_delta",
                kind=kind,
                run_id=run_id,
                phase=phase,
                native_type=native_type,
                native_stage=stage,
                source_seq=None,
                source_timestamp=None,
                previous_checkpoint_hash=previous_hash,
                checkpoint_hash=current_hash,
                lineage_refs=tuple(str(item) for item in lineage_refs),
                details=payload_details,
            )
        )

    if previous_payload is None:
        emit(
            "native_event_observed",
            "managed.initial_checkpoint",
            stage=str(current_payload.get("active_stage", "")).strip() or None,
            details={"reason": "initial checkpoint does not prove run-start chronology"},
        )
        return tuple(receipts)

    previous_revision = _flow_revision(previous_payload)
    previous_replan_count = int(previous_payload.get("replan_count", 0) or 0)
    current_replan_count = int(current_payload.get("replan_count", 0) or 0)
    if revision > previous_revision or current_replan_count > previous_replan_count:
        active_stage = str(current_payload.get("active_stage", "")).strip() or None
        emit(
            "replan_applied",
            "managed.replan_delta",
            stage=active_stage,
            phase="REPLAN",
            lineage_refs=(f"flow_revision:{previous_revision}->{revision}",),
            details={
                "replan_count_before": previous_replan_count,
                "replan_count_after": current_replan_count,
            },
        )

    previous_approvals = {str(item) for item in list(previous_payload.get("approved_gates", []))}
    current_approvals = [str(item) for item in list(current_payload.get("approved_gates", []))]
    for gate_id in current_approvals:
        if gate_id not in previous_approvals:
            active_stage = str(current_payload.get("active_stage", "")).strip() or None
            emit(
                "approval_granted",
                "managed.approved_gate_added",
                stage=active_stage,
                phase=_managed_phase(current_payload, active_stage),
                lineage_refs=(f"gate:{gate_id}",),
                details={"gate_id": gate_id},
            )

    if state_after == "AWAITING_APPROVAL" and state_before != "AWAITING_APPROVAL":
        active_stage = str(current_payload.get("active_stage", "")).strip() or None
        pending = _pending_human_gates(current_payload)
        emit(
            "approval_required",
            "managed.awaiting_approval",
            stage=active_stage,
            phase=_managed_phase(current_payload, active_stage),
            lineage_refs=tuple(f"gate:{gate_id}" for gate_id in pending),
            details={"pending_gate_ids": list(pending)},
        )

    previous_runs = dict(previous_payload.get("stage_runs", {}))
    current_runs = dict(current_payload.get("stage_runs", {}))
    stage_order = list(_flow_stage_order(current_payload))
    for stage_id in current_runs:
        if stage_id not in stage_order:
            stage_order.append(str(stage_id))
    for stage_id in stage_order:
        before = [str(item) for item in list(previous_runs.get(stage_id, []))]
        after = [str(item) for item in list(current_runs.get(stage_id, []))]
        if len(after) < len(before) or after[: len(before)] != before:
            raise ValueError(f"managed stage_run lineage is not append-only for stage {stage_id}")
        for stage_run_id in after[len(before) :]:
            emit(
                "stage_started",
                "managed.stage_run_added",
                stage=stage_id,
                phase=_managed_phase(current_payload, stage_id),
                lineage_refs=(f"stage_run:{stage_run_id}", f"flow_revision:{revision}"),
                details={"stage_run_id": stage_run_id},
            )

    previous_completed = {str(item) for item in list(previous_payload.get("completed_stages", []))}
    for stage_id in [str(item) for item in list(current_payload.get("completed_stages", []))]:
        if stage_id not in previous_completed:
            emit(
                "stage_completed",
                "managed.completed_stage_added",
                stage=stage_id,
                phase=_managed_phase(current_payload, stage_id),
                lineage_refs=(f"completed_stage:{stage_id}", f"flow_revision:{revision}"),
            )

    if state_after != state_before:
        terminal_kind: LifecycleEventKind | None = {
            "COMPLETED": "run_completed",
            "FAILED": "run_failed",
            "BLOCKED": "run_blocked",
        }.get(state_after)
        if terminal_kind is not None:
            emit(
                terminal_kind,
                f"managed.state.{state_after.lower()}",
                stage=str(current_payload.get("active_stage", "")).strip() or None,
                details={"managed_completion_is_not_finalize_or_release": state_after == "COMPLETED"},
            )

    if not receipts and (
        state_after != state_before
        or current_payload.get("active_stage") != previous_payload.get("active_stage")
        or current_hash != previous_hash
    ):
        emit(
            "native_event_observed",
            "managed.checkpoint_delta",
            stage=str(current_payload.get("active_stage", "")).strip() or None,
            details={"reason": "checkpoint changed without a safely derivable normalized transition"},
        )

    return tuple(receipts)


def assert_receipts_non_authoritative(receipts: Iterable[LifecycleEventReceipt]) -> None:
    for receipt in receipts:
        if receipt.observation_only is not True:
            raise ValueError("lifecycle event receipt must remain observation-only")
        for effect in (
            receipt.execution_effect,
            receipt.authority_effect,
            receipt.gate_effect,
            receipt.evidence_effect,
            receipt.release_effect,
        ):
            if effect != "none":
                raise ValueError("lifecycle event receipt cannot acquire runtime authority")
        if receipt.phase is not None and receipt.phase not in PHASES:
            raise ValueError(f"unknown lifecycle phase: {receipt.phase}")
