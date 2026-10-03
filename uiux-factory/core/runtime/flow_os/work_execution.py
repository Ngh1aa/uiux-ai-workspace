from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

from core.runtime.flow_os.sequence_flow import ResolvedWorkPlan


WORK_EXECUTION_VERSION = "1.0"
EXECUTION_STATUSES = frozenset({"pending", "runnable", "running", "passed", "failed", "blocked"})
TERMINAL_STATUSES = frozenset({"passed", "failed", "blocked"})

EXPECTED_OUTPUTS_BY_PHASE: dict[str, tuple[str, ...]] = {
    "audit": ("audit-findings",),
    "design": ("design-spec",),
    "implementation": ("implementation-artifact",),
    "qa": ("qa-evidence",),
}


class ExecutionTransitionError(ValueError):
    """Raised when a work-plan state transition violates execution gates."""


@dataclass(frozen=True)
class ArtifactRef:
    id: str
    kind: str
    producer_segment_id: str
    uri: str | None = None
    digest: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.kind.strip() or not self.producer_segment_id.strip():
            raise ValueError("artifact id, kind and producer_segment_id are required")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ArtifactRef:
        return cls(
            id=str(payload["id"]),
            kind=str(payload["kind"]),
            producer_segment_id=str(payload["producer_segment_id"]),
            uri=str(payload["uri"]) if payload.get("uri") else None,
            digest=str(payload["digest"]) if payload.get("digest") else None,
            metadata={str(k): str(v) for k, v in dict(payload.get("metadata") or {}).items()},
        )


@dataclass
class ExecutionNode:
    segment_id: str
    order: int
    phase: str
    scope: list[str]
    change_surface: str
    depends_on: list[str]
    owner_segment_id: str | None
    preserve: list[str]
    forbidden: list[str]
    expected_output_kinds: list[str]
    required_artifact_kinds: list[str]
    status: str = "pending"
    blocking_reason: str | None = None
    attempts: int = 0

    def __post_init__(self) -> None:
        if self.status not in EXECUTION_STATUSES:
            raise ValueError(f"invalid execution status: {self.status}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ExecutionNode:
        return cls(
            segment_id=str(payload["segment_id"]),
            order=int(payload["order"]),
            phase=str(payload["phase"]),
            scope=[str(value) for value in payload.get("scope") or []],
            change_surface=str(payload["change_surface"]),
            depends_on=[str(value) for value in payload.get("depends_on") or []],
            owner_segment_id=str(payload["owner_segment_id"]) if payload.get("owner_segment_id") else None,
            preserve=[str(value) for value in payload.get("preserve") or []],
            forbidden=[str(value) for value in payload.get("forbidden") or []],
            expected_output_kinds=[str(value) for value in payload.get("expected_output_kinds") or []],
            required_artifact_kinds=[str(value) for value in payload.get("required_artifact_kinds") or []],
            status=str(payload.get("status") or "pending"),
            blocking_reason=str(payload["blocking_reason"]) if payload.get("blocking_reason") else None,
            attempts=int(payload.get("attempts") or 0),
        )


@dataclass
class WorkExecutionPlan:
    nodes: list[ExecutionNode]
    artifacts: dict[str, ArtifactRef] = field(default_factory=dict)
    version: str = WORK_EXECUTION_VERSION
    routing_mode: str = "sequence"

    @classmethod
    def from_resolved_work_plan(cls, plan: ResolvedWorkPlan) -> WorkExecutionPlan:
        if plan.routing_mode != "sequence" or len(plan.segments) < 2:
            raise ValueError("stateful execution requires a resolved multi-work sequence")

        nodes: list[ExecutionNode] = []
        previous_segment_id: str | None = None
        previous_outputs: list[str] = []
        for segment in sorted(plan.segments, key=lambda item: item.order):
            expected = list(EXPECTED_OUTPUTS_BY_PHASE.get(segment.phase, ("work-evidence",)))
            preserve = list(getattr(segment, "preserve", []) or [])
            forbidden = list(getattr(segment, "forbidden", []) or [])
            if segment.phase == "qa" and (preserve or forbidden):
                expected.append("constraint-evidence")

            node = ExecutionNode(
                segment_id=segment.id,
                order=segment.order,
                phase=segment.phase,
                scope=list(segment.scope),
                change_surface=segment.change_surface,
                depends_on=[previous_segment_id] if previous_segment_id else [],
                owner_segment_id=segment.inherits_from,
                preserve=preserve,
                forbidden=forbidden,
                expected_output_kinds=expected,
                required_artifact_kinds=list(previous_outputs),
            )
            nodes.append(node)
            previous_segment_id = segment.id
            previous_outputs = expected

        execution = cls(nodes=nodes)
        execution.refresh()
        return execution

    def _node(self, segment_id: str) -> ExecutionNode:
        for node in self.nodes:
            if node.segment_id == segment_id:
                return node
        raise KeyError(f"unknown work segment: {segment_id}")

    def _dependency_artifacts(self, node: ExecutionNode) -> list[ArtifactRef]:
        dependencies = set(node.depends_on)
        return [
            artifact
            for artifact in self.artifacts.values()
            if artifact.producer_segment_id in dependencies
        ]

    def _missing_required_artifacts(self, node: ExecutionNode) -> list[str]:
        available = {artifact.kind for artifact in self._dependency_artifacts(node)}
        return [kind for kind in node.required_artifact_kinds if kind not in available]

    def refresh(self) -> None:
        for node in sorted(self.nodes, key=lambda item: item.order):
            if node.status in {"running", "passed", "failed"}:
                continue
            if not node.depends_on:
                node.status = "runnable"
                node.blocking_reason = None
                continue

            dependencies = [self._node(segment_id) for segment_id in node.depends_on]
            failed = [dep.segment_id for dep in dependencies if dep.status in {"failed", "blocked"}]
            if failed:
                node.status = "blocked"
                node.blocking_reason = "upstream_failed:" + ",".join(failed)
                continue

            waiting = [dep.segment_id for dep in dependencies if dep.status != "passed"]
            if waiting:
                node.status = "pending"
                node.blocking_reason = "waiting_for:" + ",".join(waiting)
                continue

            missing = self._missing_required_artifacts(node)
            if missing:
                node.status = "pending"
                node.blocking_reason = "missing_artifact:" + ",".join(missing)
                continue

            node.status = "runnable"
            node.blocking_reason = None

    def start(self, segment_id: str) -> ExecutionNode:
        self.refresh()
        node = self._node(segment_id)
        if node.status != "runnable":
            raise ExecutionTransitionError(
                f"segment {segment_id} is {node.status}, expected runnable"
                + (f" ({node.blocking_reason})" if node.blocking_reason else "")
            )
        node.status = "running"
        node.blocking_reason = None
        node.attempts += 1
        return node

    def pass_segment(self, segment_id: str, artifacts: Iterable[ArtifactRef]) -> ExecutionNode:
        node = self._node(segment_id)
        if node.status != "running":
            raise ExecutionTransitionError(f"segment {segment_id} is {node.status}, expected running")

        produced = list(artifacts)
        for artifact in produced:
            if artifact.producer_segment_id != segment_id:
                raise ExecutionTransitionError(
                    f"artifact {artifact.id} belongs to {artifact.producer_segment_id}, expected {segment_id}"
                )
        produced_kinds = {artifact.kind for artifact in produced}
        missing = [kind for kind in node.expected_output_kinds if kind not in produced_kinds]
        if missing:
            raise ExecutionTransitionError(
                f"segment {segment_id} cannot pass without expected outputs: {', '.join(missing)}"
            )
        duplicate_ids = [artifact.id for artifact in produced if artifact.id in self.artifacts]
        if duplicate_ids:
            raise ExecutionTransitionError("duplicate artifact ids: " + ", ".join(duplicate_ids))

        for artifact in produced:
            self.artifacts[artifact.id] = artifact
        node.status = "passed"
        node.blocking_reason = None
        self.refresh()
        return node

    def fail_segment(self, segment_id: str, reason: str) -> ExecutionNode:
        node = self._node(segment_id)
        if node.status not in {"running", "runnable"}:
            raise ExecutionTransitionError(
                f"segment {segment_id} is {node.status}, expected runnable or running"
            )
        node.status = "failed"
        node.blocking_reason = reason.strip() or "execution_failed"
        self.refresh()
        return node

    def _descendants_of(self, segment_id: str) -> set[str]:
        affected = {segment_id}
        changed = True
        while changed:
            changed = False
            for node in self.nodes:
                if node.segment_id in affected:
                    continue
                if any(dep in affected for dep in node.depends_on):
                    affected.add(node.segment_id)
                    changed = True
        return affected

    def reset_from(self, segment_id: str) -> list[str]:
        self._node(segment_id)
        affected = self._descendants_of(segment_id)
        for artifact_id, artifact in list(self.artifacts.items()):
            if artifact.producer_segment_id in affected:
                del self.artifacts[artifact_id]
        for node in self.nodes:
            if node.segment_id in affected:
                node.status = "pending"
                node.blocking_reason = None
        self.refresh()
        return [node.segment_id for node in self.nodes if node.segment_id in affected]

    def runnable_segment_ids(self) -> list[str]:
        self.refresh()
        return [node.segment_id for node in self.nodes if node.status == "runnable"]

    def input_artifacts(self, segment_id: str) -> list[ArtifactRef]:
        node = self._node(segment_id)
        required = set(node.required_artifact_kinds)
        return [
            artifact
            for artifact in self._dependency_artifacts(node)
            if artifact.kind in required
        ]

    @property
    def completion_status(self) -> str:
        statuses = {node.status for node in self.nodes}
        if statuses == {"passed"}:
            return "completed"
        if "failed" in statuses:
            return "failed"
        if "blocked" in statuses and not ({"runnable", "running", "pending"} & statuses):
            return "blocked"
        return "in_progress"

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "routing_mode": self.routing_mode,
            "completion_status": self.completion_status,
            "nodes": [
                {
                    **node.to_dict(),
                    "input_artifact_ids": [artifact.id for artifact in self.input_artifacts(node.segment_id)],
                    "output_artifact_ids": [
                        artifact.id
                        for artifact in self.artifacts.values()
                        if artifact.producer_segment_id == node.segment_id
                    ],
                }
                for node in sorted(self.nodes, key=lambda item: item.order)
            ],
            "artifacts": [artifact.to_dict() for artifact in self.artifacts.values()],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> WorkExecutionPlan:
        plan = cls(
            nodes=[ExecutionNode.from_dict(item) for item in payload.get("nodes") or []],
            artifacts={
                artifact.id: artifact
                for artifact in (
                    ArtifactRef.from_dict(item) for item in payload.get("artifacts") or []
                )
            },
            version=str(payload.get("version") or WORK_EXECUTION_VERSION),
            routing_mode=str(payload.get("routing_mode") or "sequence"),
        )
        plan.refresh()
        return plan
