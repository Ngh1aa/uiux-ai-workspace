from __future__ import annotations

import json

from core.verification.evidence_contract import RequirementRegistry
from core.verification.evidence_contract_v1 import EvidenceContractEvaluatorV1


BUILT_IN = {
    "semantic_visual",
    "browser_target_smoke",
    "browser_contrast_smoke",
    "browser_viewports",
    "reference_plan",
    "artifact_claim",
    "human_review",
}


def test_every_v1_registry_evaluator_has_an_implementation_path() -> None:
    registry = RequirementRegistry()
    requested = {str(rule.evaluator or "") for rule in registry.rules if rule.evaluator}
    implemented = BUILT_IN | set(EvidenceContractEvaluatorV1.DEDICATED_REPORTS)
    assert requested - implemented == set()
    assert len(registry.rules) == 56


def test_v1_artifact_contracts_require_concrete_content(tmp_path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "research.md").write_text("Media/assets reality: product imagery is required and copy remains provisional.", encoding="utf-8")
    (run_dir / "ux-ia.md").write_text(
        "## Audience & Top Tasks\n- Primary audience: People comparing fragrance online *(inferred from brief)*\n",
        encoding="utf-8",
    )
    (run_dir / "design-context.json").write_text(json.dumps({"brand_name": "Violet"}), encoding="utf-8")
    (run_dir / "art-direction.md").write_text(
        "# Art Direction\n\n## First Impression\nA sensory fragrance storefront.\n\n"
        "## Style Adjectives\n- Sensory\n- Editorial\n- Refined\n\n"
        "## Visual Signature\nLarge fragrance media anchors the opening view.\n",
        encoding="utf-8",
    )
    (run_dir / "demo-path-contract.json").write_text(
        json.dumps({"steps": [{"route": "/", "page_role": "Home"}, {"route": "/product", "page_role": "Product Detail"}], "unresolved": []}),
        encoding="utf-8",
    )
    (run_dir / "design-system.json").write_text(
        json.dumps(
            {
                "foundations": {
                    "colors": {
                        "color.brand.primary": {"value": "#5A355F"},
                        "color.neutral.950": {"value": "#111111"},
                    },
                    "semantic_colors": {
                        "text.primary": "color.neutral.950",
                        "action.primary": "color.brand.primary",
                        "state.success": "color.state.success",
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    evaluator = EvidenceContractEvaluatorV1()
    rules = {rule.id: rule for rule in evaluator.registry.rules}
    expected_pass = {
        "UNDERSTANDING-001",
        "UNDERSTANDING-002",
        "UNDERSTANDING-005",
        "UNDERSTANDING-006",
        "UNDERSTANDING-007",
        "UNDERSTANDING-008",
        "VISUAL-001",
    }
    for rule_id in expected_pass:
        result = evaluator._artifact_claim_result(
            rules[rule_id],
            run_dir,
            run_id="test-run",
            project_digest="digest",
        )
        assert result.outcome.value == "passed", (rule_id, result)


def test_exactly_three_style_adjectives_is_not_soft_passed(tmp_path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "art-direction.md").write_text(
        "## Style Adjectives\n- Clear\n- Premium\n- Modern\n- Friendly\n",
        encoding="utf-8",
    )
    evaluator = EvidenceContractEvaluatorV1()
    rule = next(rule for rule in evaluator.registry.rules if rule.id == "UNDERSTANDING-005")
    result = evaluator._artifact_claim_result(rule, run_dir, run_id="test", project_digest="digest")
    assert result.outcome.value == "failed"
