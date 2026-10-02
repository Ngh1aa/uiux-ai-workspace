from __future__ import annotations

import json
from pathlib import Path

from core.benchmarks.knowledge_ev_canonical_promotion_proposal import evaluate_knowledge_ev_canonical_promotion_proposal


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
BENCHMARKS = ROOT / "benchmarks"
KNOWLEDGE = WORKSPACE / "skills_UIUX/knowledge"


def _evaluate(review_path: Path | None = None):
    return evaluate_knowledge_ev_canonical_promotion_proposal(
        proposal_review_path=BENCHMARKS / "knowledge-ev-canonical-promotion-proposal-v1.json",
        review_path=review_path or BENCHMARKS / "knowledge-ev-canonical-promotion-review-v1.json",
        canary_trial_path=BENCHMARKS / "knowledge-ev-controlled-index-trial-v1.json",
        acceptance_trial_path=BENCHMARKS / "knowledge-candidate-acceptance-trial-v1.json",
        acceptance_mapping_path=BENCHMARKS / "knowledge-candidate-acceptance-mapping-v1.json",
        acceptance_reviews_path=BENCHMARKS / "knowledge-candidate-acceptance-human-reviews-v1.json",
        draft_corpus_path=BENCHMARKS / "knowledge-ready-candidate-drafts-v1.json",
        expansion_proposal_path=BENCHMARKS / "knowledge-expansion-proposal-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=KNOWLEDGE,
        benchmarks_root=BENCHMARKS,
    )


def test_a50_10a_ev_proposal_requires_governance_review_without_mutation() -> None:
    before = (KNOWLEDGE / "index.json").read_bytes()
    report = _evaluate()
    after = (KNOWLEDGE / "index.json").read_bytes()
    assert report.decision == "GOVERNANCE_REVIEW_REQUIRED"
    assert report.canary_decision == "CANARY_PASS"
    assert report.canary_promotion_proposal_allowed is True
    assert report.proposal_preconditions_clear is True
    assert report.candidate_unindexed is True
    assert report.canonical_index_count == 3
    assert report.review_status == "PENDING"
    assert report.separate_promotion_task_allowed is False
    assert report.index_mutation_allowed is False
    assert report.canonical_promotion_in_this_proposal is False
    assert report.auto_promotion_allowed is False
    assert before == after


def test_a50_10a_even_explicit_approval_only_allows_separate_task(tmp_path: Path) -> None:
    payload = json.loads((BENCHMARKS / "knowledge-ev-canonical-promotion-review-v1.json").read_text(encoding="utf-8"))
    payload["review_status"] = "COMPLETE"
    payload["review"] = {
        "status": "REVIEWED",
        "verdict": "APPROVE_PROMOTION_TASK",
        "rationale": "Canary, rollback and bounded canonicalization controls are sufficient for a separately reviewed promotion implementation task.",
        "reviewer": "fixture-independent-human",
        "reviewed_at": "2026-10-02",
        "source_freshness_rechecked": True,
        "rollback_plan_accepted": True,
        "cross_domain_risk_accepted": True
    }
    review_path = tmp_path / "review.json"
    review_path.write_text(json.dumps(payload), encoding="utf-8")
    before = (KNOWLEDGE / "index.json").read_bytes()
    report = _evaluate(review_path)
    after = (KNOWLEDGE / "index.json").read_bytes()
    assert report.decision == "APPROVED_FOR_EXPLICIT_PROMOTION_TASK"
    assert report.separate_promotion_task_allowed is True
    assert report.index_mutation_allowed is False
    assert report.canonical_promotion_in_this_proposal is False
    assert report.auto_promotion_allowed is False
    assert before == after


def test_a50_10a_canonical_ev_assets_do_not_exist_during_proposal() -> None:
    payload = json.loads((KNOWLEDGE / "index.json").read_text(encoding="utf-8"))
    assert len(payload["records"]) == 3
    assert "records/ev-charging-ocpp-transaction-semantics.json" not in payload["records"]
    assert not (KNOWLEDGE / "records/ev-charging-ocpp-transaction-semantics.json").exists()
    assert not (KNOWLEDGE / "content/ev-charging-ocpp-transaction-semantics.md").exists()
