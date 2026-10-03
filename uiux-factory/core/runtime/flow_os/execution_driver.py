from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol

from core.runtime.flow_os.sequence_flow import ResolvedWorkPlan, ResolvedWorkSegment
from core.runtime.flow_os.work_execution import ArtifactRef, ExecutionTransitionError, WorkExecutionPlan


EXECUTION_DRIVER_VERSION = "1.0"
RUNNER_RESULT_VERSION = "1.0"
ARTIFACT_CLASSES = frozenset({"file", "report", "screenshot", "commit", "evidence"})
REPAIR_FAILURE_CLASSES = frozenset({"PRODUCT_QA_FAILED"})
REPAIR_CAPABILITIES = (
    "ui-improvement",
    "web-ui-code-review",
    "state-feedback-and-error-recovery",
)


class RunnerContractError(ValueError):
    """Raised when a runner violates the P1.6 request/result contract."""


@dataclass(frozen=True)
class SegmentExecutionRequest:
    schema_version: str
    segment_id: str
    order: int
    phase: str
    intent: str
    scope: list[str]
    change_surface: str
    runner_mode: str
    active_stage_id: str
    agent: str
    skills: list[str]
    mandatory_skills: list[str]
    gates: list[str]
    input_artifacts: list[dict[str, Any]]
    expected_output_kinds: list[str]
    preserve: list[str]
    forbidden: list[str]
    repair_of_segment_id: str | None = None
    repair_failure_artifact_ids: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunnerArtifact:
    id: str
    kind: str
    artifact_class: str
    path: str | None = None
    uri: str | None = None
    digest: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.kind.strip():
            raise RunnerContractError("runner artifact id and kind are required")
        if self.artifact_class not in ARTIFACT_CLASSES:
            raise RunnerContractError(f"unsupported artifact class: {self.artifact_class}")
        if not self.path and not self.uri:
            raise RunnerContractError(f"artifact {self.id} must declare path or uri")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> RunnerArtifact:
        return cls(
            id=str(payload["id"]),
            kind=str(payload["kind"]),
            artifact_class=str(payload.get("artifact_class") or "evidence"),
            path=str(payload["path"]) if payload.get("path") else None,
            uri=str(payload["uri"]) if payload.get("uri") else None,
            digest=str(payload["digest"]) if payload.get("digest") else None,
            metadata={str(k): str(v) for k, v in dict(payload.get("metadata") or {}).items()},
        )


@dataclass(frozen=True)
class RunnerResult:
    schema_version: str
    status: str
    artifacts: list[RunnerArtifact]
    failure_class: str | None = None
    reason: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in {"passed", "failed"}:
            raise RunnerContractError(f"runner status must be passed or failed, got {self.status!r}")
        if self.status == "failed" and not (self.reason or self.failure_class):
            raise RunnerContractError("failed runner result requires reason or failure_class")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> RunnerResult:
        return cls(
            schema_version=str(payload.get("schema_version") or RUNNER_RESULT_VERSION),
            status=str(payload["status"]),
            artifacts=[RunnerArtifact.from_dict(item) for item in payload.get("artifacts") or []],
            failure_class=str(payload["failure_class"]) if payload.get("failure_class") else None,
            reason=str(payload["reason"]) if payload.get("reason") else None,
            metadata={str(k): str(v) for k, v in dict(payload.get("metadata") or {}).items()},
        )


class SegmentRunner(Protocol):
    def run(self, request: SegmentExecutionRequest) -> RunnerResult: ...


@dataclass
class RegistryArtifact:
    id: str
    kind: str
    artifact_class: str
    producer_segment_id: str
    uri: str
    digest: str | None
    metadata: dict[str, str]
    accepted_for_handoff: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> RegistryArtifact:
        return cls(
            id=str(payload["id"]),
            kind=str(payload["kind"]),
            artifact_class=str(payload["artifact_class"]),
            producer_segment_id=str(payload["producer_segment_id"]),
            uri=str(payload["uri"]),
            digest=str(payload["digest"]) if payload.get("digest") else None,
            metadata={str(k): str(v) for k, v in dict(payload.get("metadata") or {}).items()},
            accepted_for_handoff=bool(payload.get("accepted_for_handoff", False)),
        )


class ArtifactRegistry:
    """Persist runner outputs with provenance; only validated outputs become handoff artifacts."""

    def __init__(self, workspace_root: Path | str) -> None:
        self.workspace_root = Path(workspace_root).resolve()
        self.records: dict[str, RegistryArtifact] = {}

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return "sha256:" + digest.hexdigest()

    def ingest(self, segment_id: str, artifacts: list[RunnerArtifact]) -> list[RegistryArtifact]:
        registered: list[RegistryArtifact] = []
        for artifact in artifacts:
            if artifact.id in self.records:
                raise RunnerContractError(f"duplicate registry artifact id: {artifact.id}")
            uri = artifact.uri
            digest = artifact.digest
            metadata = dict(artifact.metadata)
            if artifact.path:
                path = Path(artifact.path)
                if not path.is_absolute():
                    path = (self.workspace_root / path).resolve()
                else:
                    path = path.resolve()
                try:
                    path.relative_to(self.workspace_root)
                except ValueError as exc:
                    raise RunnerContractError(
                        f"artifact {artifact.id} escapes workspace root: {path}"
                    ) from exc
                if not path.is_file():
                    raise RunnerContractError(f"artifact {artifact.id} file does not exist: {path}")
                actual_digest = self._sha256(path)
                if digest and digest != actual_digest:
                    raise RunnerContractError(
                        f"artifact {artifact.id} digest mismatch: declared {digest}, actual {actual_digest}"
                    )
                digest = actual_digest
                uri = path.as_uri()
                metadata.setdefault("workspace_path", str(path.relative_to(self.workspace_root)))
            if not uri:
                raise RunnerContractError(f"artifact {artifact.id} has no resolved uri")
            record = RegistryArtifact(
                id=artifact.id,
                kind=artifact.kind,
                artifact_class=artifact.artifact_class,
                producer_segment_id=segment_id,
                uri=uri,
                digest=digest,
                metadata=metadata,
            )
            self.records[record.id] = record
            registered.append(record)
        return registered

    def mark_accepted(self, artifact_ids: list[str]) -> None:
        for artifact_id in artifact_ids:
            self.records[artifact_id].accepted_for_handoff = True

    def handoff_refs(self, artifact_ids: list[str]) -> list[ArtifactRef]:
        return [
            ArtifactRef(
                id=self.records[artifact_id].id,
                kind=self.records[artifact_id].kind,
                producer_segment_id=self.records[artifact_id].producer_segment_id,
                uri=self.records[artifact_id].uri,
                digest=self.records[artifact_id].digest,
                metadata={
                    **self.records[artifact_id].metadata,
                    "artifact_class": self.records[artifact_id].artifact_class,
                },
            )
            for artifact_id in artifact_ids
        ]

    def failure_artifact_ids(self, segment_id: str) -> list[str]:
        return [
            record.id
            for record in self.records.values()
            if record.producer_segment_id == segment_id and not record.accepted_for_handoff
        ]

    def to_dict(self) -> dict[str, Any]:
        return {"artifacts": [record.to_dict() for record in self.records.values()]}

    @classmethod
    def from_dict(cls, workspace_root: Path | str, payload: dict[str, Any]) -> ArtifactRegistry:
        registry = cls(workspace_root)
        registry.records = {
            record.id: record
            for record in (RegistryArtifact.from_dict(item) for item in payload.get("artifacts") or [])
        }
        return registry


class CommandRunnerAdapter:
    """Run a concrete subprocess against a file-based request/result contract."""

    def __init__(
        self,
        command: list[str],
        *,
        work_dir: Path | str,
        exchange_dir: Path | str,
        timeout_seconds: int = 300,
        extra_env: dict[str, str] | None = None,
    ) -> None:
        if not command:
            raise ValueError("runner command is required")
        self.command = list(command)
        self.work_dir = Path(work_dir).resolve()
        self.exchange_dir = Path(exchange_dir).resolve()
        self.exchange_dir.mkdir(parents=True, exist_ok=True)
        self.timeout_seconds = int(timeout_seconds)
        self.extra_env = dict(extra_env or {})
        self.invocations = 0

    def run(self, request: SegmentExecutionRequest) -> RunnerResult:
        self.invocations += 1
        prefix = f"{request.segment_id}-attempt-{self.invocations}"
        request_path = self.exchange_dir / f"{prefix}-request.json"
        result_path = self.exchange_dir / f"{prefix}-result.json"
        request_path.write_text(json.dumps(request.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        env = os.environ.copy()
        env.update(self.extra_env)
        env.update({
            "UIUX_EXECUTION_REQUEST": str(request_path),
            "UIUX_EXECUTION_RESULT": str(result_path),
            "UIUX_EXECUTION_SEGMENT_ID": request.segment_id,
            "UIUX_EXECUTION_MODE": request.runner_mode,
        })
        completed = subprocess.run(
            self.command,
            cwd=self.work_dir,
            env=env,
            text=True,
            capture_output=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        if not result_path.is_file():
            reason = (
                f"runner exited {completed.returncode} without result contract; "
                f"stderr={completed.stderr.strip()[:500]}"
            )
            return RunnerResult(
                schema_version=RUNNER_RESULT_VERSION,
                status="failed",
                artifacts=[],
                failure_class="RUNNER_CONTRACT_FAILED",
                reason=reason,
                metadata={"returncode": str(completed.returncode)},
            )
        try:
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            result = RunnerResult.from_dict(payload)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise RunnerContractError(f"invalid runner result at {result_path}: {exc}") from exc
        return result


class JsonCheckpointStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, payload: dict[str, Any]) -> None:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=self.path.parent, delete=False, prefix=self.path.name + ".tmp."
        ) as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            temp_path = Path(handle.name)
        temp_path.replace(self.path)

    def load(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))


class ExecutionDriver:
    """Drive one eligible P1.5 node through a real runner and evidence gate at a time."""

    def __init__(
        self,
        work_plan: ResolvedWorkPlan,
        execution_plan: WorkExecutionPlan,
        runner: SegmentRunner,
        registry: ArtifactRegistry,
        *,
        checkpoint_store: JsonCheckpointStore | None = None,
        max_repair_attempts: int = 2,
    ) -> None:
        self.work_plan = work_plan
        self.execution_plan = execution_plan
        self.runner = runner
        self.registry = registry
        self.checkpoint_store = checkpoint_store
        self.max_repair_attempts = max(0, int(max_repair_attempts))
        self.repair_counts: dict[str, int] = {}
        self.repair_context: dict[str, dict[str, Any]] = {}
        self.history: list[dict[str, Any]] = []
        self.plan_fingerprint = self._fingerprint(work_plan)
        self._save_checkpoint()

    @staticmethod
    def _fingerprint(plan: ResolvedWorkPlan) -> str:
        payload = json.dumps(plan.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _segment(self, segment_id: str) -> ResolvedWorkSegment:
        for segment in self.work_plan.segments:
            if segment.id == segment_id:
                return segment
        raise KeyError(f"unknown resolved segment: {segment_id}")

    @staticmethod
    def _active_stage(segment: ResolvedWorkSegment) -> Any:
        active_ids = list(segment.active_stage_ids)
        for stage in segment.flow.stages:
            if stage.id in active_ids:
                return stage
        if segment.flow.stages:
            return segment.flow.stages[0]
        raise RunnerContractError(f"segment {segment.id} exposes no executable flow stage")

    def _request(self, segment_id: str) -> SegmentExecutionRequest:
        segment = self._segment(segment_id)
        node = self.execution_plan._node(segment_id)
        stage = self._active_stage(segment)
        repair = self.repair_context.get(segment_id)
        return SegmentExecutionRequest(
            schema_version=EXECUTION_DRIVER_VERSION,
            segment_id=segment.id,
            order=segment.order,
            phase=segment.phase,
            intent=segment.intent,
            scope=list(segment.scope),
            change_surface=segment.change_surface,
            runner_mode="repair" if repair else "normal",
            active_stage_id=stage.id,
            agent=stage.agent,
            skills=list(stage.skills),
            mandatory_skills=list(stage.mandatory_skills),
            gates=list(stage.gates),
            input_artifacts=[artifact.to_dict() for artifact in self.execution_plan.input_artifacts(segment_id)],
            expected_output_kinds=list(node.expected_output_kinds),
            preserve=list(node.preserve),
            forbidden=list(node.forbidden),
            repair_of_segment_id=str(repair["qa_segment_id"]) if repair else None,
            repair_failure_artifact_ids=list(repair.get("failure_artifact_ids", [])) if repair else [],
            required_capabilities=list(REPAIR_CAPABILITIES) if repair else [],
        )

    def _repair_owner(self, qa_segment_id: str) -> str | None:
        qa_node = self.execution_plan._node(qa_segment_id)
        before = [node for node in self.execution_plan.nodes if node.order < qa_node.order]
        for phase in ("implementation", "design"):
            for node in reversed(before):
                if node.phase != phase:
                    continue
                if not qa_node.scope or not node.scope or set(qa_node.scope).intersection(node.scope):
                    return node.segment_id
        return None

    def _save_checkpoint(self) -> None:
        if not self.checkpoint_store:
            return
        self.checkpoint_store.save({
            "version": EXECUTION_DRIVER_VERSION,
            "plan_fingerprint": self.plan_fingerprint,
            "execution_plan": self.execution_plan.to_dict(),
            "artifact_registry": self.registry.to_dict(),
            "repair_counts": dict(self.repair_counts),
            "repair_context": dict(self.repair_context),
            "history": list(self.history),
        })

    def run_next(self) -> dict[str, Any] | None:
        runnable = self.execution_plan.runnable_segment_ids()
        if not runnable:
            self._save_checkpoint()
            return None
        segment_id = runnable[0]
        request = self._request(segment_id)
        self.execution_plan.start(segment_id)
        self._save_checkpoint()

        try:
            result = self.runner.run(request)
            records = self.registry.ingest(segment_id, result.artifacts)
        except (RunnerContractError, OSError, subprocess.SubprocessError) as exc:
            self.execution_plan.fail_segment(segment_id, f"runner_contract_error:{exc}")
            event = {
                "segment_id": segment_id,
                "runner_mode": request.runner_mode,
                "status": "failed",
                "failure_class": "RUNNER_CONTRACT_FAILED",
                "reason": str(exc),
                "artifact_ids": [],
            }
            self.history.append(event)
            self._save_checkpoint()
            return event

        record_ids = [record.id for record in records]
        event = {
            "segment_id": segment_id,
            "runner_mode": request.runner_mode,
            "status": result.status,
            "failure_class": result.failure_class,
            "reason": result.reason,
            "artifact_ids": record_ids,
            "active_stage_id": request.active_stage_id,
            "agent": request.agent,
            "skills": list(request.skills),
        }

        if result.status == "passed":
            try:
                refs = self.registry.handoff_refs(record_ids)
                self.execution_plan.pass_segment(segment_id, refs)
                self.registry.mark_accepted(record_ids)
                self.repair_context.pop(segment_id, None)
            except ExecutionTransitionError as exc:
                self.execution_plan.fail_segment(segment_id, f"runner_output_gate_failed:{exc}")
                event["status"] = "failed"
                event["failure_class"] = "RUNNER_OUTPUT_GATE_FAILED"
                event["reason"] = str(exc)
        else:
            self.execution_plan.fail_segment(
                segment_id,
                result.reason or result.failure_class or "runner_failed",
            )
            if request.phase == "qa" and result.failure_class in REPAIR_FAILURE_CLASSES:
                owner = self._repair_owner(segment_id)
                if owner:
                    count = self.repair_counts.get(owner, 0)
                    if count < self.max_repair_attempts:
                        self.repair_counts[owner] = count + 1
                        failure_ids = self.registry.failure_artifact_ids(segment_id)
                        self.execution_plan.reset_from(owner)
                        self.repair_context[owner] = {
                            "qa_segment_id": segment_id,
                            "failure_class": result.failure_class,
                            "failure_artifact_ids": failure_ids,
                        }
                        event["repair_owner_segment_id"] = owner
                        event["repair_attempt"] = self.repair_counts[owner]

        self.history.append(event)
        self._save_checkpoint()
        return event

    def run_until_blocked(self, *, max_steps: int = 100) -> str:
        for _ in range(max(1, int(max_steps))):
            if self.execution_plan.completion_status == "completed":
                break
            if not self.execution_plan.runnable_segment_ids():
                break
            self.run_next()
        self._save_checkpoint()
        return self.execution_plan.completion_status

    def checkpoint_payload(self) -> dict[str, Any]:
        return {
            "version": EXECUTION_DRIVER_VERSION,
            "plan_fingerprint": self.plan_fingerprint,
            "execution_plan": self.execution_plan.to_dict(),
            "artifact_registry": self.registry.to_dict(),
            "repair_counts": dict(self.repair_counts),
            "repair_context": dict(self.repair_context),
            "history": list(self.history),
        }

    @classmethod
    def resume(
        cls,
        work_plan: ResolvedWorkPlan,
        runner: SegmentRunner,
        *,
        workspace_root: Path | str,
        checkpoint_store: JsonCheckpointStore,
        max_repair_attempts: int = 2,
    ) -> ExecutionDriver:
        payload = checkpoint_store.load()
        expected = cls._fingerprint(work_plan)
        if payload.get("plan_fingerprint") != expected:
            raise RunnerContractError("checkpoint plan fingerprint does not match resolved work plan")
        driver = cls(
            work_plan,
            WorkExecutionPlan.from_dict(dict(payload["execution_plan"])),
            runner,
            ArtifactRegistry.from_dict(workspace_root, dict(payload.get("artifact_registry") or {})),
            checkpoint_store=checkpoint_store,
            max_repair_attempts=max_repair_attempts,
        )
        driver.repair_counts = {str(k): int(v) for k, v in dict(payload.get("repair_counts") or {}).items()}
        driver.repair_context = {str(k): dict(v) for k, v in dict(payload.get("repair_context") or {}).items()}
        driver.history = [dict(item) for item in payload.get("history") or []]
        driver._save_checkpoint()
        return driver
