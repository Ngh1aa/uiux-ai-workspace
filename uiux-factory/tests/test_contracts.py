import pytest
from pydantic import ValidationError

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


def test_design_contract_minimal_handoff_round_trips_json() -> None:
    contract = DesignContract(
        project=ProjectContract(goal="Design a calm ecommerce site", domain="ecommerce"),
        ux=UXContract(),
        visual=VisualContract(signature="quiet editorial commerce"),
        constraints=ImplementationConstraints(),
        gates=EvidenceStatus(),
        sources={},
    )

    restored = DesignContract.model_validate_json(contract.model_dump_json())
    assert restored.schema_version == "0.1.0"
    assert restored.project.domain == "ecommerce"
    assert restored.constraints.do_not_invent_evidence is True


def test_design_contract_rejects_unknown_status_values() -> None:
    with pytest.raises(ValidationError):
        DesignContract(
            status="done",
            project=ProjectContract(goal="x"),
            ux=UXContract(),
            visual=VisualContract(),
            constraints=ImplementationConstraints(),
            gates=EvidenceStatus(),
            sources={},
        )


def test_design_system_contract_requires_source_provenance() -> None:
    with pytest.raises(ValidationError):
        DesignSystemContract(
            foundations=FoundationTokens(),
            gates=DesignSystemGate(),
        )


def test_visual_composition_preserves_page_and_section_roles() -> None:
    composition = VisualComposition(
        domain="ecommerce",
        project_slug="calm-store",
        visual_signature="editorial product storytelling",
        pages=[
            PageSpec(
                path="/",
                page_role="home",
                composition_family="editorial",
                first_visual_anchor="hero-product",
                sections=[
                    SectionSpec(
                        type="hero",
                        purpose="Introduce flagship product",
                        priority="P0",
                        composition="split editorial",
                        visual_anchor="product-image",
                        mobile_behavior=["stack copy before supporting proof"],
                    )
                ],
            )
        ],
        gates=VisualCompositionGate(ready_for_frontend_engineer=True),
    )

    restored = VisualComposition.model_validate_json(composition.model_dump_json())
    assert restored.pages[0].page_role == "home"
    assert restored.pages[0].sections[0].priority == "P0"
    assert restored.gates.ready_for_frontend_engineer is True


def test_visual_composition_rejects_invalid_density() -> None:
    with pytest.raises(ValidationError):
        SectionSpec(
            type="hero",
            purpose="x",
            composition="x",
            visual_anchor="x",
            density="extreme",
        )
