from __future__ import annotations

import re
from dataclasses import replace
from pathlib import Path
from typing import Any, Iterable

from core.runtime.flow_os.flow import ResolvedFlow, ResolvedStage
from core.runtime.flow_os.task_context import GoalInterpretation


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            output.append(text)
    return output


def _contains(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


class SpecialistComposer:
    """Compose JIT specialists from domain × archetype × surface × feature.

    Flow documents keep lifecycle ownership. This layer only augments the
    selected stages with contextual specialists, in a stable order, so PAGE,
    REDESIGN and PRODUCT lanes do not need to duplicate the same routing matrix.
    """

    DIMENSION_ORDER = ("domain", "archetype", "surface", "feature")

    DOMAIN_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
        (
            "commerce-retail",
            (
                "ecommerce",
                "e-commerce",
                "online store",
                "shopping",
                "catalog",
                "catalogue",
                "product detail",
                "product listing",
                "cart",
                "checkout",
                "giỏ hàng",
                "thanh toán",
                "cửa hàng trực tuyến",
            ),
        ),
        (
            "enterprise-software",
            (
                "b2b enterprise",
                "enterprise software",
                "enterprise platform",
                "enterprise dashboard",
                "back office",
                "back-office",
                "operations platform",
                "admin workspace",
                "internal tool",
                "workflow platform",
            ),
        ),
    )

    ARCHETYPE_HINTS: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
        "education-edtech": (
            (
                "learning-operations",
                (
                    "lms admin",
                    "teacher dashboard",
                    "instructor dashboard",
                    "course management",
                    "grading",
                    "student management",
                    "learning analytics",
                ),
            ),
            (
                "learning-experience",
                (
                    "course",
                    "lesson",
                    "learning path",
                    "student learning",
                    "online learning",
                    "classroom",
                    "quiz",
                    "assignment",
                ),
            ),
        ),
        "art-culture": (
            (
                "collection-discovery",
                (
                    "collection",
                    "archive",
                    "artwork",
                    "artist discovery",
                    "visual archive",
                    "browse art",
                    "drift",
                ),
            ),
            (
                "exhibition-experience",
                (
                    "exhibition",
                    "exhibit",
                    "immersive",
                    "gallery experience",
                    "museum experience",
                ),
            ),
        ),
        "industrial-services": (
            (
                "b2b-service-operations",
                (
                    "repair",
                    "maintenance",
                    "work order",
                    "service request",
                    "rfq",
                    "request a quote",
                    "industrial service",
                ),
            ),
        ),
        "enterprise-software": (
            (
                "enterprise-operations",
                (
                    "workflow",
                    "dashboard",
                    "admin",
                    "operations",
                    "approval",
                    "case management",
                    "data table",
                    "back office",
                ),
            ),
        ),
        "commerce-retail": (
            (
                "checkout-commerce",
                ("checkout", "cart", "payment", "order", "purchase", "thanh toán", "giỏ hàng"),
            ),
            (
                "catalog-commerce",
                ("catalog", "catalogue", "product listing", "category", "browse products", "product detail"),
            ),
        ),
        "ai-software": (
            (
                "ai-workspace",
                ("copilot", "agent", "assistant", "chat", "workspace", "prompt", "automation"),
            ),
        ),
        "mobility-ev": (
            (
                "charging-network",
                ("charging station", "charging network", "charger", "fleet", "route planning"),
            ),
        ),
        "travel-tourism": (
            (
                "destination-discovery",
                ("destination", "attraction", "itinerary", "city guide", "visitor guide", "discover places"),
            ),
        ),
    }

    DOMAIN_SKILLS: dict[str, dict[str, tuple[str, ...]]] = {
        "financial-services": {
            "research": ("financial-product-intelligence", "trust-credibility-and-transparency"),
            "design": ("trust-credibility-and-transparency",),
        },
        "education-edtech": {
            "research": ("education-website", "product-discovery"),
            "design": ("journey-driven-content-and-layout", "complex-workflow-and-progress-ux"),
        },
        "art-culture": {
            "research": ("site-search-and-findability",),
            "design": ("asset-media-and-art-direction", "experience-principles-and-signature-moments"),
            "qa": ("media-crop-and-layout-integrity",),
        },
        "industrial-services": {
            "research": ("corporate-website", "trust-credibility-and-transparency"),
            "design": ("service-experience-to-digital-journey",),
        },
        "enterprise-software": {
            "research": ("product-discovery",),
            "design": ("complex-workflow-and-progress-ux", "data-tables-and-enterprise-ux"),
            "implementation": ("data-tables-and-enterprise-ux",),
        },
        "commerce-retail": {
            "research": ("ecommerce-website", "conversion-and-content"),
            "design": ("conversion-and-content", "site-search-and-findability"),
            "implementation": ("state-feedback-and-error-recovery",),
        },
        "ai-software": {
            "research": ("saas-website", "product-discovery"),
            "design": ("complex-workflow-and-progress-ux",),
        },
        "mobility-ev": {
            "research": ("corporate-website", "trust-credibility-and-transparency"),
            "design": ("service-experience-to-digital-journey",),
        },
        "travel-tourism": {
            "research": ("hospitality-website",),
            "design": ("service-experience-to-digital-journey", "asset-media-and-art-direction"),
        },
    }

    ARCHETYPE_SKILLS: dict[str, dict[str, tuple[str, ...]]] = {
        "payments-infrastructure": {
            "research": ("financial-product-intelligence",),
            "design": ("trust-credibility-and-transparency",),
            "implementation": ("state-feedback-and-error-recovery",),
        },
        "compliance-operations": {
            "research": ("trust-credibility-and-transparency",),
            "implementation": ("security-and-privacy",),
        },
        "financial-operations": {
            "design": ("data-tables-and-enterprise-ux", "data-visualization-and-dashboard-ux"),
            "implementation": ("data-tables-and-enterprise-ux",),
        },
        "consumer-banking": {
            "design": ("interaction-patterns-and-form-ux", "trust-credibility-and-transparency"),
            "implementation": ("state-feedback-and-error-recovery",),
        },
        "investment-wealth": {
            "design": ("data-visualization-and-dashboard-ux", "trust-credibility-and-transparency"),
        },
        "learning-experience": {
            "design": ("journey-driven-content-and-layout", "complex-workflow-and-progress-ux"),
            "implementation": ("state-feedback-and-error-recovery",),
        },
        "learning-operations": {
            "design": ("data-tables-and-enterprise-ux", "data-visualization-and-dashboard-ux"),
            "implementation": ("complex-forms-and-wizards", "state-feedback-and-error-recovery"),
        },
        "collection-discovery": {
            "design": ("asset-media-and-art-direction", "site-search-and-findability", "experience-principles-and-signature-moments"),
            "implementation": ("site-search-and-findability",),
        },
        "exhibition-experience": {
            "design": ("visual-design-direction", "experience-principles-and-signature-moments"),
        },
        "b2b-service-operations": {
            "design": ("service-experience-to-digital-journey", "complex-workflow-and-progress-ux"),
            "implementation": ("state-feedback-and-error-recovery",),
        },
        "enterprise-operations": {
            "design": ("complex-workflow-and-progress-ux", "data-tables-and-enterprise-ux"),
            "implementation": ("complex-forms-and-wizards", "state-feedback-and-error-recovery"),
        },
        "catalog-commerce": {
            "design": ("site-search-and-findability", "conversion-and-content"),
            "implementation": ("site-search-and-findability",),
        },
        "checkout-commerce": {
            "design": ("interaction-patterns-and-form-ux", "trust-credibility-and-transparency"),
            "implementation": ("complex-forms-and-wizards", "state-feedback-and-error-recovery"),
        },
        "ai-workspace": {
            "design": ("complex-workflow-and-progress-ux",),
            "implementation": ("state-feedback-and-error-recovery",),
        },
        "charging-network": {
            "design": ("data-visualization-and-dashboard-ux", "service-experience-to-digital-journey"),
        },
        "destination-discovery": {
            "design": ("asset-media-and-art-direction", "journey-driven-content-and-layout"),
        },
    }

    SURFACE_SKILLS: dict[str, dict[str, tuple[str, ...]]] = {
        "FOCUSED": {
            "research": ("ui-improvement",),
            "implementation": ("ui-improvement",),
        },
        "PAGE": {
            "design": ("journey-driven-content-and-layout", "responsive-and-device-strategy"),
            "implementation": ("component-driven-development",),
        },
        "REDESIGN": {
            "research": ("website-audit-and-redesign",),
            "design": ("visual-taste-calibration", "design-system-and-components"),
            "implementation": ("frontend-architecture-and-refactoring",),
            "qa": ("visual-regression-and-design-drift",),
        },
        "PRODUCT": {
            "research": ("product-discovery", "information-architecture"),
            "design": ("design-system-and-components", "experience-principles-and-signature-moments"),
            "implementation": ("frontend-architecture-and-refactoring",),
            "qa": ("web-quality-and-performance",),
        },
    }

    FEATURE_SKILLS: dict[str, dict[str, tuple[str, ...]]] = {
        "dashboard": {
            "design": ("data-visualization-and-dashboard-ux", "data-tables-and-enterprise-ux"),
            "implementation": ("data-tables-and-enterprise-ux", "data-visualization-and-dashboard-ux"),
        },
        "forms": {
            "design": ("interaction-patterns-and-form-ux",),
            "implementation": ("complex-forms-and-wizards", "state-feedback-and-error-recovery"),
        },
        "search": {
            "research": ("site-search-and-findability",),
            "implementation": ("site-search-and-findability",),
        },
        "auth": {
            "implementation": ("authentication-account-and-recovery-ux", "security-and-privacy"),
        },
        "motion": {
            "design": ("motion-and-microinteractions",),
            "implementation": ("motion-and-microinteractions",),
        },
    }

    def __init__(self, skills_root: Path) -> None:
        self.skills_root = Path(skills_root)

    @staticmethod
    def _normalise(goal: str) -> str:
        return re.sub(r"\s+", " ", str(goal).strip().lower())

    def enrich_profile(self, profile: GoalInterpretation, goal: str) -> GoalInterpretation:
        text = self._normalise(goal)
        domain = profile.domain
        archetype = profile.product_archetype
        evidence = list(profile.evidence)

        if domain == "generic":
            for candidate, terms in self.DOMAIN_HINTS:
                if _contains(text, terms):
                    domain = candidate
                    evidence.append(f"specialist_domain:{candidate}")
                    break

        if archetype == "generic":
            for candidate, terms in self.ARCHETYPE_HINTS.get(domain, ()):
                if _contains(text, terms):
                    archetype = candidate
                    evidence.append(f"specialist_archetype:{candidate}")
                    break

        if domain == profile.domain and archetype == profile.product_archetype:
            return profile
        return replace(
            profile,
            domain=domain,
            product_archetype=archetype,
            confidence=max(profile.confidence, 0.9),
            evidence=_unique(evidence),
        )

    def skills_for(self, stage_id: str, context: dict[str, Any]) -> list[str]:
        selected: list[str] = []
        domain = str(context.get("domain", "generic"))
        archetype = str(context.get("product_archetype", "generic"))
        surface = str(context.get("change_surface", "PRODUCT")).upper()
        features = [str(item) for item in context.get("features", []) or []]

        selected.extend(self.DOMAIN_SKILLS.get(domain, {}).get(stage_id, ()))
        selected.extend(self.ARCHETYPE_SKILLS.get(archetype, {}).get(stage_id, ()))
        selected.extend(self.SURFACE_SKILLS.get(surface, {}).get(stage_id, ()))
        for feature in features:
            selected.extend(self.FEATURE_SKILLS.get(feature, {}).get(stage_id, ()))
        return _unique(selected)

    def compose_flow(self, flow: ResolvedFlow, context: dict[str, Any]) -> ResolvedFlow:
        stages: list[ResolvedStage] = []
        for stage in flow.stages:
            overlay = self.skills_for(stage.id, context)
            missing = [skill for skill in overlay if not (self.skills_root / skill / "SKILL.md").is_file()]
            if missing:
                raise FileNotFoundError(
                    f"specialist composition references missing skills for {stage.id}: " + ", ".join(missing)
                )

            additions = [skill for skill in overlay if skill not in set(stage.skills)]
            if not additions:
                stages.append(stage)
                continue

            jit = _unique(list(stage.jit_skills or []) + additions)
            sources = dict(stage.jit_skill_sources or {})
            for skill in additions:
                # Specialist overlays are contextual conditional JIT capabilities;
                # keep the existing Flow OS provenance vocabulary backward-compatible.
                sources[skill] = "conditional"
            stages.append(
                replace(
                    stage,
                    skills=_unique(list(stage.skills) + additions),
                    jit_skills=jit,
                    jit_skill_sources=sources,
                )
            )
        return replace(flow, stages=stages)
