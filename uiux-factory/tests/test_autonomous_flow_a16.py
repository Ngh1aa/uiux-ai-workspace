from __future__ import annotations

import subprocess
from pathlib import Path

from core.runtime.flow_os.autonomous import AutonomousFlowRunner, audit_project_truth
from core.runtime.flow_os.provider import ScriptedProvider


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills_UIUX"


def _git_project(root: Path) -> Path:
    project = root / "project"
    project.mkdir()
    (project / "README.md").write_text("# Fixture\n\nExisting product UI.\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=project, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "ci@example.com"], cwd=project, check=True)
    subprocess.run(["git", "config", "user.name", "CI"], cwd=project, check=True)
    subprocess.run(["git", "add", "README.md"], cwd=project, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=project, check=True, capture_output=True)
    return project


def test_a16_audit_is_bounded_to_existing_source_truth(tmp_path: Path) -> None:
    project = _git_project(tmp_path)
    (project / "PROJECT-CONTEXT.md").write_text("# Context\n", encoding="utf-8")
    audit = audit_project_truth(project)
    assert audit.source_truth == ("PROJECT-CONTEXT.md", "README.md")
    assert audit.git_repository is True
    assert audit.package_project is False


def test_a16_prompt_to_audit_plan_execute_qa_uses_canonical_flow(tmp_path: Path) -> None:
    project = _git_project(tmp_path)
    provider = ScriptedProvider(
        [
            {
                "status": "PASS",
                "actions": [{"tool": "read_text", "args": {"path": "README.md"}}],
                "summary": "Audited project truth.",
                "evidence": ["runtime read observation"],
                "replan_signal": None,
            },
            {
                "status": "PASS",
                "actions": [
                    {
                        "tool": "write_artifact",
                        "args": {
                            "path": "docs/uiux/autonomous-proof.md",
                            "content": "# Autonomous proof\n\nBounded implementation artifact.\n",
                        },
                    }
                ],
                "summary": "Executed bounded implementation work.",
                "evidence": ["runtime file change"],
                "replan_signal": None,
            },
            {
                "status": "PASS",
                "actions": [
                    {"tool": "read_text", "args": {"path": "docs/uiux/autonomous-proof.md"}}
                ],
                "summary": "QA inspected the implemented artifact.",
                "evidence": ["runtime QA read"],
                "replan_signal": None,
            },
        ]
    )
    runner = AutonomousFlowRunner(
        skills_root=SKILLS_ROOT,
        project_root=project,
        provider=provider,
    )
    result = runner.start(
        "Improve the existing navigation component without redesigning the whole product.",
        overrides={
            "intent": "improve",
            "change_surface": "FOCUSED",
            "mode": "interactive-prototype",
        },
        explicit_sources=["README.md"],
        auto_replan=False,
    )

    assert result.flow_id == "existing-ui-improvement"
    assert result.state == "COMPLETED"
    assert result.completed_stages == ("research", "implementation", "qa")
    assert result.lifecycle == ("audit", "plan", "execute", "qa")
    assert result.recovery_snapshot is not None
    assert result.workspace is not None
    assert len(provider.requests) == 3
    assert [request.stage_id for request in provider.requests] == [
        "research",
        "implementation",
        "qa",
    ]
    assert not (project / "docs" / "uiux" / "autonomous-proof.md").exists()
    assert "does not authorize merge/deploy/release" in result.truth_boundary


def test_a16_blocked_provider_stops_without_merging_source(tmp_path: Path) -> None:
    project = _git_project(tmp_path)
    head_before = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    provider = ScriptedProvider(
        [
            {
                "status": "BLOCKED",
                "actions": [],
                "summary": "Missing source truth.",
                "evidence": [],
                "replan_signal": "BLOCKED",
            }
        ]
    )
    result = AutonomousFlowRunner(
        skills_root=SKILLS_ROOT,
        project_root=project,
        provider=provider,
    ).start(
        "Improve the existing navigation component.",
        overrides={
            "intent": "improve",
            "change_surface": "FOCUSED",
            "mode": "interactive-prototype",
        },
        explicit_sources=["README.md"],
        auto_replan=False,
    )
    head_after = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    assert result.state == "BLOCKED"
    assert result.recovery_snapshot is not None
    assert head_before == head_after
