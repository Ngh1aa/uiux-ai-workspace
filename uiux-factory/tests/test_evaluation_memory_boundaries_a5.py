from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.file_tools import WorkspaceFileError, WorkspaceFileTools
from core.runtime.flow_os.flow import ReplanDecision
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
    _git(root, "config", "user.email", "a5-boundary@example.test")
    _git(root, "config", "user.name", "A5 Boundary Test")
    (root / "app.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")
    return root.resolve()


def test_a5_provider_file_tools_cannot_poison_runtime_memory(tmp_path: Path) -> None:
    project = _repo(tmp_path)
    tools = WorkspaceFileTools(project)
    with pytest.raises(WorkspaceFileError, match="generated/internal directory"):
        tools.write_text(
            ".uiux-agent-runs/memory/evaluation-memory.json",
            '{"schema_version":1,"records":[]}',
        )


def test_a5_prior_evaluation_insight_never_enters_replanning_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = _repo(tmp_path)
    harness = ProviderNeutralAgentHarness(SKILLS, project)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal(
        "Fix button spacing",
        authority="branch_write",
        overrides={"change_surface": "MICRO"},
    )
    managed.task_context["prior_evaluation_insight"] = {
        "advisory_only": True,
        "sample_size": 999,
        "recurrent_failure_channels": [{"channel": "pretend", "count": 999}],
    }
    captured: dict = {}

    def fake_replan(flow, signal, context, replan_count):
        captured.update(context)
        return ReplanDecision(False, signal, "test boundary")

    monkeypatch.setattr(manager.planner, "replan", fake_replan)
    decision = manager.replan(
        managed,
        "GATE_FAIL",
        context_updates={"prior_evaluation_insight": {"attempted": "override"}},
        apply=False,
    )

    assert decision.accepted is False
    assert "prior_evaluation_insight" not in captured
    assert captured["current_stage"] == managed.active_stage
