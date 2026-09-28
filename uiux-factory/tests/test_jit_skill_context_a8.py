from __future__ import annotations

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
    assert managed.flow.id == "professional-website-redesign"
    assert managed.active_stage == "research"
    stage_state = manager.start_stage(managed)
    runner = ProviderManagedRunner(manager, ScriptedProvider([]))
    return harness, manager, managed, stage_state, runner


def _skill_names(request) -> set[str]:
    return {Path(item["path"]).parent.name for item in request.skill_context}


def test_a8_initial_provider_context_loads_mandatory_skills_only(tmp_path: Path) -> None:
    _harness, _manager, managed, stage_state, runner = _research_run(tmp_path)
    stage = next(item for item in managed.flow.stages if item.id == "research")

    assert "website-audit-and-redesign" in stage.mandatory_skills
    assert "ecommerce-website" in stage.skills
    assert "ecommerce-website" not in stage.mandatory_skills

    request = runner._request(managed, stage_state, [])
    loaded = _skill_names(request)
    jit = request.task_context["jit_skill_context"]

    assert "website-audit-and-redesign" in loaded
    assert "ecommerce-website" not in loaded
    assert "ecommerce-website" in jit["available_jit_skills"]
    assert jit["active_jit_skills"] == []
    assert jit["authority_effect"] == "none"
    assert jit["gate_effect"] == "none"
    assert jit["evidence_effect"] == "none"
    assert "activate_skill_context" in {tool["name"] for tool in request.tools}


def test_a8_activation_loads_only_flow_routed_skill_on_next_turn(tmp_path: Path) -> None:
    _harness, _manager, managed, stage_state, runner = _research_run(tmp_path)

    first = runner._request(managed, stage_state, [])
    assert "ecommerce-website" not in _skill_names(first)

    result = runner._execute_one(
        managed,
        stage_state,
        "activate_skill_context",
        {"skill": "ecommerce-website"},
    )
    assert result["activated"] == "ecommerce-website"
    assert result["available_next_turn"] is True
    assert result["authority_effect"] == "none"
    assert result["gate_effect"] == "none"
    assert result["evidence_effect"] == "none"

    second = runner._request(managed, stage_state, [])
    assert "ecommerce-website" in _skill_names(second)
    jit = second.task_context["jit_skill_context"]
    assert "ecommerce-website" in jit["active_jit_skills"]
    assert "ecommerce-website" not in jit["available_jit_skills"]


def test_a8_provider_cannot_activate_skill_outside_current_flow_stage(tmp_path: Path) -> None:
    _harness, _manager, managed, stage_state, runner = _research_run(tmp_path)

    with pytest.raises(ValueError, match="not in the Flow-routed JIT pool"):
        runner._execute_one(
            managed,
            stage_state,
            "activate_skill_context",
            {"skill": "accessibility"},
        )


def test_a8_activation_limit_is_policy_owned(tmp_path: Path) -> None:
    harness, _manager, managed, stage_state, runner = _research_run(tmp_path)
    harness.policy_doc["jit_skill_context"]["max_active_per_stage"] = 1

    runner._execute_one(
        managed,
        stage_state,
        "activate_skill_context",
        {"skill": "ecommerce-website"},
    )
    with pytest.raises(ValueError, match="activation limit reached"):
        runner._execute_one(
            managed,
            stage_state,
            "activate_skill_context",
            {"skill": "conversion-and-content"},
        )


def test_a8_activation_is_context_state_not_trusted_gate_evidence(tmp_path: Path) -> None:
    _harness, _manager, managed, stage_state, runner = _research_run(tmp_path)
    trace = TraceRecorder(tmp_path / "trace.jsonl", stage_state.run_id)

    observations = runner._execute_actions(
        managed,
        stage_state,
        [{"tool": "activate_skill_context", "args": {"skill": "ecommerce-website"}}],
        trace,
        dry_run=False,
    )

    assert stage_state.context.get("evidence_records", []) == []
    assert "evidence_id" not in observations[0]
    assert observations[0]["result"]["evidence_effect"] == "none"


def test_a8_disabled_policy_preserves_pre_a8_eager_context(tmp_path: Path) -> None:
    harness, _manager, managed, stage_state, runner = _research_run(tmp_path)
    harness.policy_doc["jit_skill_context"]["enabled"] = False

    request = runner._request(managed, stage_state, [])
    loaded = _skill_names(request)
    jit = request.task_context["jit_skill_context"]

    assert "ecommerce-website" in loaded
    assert jit["enabled"] is False
    assert jit["available_jit_skills"] == []
    assert "activate_skill_context" not in {tool["name"] for tool in request.tools}


def test_a8_tampered_checkpoint_cannot_inject_unrouted_skill(tmp_path: Path) -> None:
    _harness, _manager, managed, stage_state, runner = _research_run(tmp_path)
    stage_state.context["jit_active_skills"] = ["accessibility"]

    with pytest.raises(ValueError, match="non-routed JIT skills"):
        runner._request(managed, stage_state, [])
