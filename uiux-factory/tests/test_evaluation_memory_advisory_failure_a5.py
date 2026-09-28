from __future__ import annotations

import subprocess
from pathlib import Path

from core.evaluation.run_evaluator import RunEvaluation
from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.evidence import EvidenceRecord
from core.runtime.flow_os.managed import ManagedFlowController


FACTORY = Path(__file__).resolve().parents[1]
SKILLS = FACTORY.parent / "skills_UIUX"


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir(parents=True)
    _git(root, "init")
    _git(root, "config", "user.email", "a5-advisory@example.test")
    _git(root, "config", "user.name", "A5 Advisory Test")
    (root / "app.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")
    return root.resolve()


def _corrupt_memory(project: Path) -> Path:
    memory_dir = project / ".uiux-agent-runs" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    path = memory_dir / "evaluation-memory.json"
    path.write_text("{not-json", encoding="utf-8")
    return path


def test_a5_corrupt_memory_does_not_block_new_run_or_flow_selection(tmp_path: Path) -> None:
    project = _repo(tmp_path)
    _corrupt_memory(project)
    harness = ProviderNeutralAgentHarness(SKILLS, project)
    manager = ManagedFlowController(harness)

    managed = manager.start_from_goal(
        "Fix button spacing",
        authority="branch_write",
        overrides={"change_surface": "MICRO"},
    )

    assert managed.state == "READY"
    assert managed.flow.id == "micro-ui-change"
    assert "prior_evaluation_insight" not in managed.task_context
    checkpoint = harness.resume(managed.manager_run_id)
    assert "evaluation memory is unreadable" in checkpoint.context["evaluation_memory_error"]


def test_a5_memory_write_failure_does_not_change_terminal_outcome(tmp_path: Path) -> None:
    project = _repo(tmp_path)
    harness = ProviderNeutralAgentHarness(SKILLS, project)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal(
        "Fix button spacing",
        authority="branch_write",
        overrides={"change_surface": "MICRO"},
    )
    stage = manager.start_stage(managed)
    stage.context["evidence_records"] = [
        EvidenceRecord(
            id="trusted-fail",
            type="validator_result",
            stage_id=managed.active_stage,
            tool="run_validator",
            status="FAIL",
            summary="validator failed",
            data={"name": "validate-runtime", "returncode": 1},
        ).to_dict()
    ]
    stage.state = "FAILED"
    harness.checkpoints.save(stage.run_id, stage.to_dict())
    _corrupt_memory(project)

    managed.state = "FAILED"
    manager._checkpoint_managed(managed)

    checkpoint = harness.resume(managed.manager_run_id)
    evaluation = RunEvaluation.from_dict(checkpoint.context["run_evaluation"])
    assert checkpoint.state == "FAILED"
    assert managed.state == "FAILED"
    assert evaluation.outcome == "failed"
    assert checkpoint.context["evaluation_memory_recorded"] is False
    assert "evaluation memory is unreadable" in checkpoint.context["evaluation_memory_error"]
