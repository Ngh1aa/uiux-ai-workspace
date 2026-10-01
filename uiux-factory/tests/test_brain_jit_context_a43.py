from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.brain_os.adapters.jit_context import (
    project_stage_jit_context,
    request_jit_activation,
)
from core.runtime.flow_os.flow import FlowPlanner, ResolvedStage
from core.runtime.flow_os.provider_runner import ProviderManagedRunner


FACTORY = Path(__file__).resolve().parents[1]
WORKSPACE = FACTORY.parent
SKILLS = WORKSPACE / "skills_UIUX"


def _policy() -> dict[str, object]:
    return json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


def _planner() -> FlowPlanner:
    return FlowPlanner(SKILLS, _policy())


def _page_research_stage() -> ResolvedStage:
    flow = _planner().plan(
        {
            "intent": "build",
            "website_type": "landing",
            "domain": "generic",
            "product_archetype": "generic",
            "validation_lane": "prototype",
            "mode": "interactive-prototype",
            "risk": "normal",
            "features": [],
            "scope": ["landing-page"],
            "change_surface": "PAGE",
        }
    )
    return next(stage for stage in flow.stages if stage.id == "research")


def test_a43_jit_context_projects_canonical_resolved_stage_and_policy_limits(monkeypatch: pytest.MonkeyPatch) -> None:
    policy = _policy()
    stage = _page_research_stage()
    plan = project_stage_jit_context(stage, policy)

    assert plan.stage_id == stage.id
    assert plan.agent == stage.agent
    assert plan.mandatory_skills == stage.mandatory_skills
    assert plan.routed_jit_skills == stage.jit_skills
    assert plan.jit_skill_sources == stage.jit_skill_sources
    assert plan.active_jit_skills == []
    assert plan.available_jit_skills == stage.jit_skills
    assert plan.active_skill_names == stage.mandatory_skills
    assert plan.max_active_per_stage == 6
    assert plan.provider_document_char_policy_ceiling == 180000
    assert plan.max_sections_per_skill == 64
    assert plan.max_section_chars == 12000
    assert plan.max_retrievals_per_stage == 24
    assert plan.max_total_retrieved_chars == 120000
    assert plan.max_index_chars == 60000
    assert plan.authority_effect == plan.gate_effect == plan.evidence_effect == "none"

    monkeypatch.delenv("UIUX_PROVIDER_CONTEXT_CHARS", raising=False)
    runner = object.__new__(ProviderManagedRunner)
    runner.harness = SimpleNamespace(policy_doc=policy)
    runtime_enabled, runtime_max_active = runner._jit_config()
    runtime_char_limit, runtime_source = runner._provider_context_budget()

    assert plan.jit_enabled is runtime_enabled
    assert plan.max_active_per_stage == runtime_max_active
    assert plan.provider_document_char_policy_ceiling == runtime_char_limit
    assert runtime_source == "runtime_policy"


def test_a43_jit_context_allows_only_flow_routed_non_mandatory_skills() -> None:
    stage = _page_research_stage()
    plan = project_stage_jit_context(stage, _policy())
    assert plan.routed_jit_skills, "representative PAGE research stage should expose a JIT pool"

    skill = plan.routed_jit_skills[0]
    request = request_jit_activation(plan, skill)

    assert request.skill == skill
    assert request.source == plan.jit_skill_sources[skill]
    assert request.already_active is False
    assert request.active_count_before == 0
    assert request.active_count_after == 1
    assert request.runtime_preflight_required is True
    assert request.authority_effect == request.gate_effect == request.evidence_effect == "none"

    with pytest.raises(ValueError, match="mandatory and already active"):
        request_jit_activation(plan, plan.mandatory_skills[0])

    with pytest.raises(ValueError, match="not in the Flow-routed JIT pool"):
        request_jit_activation(plan, "made-up-unrouted-skill")


def test_a43_jit_context_rejects_checkpoint_style_active_skills_outside_routed_pool() -> None:
    stage = _page_research_stage()
    with pytest.raises(ValueError, match="not in the routed stage pool"):
        project_stage_jit_context(stage, _policy(), active_jit_skills=["made-up-unrouted-skill"])


def test_a43_jit_context_enforces_max_active_per_stage_before_runtime_preflight() -> None:
    stage = ResolvedStage(
        id="qa",
        agent="qa",
        purpose="synthetic bounded JIT stage",
        skills=["m1", "j1", "j2", "j3"],
        mandatory_skills=["m1"],
        jit_skills=["j1", "j2", "j3"],
        jit_skill_sources={"j1": "optional", "j2": "conditional", "j3": "additional"},
        gates=[],
    )
    policy = _policy()
    policy = dict(policy)
    policy["jit_skill_context"] = {"enabled": True, "max_active_per_stage": 2}

    with pytest.raises(ValueError, match="exceeds runtime-policy max_active_per_stage"):
        project_stage_jit_context(stage, policy, active_jit_skills=["j1", "j2", "j3"])

    plan = project_stage_jit_context(stage, policy, active_jit_skills=["j1", "j2"])
    with pytest.raises(ValueError, match="activation limit reached"):
        request_jit_activation(plan, "j3")


def test_a43_disabled_jit_mode_exposes_full_routed_pool_as_already_active() -> None:
    stage = _page_research_stage()
    policy = _policy()
    policy = dict(policy)
    policy["jit_skill_context"] = {"enabled": False, "max_active_per_stage": 6}

    plan = project_stage_jit_context(stage, policy)

    assert plan.jit_enabled is False
    assert plan.active_jit_skills == plan.routed_jit_skills
    assert plan.available_jit_skills == []
    assert plan.active_skill_names == stage.mandatory_skills + stage.jit_skills

    if plan.routed_jit_skills:
        with pytest.raises(ValueError, match="disabled by runtime policy"):
            request_jit_activation(plan, plan.routed_jit_skills[0])


def test_a43_already_active_skill_request_is_idempotent_and_needs_no_runtime_preflight() -> None:
    stage = _page_research_stage()
    first = stage.jit_skills[0]
    plan = project_stage_jit_context(stage, _policy(), active_jit_skills=[first])

    request = request_jit_activation(plan, first)

    assert request.already_active is True
    assert request.active_count_before == request.active_count_after == 1
    assert request.runtime_preflight_required is False


def test_a43_invalid_runtime_policy_shapes_fail_closed() -> None:
    stage = _page_research_stage()

    bad_jit = _policy()
    bad_jit = dict(bad_jit)
    bad_jit["jit_skill_context"] = {"enabled": True, "max_active_per_stage": 0}
    with pytest.raises(ValueError, match="between 1 and 32"):
        project_stage_jit_context(stage, bad_jit)

    bad_provider = _policy()
    bad_provider = dict(bad_provider)
    bad_provider["provider_context"] = {"max_document_chars_per_request": 0}
    with pytest.raises(ValueError, match="between 1 and 2000000"):
        project_stage_jit_context(stage, bad_provider)
