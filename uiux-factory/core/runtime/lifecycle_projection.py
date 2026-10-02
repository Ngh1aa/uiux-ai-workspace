from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal, Mapping

from core.runtime.lifecycle_reconciliation import LifecyclePhase


ProjectionStatus = Literal[
    "pending",
    "active",
    "completed",
    "unavailable",
    "unknown",
]
ProjectionConfidence = Literal["explicit", "derived", "unmapped"]


PHASES: tuple[LifecyclePhase, ...] = (
    "INTAKE",
    "INTERPRET",
    "PLAN",
    "RESEARCH",
    "DESIGN",
    "IMPLEMENT",
    "QA",
    "REPLAN",
    "FINALIZE",
    "RELEASE",
)

FACTORY_STAGE_PHASE: dict[str, LifecyclePhase] = {
    "reference_analysis": "RESEARCH",
    "research": "RESEARCH",
    "ux_ia": "DESIGN",
    "art_direction": "DESIGN",
    "design_contract": "DESIGN",
    "design_system": "DESIGN",
    "implementation_plan": "DESIGN",
    "visual_composition": "DESIGN",
    "implementation": "IMPLEMENT",
    "external_handoff": "IMPLEMENT",
    "browser_qa": "QA",
    "visual_qa": "QA",
    "qa": "QA",
    "repair": "QA",
    "quality_loop": "QA",
}


@dataclass(frozen=True)
class LifecyclePhaseProjection:
    phase: LifecyclePhase
    status: ProjectionStatus
    confidence: ProjectionConfidence
    native_refs: tuple[str, ...] = ()
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LifecycleProjection:
    schema_version: Literal["lifecycle-projection.v1"]
    surface_id: Literal["factory_product", "managed_flow"]
    native_state: str
    active_native_stage: str | None
    phases: tuple[LifecyclePhaseProjection, ...]
    unmapped_native_stages: tuple[str, ...] = ()
    projection_only: Literal[True] = True
    execution_effect: Literal["none"] = "none"
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"
    release_effect: Literal["none"] = "none"

    def phase(self, phase: LifecyclePhase) -> LifecyclePhaseProjection:
        for item in self.phases:
            if item.phase == phase:
                return item
        raise KeyError(phase)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _factory_stage_phase(stage_id: str) -> LifecyclePhase | None:
    normalized = str(stage_id).strip().lower()
    if normalized in FACTORY_STAGE_PHASE:
        return FACTORY_STAGE_PHASE[normalized]
    if normalized.startswith("qa_") or normalized.endswith("_qa"):
        return "QA"
    return None


def _managed_stage_phase(stage: Mapping[str, Any]) -> LifecyclePhase | None:
    stage_id = str(stage.get("id", "")).strip().lower()
    agent = str(stage.get("agent", "")).strip().lower()

    # Prefer explicit specialist ownership where the declarative flow already says it.
    if agent == "research":
        return "RESEARCH"
    if agent == "implementation":
        return "IMPLEMENT"
    if agent == "qa":
        return "QA"

    # Development stages can represent design/product preparation. Use only stable,
    # auditable stage-id cues; otherwise fail safe as unmapped rather than guessing.
    if any(token in stage_id for token in ("research", "discover", "audit")):
        return "RESEARCH"
    if any(token in stage_id for token in ("implement", "build", "code")):
        return "IMPLEMENT"
    if any(token in stage_id for token in ("qa", "test", "validate", "verify")):
        return "QA"
    if any(
        token in stage_id
        for token in (
            "design",
            "ux",
            "ia",
            "strategy",
            "direction",
            "wireframe",
            "prototype",
            "content",
        )
    ):
        return "DESIGN"
    return None


def _phase_rows(
    *,
    status_by_phase: dict[LifecyclePhase, ProjectionStatus],
    confidence_by_phase: dict[LifecyclePhase, ProjectionConfidence],
    refs_by_phase: dict[LifecyclePhase, list[str]],
    notes: dict[LifecyclePhase, str] | None = None,
) -> tuple[LifecyclePhaseProjection, ...]:
    note_map = notes or {}
    return tuple(
        LifecyclePhaseProjection(
            phase=phase,
            status=status_by_phase.get(phase, "pending"),
            confidence=confidence_by_phase.get(phase, "derived"),
            native_refs=tuple(refs_by_phase.get(phase, [])),
            note=note_map.get(phase, ""),
        )
        for phase in PHASES
    )


def project_factory_lifecycle(payload: Mapping[str, Any]) -> LifecycleProjection:
    """Project a RunContext-like snapshot without mutating or executing it."""

    native_state = str(payload.get("status", "unknown")).strip().lower() or "unknown"
    active_stage_raw = payload.get("active_stage")
    active_stage = str(active_stage_raw).strip() if active_stage_raw else None
    completed_stages = [str(item) for item in list(payload.get("completed_stages", []))]
    artifacts = dict(payload.get("artifacts", {})) if isinstance(payload.get("artifacts"), Mapping) else {}

    status_by_phase: dict[LifecyclePhase, ProjectionStatus] = {phase: "pending" for phase in PHASES}
    confidence_by_phase: dict[LifecyclePhase, ProjectionConfidence] = {phase: "derived" for phase in PHASES}
    refs: dict[LifecyclePhase, list[str]] = {phase: [] for phase in PHASES}
    notes: dict[LifecyclePhase, str] = {}
    unmapped: list[str] = []

    if native_state == "created":
        status_by_phase["INTAKE"] = "active"
    else:
        status_by_phase["INTAKE"] = "completed"
    confidence_by_phase["INTAKE"] = "explicit"

    if "flow_plan" in artifacts:
        status_by_phase["INTERPRET"] = "completed"
        status_by_phase["PLAN"] = "completed"
        confidence_by_phase["INTERPRET"] = "explicit"
        confidence_by_phase["PLAN"] = "explicit"
        refs["PLAN"].append("artifact:flow_plan")
    elif native_state in {"running", "completed", "handoff_ready", "failed"}:
        status_by_phase["INTERPRET"] = "unknown"
        status_by_phase["PLAN"] = "unknown"
        confidence_by_phase["INTERPRET"] = "unmapped"
        confidence_by_phase["PLAN"] = "unmapped"
        notes["PLAN"] = "run snapshot lacks flow_plan artifact; do not infer planning completion"

    for stage in completed_stages:
        phase = _factory_stage_phase(stage)
        if phase is None:
            unmapped.append(stage)
            continue
        status_by_phase[phase] = "completed"
        confidence_by_phase[phase] = "explicit"
        refs[phase].append(stage)

    if active_stage:
        phase = _factory_stage_phase(active_stage)
        if phase is None:
            unmapped.append(active_stage)
        else:
            status_by_phase[phase] = "active"
            confidence_by_phase[phase] = "explicit"
            refs[phase].append(active_stage)

    # Factory replanning/revision is not encoded as one canonical RunContext state.
    status_by_phase["REPLAN"] = "unknown"
    confidence_by_phase["REPLAN"] = "unmapped"
    notes["REPLAN"] = "Factory revisions/replans require event/revision context beyond RunContext snapshot"

    if native_state == "completed":
        status_by_phase["FINALIZE"] = "completed"
        confidence_by_phase["FINALIZE"] = "explicit"
    elif native_state == "running":
        status_by_phase["FINALIZE"] = "pending"
    elif native_state == "failed":
        status_by_phase["FINALIZE"] = "pending"

    status_by_phase["RELEASE"] = "unavailable"
    confidence_by_phase["RELEASE"] = "explicit"
    notes["RELEASE"] = "default Factory run does not expose production deployment"

    return LifecycleProjection(
        schema_version="lifecycle-projection.v1",
        surface_id="factory_product",
        native_state=native_state,
        active_native_stage=active_stage,
        phases=_phase_rows(
            status_by_phase=status_by_phase,
            confidence_by_phase=confidence_by_phase,
            refs_by_phase=refs,
            notes=notes,
        ),
        unmapped_native_stages=tuple(dict.fromkeys(unmapped)),
    )


def project_managed_lifecycle(payload: Mapping[str, Any]) -> LifecycleProjection:
    """Project a ManagedWebsiteRun-like snapshot without advancing its state machine."""

    native_state = str(payload.get("state", "unknown")).strip().upper() or "UNKNOWN"
    active_stage = str(payload.get("active_stage", "")).strip() or None
    completed_stages = [str(item) for item in list(payload.get("completed_stages", []))]
    flow = dict(payload.get("flow", {})) if isinstance(payload.get("flow"), Mapping) else {}
    stages = [dict(item) for item in list(flow.get("stages", [])) if isinstance(item, Mapping)]
    replan_count = int(payload.get("replan_count", 0) or 0)

    status_by_phase: dict[LifecyclePhase, ProjectionStatus] = {phase: "pending" for phase in PHASES}
    confidence_by_phase: dict[LifecyclePhase, ProjectionConfidence] = {phase: "derived" for phase in PHASES}
    refs: dict[LifecyclePhase, list[str]] = {phase: [] for phase in PHASES}
    notes: dict[LifecyclePhase, str] = {}
    unmapped: list[str] = []

    for phase in ("INTAKE", "INTERPRET", "PLAN"):
        status_by_phase[phase] = "completed"
        confidence_by_phase[phase] = "explicit"

    stage_phase: dict[str, LifecyclePhase | None] = {}
    for stage in stages:
        stage_id = str(stage.get("id", "")).strip()
        if not stage_id:
            continue
        phase = _managed_stage_phase(stage)
        stage_phase[stage_id] = phase
        if phase is None:
            unmapped.append(stage_id)
        else:
            refs[phase].append(stage_id)

    completed_set = set(completed_stages)
    for phase in ("RESEARCH", "DESIGN", "IMPLEMENT", "QA"):
        phase_stage_ids = [stage_id for stage_id, mapped in stage_phase.items() if mapped == phase]
        if phase_stage_ids and all(stage_id in completed_set for stage_id in phase_stage_ids):
            status_by_phase[phase] = "completed"
            confidence_by_phase[phase] = "explicit"

    if active_stage:
        active_phase = stage_phase.get(active_stage)
        if active_phase is None:
            if active_stage not in unmapped:
                unmapped.append(active_stage)
        else:
            status_by_phase[active_phase] = "active"
            confidence_by_phase[active_phase] = "explicit"

    if native_state == "REPLANNED":
        status_by_phase["REPLAN"] = "active"
        confidence_by_phase["REPLAN"] = "explicit"
    elif replan_count > 0:
        status_by_phase["REPLAN"] = "completed"
        confidence_by_phase["REPLAN"] = "explicit"

    # Finalization/release live in ProductionReleaseController outputs, not in
    # ManagedWebsiteRun itself. Do not infer them from managed.state=COMPLETED.
    status_by_phase["FINALIZE"] = "unknown"
    confidence_by_phase["FINALIZE"] = "unmapped"
    notes["FINALIZE"] = "ManagedWebsiteRun does not encode workspace-finalize outcome"
    status_by_phase["RELEASE"] = "unknown"
    confidence_by_phase["RELEASE"] = "unmapped"
    notes["RELEASE"] = "ManagedWebsiteRun does not encode production-deploy outcome"

    return LifecycleProjection(
        schema_version="lifecycle-projection.v1",
        surface_id="managed_flow",
        native_state=native_state,
        active_native_stage=active_stage,
        phases=_phase_rows(
            status_by_phase=status_by_phase,
            confidence_by_phase=confidence_by_phase,
            refs_by_phase=refs,
            notes=notes,
        ),
        unmapped_native_stages=tuple(dict.fromkeys(unmapped)),
    )
