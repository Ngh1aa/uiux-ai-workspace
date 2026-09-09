from pathlib import Path

from core.contracts.creative_review_schema import CreativeDirective
from core.contracts.design_context_schema import DesignContext
from core.contracts.schema import (
    DesignContract,
    EvidenceStatus,
    ImplementationConstraints,
    ProjectContract,
    UXContract,
    VisualContract,
)
from core.manager.creative_director_manager import CreativeDirectorDevelopmentManager
from core.runtime.run_context import RunContext


def _directive(owner: str = "visual_composition") -> CreativeDirective:
    return CreativeDirective.model_validate(
        {
            "source_run_id": "abcdef123456",
            "status": "revise",
            "overall_direction": "Quiet luxury with one dominant editorial object.",
            "keep": ["Existing IA"],
            "revise": [
                {
                    "priority": "P1",
                    "route": "/",
                    "section": "hero",
                    "owner": owner,
                    "problem": "The hero feels interchangeable.",
                    "instruction": "Use asymmetry and a single dominant media anchor.",
                    "skills": ["visual-taste-calibration"],
                    "success_criteria": "The hero is recognizable without brand copy.",
                }
            ],
            "remove": [],
        }
    )


def test_revision_project_slug_is_retargeted_without_mutating_base_name() -> None:
    retarget = CreativeDirectorDevelopmentManager._retarget_slug

    assert (
        retarget("maison-an-abcdef123456", "abcdef123456", "123456abcdef")
        == "maison-an-123456abcdef"
    )
    assert (
        retarget("maison-an-deadbeefcafe", "abcdef123456", "123456abcdef")
        == "maison-an-123456abcdef"
    )


def test_review_context_preserves_existing_guideline_and_adds_authoritative_review() -> None:
    source = DesignContext(guideline="Preserve the supplied wordmark.")
    merged = CreativeDirectorDevelopmentManager._context_with_review(
        source,
        _directive(),
    )

    assert "Preserve the supplied wordmark." in merged.guideline
    assert "EXTERNAL CREATIVE DIRECTOR REVIEW" in merged.guideline
    assert "Quiet luxury" in merged.guideline
    assert len(merged.guideline) <= 30_000


def test_deterministic_visual_revision_injects_review_into_copied_design_contract(
    tmp_path: Path,
) -> None:
    context = RunContext(root=tmp_path, goal="Design a premium site")
    context.run_id = "123456abcdef"
    context.initialize()

    contract = DesignContract(
        project=ProjectContract(goal=context.goal, domain="hospitality"),
        ux=UXContract(),
        visual=VisualContract(
            signature="calm editorial hospitality",
            attributes=["warm"],
            layout_rules=["Keep booking action legible."],
        ),
        constraints=ImplementationConstraints(),
        gates=EvidenceStatus(),
        sources={},
    )
    contract_path = context.run_dir / "design-contract.json"
    contract_path.write_text(contract.model_dump_json(indent=2), encoding="utf-8")
    context.add_artifact("design_contract", contract_path)

    manager = object.__new__(CreativeDirectorDevelopmentManager)
    manager.creative_directive = _directive()
    manager._inject_review_constraints(context, "visual_composition")

    restored = DesignContract.model_validate_json(
        contract_path.read_text(encoding="utf-8")
    )
    assert "Quiet luxury with one dominant editorial object." in restored.visual.attributes
    assert any("Creative review [P1]" in rule for rule in restored.visual.layout_rules)
    assert any("Use asymmetry" in rule for rule in restored.visual.layout_rules)
