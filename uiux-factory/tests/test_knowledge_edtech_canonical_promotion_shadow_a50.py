from __future__ import annotations

from pathlib import Path

from core.benchmarks.knowledge_edtech_canonical_promotion_shadow import evaluate_knowledge_edtech_canonical_promotion_shadow

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
BENCHMARKS = ROOT / "benchmarks"
KNOWLEDGE = WORKSPACE / "skills_UIUX/knowledge"


def test_a50_12_shadow_is_ready_without_repository_mutation() -> None:
    before = (KNOWLEDGE / "index.json").read_bytes()
    report = evaluate_knowledge_edtech_canonical_promotion_shadow(
        shadow_trial_path=BENCHMARKS / "knowledge-edtech-canonical-promotion-shadow-v1.json",
        proposal_path=BENCHMARKS / "knowledge-edtech-canonical-promotion-proposal-v1.json",
        review_path=BENCHMARKS / "knowledge-edtech-canonical-promotion-review-v1.json",
        canonical_state_path=BENCHMARKS / "knowledge-canonical-state-v2.json",
        expansion_proposal_path=BENCHMARKS / "knowledge-expansion-proposal-v1.json",
        owner_delegation_path=BENCHMARKS / "governance-owner-delegation-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=KNOWLEDGE,
    )
    after = (KNOWLEDGE / "index.json").read_bytes()
    assert report.decision == "READY_FOR_CANONICAL_APPLY"
    assert report.pre_shadow_count == 4
    assert report.shadow_count == 5
    assert report.canonical_apply_allowed is True
    assert report.rollback_verified is True
    assert report.repository_index_unchanged is True
    assert report.repository_canonical_assets_absent is True
    assert report.product_evidence is False
    assert before == after


def test_a50_12_shadow_keeps_canonical_edtech_assets_out_of_repository() -> None:
    assert not (KNOWLEDGE / "records/edtech-lti-context-roles-services-v2.json").exists()
    assert not (KNOWLEDGE / "content/edtech-lti-context-roles-services-v2.md").exists()
