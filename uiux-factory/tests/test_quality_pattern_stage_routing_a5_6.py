from __future__ import annotations

import subprocess
from pathlib import Path

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
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
    _git(root, "config", "user.email", "a5-6-memory@example.test")
    _git(root, "config", "user.name", "A5.6 Memory Test")
    (root / "app.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")
    return root.resolve()


def _report() -> dict:
    return {
        "schema_version": 1,
        "evaluator": "touch-target-metrics",
        "requirements": {
            "RESPONSIVE-003": {
                "outcome": "failed",
                "applicable": True,
                "test_targets": ["/@mobile"],
            }
        },
    }


def _manager(tmp_path: Path) -> tuple[ManagedFlowController, object]:
    project = _repo(tmp_path)
    harness = ProviderNeutralAgentHarness(SKILLS, project)
    manager = ManagedFlowController(harness)
    manager.evaluation_memory.record_post_render_report(_report())
    return manager, harness


def test_a5_6_research_stage_never_receives_quality_memory(tmp_path: Path) -> None:
    manager, harness = _manager(tmp_path)
    managed = manager.start_from_goal(
        "Redesign the full SaaS marketing website",
        authority="branch_write",
        overrides={
            "mode": "visual-prototype",
            "website_type": "saas",
            "change_surface": "MULTI_PAGE",
        },
    )

    assert managed.active_stage == "research"
    assert "prior_quality_insight" not in managed.task_context
    manager_checkpoint = harness.resume(managed.manager_run_id)
    assert isinstance(manager_checkpoint.context.get("prior_quality_insight"), dict)

    stage_state = manager.start_stage(managed)
    assert stage_state.agent == "research"
    assert "prior_quality_insight" not in stage_state.context
    assert "prior_quality_insight" not in managed.task_context


def test_a5_6_quality_memory_is_injected_when_implementation_stage_starts(tmp_path: Path) -> None:
    manager, harness = _manager(tmp_path)
    managed = manager.start_from_goal(
        "Redesign the full SaaS marketing website",
        authority="branch_write",
        overrides={
            "mode": "visual-prototype",
            "website_type": "saas",
            "change_surface": "MULTI_PAGE",
        },
    )

    research = manager.start_stage(managed)
    research.state = "COMPLETED"
    harness.checkpoints.save(research.run_id, research.to_dict())
    assert manager.complete_stage(managed) == "design"

    assert "prior_quality_insight" not in managed.task_context
    design = manager.start_stage(managed)
    assert design.agent == "implementation"
    quality = design.context.get("prior_quality_insight")
    assert isinstance(quality, dict)
    assert quality["advisory_only"] is True
    assert quality["recurrent_attention_patterns"][0]["requirement_id"] == "RESPONSIVE-003"
    assert managed.task_context["prior_quality_insight"] == quality


def test_a5_6_routing_removes_quality_memory_if_run_returns_to_research(tmp_path: Path) -> None:
    manager, harness = _manager(tmp_path)
    managed = manager.start_from_goal(
        "Redesign the full SaaS marketing website",
        authority="branch_write",
        overrides={
            "mode": "visual-prototype",
            "website_type": "saas",
            "change_surface": "MULTI_PAGE",
        },
    )

    research = manager.start_stage(managed)
    research.state = "COMPLETED"
    harness.checkpoints.save(research.run_id, research.to_dict())
    manager.complete_stage(managed)
    design = manager.start_stage(managed)
    assert "prior_quality_insight" in managed.task_context

    managed.active_stage = "research"
    managed.state = "REPLANNED"
    manager._checkpoint_managed(managed)
    returned_research = manager.start_stage(managed)
    assert returned_research.agent == "research"
    assert "prior_quality_insight" not in returned_research.context
    assert "prior_quality_insight" not in managed.task_context


def test_a5_6_quality_routing_does_not_change_authority_or_gate_contract(tmp_path: Path) -> None:
    manager, harness = _manager(tmp_path)
    managed = manager.start_from_goal(
        "Fix button spacing on the current website",
        authority="branch_write",
        overrides={"change_surface": "MICRO"},
    )
    before_authority = managed.authority
    before_flow = managed.flow.to_dict()

    stage_state = manager.start_stage(managed)
    quality = stage_state.context.get("prior_quality_insight")
    assert isinstance(quality, dict)
    assert quality["authority_effect"] == "none"
    assert quality["flow_effect"] == "none"
    assert quality["gate_effect"] == "none"
    assert quality["replan_effect"] == "none"
    assert managed.authority == before_authority
    assert managed.flow.to_dict() == before_flow
