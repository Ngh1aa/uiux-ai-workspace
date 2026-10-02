from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from core.benchmarks.knowledge_value_trial import evaluate_knowledge_value_trial


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ROOT / "benchmarks"
TRIAL = BENCHMARKS / "knowledge-value-trial-v1.json"
MAPPING = BENCHMARKS / "knowledge-value-trial-mapping-v1.json"
REVIEWS = BENCHMARKS / "knowledge-value-human-reviews-v1.json"
DIMENSIONS = (
    "correctness",
    "specificity_actionability",
    "relevance_noise",
    "unsupported_claim_risk",
    "decision_usefulness",
)
KNOWLEDGE_LABELS = {
    "nova-amount-display": "B",
    "lumen-object-metadata": "A",
    "cennext-motor-claims": "B",
}


def _canonical_result():
    return evaluate_knowledge_value_trial(
        trial_path=TRIAL,
        mapping_path=MAPPING,
        reviews_path=REVIEWS,
    )


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _pending_reviews() -> dict:
    payload = json.loads(REVIEWS.read_text(encoding="utf-8"))
    payload["review_status"] = "PENDING"
    for case in payload["cases"]:
        case.update(
            {
                "status": "PENDING",
                "preferred_output": None,
                "scores": None,
                "rationale": None,
                "material_regression": None,
                "reviewer": None,
                "reviewed_at": None,
            }
        )
    return payload


def _completed_positive_reviews(*, regression_case: str | None = None) -> dict:
    payload = json.loads(REVIEWS.read_text(encoding="utf-8"))
    payload["review_status"] = "COMPLETE"
    for case in payload["cases"]:
        case_id = case["id"]
        knowledge_label = KNOWLEDGE_LABELS[case_id]
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


def test_a50_5_checked_in_human_review_requires_revision_before_expansion() -> None:
    result = _canonical_result()

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
    assert result.current_run_evidence is False
    assert result.product_evidence is False


def test_a50_5_pending_review_rejects_fabricated_human_fields(tmp_path: Path) -> None:
    reviews = _pending_reviews()
    reviews["cases"][0]["reviewer"] = "pretend-human"
    review_path = _write_json(tmp_path / "reviews.json", reviews)

    with pytest.raises(ValueError, match="pending review must not contain a fabricated reviewer"):
        evaluate_knowledge_value_trial(
            trial_path=TRIAL,
            mapping_path=MAPPING,
            reviews_path=review_path,
        )


def test_a50_5_complete_positive_review_can_only_consider_expansion(tmp_path: Path) -> None:
    review_path = _write_json(tmp_path / "reviews.json", _completed_positive_reviews())
    result = evaluate_knowledge_value_trial(
        trial_path=TRIAL,
        mapping_path=MAPPING,
        reviews_path=review_path,
    )

    assert result.human_review_complete is True
    assert result.knowledge_preferred_count == 3
    assert result.baseline_preferred_count == 0
    assert result.material_regression_count == 0
    assert result.expansion_recommendation == "CONSIDER_EXPANSION"
    assert result.expand_allowed is False
    assert result.auto_mutation_allowed is False


def test_a50_5_material_regression_blocks_expansion_recommendation(tmp_path: Path) -> None:
    review_path = _write_json(
        tmp_path / "reviews.json",
        _completed_positive_reviews(regression_case="lumen-object-metadata"),
    )
    result = evaluate_knowledge_value_trial(
        trial_path=TRIAL,
        mapping_path=MAPPING,
        reviews_path=review_path,
    )

    assert result.human_review_complete is True
    assert result.material_regression_count == 1
    assert result.expansion_recommendation == "REVISE_BEFORE_EXPANSION"
    assert result.expand_allowed is False


def test_a50_5_mapping_does_not_overclaim_cryptographic_blinding(tmp_path: Path) -> None:
    mapping = json.loads(MAPPING.read_text(encoding="utf-8"))
    mapping = copy.deepcopy(mapping)
    mapping["blinding"]["cryptographically_blind"] = True
    mapping_path = _write_json(tmp_path / "mapping.json", mapping)

    with pytest.raises(ValueError, match="must not overclaim cryptographic blinding"):
        evaluate_knowledge_value_trial(
            trial_path=TRIAL,
            mapping_path=mapping_path,
            reviews_path=REVIEWS,
        )
