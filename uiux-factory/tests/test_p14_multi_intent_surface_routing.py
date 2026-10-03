from __future__ import annotations

from pathlib import Path

import pytest

from core.dogfood.multi_surface_matrix import CASES, validate_matrix
from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.runtime.flow_os.flow import AmbiguousRoutingError
from core.runtime.flow_os.sequence_flow import MultiSurfaceRoutingError


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


def _factory() -> ProfessionalWebsiteFlow:
    return ProfessionalWebsiteFlow(SKILLS)


def test_p14_matrix_is_balanced_and_valid() -> None:
    validate_matrix()
    assert len(CASES) == 17
    assert sum(case.expected_mode == "sequence" for case in CASES) == 14
    assert sum(case.expected_mode == "single" for case in CASES) == 3
    assert {case.family for case in CASES} == {
        "lifecycle-chain",
        "mixed-surface",
        "constraints",
        "localization",
        "single-control",
    }


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.case_id)
def test_p14_sequence_contract_matches_declared_work_owners(case) -> None:
    contract = _factory().resolve_contract(case.goal)
    assert contract.routing_mode == case.expected_mode

    if case.expected_mode == "single":
        assert contract.segments == []
        return

    assert len(contract.segments) == len(case.expected_segments)
    for actual, expected in zip(contract.segments, case.expected_segments, strict=True):
        assert actual.phase == expected.phase
        assert actual.intent == expected.intent
        assert tuple(actual.scope) == expected.scope
        assert actual.change_surface == expected.surface
        assert actual.order >= 1
        for token in case.preserve_contains:
            assert any(token in value for value in (actual.preserve or []))
        for token in case.forbidden_contains:
            assert any(token in value for value in (actual.forbidden or []))


def test_p14_sequence_plans_each_segment_through_smallest_credible_flow() -> None:
    factory = _factory()
    for case in CASES:
        if case.expected_mode != "sequence":
            continue
        profile, work_plan = factory.resolve_work_plan(case.goal)
        assert profile.routing_status == "resolved"
        assert work_plan.routing_mode == "sequence"
        assert len(work_plan.segments) == len(case.expected_segments)
        for actual, expected in zip(work_plan.segments, case.expected_segments, strict=True):
            assert actual.flow.id == expected.flow_id
            assert actual.change_surface == expected.surface
            assert expected.active_stage in actual.active_stage_ids


def test_p14_single_flow_api_fails_closed_instead_of_collapsing_sequence() -> None:
    factory = _factory()
    goal = "Audit the landing page, redesign checkout, implement it, and QA it."
    with pytest.raises(MultiSurfaceRoutingError) as caught:
        factory.resolve(goal)
    assert len(caught.value.segment_ids) == 4


def test_p14_implementation_and_qa_inherit_previous_change_owner() -> None:
    contract = _factory().resolve_contract(
        "Audit the landing page, redesign checkout, implement it, and QA it."
    )
    redesign = contract.segments[1]
    implementation = contract.segments[2]
    qa = contract.segments[3]

    assert implementation.inherits_from == redesign.id
    assert qa.inherits_from == redesign.id
    assert implementation.scope == redesign.scope == ["checkout"]
    assert qa.scope == redesign.scope
    assert implementation.change_surface == qa.change_surface == redesign.change_surface == "PAGE"


def test_p14_initial_audit_without_object_forward_inherits_design_target() -> None:
    contract = _factory().resolve_contract(
        "Audit first → redesign the whole product → implement it → QA it."
    )
    audit, redesign, *_ = contract.segments
    assert audit.phase == "audit"
    assert audit.inherits_from == redesign.id
    assert audit.intent == redesign.intent == "redesign"
    assert audit.change_surface == redesign.change_surface == "PRODUCT"


def test_p14_constraints_are_global_but_do_not_become_fake_work_segments() -> None:
    contract = _factory().resolve_contract(
        "Fix the hero and redesign checkout; keep animation unchanged; do not change navigation."
    )
    assert len(contract.segments) == 2
    assert [segment.phase for segment in contract.segments] == ["design", "design"]
    for segment in contract.segments:
        assert any("animation" in value for value in (segment.preserve or []))
        assert any("navigation" in value for value in (segment.forbidden or []))


def test_p14_factory_stage_skill_resolution_only_uses_active_sequence_phases() -> None:
    factory = _factory()
    goal = "Audit the landing page, redesign checkout, implement it, and QA it."

    _profile, research_skills, _ = factory.resolve_skill_names("research", goal)
    _profile, design_skills, _ = factory.resolve_skill_names("art_direction", goal)
    _profile, implementation_skills, _ = factory.resolve_skill_names("implementation", goal)
    _profile, qa_skills, _ = factory.resolve_skill_names("visual_qa", goal)

    assert "audience-intent-and-top-tasks" in research_skills
    assert "visual-design-direction" in design_skills
    assert "frontend-implementation" in implementation_skills
    assert "visual-regression-and-design-drift" in qa_skills


def test_p14_single_task_controls_keep_existing_resolution_path() -> None:
    factory = _factory()
    for case in CASES:
        if case.expected_mode != "single":
            continue
        profile, flow = factory.resolve(case.goal)
        assert profile.routing_status == "resolved"
        assert flow.id


def test_p14_p13_domain_ambiguity_still_blocks_sequence_until_truth_exists() -> None:
    factory = _factory()
    goal = (
        "Audit an AI workspace for fintech treasury, redesign its dashboard, implement it, and QA it."
    )
    contract = factory.resolve_contract(goal)
    assert contract.routing_mode == "sequence"
    assert contract.profile.routing_status == "ambiguous"
    with pytest.raises(AmbiguousRoutingError):
        factory.resolve_work_plan(goal)


def test_p14_target_truth_can_resolve_domain_before_sequence_planning() -> None:
    factory = _factory()
    goal = (
        "Audit an AI workspace for fintech treasury, redesign its dashboard, implement it, and QA it."
    )
    truth = {
        "domain": "ai-software",
        "product_archetype": "ai-workspace",
        "source": "p1.4-fixture",
    }
    profile, work_plan = factory.resolve_work_plan(goal, target_truth=truth)

    assert profile.routing_status == "resolved"
    assert profile.domain == "ai-software"
    assert profile.resolution_source == "target-project-truth"
    assert len(work_plan.segments) == 4
    assert all(segment.flow.id for segment in work_plan.segments)


def test_p14_work_order_is_preserved_not_sorted_by_surface_size() -> None:
    contract = _factory().resolve_contract(
        "Redesign checkout and fix hero typography, preserve animation unchanged."
    )
    assert [segment.change_surface for segment in contract.segments] == ["PAGE", "FOCUSED"]
    assert [segment.order for segment in contract.segments] == [1, 2]
