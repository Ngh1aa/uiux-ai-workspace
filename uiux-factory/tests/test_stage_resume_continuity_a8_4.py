from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness, TraceRecorder
from core.runtime.flow_os.managed import ManagedFlowController
from core.runtime.flow_os.provider import ScriptedProvider
from core.runtime.flow_os.provider_runner import ProviderManagedRunner


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills_UIUX"


def _research_run(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    harness = ProviderNeutralAgentHarness(SKILLS_ROOT, project)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal(
        "Build a modern ecommerce website with search and forms",
        authority="branch_write",
        overrides={
            "website_type": "ecommerce",
            "mode": "interactive-prototype",
            "features": ["search", "forms"],
        },
    )
    assert managed.active_stage == "research"
    return harness, manager, managed


def _skill_names(request) -> set[str]:
    return {Path(item["path"]).parent.name for item in request.skill_context}


def test_a8_4_start_stage_is_idempotent_for_current_revision(tmp_path: Path) -> None:
    _harness, manager, managed = _research_run(tmp_path)

    first = manager.start_stage(managed)
    second = manager.start_stage(managed)

    assert second.run_id == first.run_id
    assert managed.stage_runs["research"] == [first.run_id]
    assert managed.state == "RUNNING"


def test_a8_4_managed_resume_preserves_jit_activation_and_observations(tmp_path: Path) -> None:
    harness, manager, managed = _research_run(tmp_path)
    stage_state = manager.start_stage(managed)
    first_runner = ProviderManagedRunner(manager, ScriptedProvider([]))
    trace = TraceRecorder(
        tmp_path / "trace.jsonl",
        stage_state.run_id,
    )

    observations = first_runner._execute_actions(
        managed,
        stage_state,
        [{"tool": "activate_skill_context", "args": {"skill": "ecommerce-website"}}],
        trace,
        dry_run=False,
    )
    assert observations[0]["result"]["accepted"] is True
    assert observations[0]["result"]["activated"] == "ecommerce-website"

    resumed_managed = manager.resume(managed.manager_run_id)
    provider = ScriptedProvider(
        [
            {
                "status": "BLOCKED",
                "actions": [],
                "summary": "fixture stop after resume continuity check",
                "evidence": [],
                "replan_signal": "BLOCKED",
            }
        ]
    )
    resumed_runner = ProviderManagedRunner(manager, provider)
    result = resumed_runner.run_active_stage(
        resumed_managed,
        max_turns=1,
        auto_replan=False,
    )

    assert result.state == "BLOCKED"
    assert len(provider.requests) == 1
    request = provider.requests[0]
    assert "ecommerce-website" in _skill_names(request)
    assert request.task_context["jit_skill_context"]["active_jit_skills"] == ["ecommerce-website"]
    assert request.observations[-1]["tool"] == "activate_skill_context"
    assert request.observations[-1]["result"]["activated"] == "ecommerce-website"
    assert resumed_managed.stage_runs["research"] == [stage_state.run_id]


def test_a8_4_flow_revision_invalidates_prior_stage_checkpoint(tmp_path: Path) -> None:
    harness, manager, managed = _research_run(tmp_path)
    first = manager.start_stage(managed)
    runner = ProviderManagedRunner(manager, ScriptedProvider([]))
    activation = runner._execute_one(
        managed,
        first,
        "activate_skill_context",
        {"skill": "ecommerce-website"},
    )
    assert activation["accepted"] is True
    assert harness.resume(first.run_id).context["jit_active_skills"] == ["ecommerce-website"]

    managed.flow = replace(managed.flow, revision=managed.flow.revision + 1)
    managed.state = "REPLANNED"
    manager._checkpoint_managed(managed)

    second = manager.start_stage(managed)

    assert second.run_id != first.run_id
    assert second.context["flow_revision"] == 1
    assert "jit_active_skills" not in second.context
    assert managed.stage_runs["research"] == [first.run_id, second.run_id]


def test_a8_4_same_revision_checkpoint_metadata_tamper_fails_closed(tmp_path: Path) -> None:
    harness, manager, managed = _research_run(tmp_path)
    stage_state = manager.start_stage(managed)
    stage_state.context["manager_run_id"] = "tampered-manager"
    harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())

    with pytest.raises(ValueError, match="stage checkpoint manager_run_id mismatch"):
        manager.start_stage(managed)

    assert managed.stage_runs["research"] == [stage_state.run_id]


def test_a8_4_future_revision_checkpoint_fails_closed(tmp_path: Path) -> None:
    harness, manager, managed = _research_run(tmp_path)
    stage_state = manager.start_stage(managed)
    stage_state.context["flow_revision"] = managed.flow.revision + 1
    harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())

    with pytest.raises(ValueError, match="is ahead of managed flow revision"):
        manager.start_stage(managed)


def test_a8_4_terminal_same_revision_stage_is_not_implicitly_retried(tmp_path: Path) -> None:
    harness, manager, managed = _research_run(tmp_path)
    stage_state = manager.start_stage(managed)
    stage_state.state = "FAILED"
    harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())

    with pytest.raises(ValueError, match="latest same-revision specialist run is FAILED"):
        manager.start_stage(managed)

    assert managed.stage_runs["research"] == [stage_state.run_id]


def test_a8_4_explicit_sources_cannot_mutate_resumed_stage_context(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / "brief.md").write_text("brief\n", encoding="utf-8")
    (project / "other.md").write_text("other\n", encoding="utf-8")
    harness = ProviderNeutralAgentHarness(SKILLS_ROOT, project)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal(
        "Improve the existing product UI",
        authority="branch_write",
        overrides={"mode": "interactive-prototype"},
    )

    stage_state = manager.start_stage(managed, explicit_sources=["brief.md"])
    assert stage_state.context["loaded_sources"] == ["brief.md"]

    with pytest.raises(ValueError, match="cannot change explicit source context"):
        manager.start_stage(managed, explicit_sources=["other.md"])
