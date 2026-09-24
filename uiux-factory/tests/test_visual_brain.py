from pathlib import Path

from core.contracts.design_context_schema import BrandDNA
from core.contracts.design_system_schema import (
    DesignSystemContract,
    DesignSystemGate,
    FoundationTokens,
)
from core.contracts.schema import (
    DesignContract,
    EvidenceStatus,
    ImplementationConstraints,
    ProjectContract,
    UXContract,
    VisualContract,
)
from core.contracts.visual_composition_schema import (
    PageSpec,
    SectionSpec,
    VisualComposition,
    VisualCompositionGate,
)
from core.orchestration.visual_brain import VisualBrain


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


def contract() -> DesignContract:
    return DesignContract(
        project=ProjectContract(goal="Luxury hospitality website", domain="hospitality"),
        ux=UXContract(),
        visual=VisualContract(
            signature=(
                "A quiet hospitality system recognized by architectural crop discipline, "
                "measured editorial typography and room-first spatial storytelling."
            ),
            attributes=["quiet", "architectural", "editorial"],
            media_rules=["Use rooms and material details as decision evidence."],
        ),
        constraints=ImplementationConstraints(),
        gates=EvidenceStatus(),
        sources={},
    )


def system() -> DesignSystemContract:
    return DesignSystemContract(
        domain="hospitality",
        brand=BrandDNA(
            name="Maison An",
            personality=["quiet", "crafted", "warm"],
            reference_patterns=["editorial pacing", "architectural crop"],
        ),
        source_design_contract_path="design-contract.json",
        source_design_contract_sha256="abc",
        foundations=FoundationTokens(),
        gates=DesignSystemGate(),
    )


def section(composition: str, anchor: str) -> SectionSpec:
    return SectionSpec(
        type="experience",
        purpose="Support the page decision.",
        priority="P0",
        composition=composition,
        visual_anchor=anchor,
        mobile_behavior=["Recompose around the primary decision object."],
    )


def test_visual_brain_loads_the_five_requested_skills() -> None:
    brain = VisualBrain(SKILLS)
    report = brain.evaluate(
        contract=contract(),
        design_system=system(),
        composition=VisualComposition(
            domain="hospitality",
            project_slug="maison-an",
            visual_signature=contract().visual.signature,
            pages=[
                PageSpec(
                    path="/",
                    page_role="Home",
                    composition_family="editorial-arrival",
                    first_visual_anchor="courtyard architecture",
                    sections=[section("architectural-arrival-sequence", "courtyard architecture")],
                ),
                PageSpec(
                    path="/rooms/",
                    page_role="Rooms",
                    composition_family="room-comparison",
                    first_visual_anchor="room photography + availability",
                    sections=[section("room-comparison-led", "room photography + availability")],
                ),
                PageSpec(
                    path="/experience/",
                    page_role="Experience",
                    composition_family="local-story",
                    first_visual_anchor="local craft and itinerary",
                    sections=[section("chaptered-local-story", "local craft and itinerary")],
                ),
            ],
            gates=VisualCompositionGate(),
        ),
    )
    assert len(report.skills) == 5
    assert report.score.anti_generic >= 80
    assert report.gates.five_core_skills_loaded is True
    assert report.gates.ready_for_implementation is True


def test_visual_brain_blocks_materially_generic_multi_page_composition() -> None:
    brain = VisualBrain(SKILLS)
    generic_pages = [
        PageSpec(
            path=path,
            page_role=role,
            composition_family="same-hero",
            first_visual_anchor="page-specific decision object",
            sections=[section("content-led", "page-specific decision object")],
        )
        for path, role in (("/", "Home"), ("/rooms/", "Rooms"), ("/contact/", "Contact"))
    ]
    report = brain.evaluate(
        contract=contract(),
        design_system=system(),
        composition=VisualComposition(
            domain="hospitality",
            project_slug="generic",
            visual_signature="Modern clean professional website",
            pages=generic_pages,
            gates=VisualCompositionGate(),
        ),
    )
    assert report.status == "blocked"
    assert report.gates.no_blocking_generic_pattern is False
    assert report.score.anti_generic < 68
    assert report.generic_tells


def test_visual_brain_calibration_is_written_back_to_composition() -> None:
    brain = VisualBrain(SKILLS)
    composition = VisualComposition(
        domain="hospitality",
        project_slug="maison-an",
        visual_signature=contract().visual.signature,
        pages=[
            PageSpec(
                path="/contact/",
                page_role="Contact",
                composition_family="focused-conversion",
                first_visual_anchor="inquiry form + property context",
                sections=[
                    SectionSpec(
                        type="contact-form",
                        purpose="Capture an inquiry.",
                        priority="P0",
                        composition="focused-form-conversion",
                        visual_anchor="inquiry form + property context",
                        mobile_behavior=["Keep labels, validation and submit feedback visible."],
                    )
                ],
            )
        ],
        gates=VisualCompositionGate(),
    )
    report = brain.evaluate(contract=contract(), design_system=system(), composition=composition)
    calibrated = brain.apply_calibration(composition, report)
    assert any("Visual Brain commitment:" in item for item in calibrated.composition_principles)
    assert any("validation" in item.lower() for item in calibrated.pages[0].anti_monotony_rules)
