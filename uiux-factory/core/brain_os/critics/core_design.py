from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

from pydantic import Field

from core.brain_os.contracts import BrainContractModel
from core.brain_os.critique_contracts import (
    CritiqueIssue,
    CritiqueIssueStatus,
    CritiqueSeverity,
)
from core.contracts.design_system_schema import ComponentContract, DesignSystemContract
from core.contracts.schema import DesignContract
from core.contracts.visual_composition_schema import VisualComposition
from core.orchestration.visual_brain import VisualBrain


VISUAL_BRAIN_OWNER = "core.orchestration.visual_brain.VisualBrain"


def _issue_id(critic: str, category: str, summary: str) -> str:
    raw = f"{critic}\n{category}\n{summary}".encode("utf-8")
    return f"CR-{hashlib.sha256(raw).hexdigest()[:16]}"


def _issue(
    *,
    critic: str,
    category: str,
    severity: CritiqueSeverity,
    summary: str,
    rationale: str,
    affected_artifacts: list[str],
) -> CritiqueIssue:
    return CritiqueIssue(
        id=_issue_id(critic, category, summary),
        critic=critic,
        category=category,
        severity=severity,
        status=CritiqueIssueStatus.OBSERVED,
        summary=summary,
        rationale=rationale,
        evidence_refs=[],
        affected_artifacts=affected_artifacts,
    )


class CoreCriticReport(BrainContractModel):
    """Advisory critic output; absence of issues is never runtime QA PASS."""

    schema_version: Literal["brain-core-critic.v1"] = "brain-core-critic.v1"
    critic_id: Literal["visual", "ux_ia", "design_system", "accessibility"]
    issues: list[CritiqueIssue] = Field(default_factory=list, max_length=500)
    reviewed_artifacts: list[str] = Field(default_factory=list, max_length=50)
    source_owner: str = Field(default="brain_contract_review", max_length=500)
    upstream_status: str = Field(default="", max_length=128)
    upstream_score: int | None = Field(default=None, ge=0, le=100)
    advisory_only: Literal[True] = True
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"


class VisualBrainCriticAdapter:
    """Read-only adapter over the existing deterministic VisualBrain.

    The adapter intentionally calls `evaluate()` only. It never invokes
    `apply_calibration()` and therefore does not mutate VisualComposition or write files.
    VisualBrain gate/status data is converted into advisory OBSERVED critique issues;
    Brain OS does not inherit the upstream gate authority.
    """

    _GATE_RULES = {
        "five_core_skills_loaded": (
            CritiqueSeverity.P0,
            "Visual review skill policy is incomplete",
            "Existing VisualBrain could not load all five canonical visual/interaction skills.",
        ),
        "visual_signature_specific": (
            CritiqueSeverity.P1,
            "Visual signature is not specific enough",
            "Existing VisualBrain reports that the visual signature is still generic rather than project-specific.",
        ),
        "page_roles_materially_distinct": (
            CritiqueSeverity.P1,
            "Page roles are not materially distinct",
            "Existing VisualBrain reports insufficient composition-family diversity for the declared page roles.",
        ),
        "decision_objects_specific": (
            CritiqueSeverity.P1,
            "Decision/evidence objects remain generic",
            "Existing VisualBrain reports generic first-screen anchors instead of domain-native decision/evidence objects.",
        ),
        "interaction_contracts_present": (
            CritiqueSeverity.P0,
            "Interaction contracts are incomplete",
            "Existing VisualBrain found routes whose interaction intent is not backed by explicit interaction-state rules.",
        ),
        "mobile_transformations_present": (
            CritiqueSeverity.P1,
            "Mobile transformations are incomplete",
            "Existing VisualBrain reports sections without explicit mobile transformation behavior.",
        ),
        "no_blocking_generic_pattern": (
            CritiqueSeverity.P1,
            "Blocking generic visual patterns remain",
            "Existing VisualBrain found enough generic composition signals to block a distinct visual direction.",
        ),
    }

    def __init__(self, skills_root: Path) -> None:
        self.visual_brain = VisualBrain(skills_root)

    def review(
        self,
        *,
        contract: DesignContract,
        design_system: DesignSystemContract,
        composition: VisualComposition,
    ) -> CoreCriticReport:
        upstream = self.visual_brain.evaluate(
            contract=contract,
            design_system=design_system,
            composition=composition,
        )
        issues: list[CritiqueIssue] = []
        gates = upstream.gates.model_dump()
        for gate_name, (severity, summary, rationale) in self._GATE_RULES.items():
            if gates.get(gate_name) is False:
                issues.append(
                    _issue(
                        critic="visual",
                        category=f"visual.{gate_name}",
                        severity=severity,
                        summary=summary,
                        rationale=rationale,
                        affected_artifacts=["design_contract", "design_system", "visual_composition"],
                    )
                )

        for tell in upstream.generic_tells:
            issues.append(
                _issue(
                    critic="visual",
                    category="visual.generic_tell",
                    severity=CritiqueSeverity.P1,
                    summary=str(tell)[:4000],
                    rationale="This finding is emitted by the existing VisualBrain generic-pattern detector and remains advisory until linked to evidence/retest lineage.",
                    affected_artifacts=["visual_composition"],
                )
            )

        deduped = {item.id: item for item in issues}
        return CoreCriticReport(
            critic_id="visual",
            issues=list(deduped.values()),
            reviewed_artifacts=["design_contract", "design_system", "visual_composition"],
            source_owner=VISUAL_BRAIN_OWNER,
            upstream_status=upstream.status,
            upstream_score=upstream.score.overall,
        )


class UXIACritic:
    """Bounded structural UX/IA critic over existing design contracts."""

    def review(
        self,
        *,
        contract: DesignContract,
        composition: VisualComposition,
    ) -> CoreCriticReport:
        issues: list[CritiqueIssue] = []
        ux = contract.ux

        if not ux.page_roles:
            issues.append(_issue(
                critic="ux_ia",
                category="ux_ia.page_roles_missing",
                severity=CritiqueSeverity.P0,
                summary="No UX page roles are defined",
                rationale="The design contract cannot establish page purpose or route responsibility without explicit UX page roles.",
                affected_artifacts=["design_contract"],
            ))
        else:
            names = [item.name.strip().lower() for item in ux.page_roles if item.name.strip()]
            if len(names) != len(set(names)):
                issues.append(_issue(
                    critic="ux_ia",
                    category="ux_ia.duplicate_page_roles",
                    severity=CritiqueSeverity.P1,
                    summary="Duplicate UX page-role names are present",
                    rationale="Duplicate route/page ownership makes information architecture and handoff ambiguous.",
                    affected_artifacts=["design_contract"],
                ))

        if not ux.primary_journey:
            issues.append(_issue(
                critic="ux_ia",
                category="ux_ia.primary_journey_missing",
                severity=CritiqueSeverity.P1,
                summary="Primary user journey is not defined",
                rationale="A page set without a primary journey cannot show how the top task progresses across states or routes.",
                affected_artifacts=["design_contract"],
            ))

        if not composition.pages:
            issues.append(_issue(
                critic="ux_ia",
                category="ux_ia.pages_missing",
                severity=CritiqueSeverity.P0,
                summary="Visual composition has no pages",
                rationale="There is no route-level composition to inspect against the UX contract.",
                affected_artifacts=["visual_composition"],
            ))
        else:
            paths = [page.path.strip() for page in composition.pages if page.path.strip()]
            if len(paths) != len(set(paths)):
                issues.append(_issue(
                    critic="ux_ia",
                    category="ux_ia.duplicate_routes",
                    severity=CritiqueSeverity.P0,
                    summary="Duplicate route paths exist in visual composition",
                    rationale="Multiple page definitions for the same route create ambiguous IA ownership.",
                    affected_artifacts=["visual_composition"],
                ))
            for page in composition.pages:
                if not page.page_role.strip():
                    issues.append(_issue(
                        critic="ux_ia",
                        category="ux_ia.page_role_blank",
                        severity=CritiqueSeverity.P1,
                        summary=f"Page {page.path or '(unknown)'} has no page role",
                        rationale="Every composed route needs an explicit user-facing role before visual treatment can be reviewed in context.",
                        affected_artifacts=["visual_composition"],
                    ))
                if not page.sections:
                    issues.append(_issue(
                        critic="ux_ia",
                        category="ux_ia.page_sections_missing",
                        severity=CritiqueSeverity.P1,
                        summary=f"Page {page.path or '(unknown)'} has no section structure",
                        rationale="The route has no inspectable content/action hierarchy.",
                        affected_artifacts=["visual_composition"],
                    ))

        if not composition.gates.page_roles_mapped:
            issues.append(_issue(
                critic="ux_ia",
                category="ux_ia.page_role_mapping_unconfirmed",
                severity=CritiqueSeverity.P1,
                summary="Page-role mapping is not established",
                rationale="The existing composition contract reports page_roles_mapped=false. The critic records this as an observation only and does not change that gate.",
                affected_artifacts=["visual_composition"],
            ))

        return CoreCriticReport(
            critic_id="ux_ia",
            issues=issues,
            reviewed_artifacts=["design_contract", "visual_composition"],
        )


class DesignSystemCritic:
    """Bounded critic for token/component system completeness."""

    _GATE_RULES = {
        "semantic_tokens_defined": (CritiqueSeverity.P1, "Semantic token roles are not defined"),
        "p0_component_states_defined": (CritiqueSeverity.P0, "P0 component states are incomplete"),
        "responsive_contracts_defined": (CritiqueSeverity.P1, "Responsive component contracts are incomplete"),
        "accessibility_contracts_defined": (CritiqueSeverity.P0, "Accessibility component contracts are incomplete"),
        "implementation_ready_with_fallbacks": (CritiqueSeverity.P1, "Design system is not implementation-ready with fallbacks"),
    }

    @staticmethod
    def _unresolved_token_count(system: DesignSystemContract) -> int:
        count = 0
        foundations = system.foundations
        for group_name in ("colors", "typography", "spacing", "radius", "border", "elevation", "motion", "layout"):
            group = getattr(foundations, group_name)
            count += sum(1 for token in group.values() if token.status == "unresolved")
        return count

    def review(self, *, design_system: DesignSystemContract) -> CoreCriticReport:
        issues: list[CritiqueIssue] = []
        gates = design_system.gates.model_dump()
        for gate_name, (severity, summary) in self._GATE_RULES.items():
            if gates.get(gate_name) is False:
                issues.append(_issue(
                    critic="design_system",
                    category=f"design_system.{gate_name}",
                    severity=severity,
                    summary=summary,
                    rationale=f"Existing DesignSystemGate reports {gate_name}=false; Brain records the gap but cannot change the source gate.",
                    affected_artifacts=["design_system"],
                ))

        unresolved = self._unresolved_token_count(design_system)
        if unresolved:
            issues.append(_issue(
                critic="design_system",
                category="design_system.unresolved_tokens",
                severity=CritiqueSeverity.P1,
                summary=f"{unresolved} foundation token(s) remain unresolved",
                rationale="Unresolved token values weaken implementation consistency and should be resolved or explicitly handled through an existing fallback contract.",
                affected_artifacts=["design_system"],
            ))

        names = [component.name.strip().lower() for component in design_system.components if component.name.strip()]
        if len(names) != len(set(names)):
            issues.append(_issue(
                critic="design_system",
                category="design_system.duplicate_components",
                severity=CritiqueSeverity.P1,
                summary="Duplicate component names exist in the design system",
                rationale="Duplicate component identity makes variants/states and implementation ownership ambiguous.",
                affected_artifacts=["design_system"],
            ))

        for component in design_system.components:
            if component.priority == "P0" and not component.states:
                issues.append(_issue(
                    critic="design_system",
                    category="design_system.p0_states_missing",
                    severity=CritiqueSeverity.P0,
                    summary=f"P0 component {component.name} has no states",
                    rationale="Critical components require explicit state contracts before implementation/review can be reliable.",
                    affected_artifacts=["design_system"],
                ))
            if not component.responsive_behavior:
                issues.append(_issue(
                    critic="design_system",
                    category="design_system.responsive_contract_missing",
                    severity=CritiqueSeverity.P1,
                    summary=f"Component {component.name} has no responsive behavior contract",
                    rationale="Component behavior across breakpoints is unspecified.",
                    affected_artifacts=["design_system"],
                ))

        if design_system.unresolved_items:
            issues.append(_issue(
                critic="design_system",
                category="design_system.unresolved_items",
                severity=CritiqueSeverity.P2,
                summary=f"Design system contains {len(design_system.unresolved_items)} unresolved item(s)",
                rationale="Unresolved items are retained as explicit design debt rather than silently treated as complete.",
                affected_artifacts=["design_system"],
            ))

        return CoreCriticReport(
            critic_id="design_system",
            issues=issues,
            reviewed_artifacts=["design_system"],
        )


class AccessibilityCritic:
    """Contract-level accessibility critic; runtime accessibility testing remains separate."""

    INTERACTIVE_TERMS = (
        "button", "input", "form", "select", "checkbox", "radio", "tab", "menu",
        "navigation", "nav", "modal", "dialog", "search", "checkout", "link", "toggle",
    )

    @classmethod
    def _is_interactive(cls, component: ComponentContract) -> bool:
        haystack = f"{component.name} {component.purpose}".lower()
        return any(term in haystack for term in cls.INTERACTIVE_TERMS)

    def review(self, *, design_system: DesignSystemContract) -> CoreCriticReport:
        issues: list[CritiqueIssue] = []

        if not design_system.gates.accessibility_contracts_defined:
            issues.append(_issue(
                critic="accessibility",
                category="accessibility.contract_gate_unconfirmed",
                severity=CritiqueSeverity.P0,
                summary="Accessibility contracts are not defined at design-system level",
                rationale="The source DesignSystemGate reports accessibility_contracts_defined=false. This remains a source-gate observation, not a Brain gate decision.",
                affected_artifacts=["design_system"],
            ))

        for component in design_system.components:
            interactive = self._is_interactive(component)
            if component.priority == "P0" and not component.accessibility:
                issues.append(_issue(
                    critic="accessibility",
                    category="accessibility.p0_contract_missing",
                    severity=CritiqueSeverity.P0,
                    summary=f"P0 component {component.name} has no accessibility contract",
                    rationale="Critical components need explicit accessibility behavior before runtime testing can verify the implementation.",
                    affected_artifacts=["design_system"],
                ))
            if interactive and not component.states:
                issues.append(_issue(
                    critic="accessibility",
                    category="accessibility.interactive_states_missing",
                    severity=CritiqueSeverity.P0,
                    summary=f"Interactive component {component.name} has no state contract",
                    rationale="Interactive controls need explicit states so focus, disabled, error, pending or selected behavior can be implemented and tested where applicable.",
                    affected_artifacts=["design_system"],
                ))
            if interactive and component.accessibility:
                text = " ".join(component.accessibility).lower()
                if not any(term in text for term in ("keyboard", "focus", "screen reader", "aria", "label", "semantic")):
                    issues.append(_issue(
                        critic="accessibility",
                        category="accessibility.interaction_detail_thin",
                        severity=CritiqueSeverity.P1,
                        summary=f"Interactive component {component.name} accessibility contract lacks interaction semantics",
                        rationale="The accessibility notes do not mention keyboard/focus/semantic labeling or equivalent interaction semantics; runtime verification should not have to infer the intended contract.",
                        affected_artifacts=["design_system"],
                    ))

        motion_tokens = design_system.foundations.motion
        if motion_tokens:
            a11y_text = " ".join(
                rule
                for component in design_system.components
                for rule in component.accessibility
            ).lower()
            pattern_text = " ".join(
                rule
                for pattern in design_system.patterns
                for rule in pattern.rules
            ).lower()
            if not any(term in f"{a11y_text} {pattern_text}" for term in ("reduced motion", "prefers-reduced-motion", "reduce motion")):
                issues.append(_issue(
                    critic="accessibility",
                    category="accessibility.reduced_motion_contract_missing",
                    severity=CritiqueSeverity.P1,
                    summary="Motion tokens exist without an explicit reduced-motion contract",
                    rationale="The design system defines motion but does not state how reduced-motion preference is handled. This is a contract gap, not a runtime WCAG verdict.",
                    affected_artifacts=["design_system"],
                ))

        return CoreCriticReport(
            critic_id="accessibility",
            issues=issues,
            reviewed_artifacts=["design_system"],
        )
