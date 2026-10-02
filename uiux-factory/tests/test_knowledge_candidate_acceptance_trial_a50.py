from __future__ import annotations

import json
from pathlib import Path

from core.benchmarks.knowledge_candidate_acceptance_trial import evaluate_knowledge_candidate_acceptance_trial


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
BENCHMARKS = ROOT / "benchmarks"
KNOWLEDGE = WORKSPACE / "skills_UIUX/knowledge"


def _evaluate(reviews_path: Path):
    return evaluate_knowledge_candidate_acceptance_trial(
        trial_path=BENCHMARKS / "knowledge-candidate-acceptance-trial-v1.json",
        mapping_path=BENCHMARKS / "knowledge-candidate-acceptance-mapping-v1.json",
        reviews_path=reviews_path,
        draft_corpus_path=BENCHMARKS / "knowledge-ready-candidate-drafts-v1.json",
        proposal_path=BENCHMARKS / "knowledge-expansion-proposal-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=KNOWLEDGE,
        benchmarks_root=BENCHMARKS,
    )


def _reviewed_case(case_id: str, *, preferred: str, a: dict[str, int], b: dict[str, int], regression: bool = False) -> dict:
    return {
        "id": case_id,
        "status": "REVIEWED",
        "preferred_output": preferred,
        "scores": {"A": a, "B": b},
        "rationale": "independent blind-first human review fixture",
        "material_regression": regression,
        "reviewer": "human_fixture",
        "reviewed_at": "2026-10-02",
    }


def _scores(*, correctness: int, specificity: int, relevance: int = 2, risk: int = 2, usefulness: int) -> dict[str, int]:
    return {
        "correctness": correctness,
        "specificity_actionability": specificity,
        "relevance_noise": relevance,
        "unsupported_claim_risk": risk,
        "decision_usefulness": usefulness,
    }


def _write_reviews(tmp_path: Path, cases: list[dict]) -> Path:
    source = json.loads((BENCHMARKS / "knowledge-candidate-acceptance-human-reviews-v1.json").read_text(encoding="utf-8"))
    source["review_status"] = "COMPLETE"
    source["cases"] = cases
    path = tmp_path / "reviews.json"
    path.write_text(json.dumps(source, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def test_canonical_human_review_derives_one_revision_and_one_index_trial_candidate() -> None:
    report = _evaluate(BENCHMARKS / "knowledge-candidate-acceptance-human-reviews-v1.json")
    assert report.human_review_complete is True
    assert report.reviewed_case_count == 2
    assert report.accepted_for_index_trial_count == 1
    assert report.revise_draft_count == 1
    assert report.hold_count == 0
    assert report.reject_count == 0
    by_id = {case.case_id: case for case in report.cases}
    assert by_id["edtech-lti-integration-boundaries"].verdict == "REVISE_DRAFT"
    assert by_id["edtech-lti-integration-boundaries"].joint_usefulness_win is False
    assert by_id["edtech-lti-integration-boundaries"].correctness_guard_clear is True
    assert by_id["edtech-lti-integration-boundaries"].unsupported_claim_risk_guard_clear is True
    assert by_id["ev-ocpp-charging-session-truth"].verdict == "ACCEPT_FOR_INDEX_TRIAL"
    assert by_id["ev-ocpp-charging-session-truth"].joint_usefulness_win is True
    assert by_id["ev-ocpp-charging-session-truth"].correctness_guard_clear is True
    assert by_id["ev-ocpp-charging-session-truth"].unsupported_claim_risk_guard_clear is True
    assert report.index_mutation_allowed is False
    assert report.canonical_acceptance_allowed is False
    assert report.auto_promotion_allowed is False
    assert report.vector_search_change_allowed is False
    assert report.product_evidence is False


def test_human_preference_plus_joint_usefulness_can_only_accept_for_index_trial(tmp_path: Path) -> None:
    strong = _scores(correctness=2, specificity=2, usefulness=2)
    baseline = _scores(correctness=1, specificity=1, usefulness=1)
    reviews = _write_reviews(
        tmp_path,
        [
            _reviewed_case("edtech-lti-integration-boundaries", preferred="A", a=strong, b=baseline),
            _reviewed_case("ev-ocpp-charging-session-truth", preferred="B", a=baseline, b=strong),
        ],
    )
    report = _evaluate(reviews)
    assert report.human_review_complete is True
    assert report.accepted_for_index_trial_count == 2
    assert {case.verdict for case in report.cases} == {"ACCEPT_FOR_INDEX_TRIAL"}
    assert all(case.joint_usefulness_win for case in report.cases)
    assert report.index_mutation_allowed is False
    assert report.canonical_acceptance_allowed is False
    assert report.auto_promotion_allowed is False


def test_baseline_preference_requires_revision_not_rejection(tmp_path: Path) -> None:
    strong = _scores(correctness=2, specificity=2, usefulness=2)
    weak = _scores(correctness=1, specificity=1, usefulness=1)
    reviews = _write_reviews(
        tmp_path,
        [
            _reviewed_case("edtech-lti-integration-boundaries", preferred="B", a=weak, b=strong),
            _reviewed_case("ev-ocpp-charging-session-truth", preferred="B", a=weak, b=strong),
        ],
    )
    report = _evaluate(reviews)
    by_id = {case.case_id: case for case in report.cases}
    assert by_id["edtech-lti-integration-boundaries"].verdict == "REVISE_DRAFT"
    assert by_id["ev-ocpp-charging-session-truth"].verdict == "ACCEPT_FOR_INDEX_TRIAL"


def test_tie_holds_candidate_and_material_regression_rejects(tmp_path: Path) -> None:
    equal = _scores(correctness=2, specificity=2, usefulness=2)
    reviews = _write_reviews(
        tmp_path,
        [
            _reviewed_case("edtech-lti-integration-boundaries", preferred="TIE", a=equal, b=equal),
            _reviewed_case("ev-ocpp-charging-session-truth", preferred="B", a=equal, b=equal, regression=True),
        ],
    )
    report = _evaluate(reviews)
    by_id = {case.case_id: case for case in report.cases}
    assert by_id["edtech-lti-integration-boundaries"].verdict == "HOLD"
    assert by_id["ev-ocpp-charging-session-truth"].verdict == "REJECT"


def test_acceptance_packet_does_not_reveal_condition_mapping_and_index_stays_three() -> None:
    packet = (BENCHMARKS / "knowledge-candidate-acceptance-review-packet-v1.md").read_text(encoding="utf-8")
    assert "knowledge_condition" not in packet
    assert "baseline_condition" not in packet
    assert "knowledge-candidate-acceptance-mapping-v1.json" in packet

    index = json.loads((KNOWLEDGE / "index.json").read_text(encoding="utf-8"))
    assert len(index["records"]) == 3
    assert all("drafts/" not in ref for ref in index["records"])
