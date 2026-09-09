import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from core.contracts.design_context_schema import DesignContext


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

    @property
    def run_dir(self) -> Path:
        return self.root / "runs" / self.run_id

    @property
    def state_path(self) -> Path:
        return self.run_dir / "run.json"

    def initialize(self) -> None:
        if self.state_path.exists():
            raise FileExistsError("Run ID already exists; use a new ID to preserve earlier drafts.")
        self.run_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.status = "running"

        self.save()

    def start_stage(self, stage: str) -> None:
        self.active_stage = stage
        self.save()

    def complete_stage(self, stage: str) -> None:
        if stage not in self.completed_stages:
            self.completed_stages.append(stage)

        self.active_stage = None
        self.save()

    def add_artifact(
        self,
        name: str,
        path: Path,
    ) -> None:
        self.artifacts[name] = str(
            path.resolve()
        )

        self.save()

    def add_error(self, error: Exception) -> None:
        self.errors.append(
            f"{type(error).__name__}: {error}"
        )

        self.status = "failed"
        self.save()

    def complete(self) -> None:
        self.status = "completed"
        self.active_stage = None
        self.save()

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "goal": self.goal,
            "status": self.status,
            "active_stage": self.active_stage,
            "completed_stages": self.completed_stages,
            "artifacts": self.artifacts,
            "errors": self.errors,
        }

    def save(self) -> None:
        """Persist run state without exposing readers to a partially written JSON file."""
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
            # os.replace removes the temporary path on success. This cleanup
            # only handles interrupted/failed writes.
            if temp_path.exists():
                temp_path.unlink()
