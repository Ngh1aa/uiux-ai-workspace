from __future__ import annotations

from pathlib import Path

from core.benchmarks.knowledge_edtech_canonical_promotion_proposal import evaluate_knowledge_edtech_canonical_promotion_proposal


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
BENCHMARKS = ROOT / "benchmarks"
KNOWLEDGE = WORKSPACE / "skills_UIUX/knowledge"


def _evaluate():
    return evaluate_knowledge_edtech_canonical_promotion_proposal(
        proposal_path=BENCHMARKS / "knowledge-edtech-canonical-promotion-proposal-v1.json",
        review_path=BENCHMARKS / "knowledge-edtech-canonical-promotion-review-v1.json",
        canonical_state_path=BENCHMARKS / "knowledge-canonical-state-v2.json",
        expansion_proposal_path=BENCHMARKS / "knowledge-expansion-proposal-v1.json",
        owner_delegation_path=BENCHMARKS / "governance-owner-delegation-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=KNOWLEDGE,
    )


def test_a50_11_edtech_proposal_is_approved_only_for_separate_task_without_mutation() -> None:
    before = (KNOWLEDGE / "index.json").read_bytes()
    report = _evaluate()
    after = (KNOWLEDGE / "index.json").read_bytes()
    assert report.decision == "APPROVED_FOR_EXPLICIT_PROMOTION_TASK"
    assert report.historical_canary_clear is True
    assert report.current_baseline_clear is True
    assert report.source_freshness_clear is True
    assert report.candidate_unindexed is True
    assert report.candidate_authority_boundary_clear is True
    assert report.retrieval_regression_clear is True
    assert report.negative_domain_isolation_clear is True
    assert report.rollback_contract_clear is True
    assert report.genai_hold_preserved is True
    assert report.owner_delegation_clear is True
    assert report.review_verdict == "APPROVE_PROMOTION_TASK"
    assert report.separate_promotion_task_allowed is True
    assert report.index_mutation_allowed is False
    assert report.canonical_promotion_in_this_proposal is False
    assert report.auto_promotion_allowed is False
    assert before == after


def test_a50_11_edtech_canonical_assets_do_not_exist_in_proposal_phase() -> None:
    assert not (KNOWLEDGE / "records/edtech-lti-context-roles-services-v2.json").exists()
    assert not (KNOWLEDGE / "content/edtech-lti-context-roles-services-v2.md").exists()
    index = (KNOWLEDGE / "index.json").read_text(encoding="utf-8")
    assert "records/edtech-lti-context-roles-services-v2.json" not in index
