from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from core.runtime.flow_os.flow import FlowPlanner, ResolvedFlow
from core.runtime.flow_os.sequence_router import WorkSequenceContract
from core.runtime.flow_os.work_sequence import WorkSegment


class MultiSurfaceRoutingError(ValueError):
    """Raised when a multi-work contract is sent through a single-flow execution path."""

    def __init__(self, segments: list[WorkSegment]) -> None:
        self.segment_ids = tuple(segment.id for segment in segments)
        super().__init__(
            "task contains multiple lifecycle/surface owners; use plan_sequence instead of collapsing "
            f"{len(segments)} work segments into one flow"
        )


@dataclass(frozen=True)
class ResolvedWorkSegment:
    id: str
    order: int
    phase: str
    intent: str
    scope: list[str]
    change_surface: str
    inherits_from: str | None
    preserve: list[str]
    forbidden: list[str]
    active_stage_ids: list[str]
    flow: ResolvedFlow

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["flow"] = self.flow.to_dict()
        return payload


@dataclass(frozen=True)
class ResolvedWorkPlan:
    routing_mode: str
    segments: list[ResolvedWorkSegment]
    work_sequence_version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "routing_mode": self.routing_mode,
            "work_sequence_version": self.work_sequence_version,
            "segments": [segment.to_dict() for segment in self.segments],
        }


class SequenceFlowPlanner:
    """Plan each explicit work owner independently through the canonical FlowPlanner."""

    def __init__(self, planner: FlowPlanner) -> None:
        self.planner = planner

    @staticmethod
    def _active_stage_ids(flow: ResolvedFlow, phase: str) -> list[str]:
        stage_ids = [stage.id for stage in flow.stages]
        if phase == "audit":
            return ["research"] if "research" in stage_ids else stage_ids[:1]
        if phase == "design":
            if "design" in stage_ids:
                return ["design"]
            if "implementation" in stage_ids:
                return ["implementation"]
        if phase == "implementation" and "implementation" in stage_ids:
            return ["implementation"]
        if phase == "qa" and "qa" in stage_ids:
            return ["qa"]
        return stage_ids[:1]

    def plan_single(self, contract: WorkSequenceContract) -> ResolvedFlow:
        if contract.routing_mode == "sequence":
            raise MultiSurfaceRoutingError(contract.segments)
        return self.planner.plan(contract.profile.to_context())

    def plan_sequence(self, contract: WorkSequenceContract) -> ResolvedWorkPlan:
        if contract.routing_mode != "sequence" or len(contract.segments) < 2:
            raise ValueError("work sequence planning requires at least two explicit work segments")

        base_context = contract.profile.to_context()
        resolved_segments: list[ResolvedWorkSegment] = []
        for segment in contract.segments:
            segment_context = dict(base_context)
            segment_context["intent"] = segment.intent
            segment_context["scope"] = list(segment.scope)
            segment_context["change_surface"] = segment.change_surface
            segment_context["preserve"] = list(segment.preserve or [])
            segment_context["forbidden"] = list(segment.forbidden or [])
            segment_context["routing_mode"] = "segment"
            segment_context["work_segment_id"] = segment.id
            segment_context["work_phase"] = segment.phase

            flow = self.planner.plan(segment_context)
            resolved_segments.append(
                ResolvedWorkSegment(
                    id=segment.id,
                    order=segment.order,
                    phase=segment.phase,
                    intent=segment.intent,
                    scope=list(segment.scope),
                    change_surface=segment.change_surface,
                    inherits_from=segment.inherits_from,
                    preserve=list(segment.preserve or []),
                    forbidden=list(segment.forbidden or []),
                    active_stage_ids=self._active_stage_ids(flow, segment.phase),
                    flow=flow,
                )
            )

        return ResolvedWorkPlan(
            routing_mode="sequence",
            segments=resolved_segments,
            work_sequence_version=contract.version,
        )
