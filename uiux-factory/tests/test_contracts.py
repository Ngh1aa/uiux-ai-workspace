import pytest
from pydantic import ValidationError

from core.contracts.design_system_schema import (
    DesignSystemContract,
    DesignSystemGate,
    FoundationTokens,
)
from core.contracts.design_context_schema import DesignContext
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
from core.manager.provider_intelligent_manager import ProviderIntelligentDevelopmentManager


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


def external_context() -> DesignContext:
    return DesignContext.model_validate(
        {
            "brain": "external",
            "target": {
                "repository": "Ngh1aa/Atelier",
                "branch": "redesign/test",
                "project_root": "/",
                "stack": "html-css-js",
                "commands": {
                    "install": "npm install",
                    "build": "npm run build",
                    "serve": "npm run preview",
                },
                "routes": ["/", "/about.html", "/"],
            },
        }
    )


def test_external_brain_requires_target_project_and_preserves_commands() -> None:
    context = external_context()

    assert context.target is not None
    assert context.target.repository == "Ngh1aa/Atelier"
    assert context.target.routes == ["/", "/about.html"]
    assert context.target.commands.serve == "npm run preview"


def test_external_brain_without_target_is_rejected() -> None:
    with pytest.raises(ValidationError, match="target project contract"):
        DesignContext.model_validate({"brain": "external"})


def test_external_engine_cannot_be_silently_replaced_by_internal_ai() -> None:
    context = external_context()
    ProviderIntelligentDevelopmentManager._validate_engine_context("external", context)

    with pytest.raises(ValueError, match="must use engine='external'"):
        ProviderIntelligentDevelopmentManager._validate_engine_context("ai", context)

    with pytest.raises(ValueError, match="requires DesignContext.brain='external'"):
        ProviderIntelligentDevelopmentManager._validate_engine_context(
            "external",
            DesignContext(),
        )
