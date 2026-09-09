from __future__ import annotations

from core.contracts.visual_critic_schema import (
    SemanticVisualReview,
    VisualIssue,
    VisualScore,
)


def clamp(value: float) -> int:
    return max(0, min(100, int(round(value))))


def semantic_issues(review: SemanticVisualReview) -> list[VisualIssue]:
    issues: list[VisualIssue] = []

    if review.blocking_generic:
        issues.append(
            VisualIssue(
                severity="P1",
                category="generic-ai",
                route="*",
                viewport="representative",
                evidence=(
                    "Semantic screenshot review found a site-level interchangeable/generic "
                    f"visual grammar. {review.site_summary}"
                ),
                recommendation=(
                    "Invalidate the owning art-direction/composition decision. Re-establish a "
                    "domain-specific visual signature instead of adding another cosmetic layer."
                ),
            )
        )

    if len(review.routes) >= 3 and review.cross_route_variety < 60:
        issues.append(
            VisualIssue(
                severity="P1",
                category="composition-variety",
                route="*",
                viewport="representative",
                evidence=(
                    f"Cross-route visual variety scored {review.cross_route_variety}/100; "
                    "materially different page roles are reading as the same template family."
                ),
                recommendation=(
                    "Recompose representative page roles around their different user decisions; "
                    "do not reuse the same hero + identical cards + CTA grammar everywhere."
                ),
            )
        )

    for route in review.routes:
        evidence = "; ".join(route.evidence[:3]) or "Semantic screenshot inspection."
        tells = "; ".join(route.generic_tells[:3])
        recommendation = route.recommendations[0] if route.recommendations else (
            "Revisit the owning art-direction and page-role composition from rendered evidence."
        )

        if route.blocking_generic or route.generic_ai_feel >= 45:
            issues.append(
                VisualIssue(
                    severity="P1",
                    category="generic-ai",
                    route=route.route,
                    viewport="representative",
                    evidence=f"Generic-AI feel {route.generic_ai_feel}/100. {tells or evidence}",
                    recommendation=recommendation,
                )
            )
        if route.domain_fit < 65:
            issues.append(
                VisualIssue(
                    severity="P1",
                    category="domain-fit",
                    route=route.route,
                    viewport="representative",
                    evidence=f"Domain fit {route.domain_fit}/100. {evidence}",
                    recommendation=recommendation,
                )
            )
        if route.page_role_fit < 65:
            issues.append(
                VisualIssue(
                    severity="P1",
                    category="page-role",
                    route=route.route,
                    viewport="representative",
                    evidence=f"Page-role fit {route.page_role_fit}/100. {evidence}",
                    recommendation=recommendation,
                )
            )
        if route.decision_object_dominance < 55:
            issues.append(
                VisualIssue(
                    severity="P1",
                    category="decision-object",
                    route=route.route,
                    viewport="representative",
                    evidence=(
                        "Primary decision object dominance scored "
                        f"{route.decision_object_dominance}/100. {evidence}"
                    ),
                    recommendation=recommendation,
                )
            )
        if route.media_relevance < 55:
            issues.append(
                VisualIssue(
                    severity="P1",
                    category="media",
                    route=route.route,
                    viewport="representative",
                    evidence=f"Domain/media relevance {route.media_relevance}/100. {evidence}",
                    recommendation=recommendation,
                )
            )

    return issues


def merge_semantic_score(
    base: VisualScore,
    review: SemanticVisualReview,
    issues: list[VisualIssue],
) -> VisualScore:
    if not review.routes:
        return base

    def avg(name: str) -> float:
        return sum(float(getattr(route, name)) for route in review.routes) / len(review.routes)

    semantic_visual = (
        avg("domain_fit")
        + avg("page_role_fit")
        + avg("media_relevance")
        + avg("distinctiveness")
    ) / 4
    semantic_hierarchy = (avg("hierarchy") + avg("decision_object_dominance")) / 2

    visual = clamp(base.visual * 0.4 + semantic_visual * 0.6)
    hierarchy = clamp(base.hierarchy * 0.4 + semantic_hierarchy * 0.6)
    brand = clamp(base.brand_fidelity * 0.35 + review.brand_distinctiveness * 0.65)
    generic = clamp(
        max(
            base.generic_ai_feel,
            avg("generic_ai_feel"),
            100 - review.cross_route_variety if len(review.routes) >= 3 else 0,
        )
    )
    p0 = sum(issue.severity == "P0" for issue in issues)
    p1 = sum(issue.severity == "P1" for issue in issues)
    overall = clamp(
        (
            visual
            + hierarchy
            + base.typography
            + base.spacing
            + base.responsive
            + brand
            + base.accessibility
            + (100 - generic)
        )
        / 8
        - p0 * 2
        - p1 * 0.5
    )

    return VisualScore(
        visual=visual,
        hierarchy=hierarchy,
        typography=base.typography,
        spacing=base.spacing,
        responsive=base.responsive,
        brand_fidelity=brand,
        accessibility=base.accessibility,
        generic_ai_feel=generic,
        overall=overall,
    )
