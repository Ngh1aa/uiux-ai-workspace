from __future__ import annotations

from core.contracts.reference_intelligence_schema import BenchmarkPlan, BenchmarkReference
from core.orchestration.intelligent_flow import GoalInterpreter


class ReferenceIntelligencePlanner:
    """Select a small, public, production-site benchmark set by task domain.

    These sites are not templates. They are measured by ReferenceAnalyzer and used
    only to extract transferable principles with explicit anti-copy boundaries.
    User-provided references always take precedence.
    """

    CATALOG: dict[str, tuple[BenchmarkReference, ...]] = {
        "saas": (
            BenchmarkReference(
                url="https://linear.app/",
                label="Linear",
                domain="saas",
                role="product-storytelling",
                rationale="Product-led hierarchy, dense capability storytelling and polished interaction grammar.",
            ),
            BenchmarkReference(
                url="https://stripe.com/",
                label="Stripe",
                domain="saas",
                role="visual-craft",
                rationale="Strong product narrative, responsive information hierarchy and mature visual system.",
            ),
        ),
        "startup": (
            BenchmarkReference(
                url="https://linear.app/",
                label="Linear",
                domain="startup",
                role="product-storytelling",
                rationale="Focused product positioning, progressive disclosure and distinctive product visuals.",
            ),
            BenchmarkReference(
                url="https://stripe.com/",
                label="Stripe",
                domain="startup",
                role="conversion",
                rationale="High-trust product communication and layered conversion pathways.",
            ),
        ),
        "ecommerce": (
            BenchmarkReference(
                url="https://www.aesop.com/",
                label="Aesop",
                domain="ecommerce",
                role="visual-craft",
                rationale="Editorial commerce hierarchy, restrained luxury language and product-first presentation.",
            ),
            BenchmarkReference(
                url="https://www.apple.com/",
                label="Apple",
                domain="ecommerce",
                role="product-storytelling",
                rationale="Product-led visual hierarchy, controlled density and high-quality responsive storytelling.",
            ),
        ),
        "hospitality": (
            BenchmarkReference(
                url="https://www.aman.com/",
                label="Aman",
                domain="hospitality",
                role="service-journey",
                rationale="Luxury editorial pacing, destination storytelling and experience-led media hierarchy.",
            ),
            BenchmarkReference(
                url="https://www.aman.com/destinations",
                label="Aman Destinations",
                domain="hospitality",
                role="information-architecture",
                rationale="Discovery architecture for a large destination portfolio without collapsing everything into cards.",
            ),
        ),
        "real-estate": (
            BenchmarkReference(
                url="https://www.aman.com/residences",
                label="Aman Residences",
                domain="real-estate",
                role="product-storytelling",
                rationale="Premium property storytelling, destination hierarchy and high-consideration enquiry flow.",
            ),
            BenchmarkReference(
                url="https://www.aman.com/",
                label="Aman",
                domain="real-estate",
                role="visual-craft",
                rationale="Luxury brand restraint, whitespace rhythm and media treatment transferable to premium property.",
            ),
        ),
        "government": (
            BenchmarkReference(
                url="https://www.gov.uk/",
                label="GOV.UK",
                domain="government",
                role="trust-accessibility",
                rationale="Task-first public-service information architecture, predictable navigation and accessibility discipline.",
            ),
        ),
        "education": (
            BenchmarkReference(
                url="https://education.mit.edu/",
                label="MIT Scheller Teacher Education Program",
                domain="education",
                role="information-architecture",
                rationale="Mission-led academic storytelling with program and research information hierarchy.",
            ),
            BenchmarkReference(
                url="https://www.gov.uk/education",
                label="GOV.UK Education",
                domain="education",
                role="trust-accessibility",
                rationale="Task-oriented education navigation and plain-language information architecture.",
            ),
        ),
        "news": (
            BenchmarkReference(
                url="https://www.theverge.com/",
                label="The Verge",
                domain="news",
                role="editorial",
                rationale="Editorial hierarchy, varied story density and recognizable publication rhythm.",
            ),
        ),
        "portfolio": (
            BenchmarkReference(
                url="https://selfaware.studio/",
                label="Self Aware",
                domain="portfolio",
                role="visual-craft",
                rationale="Distinctive studio identity, typography-led craft and project storytelling without generic SaaS grammar.",
            ),
        ),
        "nonprofit": (
            BenchmarkReference(
                url="https://www.charitywater.org/",
                label="charity: water",
                domain="nonprofit",
                role="conversion",
                rationale="Mission-to-action storytelling, transparent proof structure and donation-oriented journey design.",
            ),
            BenchmarkReference(
                url="https://www.gov.uk/",
                label="GOV.UK",
                domain="nonprofit",
                role="trust-accessibility",
                rationale="Plain-language task hierarchy and accessibility calibration for broad audiences.",
            ),
        ),
        "corporate": (
            BenchmarkReference(
                url="https://stripe.com/",
                label="Stripe",
                domain="corporate",
                role="product-storytelling",
                rationale="Complex business offering communicated through structured hierarchy and strong visual system.",
            ),
            BenchmarkReference(
                url="https://www.apple.com/",
                label="Apple",
                domain="corporate",
                role="visual-craft",
                rationale="Brand-led restraint, page-role variation and strong product/brand storytelling.",
            ),
        ),
        "landing": (
            BenchmarkReference(
                url="https://linear.app/",
                label="Linear",
                domain="landing",
                role="conversion",
                rationale="Focused proposition, progressive feature reveal and polished primary-action hierarchy.",
            ),
            BenchmarkReference(
                url="https://stripe.com/",
                label="Stripe",
                domain="landing",
                role="visual-craft",
                rationale="High-craft landing-page rhythm with a mature responsive design language.",
            ),
        ),
        "generic": (
            BenchmarkReference(
                url="https://stripe.com/",
                label="Stripe",
                domain="generic",
                role="visual-craft",
                rationale="General production benchmark for hierarchy, responsiveness and component-system maturity.",
            ),
            BenchmarkReference(
                url="https://linear.app/",
                label="Linear",
                domain="generic",
                role="product-storytelling",
                rationale="General benchmark for modern product storytelling and recognizable visual identity.",
            ),
        ),
    }

    def __init__(self) -> None:
        self.interpreter = GoalInterpreter()

    def plan(
        self,
        *,
        goal: str,
        user_urls: list[str],
        auto_enabled: bool = True,
        target_reference_count: int = 2,
    ) -> BenchmarkPlan:
        profile = self.interpreter.interpret(goal)
        user_urls = list(dict.fromkeys(user_urls))
        target = max(0, min(2, int(target_reference_count)))
        selected: list[BenchmarkReference] = []

        if auto_enabled and len(user_urls) < target:
            needed = target - len(user_urls)
            catalog = self.CATALOG.get(profile.website_type, self.CATALOG["generic"])
            for reference in catalog:
                if reference.url not in user_urls:
                    selected.append(reference)
                if len(selected) >= needed:
                    break

        final_urls = list(dict.fromkeys(user_urls + [item.url for item in selected]))
        return BenchmarkPlan(
            website_type=profile.website_type,
            auto_inspiration_enabled=auto_enabled,
            target_reference_count=target,
            user_reference_count=len(user_urls),
            selected=selected,
            final_reference_urls=final_urls,
            notes=[
                "User references take precedence over curated benchmarks.",
                "Benchmarks are live public production sites and may be partially unavailable during capture.",
                "Awards/popularity are not treated as evidence of usability, accessibility, conversion or project fit.",
                "The analyzer extracts measurable principles only; proprietary assets and compositions are out of bounds.",
            ],
        )
