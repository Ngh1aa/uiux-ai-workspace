from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.skills.execution_context import SkillSelection


@dataclass(frozen=True)
class RoutedSkill:
    path: str
    reason: str


class AdaptiveSkillRouter:
    """Route ONLY real skills_UIUX SKILL.md paths."""

    BASE_BY_STAGE: dict[str, tuple[RoutedSkill, ...]] = {
        "reference_analysis": (
            RoutedSkill("reference-extraction-and-design-audit/SKILL.md", "Extract measured values with source and certainty."),
            RoutedSkill("design-reference-research-and-benchmark/SKILL.md", "Separate transferable principles from proprietary brand assets."),
        ),
        "research": (
            RoutedSkill("project-context/SKILL.md", "Keep project truth and constraints explicit."),
            RoutedSkill("product-discovery/SKILL.md", "Frame audience, problem, JTBD, scope and unknowns."),
            RoutedSkill(
                "design-reference-research-and-benchmark/SKILL.md",
                "Research relevant references without confusing popularity with evidence.",
            ),
        ),
        "ux_ia": (
            RoutedSkill("ux-research-and-journey/SKILL.md", "Ground journeys and task analysis."),
            RoutedSkill("information-architecture/SKILL.md", "Own hierarchy, taxonomy, navigation and page roles."),
            RoutedSkill("audience-intent-and-top-tasks/SKILL.md", "Prioritize audience intents and top tasks."),
            RoutedSkill("journey-driven-content-and-layout/SKILL.md", "Map journey needs into content/layout structure."),
        ),
        "art_direction": (
            RoutedSkill("visual-design-direction/SKILL.md", "Own visual grammar, hierarchy and composition."),
            RoutedSkill("visual-taste-calibration/SKILL.md", "Prevent generic/template-like visual output."),
            RoutedSkill("brand-guidelines/SKILL.md", "Translate brand truth into visual rules."),
            RoutedSkill("asset-media-and-art-direction/SKILL.md", "Define media/image/icon direction."),
        ),
        "design_contract": (
            RoutedSkill("project-context/SKILL.md", "Preserve project truth in the canonical contract."),
            RoutedSkill("visual-design-direction/SKILL.md", "Carry approved visual direction into constraints."),
            RoutedSkill("design-system-and-components/SKILL.md", "Define implementation-facing system constraints."),
        ),
        "design_system": (
            RoutedSkill("design-system-and-components/SKILL.md", "Own tokens, components, variants and states."),
            RoutedSkill("brand-guidelines/SKILL.md", "Keep tokens connected to brand truth."),
            RoutedSkill("responsive-and-device-strategy/SKILL.md", "Make device behavior part of the system."),
            RoutedSkill("accessibility/SKILL.md", "Make accessibility part of component contracts."),
        ),
        "implementation_plan": (
            RoutedSkill("frontend-architecture-and-refactoring/SKILL.md", "Plan maintainable frontend ownership/boundaries."),
            RoutedSkill("frontend-implementation/SKILL.md", "Plan implementation against approved design decisions."),
            RoutedSkill("ai-agent-coding-guardrails/SKILL.md", "Require dependency-aware slices and verification."),
        ),
        "visual_composition": (
            RoutedSkill("visual-design-direction/SKILL.md", "Convert direction into page-level composition."),
            RoutedSkill("visual-taste-calibration/SKILL.md", "Check distinctiveness and anti-template quality."),
            RoutedSkill("responsive-and-device-strategy/SKILL.md", "Define mobile/tablet transformations."),
            RoutedSkill("asset-media-and-art-direction/SKILL.md", "Define page visual anchors/media role."),
        ),
        "implementation": (
            RoutedSkill("frontend-implementation/SKILL.md", "Own semantic implementation and verification."),
            RoutedSkill("ai-agent-coding-guardrails/SKILL.md", "Prevent unsafe or generic AI code."),
            RoutedSkill("design-system-and-components/SKILL.md", "Consume canonical tokens/components."),
            RoutedSkill("responsive-and-device-strategy/SKILL.md", "Implement explicit responsive behavior."),
            RoutedSkill("accessibility/SKILL.md", "Implement semantic/focus/keyboard baseline."),
        ),
        "browser_qa": (
            RoutedSkill("testing-strategy/SKILL.md", "Drive risk-based verification."),
            RoutedSkill("ui-craft-and-visual-qa/SKILL.md", "Inspect rendered UI rather than trusting build success."),
            RoutedSkill("accessibility/SKILL.md", "Verify semantic/focus accessibility baseline."),
            RoutedSkill("visual-regression-and-design-drift/SKILL.md", "Treat screenshots as regression evidence."),
        ),
        "visual_qa": (
            RoutedSkill("ui-craft-and-visual-qa/SKILL.md", "Judge rendered craft and responsive quality."),
            RoutedSkill("visual-taste-calibration/SKILL.md", "Detect generic/interchangeable visual treatment."),
            RoutedSkill("visual-regression-and-design-drift/SKILL.md", "Compare rendered evidence and design drift."),
            RoutedSkill("accessibility/SKILL.md", "Keep accessibility in acceptance."),
        ),
        "repair": (
            RoutedSkill("ui-improvement/SKILL.md", "Diagnose, preserve, route and repair existing UI."),
            RoutedSkill("frontend-implementation/SKILL.md", "Apply maintainable implementation fixes."),
            RoutedSkill("ai-agent-coding-guardrails/SKILL.md", "Keep repair bounded and verifiable."),
            RoutedSkill("visual-taste-calibration/SKILL.md", "Repair generic visual treatment."),
            RoutedSkill("responsive-and-device-strategy/SKILL.md", "Repair device-specific issues."),
            RoutedSkill("accessibility/SKILL.md", "Do not regress accessibility while repairing."),
        ),
    }

    DOMAIN_SKILLS: dict[str, tuple[RoutedSkill, ...]] = {
        "ecommerce": (
            RoutedSkill("ecommerce-website/SKILL.md", "Apply the real ecommerce discover-to-checkout playbook."),
        ),
        "corporate": (
            RoutedSkill("corporate-website/SKILL.md", "Apply the real corporate/B2B website playbook."),
        ),
        "education": (
            RoutedSkill("education-website/SKILL.md", "Apply the real education website playbook."),
        ),
        "agency": (
            RoutedSkill("corporate-website/SKILL.md", "Use the real corporate playbook for B2B credibility."),
            RoutedSkill("conversion-and-content/SKILL.md", "Use the real conversion/content skill for proof and CTA."),
        ),
    }

    OPTIONAL_BY_SIGNAL = (
        (
            ("redesign", "thiết kế lại", "website cũ", "legacy"),
            RoutedSkill("website-audit-and-redesign/SKILL.md", "Audit an existing/legacy site before redesign."),
            ("research", "ux_ia"),
        ),
        (
            ("search", "tìm kiếm", "findability"),
            RoutedSkill("site-search-and-findability/SKILL.md", "Search/findability is material to this experience."),
            ("ux_ia", "visual_composition", "implementation"),
        ),
        (
            ("form", "lead", "đăng ký", "tuyển sinh", "checkout"),
            RoutedSkill("interaction-patterns-and-form-ux/SKILL.md", "Forms/transactional input are material."),
            ("ux_ia", "design_system", "implementation"),
        ),
    )

    @staticmethod
    def infer_domain(goal: str) -> str:
        text = goal.lower()
        signals = {
            "ecommerce": ("ecommerce", "e-commerce", "thương mại điện tử", "marketplace", "shop", "shopee", "giỏ hàng", "checkout"),
            "education": ("education", "school", "academy", "trường học", "trường", "học sinh", "tuyển sinh", "phụ huynh"),
            "agency": ("agency", "digital agency", "marketing", "seo", "quảng cáo", "creative studio"),
            "corporate": ("corporate", "company", "doanh nghiệp", "công ty", "b2b", "enterprise", "technology", "công nghệ"),
        }
        scores = {
            domain: sum(1 for token in tokens if token in text)
            for domain, tokens in signals.items()
        }
        best = max(scores, key=scores.get)
        return best if scores[best] else "corporate"

    @classmethod
    def route(cls, stage: str, goal: str, domain: str | None = None) -> SkillSelection:
        resolved_domain = domain or cls.infer_domain(goal)
        selected = list(cls.BASE_BY_STAGE.get(stage, ()))

        if stage in {
            "research", "ux_ia", "art_direction", "design_system",
            "implementation_plan", "visual_composition", "implementation",
            "visual_qa", "repair",
        }:
            selected.extend(cls.DOMAIN_SKILLS.get(resolved_domain, ()))

        lowered = goal.lower()
        for signals, routed_skill, stages in cls.OPTIONAL_BY_SIGNAL:
            if stage in stages and any(signal in lowered for signal in signals):
                selected.append(routed_skill)

        deduped: dict[str, RoutedSkill] = {}
        for item in selected:
            deduped.setdefault(item.path, item)

        return SkillSelection(
            stage=stage,
            domain=resolved_domain,
            goal=goal,
            relative_paths=list(deduped),
            reasons={path: item.reason for path, item in deduped.items()},
        )

    @classmethod
    def all_declared_paths(cls) -> set[str]:
        paths: set[str] = set()
        for items in cls.BASE_BY_STAGE.values():
            paths.update(item.path for item in items)
        for items in cls.DOMAIN_SKILLS.values():
            paths.update(item.path for item in items)
        for _signals, item, _stages in cls.OPTIONAL_BY_SIGNAL:
            paths.add(item.path)
        return paths

    @classmethod
    def validate_declared_paths(cls, skills_root: Path) -> list[str]:
        return [
            relative_path
            for relative_path in sorted(cls.all_declared_paths())
            if not (skills_root / relative_path).exists()
        ]
