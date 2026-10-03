from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.runtime.flow_os.flow import FlowPlanner
from core.runtime.flow_os.task_context import GoalInterpreter


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("goal", "expected_domain", "expected_archetype"),
    [
        (
            "Build an EdTech course platform with lessons, quizzes and learning paths",
            "education-edtech",
            "learning-experience",
        ),
        (
            "Build a museum visual archive for artwork collection discovery",
            "art-culture",
            "collection-discovery",
        ),
        (
            "Build a B2B enterprise operations platform with admin dashboard and approval workflow",
            "enterprise-software",
            "enterprise-operations",
        ),
        (
            "Build an ecommerce store with product catalog, cart and checkout",
            "commerce-retail",
            "checkout-commerce",
        ),
    ],
)
def test_p11_goal_interpreter_owns_specialist_taxonomy(
    goal: str,
    expected_domain: str,
    expected_archetype: str,
) -> None:
    profile = GoalInterpreter().interpret(goal)

    assert profile.domain == expected_domain
    assert profile.product_archetype == expected_archetype
    assert f"domain:{expected_domain}" in profile.evidence
    assert f"product_archetype:{expected_archetype}" in profile.evidence


def test_p11_direct_flowplanner_gets_page_specialists_without_factory_adapter() -> None:
    interpreter = GoalInterpreter()
    planner = FlowPlanner(SKILLS, POLICY)
    profile = interpreter.interpret(
        "Create a fintech landing page for payment settlement with a lead form and motion"
    )

    resolved = planner.plan(profile.to_context())

    assert profile.change_surface == "PAGE"
    assert resolved.id == "page-ui-work"
    research = next(stage for stage in resolved.stages if stage.id == "research")
    design = next(stage for stage in resolved.stages if stage.id == "design")
    implementation = next(stage for stage in resolved.stages if stage.id == "implementation")
    assert "financial-product-intelligence" in research.skills
    assert "responsive-and-device-strategy" in design.skills
    assert "interaction-patterns-and-form-ux" in design.skills
    assert "motion-and-microinteractions" in design.skills
    assert "complex-forms-and-wizards" in implementation.skills


def test_p11_direct_flowplanner_gets_full_product_museum_specialists() -> None:
    interpreter = GoalInterpreter()
    planner = FlowPlanner(SKILLS, POLICY)
    profile = interpreter.interpret(
        "Build a museum platform for artwork collection discovery, visual archive and artist browsing"
    )

    resolved = planner.plan(profile.to_context())

    assert profile.change_surface == "PRODUCT"
    assert resolved.id == "professional-website-redesign"
    design = next(stage for stage in resolved.stages if stage.id == "design")
    implementation = next(stage for stage in resolved.stages if stage.id == "implementation")
    assert "asset-media-and-art-direction" in design.skills
    assert "experience-principles-and-signature-moments" in design.skills
    assert "site-search-and-findability" in implementation.skills


def test_p11_factory_adapter_matches_direct_canonical_runtime() -> None:
    goal = "Build a B2B enterprise operations platform with admin dashboard, approval workflow and forms"
    interpreter = GoalInterpreter()
    profile = interpreter.interpret(goal)
    direct = FlowPlanner(SKILLS, POLICY).plan(profile.to_context())

    adapter = ProfessionalWebsiteFlow(SKILLS)
    adapter_profile, adapter_flow = adapter.resolve(goal)

    assert not hasattr(adapter, "specialist_composer")
    assert adapter_profile.to_context() == profile.to_context()
    assert adapter_flow.to_dict() == direct.to_dict()


def test_p11_direct_runtime_is_deterministic_and_specialists_are_jit() -> None:
    goal = "Build an ecommerce store with product catalog, search, cart and checkout"
    profile = GoalInterpreter().interpret(goal)
    planner = FlowPlanner(SKILLS, POLICY)

    first = planner.plan(profile.to_context())
    second = planner.plan(profile.to_context())

    assert first.to_dict() == second.to_dict()
    for stage in first.stages:
        assert len(stage.skills) == len(set(stage.skills))
        assert len(stage.jit_skills or []) == len(set(stage.jit_skills or []))
        for skill in stage.jit_skills or []:
            if skill in {
                "conversion-and-content",
                "site-search-and-findability",
                "interaction-patterns-and-form-ux",
                "complex-forms-and-wizards",
                "state-feedback-and-error-recovery",
            }:
                assert stage.jit_skill_sources[skill] == "conditional"


def test_p11_exclude_skills_cannot_be_readded_by_specialist_composition() -> None:
    goal = "Build a museum platform for artwork collection discovery and artist browsing"
    profile = GoalInterpreter().interpret(goal)
    planner = FlowPlanner(SKILLS, POLICY)

    resolved = planner.plan(
        profile.to_context(),
        exclude_skills=["site-search-and-findability"],
    )

    for stage in resolved.stages:
        assert "site-search-and-findability" not in stage.skills
        assert "site-search-and-findability" not in (stage.jit_skills or [])
