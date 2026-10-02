from __future__ import annotations

import json
from pathlib import Path

from core.benchmarks.knowledge_edtech_controlled_index_trial import evaluate_knowledge_edtech_controlled_index_trial


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
BENCHMARKS = ROOT / "benchmarks"
KNOWLEDGE = WORKSPACE / "skills_UIUX/knowledge"


def _evaluate():
    return evaluate_knowledge_edtech_controlled_index_trial(
        BENCHMARKS / "knowledge-edtech-controlled-index-trial-v1.json",
        revision_trial_path=BENCHMARKS / "knowledge-edtech-revision-trial-v1.json",
        revision_mapping_path=BENCHMARKS / "knowledge-edtech-revision-mapping-v1.json",
        revision_reviews_path=BENCHMARKS / "knowledge-edtech-revision-human-review-v1.json",
        prior_trial_path=BENCHMARKS / "knowledge-candidate-acceptance-trial-v1.json",
        prior_mapping_path=BENCHMARKS / "knowledge-candidate-acceptance-mapping-v1.json",
        prior_reviews_path=BENCHMARKS / "knowledge-candidate-acceptance-human-reviews-v1.json",
        draft_corpus_path=BENCHMARKS / "knowledge-ready-candidate-drafts-v1.json",
        proposal_path=BENCHMARKS / "knowledge-expansion-proposal-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=KNOWLEDGE,
        benchmarks_root=BENCHMARKS,
    )


def test_a50_9c_edtech_canary_passes_without_canonical_promotion() -> None:
    report = _evaluate()
    assert report.decision == "CANARY_PASS"
    assert report.prior_revision_verdict == "ACCEPT_FOR_INDEX_TRIAL"
    assert report.usefulness_evidence_clear is True
    assert report.revision_record_unindexed is True
    assert report.canonical_index_count == 3
    assert report.canary_index_count == 4
    assert report.edtech_retrieval_isolated is True
    assert report.context_budget_clear is True
    assert report.promotion_proposal_allowed is True
    assert report.index_mutation_allowed is False
    assert report.canonical_promotion_allowed is False
    assert report.auto_promotion_allowed is False
    assert report.vector_search_change_allowed is False
    assert report.product_evidence is False


def test_a50_9c_preserves_canonical_retrieval_and_cross_domain_isolation() -> None:
    report = _evaluate()
    assert report.canonical_retrieval_regression_clear is True
    assert report.negative_domain_isolation_clear is True
    assert report.genai_hold_preserved is True


def test_a50_9c_rollback_restores_exact_canonical_index_bytes() -> None:
    before = (KNOWLEDGE / "index.json").read_bytes()
    report = _evaluate()
    after = (KNOWLEDGE / "index.json").read_bytes()
    assert report.rollback_verified is True
    assert report.canonical_index_hash_before == report.canonical_index_hash_after
    assert before == after


def test_a50_9c_canonical_index_stays_three_and_does_not_reference_edtech_revision() -> None:
    payload = json.loads((KNOWLEDGE / "index.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == "knowledge-index.v1"
    assert len(payload["records"]) == 3
    assert "revisions/records/edtech-lti-context-roles-services-v2.json" not in payload["records"]
    assert all(not ref.startswith(("drafts/", "revisions/")) for ref in payload["records"])
