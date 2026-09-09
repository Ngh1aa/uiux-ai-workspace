from core.contracts.visual_critic_schema import (
    SemanticVisualReview,
    VisualRouteSemanticReview,
    VisualScore,
)
from core.semantic_visual_policy import merge_semantic_score, semantic_issues


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
    assert any(issue.severity == "P1" for issue in issues)

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
    score = merge_semantic_score(_base_score(), review, issues)
    assert score.generic_ai_feel <= 18
    assert score.visual >= 90
    assert score.hierarchy >= 90
