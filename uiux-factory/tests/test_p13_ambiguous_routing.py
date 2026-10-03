from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.dogfood.ambiguous_domain_matrix import CASES, validate_matrix
from core.runtime.flow_os.flow import AmbiguousRoutingError, FlowPlanner
from core.runtime.flow_os.task_context import GoalInterpreter


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


def _planner() -> FlowPlanner:
    return FlowPlanner(SKILLS, POLICY)


def _stage_map(flow):
    return {stage.id: stage for stage in flow.stages}


def test_p13_matrix_is_balanced_and_valid() -> None:
    validate_matrix()
    assert len(CASES) == 18
    assert sum(case.expected_status == "ambiguous" for case in CASES) == 12
    assert sum(case.expected_status == "resolved" for case in CASES) == 6
    assert {case.family for case in CASES} == {
        "ai-fintech",
        "saas-commerce",
        "edtech-enterprise",
    }


@pytest.mark.parametrize("case", [case for case in CASES if case.expected_status == "ambiguous"], ids=lambda case: case.case_id)
def test_p13_unowned_mixed_domain_tasks_fail_closed(case) -> None:
    profile = GoalInterpreter().interpret(case.goal)
    context = profile.to_context()
    inference = context["inference"]

    assert profile.routing_status == "ambiguous"
    assert profile.domain == "unresolved"
    assert profile.product_archetype == "unresolved"
    assert profile.candidate_domains == list(case.expected_candidates)
    assert profile.resolution_source == "needs-evidence"
    assert profile.confidence <= 0.50
    assert inference["routing_status"] == "ambiguous"
    assert inference["candidate_domains"] == list(case.expected_candidates)
    assert f"domain_conflict:{'|'.join(case.expected_candidates)}" in profile.evidence
    assert "routing_action:needs-evidence" in profile.evidence

    with pytest.raises(AmbiguousRoutingError) as caught:
        _planner().plan(context)
    assert caught.value.candidate_domains == case.expected_candidates


@pytest.mark.parametrize("case", [case for case in CASES if case.expected_status == "resolved"], ids=lambda case: case.case_id)
def test_p13_target_truth_resolves_ambiguity_before_flow_planning(case) -> None:
    profile = GoalInterpreter().interpret(case.goal, target_truth=case.target_truth)
    context = profile.to_context()

    assert profile.routing_status == "resolved"
    assert profile.domain == case.target_truth_domain
    assert profile.product_archetype == case.target_truth_archetype
    assert profile.candidate_domains == list(case.expected_candidates)
    assert profile.resolution_source == "target-project-truth"
    assert profile.confidence >= 0.85
    assert f"domain_conflict:{'|'.join(case.expected_candidates)}" in profile.evidence
    assert f"routing_resolution:target-truth->{case.target_truth_domain}" in profile.evidence
    assert "routing_action:needs-evidence" not in profile.evidence

    flow = _planner().plan(context)
    stages = _stage_map(flow)
    for stage_id, required in case.required_stage_skills:
        assert stage_id in stages
        assert set(required).issubset(set(stages[stage_id].skills))


def test_p13_word_order_does_not_turn_ambiguity_into_a_fake_owner() -> None:
    pairs: dict[str, list[tuple[object, ...]]] = {}
    for case in CASES:
        if not case.order_pair:
            continue
        profile = GoalInterpreter().interpret(case.goal)
        signature = (
            profile.routing_status,
            tuple(profile.candidate_domains),
            profile.domain,
            profile.product_archetype,
            profile.change_surface,
            tuple(sorted(profile.features)),
            profile.confidence,
        )
        pairs.setdefault(case.order_pair, []).append(signature)

    assert pairs
    for pair, signatures in pairs.items():
        assert len(signatures) == 2, pair
        assert signatures[0] == signatures[1], pair


def test_p13_mismatched_target_truth_does_not_force_an_unrelated_domain() -> None:
    goal = "Build the whole product: an AI workspace with AI copilot for fintech treasury and payment orchestration."
    profile = GoalInterpreter().interpret(
        goal,
        target_truth={
            "domain": "art-culture",
            "product_archetype": "collection-discovery",
            "source": "bad-fixture",
        },
    )

    assert profile.routing_status == "ambiguous"
    assert profile.domain == "unresolved"
    assert profile.product_archetype == "unresolved"
    assert profile.resolution_source == "needs-evidence"
    assert "target_truth_mismatch:art-culture" in profile.evidence
    with pytest.raises(AmbiguousRoutingError):
        _planner().plan(profile.to_context())


def test_p13_p12_explicit_primary_ownership_still_wins() -> None:
    goal = (
        "Build the whole product. Primary product is an AI workspace for financial analysts. "
        "Banking and treasury data are supporting content; include an AI copilot."
    )
    profile = GoalInterpreter().interpret(goal)

    assert profile.routing_status == "resolved"
    assert profile.domain == "ai-software"
    assert profile.product_archetype == "ai-workspace"
    assert profile.candidate_domains == []
    assert profile.confidence == 0.95
    assert "domain_precedence:explicit-primary->ai-software" in profile.evidence
    _planner().plan(profile.to_context())


def test_p13_p11_generic_checkout_payment_remains_commerce_not_ambiguous() -> None:
    goal = "Build the whole ecommerce checkout with cart, payment form, order review and confirmation."
    profile = GoalInterpreter().interpret(goal)

    assert profile.routing_status == "resolved"
    assert profile.domain == "commerce-retail"
    assert profile.product_archetype == "checkout-commerce"
    assert profile.candidate_domains == []
    assert "domain_disambiguation:generic-payment->commerce-retail" in profile.evidence
    _planner().plan(profile.to_context())
