from __future__ import annotations

from collections import Counter
from pathlib import Path

from core.contracts.design_system_schema import DesignSystemContract
from core.contracts.schema import DesignContract
from core.contracts.visual_brain_schema import (
    VisualBrainGate,
    VisualBrainReport,
    VisualBrainRouteDiagnostic,
    VisualBrainScore,
)
from core.contracts.visual_composition_schema import VisualComposition
from core.skills.policy_resolver import SkillPolicyResolver


class VisualBrain:
    """Pre-code visual calibration driven by the canonical skills_UIUX policies.

    This is intentionally deterministic: it converts the five visual/interaction
    skills into an auditable gate and calibration artifact. Provider refinement
    may still improve the upstream Art Direction / Visual Composition, but it
    cannot bypass this pre-code review.
    """

    CORE_SKILLS = (
        "visual-design-direction/SKILL.md",
        "brand-distinctiveness-and-visual-signature/SKILL.md",
        "visual-taste-calibration/SKILL.md",
        "interaction-patterns-and-form-ux/SKILL.md",
        "ui-craft-and-visual-qa/SKILL.md",
    )

    GENERIC_ANCHORS = {
        "primary evidence object",
        "page-specific decision object",
        "page-specific evidence",
        "next action",
        "real evidence",
        "proof",
        "content",
    }
    GENERIC_COMPOSITIONS = {
        "content-led",
        "purpose-led",
        "generic-hero",
        "three-card-grid",
        "equal-card-grid",
    }
    INTERACTION_TERMS = {
        "search": "Define query, empty/no-result, keyboard and recovery behavior.",
        "filter": "Keep active filters/result count visible; define mobile drawer and clear behavior.",
        "form": "Define labels, validation, pending/error/success and data-preserving recovery.",
        "checkout": "Keep transaction states truthful; define validation, error recovery and completion feedback.",
        "cart": "Define quantity/remove/update feedback and recovery without hiding totals.",
        "contact": "Define form labels, validation, submit state and confirmation/recovery behavior.",
        "admission": "Define progress, validation, back behavior and completion outcome for application tasks.",
        "apply": "Define progress, validation, back behavior and completion outcome for application tasks.",
    }

    def __init__(self, skills_root: Path) -> None:
        self.skills_root = Path(skills_root).resolve()
        self.resolver = SkillPolicyResolver(self.skills_root)

    @staticmethod
    def clamp(value: float) -> int:
        return max(0, min(100, int(round(value))))

    @staticmethod
    def _specific_signature(signature: str) -> bool:
        text = (signature or "").strip().lower()
        generic = (
            "modern clean",
            "clean and modern",
            "premium website",
            "purpose-led website",
            "professional website",
            "beautiful website",
        )
        return len(text) >= 48 and not any(token in text for token in generic)

    @staticmethod
    def _interaction_requirements(page) -> list[str]:
        haystack = " ".join(
            [page.path, page.page_role]
            + [section.type + " " + section.composition for section in page.sections]
        ).lower()
        requirements = []
        for term, rule in VisualBrain.INTERACTION_TERMS.items():
            if term in haystack and rule not in requirements:
                requirements.append(rule)
        return requirements

    @staticmethod
    def _route_generic_tells(page) -> list[str]:
        tells: list[str] = []
        anchor = page.first_visual_anchor.strip().lower()
        if anchor in VisualBrain.GENERIC_ANCHORS or "page-specific" in anchor:
            tells.append("First visual anchor is generic instead of naming a real decision/evidence object.")
        for section in page.sections:
            composition = section.composition.strip().lower()
            if composition in VisualBrain.GENERIC_COMPOSITIONS:
                tells.append(f"Generic composition token: {section.composition}.")
            if "three-card" in composition or "equal-card" in composition:
                tells.append(f"Interchangeable card-grid pattern: {section.composition}.")
        return list(dict.fromkeys(tells))

    def evaluate(
        self,
        *,
        contract: DesignContract,
        design_system: DesignSystemContract,
        composition: VisualComposition,
    ) -> VisualBrainReport:
        policies = [self.resolver.load(path) for path in self.CORE_SKILLS]
        skill_map = {policy.relative_path: policy.sha256 for policy in policies}
        pages = composition.pages
        family_counts = Counter(page.composition_family for page in pages if page.composition_family)
        family_count = len(family_counts)
        required_families = min(3, max(1, len(pages)))

        signature_specific = self._specific_signature(composition.visual_signature)
        brand_evidence = (
            len(design_system.brand.personality)
            + len(design_system.brand.reference_patterns)
            + len(contract.visual.attributes)
        )
        brand_recognition = self.clamp(
            58
            + (22 if signature_specific else 0)
            + min(14, brand_evidence * 3)
        )

        route_diagnostics: list[VisualBrainRouteDiagnostic] = []
        generic_tells: list[str] = []
        specific_anchor_count = 0
        interaction_route_count = 0
        interaction_defined_count = 0
        mobile_section_count = 0
        total_section_count = 0

        for page in pages:
            tells = self._route_generic_tells(page)
            requirements = self._interaction_requirements(page)
            generic_tells.extend(f"{page.path}: {tell}" for tell in tells)
            if not tells:
                specific_anchor_count += 1
            if requirements:
                interaction_route_count += 1
                # Existing composition carries interaction intent when the
                # relevant pattern appears in composition/notes/mobile rules.
                interaction_text = " ".join(
                    section.composition + " " + " ".join(section.notes + section.mobile_behavior)
                    for section in page.sections
                ).lower()
                markers = ("form", "filter", "search", "transaction", "drawer", "validation", "action")
                if any(marker in interaction_text for marker in markers):
                    interaction_defined_count += 1

            for section in page.sections:
                total_section_count += 1
                if section.mobile_behavior:
                    mobile_section_count += 1

            directives = [
                "Make the first screen answer this page role's user question before decorative storytelling.",
                "Preserve one shared brand signature cue while keeping this page's decision object unique.",
            ]
            if tells:
                directives.append("Replace generic anchor/composition language with a domain-native object or evidence role before coding.")
            if requirements:
                directives.extend(requirements)

            route_diagnostics.append(
                VisualBrainRouteDiagnostic(
                    path=page.path,
                    page_role=page.page_role,
                    composition_family=page.composition_family,
                    first_visual_anchor=page.first_visual_anchor,
                    generic_tells=tells,
                    interaction_requirements=requirements,
                    calibration_directives=list(dict.fromkeys(directives)),
                )
            )

        decision_objects_specific = bool(pages) and specific_anchor_count == len(pages)
        page_role_diversity = self.clamp(
            60 + min(40, (family_count / max(1, required_families)) * 40)
        )
        if len(pages) >= 5 and family_count < 3:
            page_role_diversity = min(page_role_diversity, 65)
            generic_tells.append("Site has 5+ page roles but fewer than three composition families.")

        subject_fit = self.clamp(
            64
            + (22 if decision_objects_specific else 0)
            + min(12, len(contract.visual.media_rules) * 2)
        )
        interaction_clarity = 94 if interaction_route_count == 0 else self.clamp(
            55 + 45 * (interaction_defined_count / interaction_route_count)
        )
        responsive_intent = self.clamp(
            45 + 55 * (mobile_section_count / max(1, total_section_count))
        )

        repeated_penalty = sum(max(0, count - 2) * 6 for count in family_counts.values())
        generic_penalty = min(48, len(generic_tells) * 10 + repeated_penalty)
        anti_generic = self.clamp(96 - generic_penalty)
        overall = self.clamp(
            (
                brand_recognition
                + subject_fit
                + page_role_diversity
                + interaction_clarity
                + responsive_intent
                + anti_generic
            )
            / 6
        )

        blocking_generic = (
            len(pages) >= 3
            and len(generic_tells) > max(1, len(pages) // 2)
        )
        gates = VisualBrainGate(
            five_core_skills_loaded=len(skill_map) == len(self.CORE_SKILLS),
            visual_signature_specific=signature_specific,
            page_roles_materially_distinct=(family_count >= required_families),
            decision_objects_specific=decision_objects_specific,
            interaction_contracts_present=(
                interaction_route_count == 0
                or interaction_defined_count == interaction_route_count
            ),
            mobile_transformations_present=(
                total_section_count > 0 and mobile_section_count == total_section_count
            ),
            no_blocking_generic_pattern=not blocking_generic,
            ready_for_implementation=(
                len(skill_map) == len(self.CORE_SKILLS)
                and signature_specific
                and family_count >= required_families
                and responsive_intent >= 90
                and anti_generic >= 68
                and not blocking_generic
            ),
        )

        personality = ", ".join(design_system.brand.personality[:3]) or contract.project.domain
        memorable_commitment = (
            composition.visual_signature
            if signature_specific
            else f"Make {personality} recognizable through one repeated structural cue, not logo/color alone."
        )
        signature_cues = [
            "Repeat one composition/wayfinding motif across page roles without repeating the same hero shell.",
            "Use typography behavior and spacing rhythm as brand memory, not only token values.",
            "Keep media crop and decision-object treatment consistent with the project's subject matter.",
            "Keep interaction conventions familiar while making expression ownable.",
        ]
        keep = [
            "Page-role-specific composition families.",
            "Explicit mobile transformation rules.",
            "Decision/evidence objects that are stronger than decoration.",
        ]
        revise = list(dict.fromkeys(generic_tells))[:12]
        if not signature_specific:
            revise.insert(0, "Visual signature is too generic; define a one-sentence recognition commitment traceable to brand/domain truth.")
        remove = [
            "Interchangeable hero/card patterns that could move unchanged to an unrelated industry.",
            "Decorative badges, gradients or motion with no hierarchy/state/brand role.",
        ]

        return VisualBrainReport(
            status="passed" if gates.ready_for_implementation else ("blocked" if blocking_generic else "calibrated"),
            domain=contract.project.domain,
            memorable_commitment=memorable_commitment,
            signature_cues=signature_cues,
            generic_tells=list(dict.fromkeys(generic_tells)),
            keep=keep,
            revise=revise,
            remove=remove,
            route_diagnostics=route_diagnostics,
            skills=skill_map,
            score=VisualBrainScore(
                brand_recognition=brand_recognition,
                subject_fit=subject_fit,
                page_role_diversity=page_role_diversity,
                interaction_clarity=interaction_clarity,
                responsive_intent=responsive_intent,
                anti_generic=anti_generic,
                overall=overall,
            ),
            gates=gates,
        )

    @staticmethod
    def apply_calibration(
        composition: VisualComposition,
        report: VisualBrainReport,
    ) -> VisualComposition:
        calibrated = composition.model_copy(deep=True)
        calibrated.composition_principles = list(
            dict.fromkeys(
                calibrated.composition_principles
                + [f"Visual Brain commitment: {report.memorable_commitment}"]
                + [f"Signature cue: {cue}" for cue in report.signature_cues]
                + [f"REMOVE: {item}" for item in report.remove]
            )
        )
        by_path = {item.path: item for item in report.route_diagnostics}
        for page in calibrated.pages:
            diagnostic = by_path.get(page.path)
            if not diagnostic:
                continue
            page.anti_monotony_rules = list(
                dict.fromkeys(page.anti_monotony_rules + diagnostic.calibration_directives)
            )
        return calibrated
