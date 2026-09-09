from __future__ import annotations

from core.contracts.reference_intelligence_schema import (
    BenchmarkPlan,
    BenchmarkReference,
)
from core.orchestration.intelligent_flow import GoalInterpreter
from core.research.domain_intelligence import DomainInterpreter


def _reference(
    url: str,
    label: str,
    domain: str,
    role: str,
    rationale: str,
) -> BenchmarkReference:
    return BenchmarkReference(
        url=url,
        label=label,
        domain=domain,
        role=role,
        rationale=rationale,
    )


class ReferenceIntelligencePlanner:
    """Choose up to four measurable finalists; broader discovery belongs to ResearchAgent."""

    CATALOG: dict[str, tuple[BenchmarkReference, ...]] = {
        "saas": (
            _reference(
                "https://linear.app/",
                "Linear",
                "saas",
                "product-storytelling",
                "Product-led hierarchy, capability storytelling and polished interaction grammar.",
            ),
            _reference(
                "https://stripe.com/",
                "Stripe",
                "saas",
                "visual-craft",
                "Responsive product narrative, proof and a mature visual system.",
            ),
        ),
        "startup": (
            _reference(
                "https://linear.app/",
                "Linear",
                "startup",
                "product-storytelling",
                "Focused positioning, progressive disclosure and distinctive product visuals.",
            ),
            _reference(
                "https://stripe.com/",
                "Stripe",
                "startup",
                "conversion",
                "High-trust product communication and layered conversion pathways.",
            ),
        ),
        "ecommerce": (
            _reference(
                "https://www.aesop.com/",
                "Aesop",
                "ecommerce",
                "visual-craft",
                "Editorial commerce hierarchy and restrained product-first presentation.",
            ),
            _reference(
                "https://www.apple.com/",
                "Apple",
                "ecommerce",
                "product-storytelling",
                "Product-led hierarchy, controlled density and responsive storytelling.",
            ),
        ),
        "hospitality": (
            _reference(
                "https://www.aman.com/",
                "Aman",
                "hospitality",
                "service-journey",
                "Destination storytelling and experience-led media connected to booking.",
            ),
            _reference(
                "https://www.aman.com/destinations",
                "Aman Destinations",
                "hospitality",
                "information-architecture",
                "Portfolio discovery without collapsing the entire experience into cards.",
            ),
        ),
        "real-estate": (
            _reference(
                "https://www.aman.com/residences",
                "Aman Residences",
                "real-estate",
                "product-storytelling",
                "Premium property storytelling and high-consideration enquiry hierarchy.",
            ),
            _reference(
                "https://www.aman.com/",
                "Aman",
                "real-estate",
                "visual-craft",
                "Luxury brand restraint, whitespace rhythm and media treatment.",
            ),
        ),
        "government": (
            _reference(
                "https://www.gov.uk/",
                "GOV.UK",
                "government",
                "trust-accessibility",
                "Task-first public-service IA, predictable navigation and accessibility discipline.",
            ),
        ),
        "education": (
            _reference(
                "https://education.mit.edu/",
                "MIT Scheller Teacher Education Program",
                "education",
                "information-architecture",
                "Mission-led academic storytelling with programme and research hierarchy.",
            ),
            _reference(
                "https://www.gov.uk/education",
                "GOV.UK Education",
                "education",
                "trust-accessibility",
                "Task-oriented education navigation and plain-language information architecture.",
            ),
        ),
        "news": (
            _reference(
                "https://www.theverge.com/",
                "The Verge",
                "news",
                "editorial",
                "Editorial hierarchy, varied story density and recognizable publication rhythm.",
            ),
        ),
        "portfolio": (
            _reference(
                "https://selfaware.studio/",
                "Self Aware",
                "portfolio",
                "visual-craft",
                "Distinctive studio identity and project storytelling without generic SaaS grammar.",
            ),
        ),
        "nonprofit": (
            _reference(
                "https://www.charitywater.org/",
                "charity: water",
                "nonprofit",
                "conversion",
                "Mission-to-action storytelling, transparent proof and donation journey design.",
            ),
            _reference(
                "https://www.gov.uk/",
                "GOV.UK",
                "nonprofit",
                "trust-accessibility",
                "Plain-language task hierarchy and accessibility calibration for broad audiences.",
            ),
        ),
        "corporate": (
            _reference(
                "https://stripe.com/",
                "Stripe",
                "corporate",
                "product-storytelling",
                "Complex offering communicated through structured hierarchy and proof.",
            ),
            _reference(
                "https://www.apple.com/",
                "Apple",
                "corporate",
                "visual-craft",
                "Brand-led restraint and strong page-role variation.",
            ),
        ),
        "landing": (
            _reference(
                "https://linear.app/",
                "Linear",
                "landing",
                "conversion",
                "Focused proposition, progressive reveal and polished primary-action hierarchy.",
            ),
            _reference(
                "https://stripe.com/",
                "Stripe",
                "landing",
                "visual-craft",
                "High-craft landing-page rhythm with a mature responsive design language.",
            ),
        ),
        "generic": (
            _reference(
                "https://stripe.com/",
                "Stripe",
                "generic",
                "visual-craft",
                "General production benchmark for hierarchy, responsiveness and system maturity.",
            ),
            _reference(
                "https://linear.app/",
                "Linear",
                "generic",
                "product-storytelling",
                "General benchmark for modern product storytelling and recognizable identity.",
            ),
        ),
    }

    VERTICAL_CATALOG: dict[str, tuple[BenchmarkReference, ...]] = {
        "luxury-fragrance": (
            _reference(
                "https://www.diptyqueparis.com/",
                "Diptyque",
                "luxury-fragrance",
                "information-architecture",
                "Fragrance-native catalogue, discovery and olfactory education patterns.",
            ),
            _reference(
                "https://www.lelabofragrances.com/",
                "Le Labo",
                "luxury-fragrance",
                "product-storytelling",
                "Fragrance-house identity, collection architecture and product storytelling.",
            ),
            _reference(
                "https://www.byredo.com/",
                "Byredo",
                "luxury-fragrance",
                "visual-craft",
                "Image-led luxury art direction and controlled editorial-commerce rhythm.",
            ),
            _reference(
                "https://www.aesop.com/",
                "Aesop",
                "luxury-fragrance",
                "conversion",
                "Restrained premium commerce with clear product and service pathways.",
            ),
        ),
        "fashion": (
            _reference(
                "https://www.cos.com/",
                "COS",
                "fashion",
                "visual-craft",
                "Editorial fashion imagery with strong product-grid discipline.",
            ),
            _reference(
                "https://www.uniqlo.com/",
                "UNIQLO",
                "fashion",
                "information-architecture",
                "Apparel discovery using category, fit, colour and product attributes.",
            ),
        ),
        "beauty-skincare": (
            _reference(
                "https://www.sephora.com/",
                "Sephora",
                "beauty-skincare",
                "information-architecture",
                "Beauty-specific filtering, product proof, reviews and discovery architecture.",
            ),
            _reference(
                "https://www.aesop.com/",
                "Aesop",
                "beauty-skincare",
                "visual-craft",
                "Premium product storytelling and restrained editorial presentation.",
            ),
        ),
        "electronics": (
            _reference(
                "https://www.apple.com/",
                "Apple",
                "electronics",
                "product-storytelling",
                "Hardware storytelling with controlled specification reveal.",
            ),
            _reference(
                "https://www.samsung.com/",
                "Samsung",
                "electronics",
                "information-architecture",
                "Device catalogue with comparison, specification and purchase pathways.",
            ),
        ),
        "hotel-resort": (
            _reference(
                "https://www.aman.com/",
                "Aman",
                "hotel-resort",
                "service-journey",
                "Experience-led storytelling connected to practical booking tasks.",
            ),
        ),
        "higher-education": (
            _reference(
                "https://www.mit.edu/",
                "MIT",
                "higher-education",
                "information-architecture",
                "Institution-wide information architecture across audiences and academic content.",
            ),
        ),
        "fintech": (
            _reference(
                "https://stripe.com/",
                "Stripe",
                "fintech",
                "product-storytelling",
                "Financial infrastructure communicated with proof, trust and progressive detail.",
            ),
        ),
        "developer-tools": (
            _reference(
                "https://linear.app/",
                "Linear",
                "developer-tools",
                "product-storytelling",
                "Product proof, workflow narrative and interaction-led software communication.",
            ),
        ),
        "news-publication": (
            _reference(
                "https://www.theverge.com/",
                "The Verge",
                "news-publication",
                "editorial",
                "Distinctive publication hierarchy and varied story density.",
            ),
        ),
    }

    def __init__(self) -> None:
        self.interpreter = GoalInterpreter()
        self.domain_interpreter = DomainInterpreter()

    def _profile(self, goal: str):
        goal_profile = self.interpreter.interpret(goal)
        return self.domain_interpreter.interpret(
            goal,
            goal_profile.website_type,
        )

    def references_for(self, goal: str) -> tuple[BenchmarkReference, ...]:
        domain_profile = self._profile(goal)
        vertical = self.VERTICAL_CATALOG.get(domain_profile.vertical, ())
        archetype = self.CATALOG.get(
            domain_profile.website_type,
            self.CATALOG["generic"],
        )
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
        domain_profile = self._profile(goal)
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
            website_type=domain_profile.website_type,
            vertical=domain_profile.vertical,
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
