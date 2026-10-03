from __future__ import annotations

from pathlib import Path

import pytest

from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.runtime.flow_os.specialist_composition import SpecialistComposer
from core.runtime.flow_os.task_context import GoalInterpreter


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


@pytest.mark.parametrize(
    ("goal", "expected_domain", "expected_archetype"),
    [
        (
            "Build a fintech payment orchestration platform for multi-rail settlement and payouts",
            "financial-services",
            "payments-infrastructure",
        ),
        (
            "Build an EdTech learning platform with courses, lessons and student learning paths",
            "education-edtech",
            "learning-experience",
        ),
        (
            "Build a B2B enterprise operations platform with admin dashboard and approval workflow",
            "enterprise-software",
            "enterprise-operations",
        ),
        (
            "Build a museum visual archive for artwork collection discovery and artist browsing",
            "art-culture",
            "collection-discovery",
        ),
        (
            "Build an ecommerce store with product catalog, cart and checkout",
            "commerce-retail",
            "checkout-commerce",
        ),
    ],
)
def test_p1_profile_enrichment_covers_representative_specialisms(
    goal: str,
    expected_domain: str,
    expected_archetype: str,
) -> None:
    composer = SpecialistComposer(SKILLS)
    profile = composer.enrich_profile(GoalInterpreter().interpret(goal), goal)

    assert profile.domain == expected_domain
    assert profile.product_archetype == expected_archetype


def test_p1_page_fintech_gets_domain_surface_and_feature_specialists() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    goal = "Create a fintech landing page for payment settlement with a lead form and motion"

    profile, resolved = flow.resolve(goal)
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


def test_p1_product_museum_gets_collection_discovery_specialists() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    goal = "Build a museum platform for artwork collection discovery, visual archive and artist browsing"

    profile, resolved = flow.resolve(goal)
    assert profile.domain == "art-culture"
    assert profile.product_archetype == "collection-discovery"
    assert profile.change_surface == "PRODUCT"
    assert resolved.id == "professional-website-redesign"

    design = next(stage for stage in resolved.stages if stage.id == "design")
    implementation = next(stage for stage in resolved.stages if stage.id == "implementation")

    assert "asset-media-and-art-direction" in design.skills
    assert "experience-principles-and-signature-moments" in design.skills
    assert "site-search-and-findability" in design.skills
    assert "site-search-and-findability" in implementation.skills


def test_p1_product_enterprise_gets_operations_specialists() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    goal = "Build a B2B enterprise operations platform with admin dashboard, approval workflow and forms"

    profile, resolved = flow.resolve(goal)
    assert profile.domain == "enterprise-software"
    assert profile.product_archetype == "enterprise-operations"
    assert resolved.id == "professional-website-redesign"

    design = next(stage for stage in resolved.stages if stage.id == "design")
    implementation = next(stage for stage in resolved.stages if stage.id == "implementation")

    assert "complex-workflow-and-progress-ux" in design.skills
    assert "data-tables-and-enterprise-ux" in design.skills
    assert "data-visualization-and-dashboard-ux" in design.skills
    assert "complex-forms-and-wizards" in implementation.skills


def test_p1_product_edtech_and_ecommerce_route_distinct_specialists() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)

    edtech_profile, edtech_flow = flow.resolve(
        "Build an EdTech learning platform with courses, lessons and student learning paths"
    )
    commerce_profile, commerce_flow = flow.resolve(
        "Build an ecommerce store with product catalog, search, cart and checkout"
    )

    edtech_design = next(stage for stage in edtech_flow.stages if stage.id == "design")
    commerce_design = next(stage for stage in commerce_flow.stages if stage.id == "design")

    assert edtech_profile.product_archetype == "learning-experience"
    assert "complex-workflow-and-progress-ux" in edtech_design.skills
    assert "education-website" in next(stage for stage in edtech_flow.stages if stage.id == "research").skills

    assert commerce_profile.domain == "commerce-retail"
    assert commerce_profile.product_archetype == "checkout-commerce"
    assert "conversion-and-content" in commerce_design.skills
    assert "site-search-and-findability" in commerce_design.skills


def test_p1_composition_is_stable_and_deduplicated() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    goal = "Build a B2B enterprise operations platform with dashboard, forms and search"

    profile_a, resolved_a = flow.resolve(goal)
    profile_b, resolved_b = flow.resolve(goal)

    assert profile_a.to_context() == profile_b.to_context()
    assert resolved_a.to_dict() == resolved_b.to_dict()
    for stage in resolved_a.stages:
        assert len(stage.skills) == len(set(stage.skills))
        assert len(stage.jit_skills or []) == len(set(stage.jit_skills or []))
