from __future__ import annotations

from collections import Counter

from core.contracts.visual_critic_schema import (
    SemanticVisualReview,
    VisualIssue,
    VisualScore,
)
from core.domain_visual_profiles import resolve_visual_profile


def clamp(value: float) -> int:
    return max(0, min(100, int(round(value))))


def semantic_profile(review: SemanticVisualReview) -> dict:
    return resolve_visual_profile(review.website_type, review.vertical)


def semantic_blocking_generic(review: SemanticVisualReview) -> bool:
    profile = semantic_profile(review)
    thresholds = profile["thresholds"]
    generic_block = int(thresholds["generic_ai_block"])

    if review.blocking_generic:
        return True
    if any(route.blocking_generic or route.generic_ai_feel >= generic_block for route in review.routes):
        return True

    # Low cross-route variety is normally repairable. It becomes a hard generic
    # blocker only when it is materially below the domain policy floor.
    variety_floor = int(thresholds["cross_route_variety_min"])
    if len(review.routes) >= 3 and review.cross_route_variety < max(35, variety_floor - 22):
        return True
    return False


def semantic_coverage_issues(
    review: SemanticVisualReview,
    expected_routes: list[str],
) -> list[VisualIssue]:
    issues: list[VisualIssue] = []
    expected = list(dict.fromkeys(route for route in expected_routes if route))
    actual = [route.route for route in review.routes if route.route]
    counts = Counter(actual)

    missing = [route for route in expected if route not in counts]
    unexpected = [route for route in counts if route not in expected]
    duplicates = [route for route, count in counts.items() if count > 1]

    if not review.reviewed:
        issues.append(
            VisualIssue(
                severity="P1",
                category="semantic-coverage",
                route="*",
                viewport="representative",
                evidence="Vision response did not affirm that rendered screenshots were reviewed.",
                recommendation="Re-run semantic visual QA and require screenshot-grounded route review before PASS.",
            )
        )

    if missing:
        issues.append(
            VisualIssue(
                severity="P1",
                category="semantic-coverage",
                route="*",
                viewport="representative",
                evidence="Semantic review omitted supplied routes: " + ", ".join(missing),
                recommendation="Review every supplied representative screenshot; proxy or partial coverage cannot establish visual PASS.",
            )
        )

    if unexpected:
        issues.append(
            VisualIssue(
                severity="P1",
                category="semantic-coverage",
                route="*",
                viewport="representative",
                evidence="Semantic review invented or returned unsupplied routes: " + ", ".join(unexpected),
                recommendation="Ground the semantic response only in screenshots supplied by BrowserQA.",
            )
        )

    if duplicates:
        issues.append(
            VisualIssue(
                severity="P1",
                category="semantic-coverage",
                route="*",
                viewport="representative",
                evidence="Semantic review duplicated route objects: " + ", ".join(duplicates),
                recommendation="Return exactly one semantic review object per supplied route screenshot.",
            )
        )

    for route in review.routes:
        grounded = [item.strip() for item in route.evidence if item.strip()]
        if not grounded:
            issues.append(
                VisualIssue(
                    severity="P1",
                    category="semantic-evidence",
                    route=route.route or "*",
                    viewport="representative",
                    evidence="Semantic scores were returned without visible screenshot evidence.",
                    recommendation="Name concrete visible evidence for hierarchy, media, decision-object and generic-pattern judgments.",
                )
            )

    return issues


def semantic_issues(review: SemanticVisualReview) -> list[VisualIssue]:
    issues: list[VisualIssue] = []
    profile = semantic_profile(review)
    thresholds = profile["thresholds"]

    domain_min = int(thresholds["domain_fit_min"])
    role_min = int(thresholds["page_role_fit_min"])
    decision_min = int(thresholds["decision_object_min"])
    media_min = int(thresholds["media_relevance_min"])
    distinct_min = int(thresholds["distinctiveness_min"])
    generic_block = int(thresholds["generic_ai_block"])
    variety_min = int(thresholds["cross_route_variety_min"])
    brand_min = int(thresholds["brand_distinctiveness_min"])

    if semantic_blocking_generic(review):
        issues.append(
            VisualIssue(
                severity="P1",
                category="generic-ai",
                route="*",
                viewport="representative",
                evidence=(
                    "Semantic screenshot review found a materially interchangeable/generic "
                    f"visual grammar under policy {profile['id']}. {review.site_summary}"
                ),
                recommendation=(
                    "Invalidate the owning art-direction/composition decision. Re-establish a "
                    "domain-specific visual signature instead of adding another cosmetic layer."
                ),
            )
        )

    if len(review.routes) >= 3 and review.cross_route_variety < variety_min:
        issues.append(
            VisualIssue(
                severity="P1",
                category="composition-variety",
                route="*",
                viewport="representative",
                evidence=(
                    f"Cross-route visual variety scored {review.cross_route_variety}/100; "
                    f"the {profile['id']} policy floor is {variety_min}. Materially different "
                    "page roles are reading as the same template family."
                ),
                recommendation=(
                    "Recompose representative page roles around their different user decisions; "
                    "do not reuse the same hero + identical cards + CTA grammar everywhere."
                ),
            )
        )

    if review.brand_distinctiveness < brand_min:
        issues.append(
            VisualIssue(
                severity="P1",
                category="brand-distinctiveness",
                route="*",
                viewport="representative",
                evidence=(
                    f"Brand distinctiveness scored {review.brand_distinctiveness}/100; "
                    f"the {profile['id']} policy floor is {brand_min}."
                ),
                recommendation=(
                    "Strengthen a brief/domain-specific visual signature through imagery, type, "
                    "composition and rhythm rather than generic decorative chrome."
                ),
            )
        )

    for route in review.routes:
        evidence = "; ".join(route.evidence[:3]) or "Semantic screenshot inspection."
        tells = "; ".join(route.generic_tells[:3])
        recommendation = route.recommendations[0] if route.recommendations else (
            "Revisit the owning art-direction and page-role composition from rendered evidence."
        )

        if route.blocking_generic or route.generic_ai_feel >= generic_block:
            issues.append(
                VisualIssue(
                    severity="P1",
                    category="generic-ai",
                    route=route.route,
                    viewport="representative",
                    evidence=(
                        f"Generic-AI feel {route.generic_ai_feel}/100; policy block threshold is "
                        f"{generic_block}. {tells or evidence}"
                    ),
                    recommendation=recommendation,
                )
            )
        if route.domain_fit < domain_min:
            issues.append(
                VisualIssue(
                    severity="P1",
                    category="domain-fit",
                    route=route.route,
                    viewport="representative",
                    evidence=f"Domain fit {route.domain_fit}/100; policy floor {domain_min}. {evidence}",
                    recommendation=recommendation,
                )
            )
        if route.page_role_fit < role_min:
            issues.append(
                VisualIssue(
                    severity="P1",
                    category="page-role",
                    route=route.route,
                    viewport="representative",
                    evidence=f"Page-role fit {route.page_role_fit}/100; policy floor {role_min}. {evidence}",
                    recommendation=recommendation,
                )
            )
        if route.decision_object_dominance < decision_min:
            issues.append(
                VisualIssue(
                    severity="P1",
                    category="decision-object",
                    route=route.route,
                    viewport="representative",
                    evidence=(
                        "Primary decision object dominance scored "
                        f"{route.decision_object_dominance}/100; policy floor {decision_min}. {evidence}"
                    ),
                    recommendation=recommendation,
                )
            )
        if route.media_relevance < media_min:
            issues.append(
                VisualIssue(
                    severity="P1",
                    category="media",
                    route=route.route,
                    viewport="representative",
                    evidence=(
                        f"Domain/media relevance {route.media_relevance}/100; "
                        f"policy floor {media_min}. {evidence}"
                    ),
                    recommendation=recommendation,
                )
            )
        if route.distinctiveness < distinct_min:
            issues.append(
                VisualIssue(
                    severity="P1",
                    category="distinctiveness",
                    route=route.route,
                    viewport="representative",
                    evidence=(
                        f"Visible distinctiveness {route.distinctiveness}/100; "
                        f"policy floor {distinct_min}. {evidence}"
                    ),
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
