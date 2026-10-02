from __future__ import annotations

import json
from pathlib import Path

from core.benchmarks.knowledge_ev_canonical_promotion_shadow import evaluate_knowledge_ev_canonical_promotion_shadow


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
BENCHMARKS = ROOT / "benchmarks"
KNOWLEDGE = WORKSPACE / "skills_UIUX/knowledge"


def _evaluate():
    return evaluate_knowledge_ev_canonical_promotion_shadow(
        BENCHMARKS / "knowledge-ev-canonical-promotion-shadow-v1.json",
        canary_trial_path=BENCHMARKS / "knowledge-ev-controlled-index-trial-v1.json",
        acceptance_trial_path=BENCHMARKS / "knowledge-candidate-acceptance-trial-v1.json",
        acceptance_mapping_path=BENCHMARKS / "knowledge-candidate-acceptance-mapping-v1.json",
        acceptance_reviews_path=BENCHMARKS / "knowledge-candidate-acceptance-human-reviews-v1.json",
        draft_corpus_path=BENCHMARKS / "knowledge-ready-candidate-drafts-v1.json",
        expansion_proposal_path=BENCHMARKS / "knowledge-expansion-proposal-v1.json",
        promotion_proposal_path=BENCHMARKS / "knowledge-ev-canonical-promotion-proposal-v1.json",
        owner_delegation_path=BENCHMARKS / "governance-owner-delegation-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=KNOWLEDGE,
        benchmarks_root=BENCHMARKS,
    )


def test_a50_10b_shadow_promotion_is_ready_without_repository_mutation() -> None:
    before = (KNOWLEDGE / "index.json").read_bytes()
    report = _evaluate()
    after = (KNOWLEDGE / "index.json").read_bytes()
    assert report.decision == "READY_FOR_CANONICAL_APPLY"
    assert report.canary_decision == "CANARY_PASS"
    assert report.owner_delegation_clear is True
    assert report.source_freshness_clear is True
    assert report.canonical_index_count_before == 3
    assert report.shadow_index_count == 4
    assert report.repository_index_unchanged is True
    assert report.repository_canonical_assets_absent is True
    assert report.repository_index_mutation_allowed is False
    assert report.auto_promotion_in_this_phase is False
    assert before == after


def test_a50_10b_shadow_promotion_preserves_retrieval_isolation_and_rollback() -> None:
    report = _evaluate()
    assert report.canonical_record_contract_clear is True
    assert report.canonical_content_ref_rewritten is True
    assert report.ev_retrieval_isolated is True
    assert report.canonical_retrieval_regression_clear is True
    assert report.negative_domain_isolation_clear is True
    assert report.context_budget_clear is True
    assert report.rollback_verified is True
    assert report.genai_hold_preserved is True
    assert report.vector_search_change_allowed is False
    assert report.product_evidence is False


def test_a50_10b_declares_post_promotion_validator_migration_before_apply() -> None:
    contract = json.loads((BENCHMARKS / "knowledge-ev-canonical-promotion-shadow-v1.json").read_text(encoding="utf-8"))
    migration = contract["post_promotion_migration"]
    assert migration["next_phase"] == "A50.10C"
    assert migration["historical_three_record_validators_must_transition_before_repository_apply"] is True
    assert set(migration["historical_validators"]) == {
        "validate_knowledge_ev_controlled_index_trial.py",
        "validate_knowledge_edtech_controlled_index_trial.py",
        "validate_knowledge_ev_canonical_promotion_proposal.py",
    }
    payload = json.loads((KNOWLEDGE / "index.json").read_text(encoding="utf-8"))
    assert len(payload["records"]) == 3
    assert "records/ev-charging-ocpp-transaction-semantics.json" not in payload["records"]
