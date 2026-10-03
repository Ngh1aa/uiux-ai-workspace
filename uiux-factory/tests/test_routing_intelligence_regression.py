from __future__ import annotations

import json
from pathlib import Path

from core.runtime.flow_os.flow import FlowPlanner
from core.runtime.flow_os.task_context import GoalInterpreter


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


def _planner() -> FlowPlanner:
    policy = json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))
    return FlowPlanner(SKILLS, policy)


def test_sentry_audit_routes_as_read_only_fraud_operations_not_portfolio_site() -> None:
    goal = (
        "Audit existing Sentry fintech and fraud operations console, audit-only and read-only. "
        "This is a high-fidelity fintech and fraud operations portfolio project. "
        "Review the fraud case queue, transaction table, risk score, dispute and chargeback flows, "
        "3DS case review dashboard. Do not change code."
    )

    profile = GoalInterpreter().interpret(goal)

    assert profile.intent == "audit"
    assert profile.authority == "read_only"
    assert profile.website_type == "saas"
    assert profile.domain == "financial-services"
    assert profile.product_archetype == "trust-safety-risk"
    assert profile.risk == "high"
    assert profile.validation_lane == "evidence-led"
    assert "dashboard" in profile.features
    assert "data-tables" in profile.features
    assert "website_type:portfolio" not in profile.evidence


def test_sentry_audit_uses_non_mutating_flow_and_risk_specialists() -> None:
    goal = (
        "Audit existing Sentry fintech fraud operations console, audit-only. "
        "Inspect the case queue, transaction table, chargeback and dispute review dashboard. "
        "Do not change code."
    )
    profile = GoalInterpreter().interpret(goal)
    plan = _planner().plan(profile.to_context())

    assert plan.id == "audit-review"
    assert [stage.id for stage in plan.stages] == ["research", "qa"]

    research = plan.stages[0]
    qa = plan.stages[1]

    assert {
        "financial-product-intelligence",
        "trust-credibility-and-transparency",
        "data-tables-and-enterprise-ux",
        "complex-workflow-and-progress-ux",
        "security-and-privacy",
        "data-visualization-and-dashboard-ux",
    }.issubset(set(research.skills))
    assert {
        "data-tables-and-enterprise-ux",
        "state-feedback-and-error-recovery",
        "security-and-privacy",
        "data-visualization-and-dashboard-ux",
    }.issubset(set(qa.skills))


def test_existing_ui_improvement_composes_trust_safety_specialists() -> None:
    context = {
        "intent": "improve",
        "change_surface": "FOCUSED",
        "website_type": "saas",
        "domain": "financial-services",
        "product_archetype": "trust-safety-risk",
        "validation_lane": "evidence-led",
        "mode": "interactive-prototype",
        "risk": "high",
        "features": ["dashboard", "data-tables"],
    }

    plan = _planner().plan(context)

    assert plan.id == "existing-ui-improvement"
    research, implementation, qa = plan.stages
    assert "financial-product-intelligence" in research.skills
    assert "complex-workflow-and-progress-ux" in research.skills
    assert "data-tables-and-enterprise-ux" in implementation.skills
    assert "state-feedback-and-error-recovery" in implementation.skills
    assert "security-and-privacy" in qa.skills
    assert "data-visualization-and-dashboard-ux" in qa.skills


def test_domain_language_review_does_not_hijack_build_intent() -> None:
    profile = GoalInterpreter().interpret(
        "Build a fintech fraud case review dashboard with a case queue and transaction table."
    )

    assert profile.intent == "build"
    assert profile.product_archetype == "trust-safety-risk"
    assert profile.website_type == "saas"


def test_explicit_portfolio_website_still_routes_as_portfolio() -> None:
    profile = GoalInterpreter().interpret(
        "Build a personal portfolio website with project case studies and a contact form."
    )

    assert profile.intent == "build"
    assert profile.website_type == "portfolio"
