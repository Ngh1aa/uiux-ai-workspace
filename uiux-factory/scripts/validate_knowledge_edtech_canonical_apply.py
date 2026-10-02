from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_edtech_canonical_apply import evaluate_knowledge_edtech_canonical_apply


def main() -> int:
    benchmarks = ROOT / "benchmarks"
    report = evaluate_knowledge_edtech_canonical_apply(
        benchmarks / "knowledge-canonical-state-v3.json",
        workspace_root=WORKSPACE,
        knowledge_root=WORKSPACE / "skills_UIUX/knowledge",
        expansion_proposal_path=benchmarks / "knowledge-expansion-proposal-v1.json",
        owner_delegation_path=benchmarks / "governance-owner-delegation-v1.json",
        workflow_path=WORKSPACE / ".github/workflows/uiux-factory-ci.yml",
        conftest_path=ROOT / "tests/conftest.py",
    )
    print(f"A50.13 EdTech canonical apply: decision={report.decision} canonical={report.canonical_index_count}")
    for name in (
        "exact_record_set_clear", "promoted_record_contract_clear", "promoted_content_exact_copy",
        "promoted_record_semantic_copy", "source_freshness_metadata_clear", "authority_boundary_clear",
        "retrieval_regression_clear", "negative_domain_isolation_clear", "context_budget_clear",
        "vector_search_disabled", "genai_hold_preserved", "owner_delegation_clear",
        "historical_tests_frozen", "historical_validators_removed_from_active_ci",
        "post_promotion_validator_active", "rollback_contract_clear", "final_owner_review_deferred",
        "product_evidence",
    ):
        print(f"{name}={getattr(report, name)}")
    expected = (
        report.decision == "CANONICAL_APPLY_PASS"
        and report.canonical_index_count == 5
        and report.exact_record_set_clear
        and report.promoted_record_contract_clear
        and report.promoted_content_exact_copy
        and report.promoted_record_semantic_copy
        and report.source_freshness_metadata_clear
        and report.authority_boundary_clear
        and report.retrieval_regression_clear
        and report.negative_domain_isolation_clear
        and report.context_budget_clear
        and report.vector_search_disabled
        and report.genai_hold_preserved
        and report.owner_delegation_clear
        and report.historical_tests_frozen
        and report.historical_validators_removed_from_active_ci
        and report.post_promotion_validator_active
        and report.rollback_contract_clear
        and report.final_owner_review_deferred
        and report.product_evidence is False
    )
    return 0 if expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
