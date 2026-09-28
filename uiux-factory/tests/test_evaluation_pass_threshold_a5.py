from __future__ import annotations

import subprocess
from pathlib import Path

from core.evaluation.run_evaluator import RunEvaluator
from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.evidence import EvidenceRecord
from core.runtime.flow_os.managed import ManagedFlowController


FACTORY = Path(__file__).resolve().parents[1]
SKILLS = FACTORY.parent / "skills_UIUX"


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir(parents=True)
    _git(root, "init")
    _git(root, "config", "user.email", "a5-pass@example.test")
    _git(root, "config", "user.name", "A5 Pass Test")
    (root / "app.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")
    return root.resolve()


def test_a5_completed_run_with_observation_only_is_insufficient_evidence(tmp_path: Path) -> None:
    project = _repo(tmp_path)
    harness = ProviderNeutralAgentHarness(SKILLS, project)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal(
        "Inspect current button spacing",
        authority="read_only",
        overrides={"change_surface": "MICRO"},
    )
    stage = manager.start_stage(managed)
    stage.context["evidence_records"] = [
        EvidenceRecord(
            id="observed-read",
            type="file_read",
            stage_id=managed.active_stage,
            tool="read_text",
            status="OBSERVED",
            summary="runtime read a file",
            data={"path": "app.txt"},
        ).to_dict()
    ]
    harness.checkpoints.save(stage.run_id, stage.to_dict())
    managed.state = "COMPLETED"

    evaluation = RunEvaluator().evaluate(managed, harness)

    assert evaluation.outcome == "insufficient_evidence"
    assert evaluation.status_counts == {"OBSERVED": 1}
    assert evaluation.passing_evidence_types == []
    assert evaluation.memory_eligible is False
