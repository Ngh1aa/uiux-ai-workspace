from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_edtech_canonical_promotion_proposal import evaluate_knowledge_edtech_canonical_promotion_proposal


def main() -> int:
    benchmarks = ROOT / "benchmarks"
    report = evaluate_knowledge_edtech_canonical_promotion_proposal(
        proposal_path=benchmarks / "knowledge-edtech-canonical-promotion-proposal-v1.json",
        review_path=benchmarks / "knowledge-edtech-canonical-promotion-review-v1.json",
        canonical_state_path=benchmarks / "knowledge-canonical-state-v2.json",
        expansion_proposal_path=benchmarks / "knowledge-expansion-proposal-v1.json",
        owner_delegation_path=benchmarks / "governance-owner-delegation-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=WORKSPACE / "skills_UIUX/knowledge",
    )
    print(
        "A50.11 EdTech canonical promotion proposal: "
        f"decision={report.decision} review={report.review_status}"
    )
    for name in (
        "historical_canary_clear", "current_baseline_clear", "source_freshness_clear",
        "candidate_unindexed", "candidate_authority_boundary_clear", "retrieval_regression_clear",
        "negative_domain_isolation_clear", "rollback_contract_clear", "genai_hold_preserved",
        "owner_delegation_clear", "separate_promotion_task_allowed", "index_mutation_allowed",
        "canonical_promotion_in_this_proposal", "auto_promotion_allowed",
        "vector_search_change_allowed", "product_evidence",
    ):
        print(f"{name}={getattr(report, name)}")

    expected = (
        report.decision == "APPROVED_FOR_EXPLICIT_PROMOTION_TASK"
        and report.historical_canary_clear is True
        and report.current_baseline_clear is True
        and report.source_freshness_clear is True
        and report.candidate_unindexed is True
        and report.candidate_authority_boundary_clear is True
        and report.retrieval_regression_clear is True
        and report.negative_domain_isolation_clear is True
        and report.rollback_contract_clear is True
        and report.genai_hold_preserved is True
        and report.owner_delegation_clear is True
        and report.review_status == "REVIEWED"
        and report.review_verdict == "APPROVE_PROMOTION_TASK"
        and report.separate_promotion_task_allowed is True
        and report.index_mutation_allowed is False
        and report.canonical_promotion_in_this_proposal is False
        and report.auto_promotion_allowed is False
        and report.vector_search_change_allowed is False
        and report.product_evidence is False
    )
    return 0 if expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
