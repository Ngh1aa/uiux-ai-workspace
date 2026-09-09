from core.contracts.visual_critic_schema import (
    SemanticVisualReview,
    VisualRouteSemanticReview,
    VisualScore,
)
from core.domain_visual_profiles import resolve_visual_profile
from core.semantic_visual_policy import (
    merge_semantic_score,
    semantic_blocking_generic,
    semantic_coverage_issues,
    semantic_issues,
)


def _base_score() -> VisualScore:
    return VisualScore(
        visual=96,
        hierarchy=95,
        typography=96,
        spacing=95,
        responsive=100,
        brand_fidelity=92,
        accessibility=100,
        generic_ai_feel=18,
        overall=96,
    )


def test_luxury_fragrance_card_soup_creates_blocking_semantic_issues() -> None:
    review = SemanticVisualReview(
        website_type="ecommerce",
        vertical="luxury-fragrance",
        site_summary="The catalogue reads like a generic SaaS card board rather than fragrance discovery.",
        blocking_generic=True,
        cross_route_variety=42,
        brand_distinctiveness=40,
        routes=[
            VisualRouteSemanticReview(
                route="/fragrances/",
                page_role="product-listing",
                domain_fit=48,
                page_role_fit=55,
                decision_object_dominance=38,
                media_relevance=45,
                hierarchy=58,
                distinctiveness=35,
                generic_ai_feel=72,
                blocking_generic=True,
                generic_tells=[
                    "identical rounded cards dominate the viewport",
                    "perfume imagery is secondary to generic containers",
                ],
                evidence=["Products occupy small repeated frames with equal-weight copy and chrome."],
                recommendations=["Return to art direction and make fragrance/media the primary browsing object."],
            )
        ],
    )

    issues = semantic_issues(review)
    categories = {issue.category for issue in issues}
    assert "generic-ai" in categories
    assert "domain-fit" in categories
    assert "page-role" in categories
    assert "decision-object" in categories
    assert "media" in categories
    assert "distinctiveness" in categories
    assert "brand-distinctiveness" in categories
    assert any(issue.severity == "P1" for issue in issues)
    assert semantic_blocking_generic(review) is True

    score = merge_semantic_score(_base_score(), review, issues)
    assert score.generic_ai_feel >= 70
    assert score.overall < _base_score().overall


def test_domain_specific_visual_review_can_pass_without_generic_false_positive() -> None:
    review = SemanticVisualReview(
        website_type="ecommerce",
        vertical="luxury-fragrance",
        site_summary="Fragrance imagery and olfactory discovery clearly lead the experience.",
        blocking_generic=False,
        cross_route_variety=84,
        brand_distinctiveness=88,
        routes=[
            VisualRouteSemanticReview(
                route="/",
                page_role="home-orientation",
                domain_fit=92,
                page_role_fit=90,
                decision_object_dominance=88,
                media_relevance=94,
                hierarchy=90,
                distinctiveness=88,
                generic_ai_feel=12,
                blocking_generic=False,
                evidence=["Large fragrance imagery establishes category identity immediately."],
            ),
            VisualRouteSemanticReview(
                route="/fragrances/",
                page_role="product-listing",
                domain_fit=91,
                page_role_fit=93,
                decision_object_dominance=90,
                media_relevance=92,
                hierarchy=91,
                distinctiveness=84,
                generic_ai_feel=14,
                blocking_generic=False,
                evidence=["Product media dominates browse decisions while filtering remains secondary."],
            ),
            VisualRouteSemanticReview(
                route="/fragrance/violette-03/",
                page_role="product-detail",
                domain_fit=94,
                page_role_fit=95,
                decision_object_dominance=93,
                media_relevance=96,
                hierarchy=92,
                distinctiveness=89,
                generic_ai_feel=10,
                blocking_generic=False,
                evidence=["Gallery, scent character and buying controls have distinct PDP hierarchy."],
            ),
        ],
    )

    issues = semantic_issues(review)
    assert issues == []
    assert semantic_blocking_generic(review) is False
    score = merge_semantic_score(_base_score(), review, issues)
    assert score.generic_ai_feel <= 18
    assert score.visual >= 90
    assert score.hierarchy >= 90


def test_semantic_review_requires_complete_route_coverage_and_visible_evidence() -> None:
    review = SemanticVisualReview(
        website_type="ecommerce",
        vertical="luxury-fragrance",
        cross_route_variety=90,
        brand_distinctiveness=90,
        routes=[
            VisualRouteSemanticReview(
                route="/",
                page_role="home",
                domain_fit=90,
                page_role_fit=90,
                decision_object_dominance=90,
                media_relevance=90,
                hierarchy=90,
                distinctiveness=90,
                generic_ai_feel=5,
                evidence=[],
            )
        ],
    )

    issues = semantic_coverage_issues(review, ["/", "/fragrances/"])
    categories = {issue.category for issue in issues}
    assert "semantic-coverage" in categories
    assert "semantic-evidence" in categories
    assert any("/fragrances/" in issue.evidence for issue in issues)


def test_domain_profiles_do_not_apply_one_visual_recipe_to_every_site() -> None:
    fragrance = resolve_visual_profile("ecommerce", "luxury-fragrance")
    government = resolve_visual_profile("government", "generic")

    assert fragrance["id"].endswith("luxury-fragrance")
    assert fragrance["thresholds"]["media_relevance_min"] > government["thresholds"]["media_relevance_min"]
    assert fragrance["thresholds"]["generic_ai_block"] < government["thresholds"]["generic_ai_block"]
    assert "fragrance" in fragrance["decision_model"].lower()
    assert "public-service" in government["decision_model"].lower()


def test_domain_policy_can_derive_generic_block_even_when_model_flag_is_false() -> None:
    route = VisualRouteSemanticReview(
        route="/fragrances/",
        page_role="product-listing",
        domain_fit=80,
        page_role_fit=80,
        decision_object_dominance=75,
        media_relevance=80,
        hierarchy=80,
        distinctiveness=70,
        generic_ai_feel=38,
        blocking_generic=False,
        evidence=["Repeated equal rounded cards dominate the listing."],
    )
    fragrance = SemanticVisualReview(
        website_type="ecommerce",
        vertical="luxury-fragrance",
        blocking_generic=False,
        cross_route_variety=80,
        brand_distinctiveness=80,
        routes=[route],
    )
    government = fragrance.model_copy(deep=True)
    government.website_type = "government"
    government.vertical = "generic"

    assert semantic_blocking_generic(fragrance) is True
    assert semantic_blocking_generic(government) is False
