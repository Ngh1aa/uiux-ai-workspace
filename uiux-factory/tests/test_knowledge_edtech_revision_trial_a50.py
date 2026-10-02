from __future__ import annotations

import json
from pathlib import Path

from core.benchmarks.knowledge_edtech_revision_trial import evaluate_knowledge_edtech_revision_trial


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
BENCHMARKS = ROOT / "benchmarks"
KNOWLEDGE = WORKSPACE / "skills_UIUX/knowledge"


def _evaluate(reviews_path: Path):
    return evaluate_knowledge_edtech_revision_trial(
        trial_path=BENCHMARKS / "knowledge-edtech-revision-trial-v1.json",
        mapping_path=BENCHMARKS / "knowledge-edtech-revision-mapping-v1.json",
        reviews_path=reviews_path,
        prior_trial_path=BENCHMARKS / "knowledge-candidate-acceptance-trial-v1.json",
        prior_mapping_path=BENCHMARKS / "knowledge-candidate-acceptance-mapping-v1.json",
        prior_reviews_path=BENCHMARKS / "knowledge-candidate-acceptance-human-reviews-v1.json",
        draft_corpus_path=BENCHMARKS / "knowledge-ready-candidate-drafts-v1.json",
        proposal_path=BENCHMARKS / "knowledge-expansion-proposal-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=KNOWLEDGE,
        benchmarks_root=BENCHMARKS,
    )


def _scores(correctness: int, specificity: int, usefulness: int, *, relevance: int = 2, risk: int = 2) -> dict[str, int]:
    return {
        "correctness": correctness,
        "specificity_actionability": specificity,
        "relevance_noise": relevance,
        "unsupported_claim_risk": risk,
        "decision_usefulness": usefulness,
    }


def _review_file(tmp_path: Path, *, preferred: str, a: dict[str, int], b: dict[str, int], regression: bool = False) -> Path:
    payload = json.loads((BENCHMARKS / "knowledge-edtech-revision-human-review-v1.json").read_text(encoding="utf-8"))
    payload["review_status"] = "COMPLETE"
    payload["case"] = {
        "id": "edtech-lti-integration-boundaries-revision-v2",
        "status": "REVIEWED",
        "preferred_output": preferred,
        "scores": {"A": a, "B": b},
        "rationale": "independent blind-first human review fixture",
        "material_regression": regression,
        "reviewer": "human_fixture",
        "reviewed_at": "2026-10-02",
    }
    path = tmp_path / "review.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def test_a50_9a_pending_review_holds_and_revision_is_unindexed() -> None:
    report = _evaluate(BENCHMARKS / "knowledge-edtech-revision-human-review-v1.json")
    assert report.prior_verdict == "REVISE_DRAFT"
    assert report.revised_record_id == "knowledge.domain.edtech-lti-context-roles-services.v2"
    assert report.revised_record_unindexed is True
    assert report.shadow_retrieval_isolated is True
    assert report.required_state_guidance_present is True
    assert report.human_review_complete is False
    assert report.verdict == "HOLD"
    assert report.canonical_index_count == 3
    assert report.index_mutation_allowed is False
    assert report.canonical_acceptance_allowed is False
    assert report.auto_promotion_allowed is False
    assert report.vector_search_change_allowed is False
    assert report.product_evidence is False


def test_a50_9a_strict_usefulness_win_can_only_accept_for_index_trial(tmp_path: Path) -> None:
    baseline = _scores(1, 1, 1)
    knowledge = _scores(2, 2, 2)
    review = _review_file(tmp_path, preferred="B", a=baseline, b=knowledge)
    report = _evaluate(review)
    assert report.human_review_complete is True
    assert report.knowledge_condition == "B"
    assert report.verdict == "ACCEPT_FOR_INDEX_TRIAL"
    assert report.joint_usefulness_win is True
    assert report.correctness_guard_clear is True
    assert report.unsupported_claim_risk_guard_clear is True
    assert report.index_mutation_allowed is False
    assert report.canonical_acceptance_allowed is False


def test_a50_9a_baseline_preference_requires_revision(tmp_path: Path) -> None:
    strong = _scores(2, 2, 2)
    weak = _scores(1, 1, 1)
    review = _review_file(tmp_path, preferred="A", a=strong, b=weak)
    report = _evaluate(review)
    assert report.verdict == "REVISE_DRAFT"


def test_a50_9a_material_regression_rejects(tmp_path: Path) -> None:
    strong = _scores(2, 2, 2)
    review = _review_file(tmp_path, preferred="B", a=strong, b=strong, regression=True)
    report = _evaluate(review)
    assert report.verdict == "REJECT"


def test_a50_9a_preserves_history_and_packet_blinding() -> None:
    assert (KNOWLEDGE / "drafts/records/edtech-lti-context-roles-services.json").is_file()
    assert (KNOWLEDGE / "drafts/content/edtech-lti-context-roles-services.md").is_file()
    assert (KNOWLEDGE / "drafts/records/edtech-lti-context-roles-services-v2.json").is_file()
    assert (KNOWLEDGE / "drafts/content/edtech-lti-context-roles-services-v2.md").is_file()

    packet = (BENCHMARKS / "knowledge-edtech-revision-review-packet-v1.md").read_text(encoding="utf-8")
    assert "knowledge_condition" not in packet
    assert "baseline_condition" not in packet
    assert "knowledge-edtech-revision-mapping-v1.json" in packet

    index = json.loads((KNOWLEDGE / "index.json").read_text(encoding="utf-8"))
    assert len(index["records"]) == 3
    assert all("drafts/" not in ref for ref in index["records"])
