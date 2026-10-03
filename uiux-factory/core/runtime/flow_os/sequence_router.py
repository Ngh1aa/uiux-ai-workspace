from __future__ import annotations

from dataclasses import dataclass

from core.runtime.flow_os.task_context import GoalInterpretation, GoalInterpreter
from core.runtime.flow_os.work_sequence import WorkSegment, decompose_work_segments


WORK_SEQUENCE_CONTRACT_VERSION = "1.0"


@dataclass(frozen=True)
class WorkSequenceContract:
    """Non-breaking envelope for one canonical Task Contract plus ordered work segments."""

    profile: GoalInterpretation
    routing_mode: str
    segments: list[WorkSegment]
    version: str = WORK_SEQUENCE_CONTRACT_VERSION

    def to_context(self) -> dict[str, object]:
        context = self.profile.to_context()
        context["routing_mode"] = self.routing_mode
        context["work_sequence_version"] = self.version
        context["work_segments"] = [segment.to_dict() for segment in self.segments]
        return context

    def to_dict(self) -> dict[str, object]:
        return {
            "routing_mode": self.routing_mode,
            "work_sequence_version": self.version,
            "profile": self.profile.to_dict(),
            "work_segments": [segment.to_dict() for segment in self.segments],
        }


class WorkSequenceInterpreter:
    """Detect multi-intent/multi-surface work without replacing GoalInterpreter."""

    def __init__(self, interpreter: GoalInterpreter | None = None) -> None:
        self.interpreter = interpreter or GoalInterpreter()

    def interpret(
        self,
        goal: str,
        target_truth: dict[str, str] | None = None,
    ) -> WorkSequenceContract:
        profile = self.interpreter.interpret(goal, target_truth=target_truth)
        segments = decompose_work_segments(
            goal,
            infer_intent=self.interpreter._intent,
            infer_scope=self.interpreter._scope,
            preserve=list(profile.preserve),
            forbidden=list(profile.forbidden),
        )
        return WorkSequenceContract(
            profile=profile,
            routing_mode="sequence" if len(segments) >= 2 else "single",
            segments=segments,
        )
