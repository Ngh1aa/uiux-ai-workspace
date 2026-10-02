from __future__ import annotations

from pathlib import Path

from core.benchmarks.knowledge_edtech_canonical_apply import evaluate_knowledge_edtech_canonical_apply

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
BENCHMARKS = ROOT / "benchmarks"
KNOWLEDGE = WORKSPACE / "skills_UIUX/knowledge"


def _evaluate():
    return evaluate_knowledge_edtech_canonical_apply(
        BENCHMARKS / "knowledge-canonical-state-v3.json",
        workspace_root=WORKSPACE,
        knowledge_root=KNOWLEDGE,
        expansion_proposal_path=BENCHMARKS / "knowledge-expansion-proposal-v1.json",
        owner_delegation_path=BENCHMARKS / "governance-owner-delegation-v1.json",
        workflow_path=WORKSPACE / ".github/workflows/uiux-factory-ci.yml",
        conftest_path=ROOT / "tests/conftest.py",
    )


def test_a50_13_edtech_canonical_apply_is_current_five_record_truth() -> None:
    report = _evaluate()
    assert report.decision == "CANONICAL_APPLY_PASS"
    assert report.canonical_index_count == 5
    assert report.exact_record_set_clear is True
    assert report.promoted_record_contract_clear is True
    assert report.promoted_content_exact_copy is True
    assert report.promoted_record_semantic_copy is True
    assert report.source_freshness_metadata_clear is True
    assert report.authority_boundary_clear is True
    assert report.retrieval_regression_clear is True
    assert report.negative_domain_isolation_clear is True
    assert report.context_budget_clear is True
    assert report.vector_search_disabled is True
    assert report.genai_hold_preserved is True
    assert report.owner_delegation_clear is True
    assert report.historical_tests_frozen is True
    assert report.historical_validators_removed_from_active_ci is True
    assert report.post_promotion_validator_active is True
    assert report.rollback_contract_clear is True
    assert report.final_owner_review_deferred is True
    assert report.product_evidence is False


def test_a50_13_index_contains_exactly_one_edtech_ref_and_preserves_ev() -> None:
    import json
    payload = json.loads((KNOWLEDGE / "index.json").read_text(encoding="utf-8"))
    refs = payload["records"]
    edtech = "records/edtech-lti-context-roles-services-v2.json"
    ev = "records/ev-charging-ocpp-transaction-semantics.json"
    assert len(refs) == 5
    assert refs.count(edtech) == 1
    assert ev in refs


def test_a50_13_canonical_content_and_record_exist() -> None:
    assert (KNOWLEDGE / "records/edtech-lti-context-roles-services-v2.json").is_file()
    assert (KNOWLEDGE / "content/edtech-lti-context-roles-services-v2.md").is_file()
