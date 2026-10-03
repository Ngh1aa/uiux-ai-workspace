from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pytest

from core.dogfood.mixed_domain_matrix import CASES, validate_matrix
from core.runtime.flow_os.flow import FlowPlanner
from core.runtime.flow_os.task_context import GoalInterpreter


FACTORY_ROOT = Path(__file__).resolve().parents[1]
SKILLS = FACTORY_ROOT.parent / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


def _stage_map(flow):
    return {stage.id: stage for stage in flow.stages}


def test_p12_matrix_shape_and_coverage() -> None:
    validate_matrix()
    assert len(CASES) == 12
    assert {case.family for case in CASES} == {"ai-fintech", "saas-commerce", "edtech-enterprise"}
    pairs = defaultdict(list)
    for case in CASES:
        pairs[case.order_pair].append(case)
    assert len(pairs) == 6
    assert all(len(items) == 2 for items in pairs.values())


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.case_id)
def test_p12_explicit_primary_semantics_own_mixed_domain_routing(case) -> None:
    profile = GoalInterpreter().interpret(case.goal)
    assert profile.domain == case.expected_domain
    assert profile.product_archetype == case.expected_archetype
    assert profile.change_surface == case.expected_change_surface
    assert f"domain:{case.expected_domain}" in profile.evidence
    assert f"domain_precedence:explicit-primary->{case.expected_domain}" in profile.evidence
    for secondary in case.expected_secondary_domains:
        assert f"secondary_domain:{secondary}" in profile.evidence

    final_domain_evidence = [item for item in profile.evidence if item.startswith("domain:")]
    assert final_domain_evidence == [f"domain:{case.expected_domain}"]

    flow = FlowPlanner(SKILLS, POLICY).plan(profile.to_context())
    assert flow.id == case.expected_flow_id
    stages = _stage_map(flow)
    for stage_id, required in case.required_stage_skills:
        assert stage_id in stages
        stage_skills = set(stages[stage_id].skills)
        assert set(required).issubset(stage_skills)


def test_p12_word_order_does_not_change_primary_route_or_feature_inference() -> None:
    pairs = defaultdict(list)
    for case in CASES:
        profile = GoalInterpreter().interpret(case.goal)
        flow = FlowPlanner(SKILLS, POLICY).plan(profile.to_context())
        pairs[case.order_pair].append(
            (
                profile.domain,
                profile.product_archetype,
                profile.change_surface,
                flow.id,
                tuple(sorted(profile.features)),
                tuple(sorted(item for item in profile.evidence if item.startswith("secondary_domain:"))),
            )
        )

    for pair_id, outcomes in pairs.items():
        assert len(outcomes) == 2, pair_id
        assert outcomes[0] == outcomes[1], pair_id


def test_p12_payment_orchestration_is_not_agentic_without_agent_language() -> None:
    profile = GoalInterpreter().interpret(
        "Build the whole product. Primary product is a fintech payment orchestration and treasury platform."
    )
    assert profile.domain == "financial-services"
    assert profile.product_archetype == "payments-infrastructure"
    assert "agentic-workflow" not in profile.features


def test_p12_ai_copilot_is_agentic_even_inside_fintech() -> None:
    profile = GoalInterpreter().interpret(
        "Build the whole product. Primary product is a fintech treasury platform. An AI copilot is a supporting capability."
    )
    assert profile.domain == "financial-services"
    assert "agentic-workflow" in profile.features
