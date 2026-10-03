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


def _plan(goal: str):
    profile = GoalInterpreter().interpret(goal)
    return profile, _planner().plan(profile.to_context())


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


def test_edtech_full_product_infers_learning_platform_and_composes_learning_specialists() -> None:
    profile, plan = _plan(
        "Build an EdTech learning platform with courses, lessons, assignments and student progress."
    )

    assert profile.domain == "education-edtech"
    assert profile.product_archetype == "learning-platform"
    assert plan.id == "professional-website-redesign"

    stages = {stage.id: stage for stage in plan.stages}
    assert {"product-discovery", "complex-workflow-and-progress-ux", "information-architecture"}.issubset(
        set(stages["research"].skills)
    )
    assert {"complex-workflow-and-progress-ux", "interaction-patterns-and-form-ux", "accessibility"}.issubset(
        set(stages["design"].skills)
    )
    assert "state-feedback-and-error-recovery" in stages["implementation"].skills


def test_museum_full_product_infers_visual_discovery_and_composes_visual_specialists() -> None:
    profile, plan = _plan(
        "Build an immersive digital museum experience for artwork discovery, exhibitions and an art collection."
    )

    assert profile.domain == "art-culture"
    assert profile.product_archetype == "visual-discovery-museum"
    assert plan.id == "professional-website-redesign"

    stages = {stage.id: stage for stage in plan.stages}
    assert {"asset-media-and-art-direction", "experience-principles-and-signature-moments"}.issubset(
        set(stages["research"].skills)
    )
    assert "motion-and-microinteractions" in stages["design"].skills
    assert "prototype-visual-experience-qa" in stages["qa"].skills


def test_industrial_full_product_infers_enterprise_service_and_composes_service_specialists() -> None:
    profile, plan = _plan(
        "Build an industrial electric motor repair service website with service request and request a quote flows."
    )

    assert profile.domain == "industrial-services"
    assert profile.product_archetype == "enterprise-service"
    assert plan.id == "professional-website-redesign"

    stages = {stage.id: stage for stage in plan.stages}
    assert {"corporate-website", "service-experience-to-digital-journey", "trust-credibility-and-transparency"}.issubset(
        set(stages["research"].skills)
    )
    assert {"conversion-and-content", "interaction-patterns-and-form-ux"}.issubset(set(stages["design"].skills))
    assert "complex-forms-and-wizards" in stages["implementation"].skills


def test_ecommerce_page_infers_storefront_and_composes_page_specialists() -> None:
    profile, plan = _plan(
        "Redesign one ecommerce product detail page with product gallery, cart, checkout and site search."
    )

    assert profile.website_type == "ecommerce"
    assert profile.product_archetype == "commerce-storefront"
    assert profile.change_surface == "PAGE"
    assert plan.id == "page-ui-work"

    stages = {stage.id: stage for stage in plan.stages}
    assert {"ecommerce-website", "site-search-and-findability", "asset-media-and-art-direction"}.issubset(
        set(stages["research"].skills)
    )
    assert {"journey-driven-content-and-layout", "interaction-patterns-and-form-ux"}.issubset(
        set(stages["design"].skills)
    )
    assert {"media-crop-and-layout-integrity", "state-feedback-and-error-recovery"}.issubset(
        set(stages["qa"].skills)
    )


def test_generic_domain_does_not_receive_unrelated_archetype_specialists() -> None:
    profile, plan = _plan("Build one generic landing page for a newsletter signup.")

    assert profile.product_archetype == "generic"
    all_skills = {skill for stage in plan.stages for skill in stage.skills}
    assert "financial-product-intelligence" not in all_skills
    assert "education-website" not in all_skills
    assert "service-experience-to-digital-journey" not in all_skills
