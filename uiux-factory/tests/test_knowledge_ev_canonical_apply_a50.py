from __future__ import annotations

import json
from pathlib import Path

from core.benchmarks.knowledge_ev_canonical_apply import evaluate_knowledge_ev_canonical_apply


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
BENCHMARKS = ROOT / "benchmarks"
KNOWLEDGE = WORKSPACE / "skills_UIUX/knowledge"


def _evaluate():
    return evaluate_knowledge_ev_canonical_apply(
        BENCHMARKS / "knowledge-canonical-state-v2.json",
        workspace_root=WORKSPACE,
        knowledge_root=KNOWLEDGE,
        expansion_proposal_path=BENCHMARKS / "knowledge-expansion-proposal-v1.json",
        owner_delegation_path=BENCHMARKS / "governance-owner-delegation-v1.json",
        workflow_path=WORKSPACE / ".github/workflows/uiux-factory-ci.yml",
        conftest_path=ROOT / "tests/conftest.py",
    )


def test_a50_10c_canonical_apply_matches_exact_approved_state() -> None:
    report = _evaluate()
    assert report.decision == "CANONICAL_APPLY_PASS"
    assert report.canonical_index_count == 4
    assert report.exact_record_set_clear is True
    assert report.promoted_record_contract_clear is True
    assert report.promoted_content_exact_copy is True
    assert report.promoted_record_semantic_copy is True
    assert report.source_freshness_metadata_clear is True
    assert report.authority_boundary_clear is True


def test_a50_10c_active_retrieval_regression_and_isolation_are_clear() -> None:
    report = _evaluate()
    assert report.retrieval_regression_clear is True
    assert report.negative_domain_isolation_clear is True
    assert report.context_budget_clear is True
    assert report.vector_search_disabled is True
    assert report.genai_hold_preserved is True
    assert report.product_evidence is False


def test_a50_10c_migration_and_rollback_governance_are_explicit() -> None:
    report = _evaluate()
    assert report.owner_delegation_clear is True
    assert report.historical_tests_frozen is True
    assert report.historical_validators_removed_from_active_ci is True
    assert report.post_promotion_validator_active is True
    assert report.rollback_contract_clear is True
    assert report.final_owner_review_deferred is True

    state = json.loads((BENCHMARKS / "knowledge-canonical-state-v2.json").read_text(encoding="utf-8"))
    assert state["rollback"]["restore_index_refs"] == [
        "records/financial-currency-locale-formatting.json",
        "records/cultural-object-metadata-rights-iiif.json",
        "records/industrial-motor-system-claims-doe.json",
    ]
    assert state["rollback"]["preserve_drafts"] is True
    assert state["rollback"]["preserve_governance_history"] is True
