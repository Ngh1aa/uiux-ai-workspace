from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from core.benchmarks.knowledge_value_trial import evaluate_knowledge_value_trial


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ROOT / "benchmarks"
DIMENSIONS = (
    "correctness",
    "specificity_actionability",
    "relevance_noise",
    "unsupported_claim_risk",
    "decision_usefulness",
)
KNOWLEDGE_LABELS_V1 = {
    "nova-amount-display": "B",
    "lumen-object-metadata": "A",
    "cennext-motor-claims": "B",
}
KNOWLEDGE_LABELS_V2 = {
    "nova-amount-display": "A",
    "lumen-object-metadata": "B",
    "cennext-motor-claims": "A",
}


def _paths(version: int) -> tuple[Path, Path, Path]:
    return (
        BENCHMARKS / f"knowledge-value-trial-v{version}.json",
        BENCHMARKS / f"knowledge-value-trial-mapping-v{version}.json",
        BENCHMARKS / f"knowledge-value-human-reviews-v{version}.json",
    )


def _result(version: int):
    trial, mapping, reviews = _paths(version)
    return evaluate_knowledge_value_trial(
        trial_path=trial,
        mapping_path=mapping,
        reviews_path=reviews,
    )


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _completed_positive_reviews(version: int, *, regression_case: str | None = None) -> dict:
    _, _, reviews_path = _paths(version)
    payload = json.loads(reviews_path.read_text(encoding="utf-8"))
    payload["review_status"] = "COMPLETE"
    labels = KNOWLEDGE_LABELS_V1 if version == 1 else KNOWLEDGE_LABELS_V2
    for case in payload["cases"]:
        case_id = case["id"]
        knowledge_label = labels[case_id]
        baseline_label = "A" if knowledge_label == "B" else "B"
        scores = {
            baseline_label: {dimension: 1 for dimension in DIMENSIONS},
            knowledge_label: {dimension: 2 for dimension in DIMENSIONS},
        }
        case.update(
            {
                "status": "REVIEWED",
                "preferred_output": knowledge_label,
                "scores": scores,
                "rationale": "Knowledge-labelled output was more specific and decision-useful without adding unsupported claims.",
                "material_regression": case_id == regression_case,
                "reviewer": "independent-reviewer",
                "reviewed_at": "2026-10-02",
            }
        )
    return payload


def test_a50_5_round_one_history_requires_revision_before_expansion() -> None:
    result = _result(1)

    assert result.case_count == 3
    assert result.reviewed_case_count == 3
    assert result.human_review_complete is True
    assert result.knowledge_preferred_count == 2
    assert result.baseline_preferred_count == 0
    assert result.tie_count == 1
    assert result.material_regression_count == 0
    assert result.expansion_recommendation == "REVISE_BEFORE_EXPANSION"
    assert result.expand_allowed is False
    assert result.auto_mutation_allowed is False


def test_a50_5r_round_two_starts_pending_and_holds_expansion() -> None:
    result = _result(2)

    assert result.trial_id == "knowledge-value-trial-v2"
    assert result.case_count == 3
    assert result.reviewed_case_count == 0
    assert result.human_review_complete is False
    assert result.expansion_recommendation == "HOLD_PENDING_HUMAN"
    assert result.expand_allowed is False
    assert result.auto_mutation_allowed is False
    assert result.current_run_evidence is False
    assert result.product_evidence is False


def test_a50_5r_round_two_keeps_baselines_fixed_and_lumen_as_control() -> None:
    v1 = json.loads((_paths(1)[0]).read_text(encoding="utf-8"))
    v2 = json.loads((_paths(2)[0]).read_text(encoding="utf-8"))
    one = {case["id"]: case for case in v1["cases"]}
    two = {case["id"]: case for case in v2["cases"]}

    assert two["nova-amount-display"]["output_b"] == one["nova-amount-display"]["output_a"]
    assert two["cennext-motor-claims"]["output_b"] == one["cennext-motor-claims"]["output_a"]
    assert two["lumen-object-metadata"]["output_a"] == one["lumen-object-metadata"]["output_b"]
    assert two["lumen-object-metadata"]["output_b"] == one["lumen-object-metadata"]["output_a"]


def test_a50_5r_revised_outputs_cover_human_review_gaps() -> None:
    v2 = json.loads((_paths(2)[0]).read_text(encoding="utf-8"))
    cases = {case["id"]: case for case in v2["cases"]}

    nova = " ".join(cases["nova-amount-display"]["output_a"]).lower()
    for concept in (
        "shared money-formatting",
        "explicit project fallback",
        "qa matrix",
        "negative",
        "same-symbol",
    ):
        assert concept in nova

    cennext = " ".join(cases["cennext-motor-claims"]["output_a"]).lower()
    for concept in (
        "buyer decision path",
        "customer approval",
        "proof modules",
        "repair-versus-replace",
        "efficiency-gain",
    ):
        assert concept in cennext


def test_a50_5r_pending_review_rejects_fabricated_human_fields(tmp_path: Path) -> None:
    trial, mapping, reviews_path = _paths(2)
    reviews = json.loads(reviews_path.read_text(encoding="utf-8"))
    reviews["cases"][0]["reviewer"] = "pretend-human"
    review_path = _write_json(tmp_path / "reviews.json", reviews)

    with pytest.raises(ValueError, match="pending review must not contain a fabricated reviewer"):
        evaluate_knowledge_value_trial(
            trial_path=trial,
            mapping_path=mapping,
            reviews_path=review_path,
        )


def test_a50_5r_positive_round_two_can_only_consider_expansion(tmp_path: Path) -> None:
    trial, mapping, _ = _paths(2)
    review_path = _write_json(tmp_path / "reviews.json", _completed_positive_reviews(2))
    result = evaluate_knowledge_value_trial(
        trial_path=trial,
        mapping_path=mapping,
        reviews_path=review_path,
    )

    assert result.human_review_complete is True
    assert result.knowledge_preferred_count == 3
    assert result.baseline_preferred_count == 0
    assert result.material_regression_count == 0
    assert result.expansion_recommendation == "CONSIDER_EXPANSION"
    assert result.expand_allowed is False
    assert result.auto_mutation_allowed is False


def test_a50_5r_material_regression_still_blocks_expansion(tmp_path: Path) -> None:
    trial, mapping, _ = _paths(2)
    review_path = _write_json(
        tmp_path / "reviews.json",
        _completed_positive_reviews(2, regression_case="cennext-motor-claims"),
    )
    result = evaluate_knowledge_value_trial(
        trial_path=trial,
        mapping_path=mapping,
        reviews_path=review_path,
    )

    assert result.material_regression_count == 1
    assert result.expansion_recommendation == "REVISE_BEFORE_EXPANSION"
    assert result.expand_allowed is False


def test_a50_5r_mapping_is_mixed_and_not_cryptographically_blind(tmp_path: Path) -> None:
    trial, mapping_path, reviews = _paths(2)
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    labels = {
        case["id"]: "A" if case["output_a_condition"] == "with_retrieved_knowledge" else "B"
        for case in mapping["cases"]
    }
    assert labels == KNOWLEDGE_LABELS_V2
    assert len(set(labels.values())) == 2

    broken = copy.deepcopy(mapping)
    broken["blinding"]["cryptographically_blind"] = True
    broken_path = _write_json(tmp_path / "mapping.json", broken)
    with pytest.raises(ValueError, match="must not overclaim cryptographic blinding"):
        evaluate_knowledge_value_trial(
            trial_path=trial,
            mapping_path=broken_path,
            reviews_path=reviews,
        )


def test_a50_5_versioned_trials_reject_cross_version_ledgers() -> None:
    trial_v2, mapping_v2, _ = _paths(2)
    reviews_v1 = _paths(1)[2]
    with pytest.raises(ValueError, match="human review ledger trial id mismatch"):
        evaluate_knowledge_value_trial(
            trial_path=trial_v2,
            mapping_path=mapping_v2,
            reviews_path=reviews_v1,
        )
