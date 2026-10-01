from __future__ import annotations

from pathlib import Path

from core.brain_os.critics.core_design import (
    VISUAL_BRAIN_OWNER,
    AccessibilityCritic,
    DesignSystemCritic,
    UXIACritic,
    VisualBrainCriticAdapter,
)
from core.brain_os.critique_contracts import CritiqueIssueStatus
from core.contracts.design_context_schema import BrandDNA
from core.contracts.design_system_schema import (
    ComponentContract,
    DesignSystemContract,
    DesignSystemGate,
    FoundationTokens,
    PatternContract,
    TokenValue,
)
from core.contracts.schema import (
    DesignContract,
    EvidenceStatus,
    ImplementationConstraints,
    ProjectContract,
    UXContract,
    UXPageRole,
    VisualContract,
)
from core.contracts.visual_composition_schema import (
    PageSpec,
    SectionSpec,
    VisualComposition,
    VisualCompositionGate,
)


FACTORY = Path(__file__).resolve().parents[1]
SKILLS = FACTORY.parent / "skills_UIUX"


def _contract(*, complete_ux: bool = True) -> DesignContract:
    return DesignContract(
        project=ProjectContract(goal="Design a product experience", domain="generic"),
        ux=UXContract(
            principles=["Keep top tasks explicit"],
            page_roles=(
                [
                    UXPageRole(name="home", role="orientation"),
                    UXPageRole(name="detail", role="decision"),
                    UXPageRole(name="support", role="recovery"),
                ]
                if complete_ux
                else []
            ),
            primary_journey=(
                ["orient", "inspect", "decide", "recover"] if complete_ux else []
            ),
        ),
        visual=VisualContract(
            signature="A project-specific structural rhythm built around one evidence object per route and a repeated asymmetric wayfinding cue.",
            attributes=["clear", "specific", "evidence-led"],
            layout_rules=["Preserve route-specific composition"],
            media_rules=["Use subject-native media"],
        ),
        constraints=ImplementationConstraints(),
        gates=EvidenceStatus(),
        sources={},
    )


def _system(*, healthy: bool = False) -> DesignSystemContract:
    components = [
        ComponentContract(
            name="Primary Button",
            priority="P0",
            purpose="Submit the primary action",
            variants=["primary"],
            states=(
                ["default", "hover", "focus", "disabled", "loading"]
                if healthy
                else []
            ),
            responsive_behavior=(
                ["Full-width on compact viewports"] if healthy else []
            ),
            accessibility=(
                ["Keyboard focus remains visible and semantic button labeling is preserved"]
                if healthy
                else []
            ),
        )
    ]
    foundations = FoundationTokens(
        colors={"brand": TokenValue(value="#111111", status="confirmed", source="brand")},
        semantic_colors={"action.primary": "brand"} if healthy else {},
        typography={"body": TokenValue(value="Inter", status="confirmed", source="brand")},
        spacing={"space.2": TokenValue(value="8px", status="confirmed", source="system")},
        motion=(
            {"duration.fast": TokenValue(value="120ms", status="confirmed", source="system")}
            if healthy
            else {"duration.fast": TokenValue(value=None, status="unresolved", source="")}
        ),
    )
    return DesignSystemContract(
        domain="generic",
        brand=BrandDNA(
            name="Demo",
            personality=["precise", "calm", "distinct"],
            reference_patterns=["asymmetric evidence rail"],
        ),
        source_design_contract_path="design-contract.json",
        source_design_contract_sha256="a" * 64,
        relevant_skills=["design-system-and-components"],
        foundations=foundations,
        components=components,
        patterns=(
            [PatternContract(name="Motion accessibility", purpose="Respect user preference", rules=["Use prefers-reduced-motion to reduce motion"])]
            if healthy
            else []
        ),
        unresolved_items=[] if healthy else ["Confirm disabled-state contrast"],
        gates=DesignSystemGate(
            semantic_tokens_defined=healthy,
            p0_component_states_defined=healthy,
            responsive_contracts_defined=healthy,
            accessibility_contracts_defined=healthy,
            implementation_ready_with_fallbacks=healthy,
            final_visual_lock=False,
        ),
    )


def _composition(*, healthy: bool = True) -> VisualComposition:
    pages = []
    families = ["portal", "detail", "support"] if healthy else ["generic-hero"] * 3
    anchors = ["account balance evidence", "product comparison evidence", "support case status"] if healthy else ["content"] * 3
    for index, path in enumerate(("/", "/detail", "/support")):
        pages.append(
            PageSpec(
                path=path,
                page_role=("orientation", "decision", "recovery")[index],
                composition_family=families[index],
                first_visual_anchor=anchors[index],
                sections=[
                    SectionSpec(
                        type="evidence",
                        purpose="Answer the route's top user question",
                        priority="P0",
                        composition=("evidence-led asymmetric rail" if healthy else "three-card-grid"),
                        visual_anchor=anchors[index],
                        mobile_behavior=(
                            ["Stack evidence before secondary actions"] if healthy else []
                        ),
                        notes=["Preserve decision object"],
                    )
                ],
            )
        )
    return VisualComposition(
        domain="generic",
        project_slug="demo",
        visual_signature=(
            "A project-specific evidence rail repeated through asymmetric wayfinding and route-specific decision objects."
            if healthy
            else "clean and modern"
        ),
        composition_principles=["Evidence before decoration"],
        pages=pages,
        gates=VisualCompositionGate(
            page_roles_mapped=healthy,
            composition_families_diverse=healthy,
            mobile_transformations_defined=healthy,
            visual_anchors_defined=healthy,
            ready_for_frontend_engineer=healthy,
        ),
    )


def test_a44_visual_adapter_reuses_existing_visual_brain_without_mutating_artifacts() -> None:
    contract = _contract()
    system = _system(healthy=True)
    composition = _composition(healthy=False)
    before = composition.model_dump()

    report = VisualBrainCriticAdapter(SKILLS).review(
        contract=contract,
        design_system=system,
        composition=composition,
    )

    assert composition.model_dump() == before
    assert report.critic_id == "visual"
    assert report.source_owner == VISUAL_BRAIN_OWNER
    assert report.advisory_only is True
    assert report.authority_effect == report.gate_effect == report.evidence_effect == "none"
    assert report.issues
    assert all(issue.status is CritiqueIssueStatus.OBSERVED for issue in report.issues)
    assert all(issue.evidence_refs == [] for issue in report.issues)
    assert any(issue.category == "visual.visual_signature_specific" for issue in report.issues)
    assert any(issue.category == "visual.generic_tell" for issue in report.issues)


def test_a44_ux_ia_critic_flags_structure_gaps_without_changing_source_gate() -> None:
    contract = _contract(complete_ux=False)
    composition = _composition(healthy=False)
    before = composition.gates.model_dump()

    report = UXIACritic().review(contract=contract, composition=composition)
    categories = {issue.category for issue in report.issues}

    assert "ux_ia.page_roles_missing" in categories
    assert "ux_ia.primary_journey_missing" in categories
    assert "ux_ia.page_role_mapping_unconfirmed" in categories
    assert composition.gates.model_dump() == before
    assert report.gate_effect == "none"


def test_a44_design_system_critic_surfaces_p0_states_tokens_responsive_and_unresolved_debt() -> None:
    system = _system(healthy=False)
    before = system.model_dump()

    report = DesignSystemCritic().review(design_system=system)
    categories = {issue.category for issue in report.issues}

    assert "design_system.p0_component_states_defined" in categories
    assert "design_system.p0_states_missing" in categories
    assert "design_system.responsive_contract_missing" in categories
    assert "design_system.unresolved_tokens" in categories
    assert "design_system.unresolved_items" in categories
    assert system.model_dump() == before
    assert report.authority_effect == "none"


def test_a44_accessibility_critic_is_contract_level_and_never_claims_runtime_pass() -> None:
    system = _system(healthy=False)
    report = AccessibilityCritic().review(design_system=system)
    categories = {issue.category for issue in report.issues}

    assert "accessibility.contract_gate_unconfirmed" in categories
    assert "accessibility.p0_contract_missing" in categories
    assert "accessibility.interactive_states_missing" in categories
    assert "accessibility.reduced_motion_contract_missing" in categories
    assert all(issue.status is CritiqueIssueStatus.OBSERVED for issue in report.issues)
    assert report.advisory_only is True
    assert report.gate_effect == "none"
    assert not hasattr(report, "passed")


def test_a44_healthy_contracts_can_produce_empty_non_visual_critic_findings_without_implying_pass() -> None:
    contract = _contract(complete_ux=True)
    system = _system(healthy=True)
    composition = _composition(healthy=True)

    ux_report = UXIACritic().review(contract=contract, composition=composition)
    system_report = DesignSystemCritic().review(design_system=system)
    a11y_report = AccessibilityCritic().review(design_system=system)

    assert ux_report.issues == []
    assert system_report.issues == []
    assert a11y_report.issues == []
    for report in (ux_report, system_report, a11y_report):
        assert report.advisory_only is True
        assert report.gate_effect == "none"
        assert report.evidence_effect == "none"
        assert not hasattr(report, "passed")


def test_a44_core_critics_do_not_define_execution_or_gate_authority() -> None:
    source = (FACTORY / "core" / "brain_os" / "critics" / "core_design.py").read_text(encoding="utf-8")
    forbidden = (
        "ProviderManagedRunner",
        "ManagedFlowController",
        "ProductionReleaseController",
        "release_action",
        "run_target_command",
        "gate_evidence_errors",
        ".apply_calibration(",
    )
    for token in forbidden:
        assert token not in source
