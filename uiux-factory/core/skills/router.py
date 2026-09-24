from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.orchestration.intelligent_flow import GoalInterpreter, ProfessionalWebsiteFlow
from core.skills.execution_context import SkillSelection


@dataclass(frozen=True)
class RoutedSkill:
    path: str
    reason: str


class AdaptiveSkillRouter:
    """Route real skills_UIUX paths using its declarative professional website flow."""

class AdaptiveSkillRouter:
    """Route real skills_UIUX paths using its declarative professional website flow."""

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
            RoutedSkill("ux-benchmarking-and-metrics/SKILL.md", "Establish measurable UX quality baselines."),
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
            RoutedSkill("motion-and-microinteractions/SKILL.md", "Define motion language, easing curves and micro-interactions."),
            RoutedSkill("experience-principles-and-signature-moments/SKILL.md", "Define signature design moments that make the product memorable."),
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
            RoutedSkill("component-driven-development/SKILL.md", "Structure components for composition and reuse."),
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
            RoutedSkill("trust-credibility-and-transparency/SKILL.md", "Ensure trust signals and credibility are designed into composition."),
            RoutedSkill("ux-laws-and-heuristics/SKILL.md", "Apply proven UX laws to layout and interaction design."),
        ),
        "implementation": (
            RoutedSkill("frontend-implementation/SKILL.md", "Own semantic implementation and verification."),
            RoutedSkill("ai-agent-coding-guardrails/SKILL.md", "Prevent unsafe or generic AI code."),
            RoutedSkill("design-system-and-components/SKILL.md", "Consume canonical tokens/components."),
            RoutedSkill("responsive-and-device-strategy/SKILL.md", "Implement explicit responsive behavior."),
            RoutedSkill("accessibility/SKILL.md", "Implement semantic/focus/keyboard baseline."),
            RoutedSkill("motion-and-microinteractions/SKILL.md", "Implement CSS transitions, keyframes and scroll-triggered animations."),
            RoutedSkill("state-feedback-and-error-recovery/SKILL.md", "Implement loading, empty, error and success states."),
        ),
        "browser_qa": (
            RoutedSkill("testing-strategy/SKILL.md", "Drive risk-based verification."),
            RoutedSkill("ui-craft-and-visual-qa/SKILL.md", "Inspect rendered UI rather than trusting build success."),
            RoutedSkill("accessibility/SKILL.md", "Verify semantic/focus accessibility baseline."),
            RoutedSkill("visual-regression-and-design-drift/SKILL.md", "Treat screenshots as regression evidence."),
            RoutedSkill("web-quality-and-performance/SKILL.md", "Check Core Web Vitals and rendering performance."),
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

    _interpreter = GoalInterpreter()

    @classmethod
    def infer_domain(cls, goal: str) -> str:
        return cls._interpreter.interpret(goal).website_type

    @classmethod
    def route(
        cls,
        stage: str,
        goal: str,
        domain: str | None = None,
        skills_root: Path | None = None,
    ) -> SkillSelection:
        if skills_root is None:
            workspace_root = Path(__file__).resolve().parents[3]
            skills_root = workspace_root / "skills_UIUX"

        flow = ProfessionalWebsiteFlow(skills_root)
        profile, paths, mandatory_paths = flow.resolve_paths(stage, goal)
        resolved_domain = domain or profile.website_type

        reasons: dict[str, str] = {}
        mandatory = set(mandatory_paths)
        for path in paths:
            skill_name = path.removesuffix("/SKILL.md")
            if path in mandatory:
                reasons[path] = (
                    f"Mandatory capability from skills_UIUX professional website flow "
                    f"for {flow.FACTORY_TO_FLOW_STAGE[stage]} stage: {skill_name}."
                )
            else:
                reasons[path] = (
                    f"Domain/factory-stage capability selected for website_type="
                    f"{profile.website_type}: {skill_name}."
                )

        return SkillSelection(
            stage=stage,
            domain=resolved_domain,
            goal=goal,
            relative_paths=paths,
            mandatory_paths=mandatory_paths,
            reasons=reasons,
        )

    @classmethod
    def all_declared_paths(cls, skills_root: Path | None = None) -> set[str]:
        if skills_root is None:
            workspace_root = Path(__file__).resolve().parents[3]
            skills_root = workspace_root / "skills_UIUX"
        paths: set[str] = set()
        flow = ProfessionalWebsiteFlow(skills_root)
        document = flow.document
        for stage in document.get("stages", []):
            for skill in stage.get("required_skills", []):
                paths.add(f"{skill}/SKILL.md")
            for rule in stage.get("conditional_skills", []):
                for skill in rule.get("skills", []):
                    paths.add(f"{skill}/SKILL.md")
        for extras in flow.EXTRA_BY_FACTORY_STAGE.values():
            paths.update(f"{skill}/SKILL.md" for skill in extras)
        paths.update(
            {
                "web-ui-code-review/SKILL.md",
                "state-feedback-and-error-recovery/SKILL.md",
            }
        )
        return paths

    @classmethod
    def validate_declared_paths(cls, skills_root: Path) -> list[str]:
        return [
            relative_path
            for relative_path in sorted(cls.all_declared_paths(skills_root))
            if not (Path(skills_root) / relative_path).is_file()
        ]
