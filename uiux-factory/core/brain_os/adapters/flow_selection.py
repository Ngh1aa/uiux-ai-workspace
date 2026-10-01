from __future__ import annotations

from enum import Enum
from typing import Iterable, Literal

from pydantic import Field, field_validator, model_validator

from core.brain_os.contracts import BrainContractModel, ChangeSurface
from core.runtime.flow_os.adaptive_surface import CHANGE_SURFACES, classify_change_surface
from core.runtime.flow_os.flow import FlowPlanner


CANONICAL_FLOW_OWNER = "core.runtime.flow_os.flow.FlowPlanner"
CANONICAL_SURFACE_OWNER = "core.runtime.flow_os.adaptive_surface.classify_change_surface"


class SurfaceSource(str, Enum):
    TASK_CONTRACT = "TASK_CONTRACT"
    CANONICAL_CLASSIFIER = "CANONICAL_CLASSIFIER"
    BOUNDED_ESCALATION = "BOUNDED_ESCALATION"


class EscalationTrigger(str, Enum):
    SCOPE_INSUFFICIENT = "SCOPE_INSUFFICIENT"
    REQUIRED_STAGE_MISSING = "REQUIRED_STAGE_MISSING"
    EVIDENCE_REVEALED_BROADER_SCOPE = "EVIDENCE_REVEALED_BROADER_SCOPE"


class FlowSelectionDecision(BrainContractModel):
    """Advisory view of a decision already made by the canonical FlowPlanner.

    This object records which surface/context was supplied to the canonical owner and
    which declarative flow that owner selected. It does not select or execute a flow by
    itself and cannot grant execution authority.
    """

    schema_version: Literal["brain-flow-selection.v1"] = "brain-flow-selection.v1"
    change_surface: ChangeSurface
    surface_source: SurfaceSource
    flow_id: str = Field(min_length=1, max_length=256)
    flow_source: str = Field(min_length=1, max_length=1000)
    score: int
    canonical_owner: Literal["core.runtime.flow_os.flow.FlowPlanner"] = CANONICAL_FLOW_OWNER
    classifier_owner: Literal[
        "core.runtime.flow_os.adaptive_surface.classify_change_surface"
    ] = CANONICAL_SURFACE_OWNER
    rationale: str = Field(min_length=1, max_length=4000)


class FlowEscalationProposal(BrainContractModel):
    """Bounded advisory request to widen change surface by exactly one rung.

    The proposal does not mutate a running flow. A caller must submit the widened
    context back through the canonical FlowPlanner to obtain a new flow selection.
    """

    schema_version: Literal["brain-flow-escalation.v1"] = "brain-flow-escalation.v1"
    from_surface: ChangeSurface
    to_surface: ChangeSurface
    trigger: EscalationTrigger
    reason: str = Field(min_length=1, max_length=4000)
    evidence_refs: list[str] = Field(default_factory=list, max_length=100)
    bounded: Literal[True] = True

    @field_validator("evidence_refs")
    @classmethod
    def _normalize_evidence_refs(cls, values: list[str]) -> list[str]:
        seen: set[str] = set()
        output: list[str] = []
        for raw in values:
            value = str(raw).strip()
            if value and value not in seen:
                seen.add(value)
                output.append(value)
        return output

    @model_validator(mode="after")
    def _validate_adjacent_escalation(self) -> "FlowEscalationProposal":
        source_index = CHANGE_SURFACES.index(self.from_surface)
        if source_index >= len(CHANGE_SURFACES) - 1:
            raise ValueError("PRODUCT is already the widest change surface")
        expected = CHANGE_SURFACES[source_index + 1]
        if self.to_surface != expected:
            raise ValueError(
                f"bounded escalation must move one surface at a time: {self.from_surface} -> {expected}"
            )
        if (
            self.trigger is EscalationTrigger.EVIDENCE_REVEALED_BROADER_SCOPE
            and not self.evidence_refs
        ):
            raise ValueError("evidence-driven escalation requires at least one evidence reference")
        return self


def _clean_scope(scope: Iterable[str] | None) -> list[str]:
    if scope is None:
        return []
    return [str(item).strip() for item in scope if str(item).strip()]


def classify_smallest_surface(
    *,
    goal: str,
    intent: str,
    scope: Iterable[str] | None = None,
) -> ChangeSurface:
    """Delegate change-surface classification to the canonical runtime owner."""

    return classify_change_surface(str(goal), str(intent), _clean_scope(scope))  # type: ignore[return-value]


def select_canonical_flow(
    planner: FlowPlanner,
    *,
    context: dict[str, object],
    goal: str = "",
    scope: Iterable[str] | None = None,
) -> FlowSelectionDecision:
    """Route through the canonical FlowPlanner while preferring the smallest surface.

    If the Task Contract already contains `change_surface`, that canonical value is
    preserved. Otherwise the existing adaptive-surface classifier supplies the narrowest
    credible surface before FlowPlanner receives the context.
    """

    effective = dict(context)
    raw_surface = str(effective.get("change_surface", "")).strip().upper()
    if raw_surface:
        normalized = planner.flow_resolver.normalize_context(effective)
        surface = str(normalized["change_surface"])
        source = SurfaceSource.TASK_CONTRACT
        effective = normalized
    else:
        intent = str(effective.get("intent", "build"))
        effective_scope = _clean_scope(scope)
        if not effective_scope:
            raw_scope = effective.get("scope", [])
            if isinstance(raw_scope, (list, tuple, set)):
                effective_scope = _clean_scope(raw_scope)
        surface = classify_smallest_surface(goal=goal, intent=intent, scope=effective_scope)
        effective["change_surface"] = surface
        source = SurfaceSource.CANONICAL_CLASSIFIER

    resolved = planner.plan(effective)
    return FlowSelectionDecision(
        change_surface=surface,  # type: ignore[arg-type]
        surface_source=source,
        flow_id=resolved.id,
        flow_source=resolved.source,
        score=resolved.score,
        rationale=(
            f"Canonical FlowPlanner selected {resolved.id} for change_surface={surface}; "
            "Brain OS records the selection but does not own execution."
        ),
    )


def propose_bounded_escalation(
    *,
    current_surface: ChangeSurface,
    trigger: EscalationTrigger,
    reason: str,
    evidence_refs: list[str] | None = None,
) -> FlowEscalationProposal:
    """Propose widening scope by one adjacent surface only."""

    index = CHANGE_SURFACES.index(current_surface)
    if index >= len(CHANGE_SURFACES) - 1:
        raise ValueError("PRODUCT is already the widest change surface")
    return FlowEscalationProposal(
        from_surface=current_surface,
        to_surface=CHANGE_SURFACES[index + 1],  # type: ignore[arg-type]
        trigger=trigger,
        reason=reason,
        evidence_refs=evidence_refs or [],
    )


def select_after_bounded_escalation(
    planner: FlowPlanner,
    *,
    context: dict[str, object],
    proposal: FlowEscalationProposal,
) -> FlowSelectionDecision:
    """Resubmit one bounded escalation through the canonical FlowPlanner."""

    effective = planner.flow_resolver.normalize_context(dict(context))
    current = str(effective["change_surface"])
    if current != proposal.from_surface:
        raise ValueError(
            f"escalation source mismatch: context={current}, proposal={proposal.from_surface}"
        )
    effective["change_surface"] = proposal.to_surface
    resolved = planner.plan(effective)
    return FlowSelectionDecision(
        change_surface=proposal.to_surface,
        surface_source=SurfaceSource.BOUNDED_ESCALATION,
        flow_id=resolved.id,
        flow_source=resolved.source,
        score=resolved.score,
        rationale=(
            f"Canonical FlowPlanner re-selected {resolved.id} after bounded escalation "
            f"{proposal.from_surface}->{proposal.to_surface}: {proposal.reason}"
        ),
    )
