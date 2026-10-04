from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.runtime.flow_os.external_task import build_external_task_manifest
from core.runtime.flow_os.flow import FlowPlanner
from core.runtime.flow_os.task_context import GoalInterpreter
from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow


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


@pytest.mark.parametrize("goal", [
    "Audit existing Sentry fraud console, read-only; recommend fixes for the case queue.",
    "Chỉ audit Sentry fraud console; đề xuất task sửa lỗi, không thay đổi code.",
    "Review the existing Sentry fraud dashboard and propose improvements.",
    "Validate Sentry fraud dashboard with a transaction table.",
    "Research Sentry fraud dashboard and transaction table.",
    "QA Sentry fraud dashboard and transaction table.",
])
def test_read_only_findings_never_select_implementation(goal: str) -> None:
    profile = GoalInterpreter().interpret(goal)
    assert profile.intent in {"audit", "review", "research", "validate", "qa"}
    assert profile.authority == "read_only"
    manifest = build_external_task_manifest(
        SKILLS, _planner().policy_doc, goal, "Ngh1aa/Sentry", authority="branch_write",
    )
    assert manifest.authority == "read_only"
    assert manifest.resolved_flow["id"] == "audit-review"
    assert [stage["id"] for stage in manifest.stages] == ["research", "qa"]


def test_read_only_audit_survives_mutating_routing_override() -> None:
    manifest = build_external_task_manifest(
        SKILLS, _planner().policy_doc,
        "Audit existing Sentry fraud dashboard with a transaction table, read-only.",
        "Ngh1aa/Sentry", authority="read_only", overrides={"intent": "fix"},
    )
    assert manifest.authority == "read_only"
    assert manifest.task_contract["intent"] == "audit"
    assert manifest.task_contract["routing_provenance"]["field_sources"]["intent"] == "authority_boundary"
    assert manifest.resolved_flow["id"] == "audit-review"
    assert [stage["id"] for stage in manifest.stages] == ["research", "qa"]


def test_read_only_build_routing_probe_preserves_composition_without_write_authority() -> None:
    manifest = build_external_task_manifest(
        SKILLS, _planner().policy_doc,
        "Build a whole product for fintech fraud operations with a dashboard and transaction table.",
        "Ngh1aa/Sentry", authority="read_only",
    )
    assert manifest.authority == "read_only"
    assert manifest.task_contract["intent"] == "build"
    assert manifest.resolved_flow["id"] == "professional-website-redesign"
    assert "implementation" in [stage["id"] for stage in manifest.stages]
    assert manifest.evidence_boundary["manifest_is_not_qa_pass"] is True


def test_audit_and_qa_sequence_has_no_mutating_stages() -> None:
    profile, work_plan = ProfessionalWebsiteFlow(SKILLS).resolve_work_plan(
        "Audit Sentry fraud dashboard, then QA Sentry transaction table."
    )
    assert profile.authority == "read_only"
    assert work_plan.routing_mode == "sequence"
    assert len(work_plan.segments) == 2
    for segment in work_plan.segments:
        assert segment.flow.id == "audit-review"
        assert [stage.id for stage in segment.flow.stages] == ["research", "qa"]


@pytest.mark.parametrize("surface", ["PAGE", "PRODUCT"])
def test_sentry_specialists_use_canonical_composer_on_broader_surfaces(surface: str) -> None:
    context = GoalInterpreter().interpret(
        "Build a fintech fraud case review dashboard with a transaction table."
    ).to_context()
    context["change_surface"] = surface
    plan = _planner().plan(context)
    assert plan.id == ("page-ui-work" if surface == "PAGE" else "professional-website-redesign")
    for stage in plan.stages:
        assert len(stage.skills) == len(set(stage.skills))
        assert set(stage.mandatory_skills).isdisjoint(stage.jit_skills)
        assert "security-and-privacy" in stage.skills
    assert "complex-workflow-and-progress-ux" in plan.stages[0].skills
    assert "state-feedback-and-error-recovery" in plan.stages[-1].skills


def test_edtech_full_product_composes_learning_experience_specialists() -> None:
    profile, plan = _plan(
        "Build an EdTech learning platform with courses, lessons, assignments and student progress."
    )

    assert profile.domain == "education-edtech"
    assert profile.product_archetype == "learning-experience"
    assert plan.id == "professional-website-redesign"

    stages = {stage.id: stage for stage in plan.stages}
    assert {"product-discovery", "complex-workflow-and-progress-ux", "information-architecture"}.issubset(
        set(stages["research"].skills)
    )
    assert {"complex-workflow-and-progress-ux", "interaction-patterns-and-form-ux", "accessibility"}.issubset(
        set(stages["design"].skills)
    )
    assert "state-feedback-and-error-recovery" in stages["implementation"].skills


def test_museum_full_product_composes_collection_discovery_specialists() -> None:
    profile, plan = _plan(
        "Build an immersive digital museum for artwork collection discovery, visual archive and artist browsing."
    )

    assert profile.domain == "art-culture"
    assert profile.product_archetype == "collection-discovery"
    assert plan.id == "professional-website-redesign"

    stages = {stage.id: stage for stage in plan.stages}
    assert {"design-reference-research-and-benchmark", "asset-media-and-art-direction"}.issubset(
        set(stages["research"].skills)
    )
    assert "motion-and-microinteractions" in stages["design"].skills
    assert "prototype-visual-experience-qa" in stages["qa"].skills


def test_industrial_full_product_composes_service_operations_specialists() -> None:
    profile, plan = _plan(
        "Build an industrial electric motor repair service website with service request and request a quote flows."
    )

    assert profile.domain == "industrial-services"
    assert profile.product_archetype == "b2b-service-operations"
    assert plan.id == "professional-website-redesign"

    stages = {stage.id: stage for stage in plan.stages}
    assert {"service-experience-to-digital-journey", "audience-intent-and-top-tasks"}.issubset(
        set(stages["research"].skills)
    )
    assert {"conversion-and-content", "interaction-patterns-and-form-ux"}.issubset(set(stages["design"].skills))
    assert "complex-forms-and-wizards" in stages["implementation"].skills


def test_ecommerce_page_composes_checkout_commerce_specialists() -> None:
    profile, plan = _plan(
        "Redesign one ecommerce product detail page with product gallery, cart, checkout and site search."
    )

    assert profile.website_type == "ecommerce"
    assert profile.domain == "commerce-retail"
    assert profile.product_archetype == "checkout-commerce"
    assert profile.change_surface == "PAGE"
    assert plan.id == "page-ui-work"

    stages = {stage.id: stage for stage in plan.stages}
    assert {"ecommerce-website", "site-search-and-findability"}.issubset(
        set(stages["research"].skills)
    )
    assert "asset-media-and-art-direction" in stages["design"].skills
    assert {"journey-driven-content-and-layout", "interaction-patterns-and-form-ux"}.issubset(
        set(stages["design"].skills)
    )
    assert {"media-crop-and-layout-integrity", "state-feedback-and-error-recovery"}.issubset(
        set(stages["qa"].skills)
    )


def test_generic_landing_does_not_receive_vertical_archetype_overlays() -> None:
    profile, plan = _plan("Build one generic landing page for a newsletter signup.")

    assert profile.product_archetype == "generic"
    all_skills = {skill for stage in plan.stages for skill in stage.skills}
    assert "financial-product-intelligence" not in all_skills
    assert "education-website" not in all_skills
    assert "service-experience-to-digital-journey" not in all_skills
