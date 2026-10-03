from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.dogfood.archetype_matrix import PROJECTS
from core.runtime.flow_os.flow import FlowPlanner
from core.runtime.flow_os.task_context import GoalInterpreter


FACTORY_ROOT = Path(__file__).resolve().parents[1]
SKILLS = FACTORY_ROOT.parent / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


def _cases():
    for project in PROJECTS.values():
        for case in project.cases:
            yield project, case


def test_p11_real_task_matrix_covers_all_four_missing_archetypes() -> None:
    archetypes = {
        case.expected_archetype
        for project in PROJECTS.values()
        for case in project.cases
    }
    assert archetypes == {
        "learning-experience",
        "learning-operations",
        "catalog-commerce",
        "checkout-commerce",
    }
    assert set(PROJECTS) == {"edtech", "luxroom"}


@pytest.mark.parametrize(("project", "case"), list(_cases()), ids=lambda value: getattr(value, "case_id", getattr(value, "project_id", str(value))))
def test_p11_real_task_goals_route_through_canonical_interpreter_and_planner(project, case) -> None:
    project.validate()
    profile = GoalInterpreter().interpret(case.goal)

    assert profile.domain == case.expected_domain
    assert profile.product_archetype == case.expected_archetype
    assert profile.change_surface == case.expected_change_surface
    assert f"product_archetype:{case.expected_archetype}" in profile.evidence

    flow = FlowPlanner(SKILLS, POLICY).plan(profile.to_context())
    assert flow.id == case.expected_flow_id
    stages = {stage.id: stage for stage in flow.stages}

    for stage_id, required_skills in case.required_stage_skills:
        assert stage_id in stages
        stage = stages[stage_id]
        for skill in required_skills:
            assert skill in stage.skills
            if skill not in stage.mandatory_skills:
                assert skill in (stage.jit_skills or [])
                assert stage.jit_skill_sources[skill] == "conditional"


def test_p11_platform_token_does_not_create_fake_form_scope_or_feature() -> None:
    case = PROJECTS["edtech"].cases[0]
    profile = GoalInterpreter().interpret(case.goal)

    assert "form" not in profile.scope
    assert "forms" not in profile.features
    assert "scope:form" not in profile.evidence
    assert "feature:forms" not in profile.evidence
    assert profile.change_surface == "PRODUCT"


def test_p11_ecommerce_payment_disambiguation_leaves_only_final_domain_evidence() -> None:
    case = PROJECTS["luxroom"].cases[1]
    profile = GoalInterpreter().interpret(case.goal)

    assert profile.domain == "commerce-retail"
    assert "domain:financial-services" not in profile.evidence
    assert "domain:commerce-retail" in profile.evidence
    assert "domain_disambiguation:generic-payment->commerce-retail" in profile.evidence


def test_p11_dogfood_matrix_uses_actual_owned_target_repositories() -> None:
    assert PROJECTS["edtech"].repo == "Ngh1aa/EdTech"
    assert PROJECTS["luxroom"].repo == "Ngh1aa/LuxRoom"
    assert {"index.html", "app.js", "style.css"}.issubset(PROJECTS["edtech"].evidence_paths)
    assert {"index.html", "detail.html", "cart.html", "checkout.html"}.issubset(PROJECTS["luxroom"].evidence_paths)
