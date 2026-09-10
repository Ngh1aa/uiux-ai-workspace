import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from core.contracts.design_context_schema import DesignContext
from core.events.run_event_bus import RunEventBus


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

    def _finalize_prototype_acceptance(self) -> None:
        """Create the 56-rule evidence ledger before a quality run can complete.

        Intelligence-only runs intentionally have no quality-loop artifact and skip this
        step. Full runs bind the acceptance report to the final BrowserQA/VisualCritic
        evidence referenced by quality-loop.json. Only implemented machine requirements
        can block completion in V1; planned/manual requirements remain explicit in the
        ledger and therefore cannot be mistaken for final approval.
        """
        quality_raw = self.artifacts.get("quality_loop")
        if not quality_raw:
            return

        quality_path = Path(quality_raw)
        if not quality_path.is_file():
            raise RuntimeError(f"Quality-loop artifact is missing: {quality_path}")

        from core.contracts.quality_loop_schema import QualityLoopResult
        from core.verification.prototype_acceptance import PrototypeAcceptanceEvaluator

        quality = QualityLoopResult.model_validate_json(
            quality_path.read_text(encoding="utf-8")
        )
        if not quality.browser_report_path or not quality.visual_critic_path:
            raise RuntimeError(
                "Completed full run has no final BrowserQA/VisualCritic evidence for prototype acceptance."
            )

        report = PrototypeAcceptanceEvaluator().evaluate(
            run_id=self.run_id,
            browser_report_path=Path(quality.browser_report_path),
            visual_critic_path=Path(quality.visual_critic_path),
        )
        acceptance_path = self.run_dir / "prototype-acceptance.json"
        acceptance_path.write_text(
            report.model_dump_json(indent=2),
            encoding="utf-8",
        )
        self.add_artifact("prototype_acceptance", acceptance_path)
        self.event_bus().emit(
            "verification.prototype_acceptance",
            data={
                "machine_status": report.machine_status,
                "final_status": report.final_status,
                "project_digest": report.project_digest,
                "passed": report.summary.passed,
                "failed": report.summary.failed,
                "cantTell": report.summary.cantTell,
                "untested": report.summary.untested,
                "blocking_requirement_ids": report.blocking_requirement_ids,
                "human_review_requirement_ids": report.human_review_requirement_ids,
            },
        )

        if report.machine_status != "passed":
            raise RuntimeError(
                "Prototype machine acceptance blocked completion: "
                + ", ".join(report.blocking_requirement_ids)
            )

    def complete(self) -> None:
        self._finalize_prototype_acceptance()
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