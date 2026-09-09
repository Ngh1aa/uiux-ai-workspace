from __future__ import annotations

from core.contracts.reference_intelligence_schema import (
    BenchmarkPlan,
    BenchmarkReference,
)
from core.orchestration.intelligent_flow import GoalInterpreter
from core.research.domain_intelligence import DomainInterpreter


class ReferenceIntelligencePlanner:
    """Select a small, public, production-site finalist set by archetype + vertical.

    These are not templates and are not the complete research pool. The ResearchAgent
    is responsible for broader 10–20 candidate discovery. This planner only supplies
    up to four high-signal references that can be measured by ReferenceAnalyzer.
    User-provided references always take precedence.
    """

    CATALOG: dict[str, tuple[BenchmarkReference, ...]] = {
        "saas": (
            BenchmarkReference(
                url="https://linear.app/",
                label="Linear",
                domain="saas",
                role="product-storytelling",
                rationale=(
                    "Product-led hierarchy, dense capability storytelling "
                    "and polished interaction grammar."
                ),
            ),
            BenchmarkReference(
                url="https://stripe.com/",
                label="Stripe",
                domain="saas",
                role="visual-craft",
                rationale=(
                    "Strong product narrative, responsive information hierarchy "
                    "and mature visual system."
                ),
            ),
        ),
        "startup": (
            BenchmarkReference(
                url="https://linear.app/",
                label="Linear",
                domain="startup",
                role="product-storytelling",
                rationale=(
                    "Focused product positioning, progressive disclosure "
                    "and distinctive product visuals."
                ),
            ),
            BenchmarkReference(
                url="https://stripe.com/",
                label="Stripe",
                domain="startup",
                role="conversion",
                rationale=(
                    "High-trust product communication and layered conversion pathways."
                ),
            ),
        ),
        "ecommerce": (
            BenchmarkReference(
                url="https://www.aesop.com/",
                label="Aesop",
                domain="ecommerce",
                role="visual-craft",
                rationale=(
                    "Editorial commerce hierarchy, restrained brand language "
                    "and product-first presentation."
                ),
            ),
            BenchmarkReference(
                url="https://www.apple.com/",
                label="Apple",
                domain="ecommerce",
                role="product-storytelling",
                rationale=(
                    "Product-led visual hierarchy, controlled density "
                    "and responsive storytelling."
                ),
            ),
        ),
        "hospitality": (
            BenchmarkReference(
                url="https://www.aman.com/",
                label="Aman",
                domain="hospitality",
                role="service-journey",
                rationale=(
                    "Luxury editorial pacing, destination storytelling "
                    "and experience-led media hierarchy."
                ),
            ),
            BenchmarkReference(
                url="https://www.aman.com/destinations",
                label="Aman Destinations",
                domain="hospitality",
                role="information-architecture",
                rationale=(
                    "Discovery architecture for a large destination portfolio "
                    "without collapsing everything into cards."
                ),
            ),
        ),
        "real-estate": (
            BenchmarkReference(
                url="https://www.aman.com/residences",
                label="Aman Residences",
                domain="real-estate",
                role="product-storytelling",
                rationale=(
                    "Premium property storytelling, destination hierarchy "
                    "and high-consideration enquiry flow."
                ),
            ),
            BenchmarkReference(
                url="https://www.aman.com/",
                label="Aman",
                domain="real-estate",
                role="visual-craft",
                rationale=(
                    "Luxury brand restraint, whitespace rhythm "
                    "and media treatment transferable to premium property."
                ),
            ),
        ),
        "government": (
            BenchmarkReference(
                url="https://www.gov.uk/",
                label="GOV.UK",
                domain="government",
                role="trust-accessibility",
                rationale=(
                    "Task-first public-service information architecture, "
                    "predictable navigation and accessibility discipline."
                ),
            ),
        ),
        "education": (
            BenchmarkReference(
                url="https://education.mit.edu/",
                label="MIT Scheller Teacher Education Program",
                domain="education",
                role="information-architecture",
                rationale=(
                    "Mission-led academic storytelling with programme "
                    "and research information hierarchy."
                ),
            ),
            BenchmarkReference(
                url="https://www.gov.uk/education",
                label="GOV.UK Education",
                domain="education",
                role="trust-accessibility",
                rationale=(
                    "Task-oriented education navigation and plain-language "
                    "information architecture."
                ),
            ),
        ),
        "news": (
            BenchmarkReference(
                url="https://www.theverge.com/",
                label="The Verge",
                domain="news",
                role="editorial",
                rationale=(
                    "Editorial hierarchy, varied story density "
                    "and recognizable publication rhythm."
                ),
            ),
        ),
        "portfolio": (
            BenchmarkReference(
                url="https://selfaware.studio/",
                label="Self Aware",
                domain="portfolio",
                role="visual-craft",
                rationale=(
                    "Distinctive studio identity, typography-led craft "
                    "and project storytelling without generic SaaS grammar."
                ),
            ),
        ),
        "nonprofit": (
            BenchmarkReference(
                url="https://www.charitywater.org/",
                label="charity: water",
                domain="nonprofit",
                role="conversion",
                rationale=(
                    "Mission-to-action storytelling, transparent proof structure "
                    "and donation-oriented journey design."
                ),
            ),
            BenchmarkReference(
                url="https://www.gov.uk/",
                label="GOV.UK",
                domain="nonprofit",
                role="trust-accessibility",
                rationale=(
                    "Plain-language task hierarchy and accessibility calibration "
                    "for broad audiences."
                ),
            ),
        ),
        "corporate": (
            BenchmarkReference(
                url="https://stripe.com/",
                label="Stripe",
                domain="corporate",
                role="product-storytelling",
                rationale=(
                    "Complex business offering communicated through structured "
                    "hierarchy and a strong visual system."
                ),
            ),
            BenchmarkReference(
                url="https://www.apple.com/",
                label="Apple",
                domain="corporate",
                role="visual-craft",
                rationale=(
                    "Brand-led restraint, page-role variation "
                    "and strong product/brand storytelling."
                ),
            ),
        ),
        "landing": (
            BenchmarkReference(
                url="https://linear.app/",
                label="Linear",
                domain="landing",
                role="conversion",
                rationale=(
                    "Focused proposition, progressive feature reveal "
                    "and polished primary-action hierarchy."
                ),
            ),
            BenchmarkReference(
                url="https://stripe.com/",
                label="Stripe",
                domain="landing",
                role="visual-craft",
                rationale=(
                    "High-craft landing-page rhythm with a mature "
                    "responsive design language."
                ),
            ),
        ),
        "generic": (
            BenchmarkReference(
                url="https://stripe.com/",
                label="Stripe",
                domain="generic",
                role="visual-craft",
                rationale=(
                    "General production benchmark for hierarchy, responsiveness "
                    "and component-system maturity."
                ),
            ),
            BenchmarkReference(
                url="https://linear.app/",
                label="Linear",
                domain="generic",
                role="product-storytelling",
                rationale=(
                    "General benchmark for modern product storytelling "
                    "and recognizable visual identity."
                ),
            ),
        ),
    }

    VERTICAL_CATALOG: dict[str, tuple[BenchmarkReference, ...]] = {
        "luxury-fragrance": (
            BenchmarkReference(
                url="https://www.diptyqueparis.com/",
                label="Diptyque",
                domain="luxury-fragrance",
                role="information-architecture",
                rationale=(
                    "Fragrance-native catalogue, discovery and olfactory education "
                    "patterns rather than generic ecommerce taxonomy."
                ),
            ),
            BenchmarkReference(
                url="https://www.lelabofragrances.com/",
                label="Le Labo",
                domain="luxury-fragrance",
                role="product-storytelling",
                rationale=(
                    "Strong fragrance-house identity, collection architecture "
                    "and product storytelling."
                ),
            ),
            BenchmarkReference(
                url="https://www.byredo.com/",
                label="Byredo",
                domain="luxury-fragrance",
                role="visual-craft",
                rationale=(
                    "Image-led luxury art direction and controlled editorial-commerce rhythm."
                ),
            ),
            BenchmarkReference(
                url="https://www.aesop.com/",
                label="Aesop",
                domain="luxury-fragrance",
                role="conversion",
                rationale=(
                    "Restrained premium commerce with clear product and service pathways."
                ),
            ),
        ),
        "fashion": (
            BenchmarkReference(
                url="https://www.cos.com/",
                label="COS",
                domain="fashion",
                role="visual-craft",
                rationale=(
                    "Editorial fashion imagery with strong product-grid discipline."
                ),
            ),
            BenchmarkReference(
                url="https://www.uniqlo.com/",
                label="UNIQLO",
                domain="fashion",
                role="information-architecture",
                rationale=(
                    "Large apparel catalogue with category, fit, colour and product discovery patterns."
                ),
            ),
        ),
        "beauty-skincare": (
            BenchmarkReference(
                url="https://www.sephora.com/",
                label="Sephora",
                domain="beauty-skincare",
                role="information-architecture",
                rationale=(
                    "Beauty-specific filtering, product proof, reviews and discovery architecture."
                ),
            ),
            BenchmarkReference(
                url="https://www.aesop.com/",
                label="Aesop",
                domain="beauty-skincare",
                role="visual-craft",
                rationale=(
                    "Premium product storytelling and restrained editorial presentation."
                ),
            ),
        ),
        "electronics": (
            BenchmarkReference(
                url="https://www.apple.com/",
                label="Apple",
                domain="electronics",
                role="product-storytelling",
                rationale=(
                    "High-consideration hardware storytelling with controlled specification reveal."
                ),
            ),
            BenchmarkReference(
                url="https://www.samsung.com/",
                label="Samsung",
                domain="electronics",
                role="information-architecture",
                rationale=(
                    "Broad device catalogue with comparison, specification and purchase pathways."
                ),
            ),
        ),
        "hotel-resort": (
            BenchmarkReference(
                url="https://www.aman.com/",
                label="Aman",
                domain="hotel-resort",
                role="service-journey",
                rationale=(
                    "Experience-led destination storytelling connected to practical booking tasks."
                ),
            ),
        ),
        "higher-education": (
            BenchmarkReference(
                url="https://www.mit.edu/",
                label="MIT",
                domain="higher-education",
                role="information-architecture",
                rationale=(
                    "Institution-wide information architecture across audiences and academic content."
                ),
            ),
        ),
        "fintech": (
            BenchmarkReference(
                url="https://stripe.com/",
                label="Stripe",
                domain="fintech",
                role="product-storytelling",
                rationale=(
                    "Complex financial infrastructure communicated with proof, trust and progressive detail."
                ),
            ),
        ),
        "developer-tools": (
            BenchmarkReference(
                url="https://linear.app/",
                label="Linear",
                domain="developer-tools",
                role="product-storytelling",
                rationale=(
                    "Product proof, workflow narrative and interaction-led software communication."
                ),
            ),
        ),
        "news-publication": (
            BenchmarkReference(
                url="https://www.theverge.com/",
                label="The Verge",
                domain="news-publication",
                role="editorial",
                rationale=(
                    "Distinctive publication hierarchy and varied story density."
                ),
            ),
        ),
    }

    def __init__(self) -> None:
        self.interpreter = GoalInterpreter()
        self.domain_interpreter = DomainInterpreter()

    def references_for(self, goal: str) -> tuple[BenchmarkReference, ...]:
        profile = self.interpreter.interpret(goal)
        domain = self.domain_interpreter.interpret(goal, profile.website_type)
        vertical = self.VERTICAL_CATALOG.get(domain.vertical, ())
        archetype = self.CATALOG.get(profile.website_type, self.CATALOG["generic"])
        merged: list[BenchmarkReference] = []
        seen: set[str] = set()
        for reference in (*vertical, *archetype):
            if reference.url in seen:
                continue
            seen.add(reference.url)
            merged.append(reference)
        return tuple(merged)

    def plan(
        self,
        *,
        goal: str,
        user_urls: list[str],
        auto_enabled: bool = True,
        target_reference_count: int = 4,
    ) -> BenchmarkPlan:
        profile = self.interpreter.interpret(goal)
        domain = self.domain_interpreter.interpret(goal, profile.website_type)
        user_urls = list(dict.fromkeys(user_urls))
        target = max(0, min(4, int(target_reference_count)))
        selected: list[BenchmarkReference] = []

        if auto_enabled and len(user_urls) < target:
            needed = target - len(user_urls)
            for reference in self.references_for(goal):
                if reference.url not in user_urls:
                    selected.append(reference)
                if len(selected) >= needed:
                    break

        final_urls = list(
            dict.fromkeys(user_urls + [item.url for item in selected])
        )
        return BenchmarkPlan(
            website_type=profile.website_type,
            vertical=domain.vertical,
            auto_inspiration_enabled=auto_enabled,
            target_reference_count=target,
            user_reference_count=len(user_urls),
            selected=selected,
            final_reference_urls=final_urls,
            notes=[
                "User references take precedence over curated benchmarks.",
                (
                    "The planner selects at most four finalists for ReferenceAnalyzer; "
                    "it is not the complete research candidate pool."
                ),
                (
                    "ResearchAgent should discover 10–20 candidates for substantial redesigns "
                    "and shortlist 3–6 by page-role job."
                ),
                (
                    "Benchmarks are public production sites and may be partially unavailable "
                    "during capture."
                ),
                (
                    "Awards/popularity are not treated as evidence of usability, accessibility, "
                    "conversion or project fit."
                ),
                (
                    "Extract measurable principles only; proprietary assets and compositions "
                    "are out of bounds."
                ),
            ],
        )
