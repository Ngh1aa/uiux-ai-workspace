from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_edtech_canonical_promotion_shadow import evaluate_knowledge_edtech_canonical_promotion_shadow


def main() -> int:
    benchmarks = ROOT / "benchmarks"
    report = evaluate_knowledge_edtech_canonical_promotion_shadow(
        shadow_trial_path=benchmarks / "knowledge-edtech-canonical-promotion-shadow-v1.json",
        proposal_path=benchmarks / "knowledge-edtech-canonical-promotion-proposal-v1.json",
        review_path=benchmarks / "knowledge-edtech-canonical-promotion-review-v1.json",
        canonical_state_path=benchmarks / "knowledge-canonical-state-v2.json",
        expansion_proposal_path=benchmarks / "knowledge-expansion-proposal-v1.json",
        owner_delegation_path=benchmarks / "governance-owner-delegation-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=WORKSPACE / "skills_UIUX/knowledge",
    )
    print(f"A50.12 EdTech canonical shadow: decision={report.decision} {report.pre_shadow_count}->{report.shadow_count}")
    for name in (
        "record_contract_clear", "content_exact_copy", "semantic_copy_clear",
        "retrieval_regression_clear", "edtech_retrieval_isolated", "ai_negative_isolation_clear",
        "context_budget_clear", "vector_search_disabled", "rollback_verified",
        "repository_index_unchanged", "repository_canonical_assets_absent",
        "genai_hold_preserved", "canonical_apply_allowed", "product_evidence",
    ):
        print(f"{name}={getattr(report, name)}")
    expected = (
        report.decision == "READY_FOR_CANONICAL_APPLY"
        and report.proposal_decision == "APPROVED_FOR_EXPLICIT_PROMOTION_TASK"
        and report.pre_shadow_count == 4
        and report.shadow_count == 5
        and report.record_contract_clear
        and report.content_exact_copy
        and report.semantic_copy_clear
        and report.retrieval_regression_clear
        and report.edtech_retrieval_isolated
        and report.ai_negative_isolation_clear
        and report.context_budget_clear
        and report.vector_search_disabled
        and report.rollback_verified
        and report.repository_index_unchanged
        and report.repository_canonical_assets_absent
        and report.genai_hold_preserved
        and report.canonical_apply_allowed
        and report.product_evidence is False
    )
    return 0 if expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
