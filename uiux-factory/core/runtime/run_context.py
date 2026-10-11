import json
import hashlib
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from core.contracts.design_context_schema import DesignContext
from core.events.run_event_bus import RunEventBus
from core.runtime.flow_os.execution_driver import ExecutionGrant, POLICY_PATH
from core.runtime.flow_os.agent import PermissionGate, ToolSpec
from core.runtime.flow_os.task_context import GoalInterpreter


def require_frozen_specification(context) -> tuple[Path, Path]:
    paths = []
    for key in ("full_build_spec", "implementation_prompt_spec", "spec_manifest"):
        raw = context.artifacts.get(key)
        if not raw:
            raise RuntimeError(f"Required artifact missing: {key}")
        path = Path(raw)
        if not path.is_file():
            raise RuntimeError(f"Required artifact not found: {path}")
        paths.append(path)
    spec, prompt, manifest_path = paths
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as error:
        raise RuntimeError("Frozen spec manifest is invalid; recompile specification.") from error
    if not isinstance(manifest, dict):
        raise RuntimeError("Frozen spec manifest must be an object; recompile specification.")
    if (manifest.get("frozen") is not True
            or Path(str(manifest.get("source_of_truth", ""))).resolve() != spec.resolve()
            or manifest.get("full_build_spec_sha256") != hashlib.sha256(spec.read_bytes()).hexdigest()
            or not spec.read_text(encoding="utf-8").strip()
            or "02-FULL-BUILD-SPEC.md" not in prompt.read_text(encoding="utf-8")):
        raise RuntimeError("Frozen specification is missing, invalid or stale; recompile specification.")
    return spec, prompt


def require_native_execution_grant(context) -> None:
    grant = getattr(context, "execution_grant", None)
    authority = grant.authority if isinstance(grant, ExecutionGrant) else ""
    if GoalInterpreter().interpret(context.goal).authority == "read_only":
        authority = "read_only"
    allowed, reason = PermissionGate(POLICY_PATH).authorize(
        ToolSpec("native_executor", "Implementation/repair executor", "HIGH_WRITE", "branch_write", True), authority)
    if not allowed:
        raise RuntimeError("Native executor authority denied: " + reason)
    if grant.approval_mode == "manual":
        spec, _ = require_frozen_specification(context)
        if getattr(context, "execution_approval", None) != hashlib.sha256(spec.read_bytes()).hexdigest():
            raise RuntimeError("AWAITING_APPROVAL: execution approval is missing or stale for the frozen spec")


@dataclass
class RunContext:
    root: Path
    goal: str

    run_id: str = field(
        default_factory=lambda: datetime.now().strftime(
            "%Y%m%d-%H%M%S"
        ) + "-" + uuid4().hex[:8]
    )

    design_context: DesignContext = field(default_factory=DesignContext)
    runtime_preset: str = "standard"
    execution_grant: ExecutionGrant | None = None
    execution_approval: str | None = None

    status: str = "created"
    active_stage: str | None = None

    completed_stages: list[str] = field(
        default_factory=list
    )

    artifacts: dict[str, str] = field(
        default_factory=dict
    )

    errors: list[str] = field(
        default_factory=list
    )

    _event_bus: RunEventBus | None = field(
        default=None,
        init=False,
        repr=False,
        compare=False,
    )

    @property
    def run_dir(self) -> Path:
        return self.root / "runs" / self.run_id

    @property
    def state_path(self) -> Path:
        return self.run_dir / "run.json"

    def event_bus(self) -> RunEventBus:
        if self._event_bus is None:
            self._event_bus = RunEventBus(
                event_path=self.run_dir / "events.jsonl",
                run_id=self.run_id,
            )
        return self._event_bus

    def initialize(self) -> None:
        if self.state_path.exists():
            raise FileExistsError("Run ID already exists; use a new ID to preserve earlier drafts.")
        self.run_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.status = "running"
        bus = self.event_bus()
        self.artifacts["events"] = str(bus.event_path.resolve())
        bus.emit(
            "run.created",
            data={
                "runtime_preset": self.runtime_preset,
            },
        )
        self.save()

    def start_stage(self, stage: str) -> None:
        self.event_bus().emit("stage.started", stage=stage)
        self.active_stage = stage
        self.save()

    def complete_stage(self, stage: str) -> None:
        self.event_bus().emit("stage.completed", stage=stage)
        if stage not in self.completed_stages:
            self.completed_stages.append(stage)

        self.active_stage = None
        self.save()

    def add_artifact(
        self,
        name: str,
        path: Path,
    ) -> None:
        resolved = str(path.resolve())
        self.event_bus().emit(
            "artifact.registered",
            data={"name": name, "path": resolved},
        )
        self.artifacts[name] = resolved
        self.save()

    def add_error(self, error: Exception) -> None:
        message = f"{type(error).__name__}: {error}"
        self.event_bus().emit(
            "run.failed",
            data={"error": message},
        )
        self.errors.append(message)
        self.status = "failed"
        self.active_stage = None
        self.save()

    def complete(self) -> None:
        self.event_bus().emit("run.completed")
        self.status = "completed"
        self.active_stage = None
        self.save()

    def projected_state(self) -> dict[str, Any]:
        return self.event_bus().project_run_state()

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "goal": self.goal,
            "runtime_preset": self.runtime_preset,
            "execution_grant": ({"authority": self.execution_grant.authority,
                                  "approval_mode": self.execution_grant.approval_mode}
                                 if self.execution_grant else None),
            "execution_approval": self.execution_approval,
            "status": self.status,
            "active_stage": self.active_stage,
            "completed_stages": self.completed_stages,
            "artifacts": self.artifacts,
            "errors": self.errors,
        }

    def save(self) -> None:
        """Persist a fast run snapshot; the append-only event log remains the chronology."""
        self.run_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = json.dumps(
            self.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
        temp_path = self.state_path.with_name(
            f".{self.state_path.name}.{uuid4().hex}.tmp"
        )

        try:
            with temp_path.open(
                "w",
                encoding="utf-8",
                newline="\n",
            ) as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())

            os.replace(temp_path, self.state_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()
