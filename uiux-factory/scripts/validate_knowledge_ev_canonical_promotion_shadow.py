from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_ev_canonical_promotion_shadow import evaluate_knowledge_ev_canonical_promotion_shadow


def main() -> int:
    benchmarks = ROOT / "benchmarks"
    report = evaluate_knowledge_ev_canonical_promotion_shadow(
        benchmarks / "knowledge-ev-canonical-promotion-shadow-v1.json",
        canary_trial_path=benchmarks / "knowledge-ev-controlled-index-trial-v1.json",
        acceptance_trial_path=benchmarks / "knowledge-candidate-acceptance-trial-v1.json",
        acceptance_mapping_path=benchmarks / "knowledge-candidate-acceptance-mapping-v1.json",
        acceptance_reviews_path=benchmarks / "knowledge-candidate-acceptance-human-reviews-v1.json",
        draft_corpus_path=benchmarks / "knowledge-ready-candidate-drafts-v1.json",
        expansion_proposal_path=benchmarks / "knowledge-expansion-proposal-v1.json",
        promotion_proposal_path=benchmarks / "knowledge-ev-canonical-promotion-proposal-v1.json",
        owner_delegation_path=benchmarks / "governance-owner-delegation-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=WORKSPACE / "skills_UIUX/knowledge",
        benchmarks_root=benchmarks,
    )
    print(
        "A50.10B EV canonical promotion shadow: "
        f"decision={report.decision} canary={report.canary_decision} "
        f"canonical_before={report.canonical_index_count_before} shadow={report.shadow_index_count}"
    )
    for field in (
        "owner_delegation_clear",
        "source_freshness_clear",
        "candidate_unindexed_before",
        "canonical_record_contract_clear",
        "canonical_content_ref_rewritten",
        "ev_retrieval_isolated",
        "canonical_retrieval_regression_clear",
        "negative_domain_isolation_clear",
        "context_budget_clear",
        "rollback_verified",
        "repository_index_unchanged",
        "repository_canonical_assets_absent",
        "migration_contract_clear",
        "genai_hold_preserved",
    ):
        print(f"{field}={getattr(report, field)}")
    print(f"repository_index_mutation_allowed={report.repository_index_mutation_allowed}")
    print(f"repository_canonical_assets_commit_allowed={report.repository_canonical_assets_commit_allowed}")
    print(f"auto_promotion_in_this_phase={report.auto_promotion_in_this_phase}")
    print(f"vector_search_change_allowed={report.vector_search_change_allowed}")
    print(f"product_evidence={report.product_evidence}")

    expected = (
        report.decision == "READY_FOR_CANONICAL_APPLY"
        and report.canary_decision == "CANARY_PASS"
        and report.owner_delegation_clear is True
        and report.source_freshness_clear is True
        and report.candidate_unindexed_before is True
        and report.canonical_index_count_before == 3
        and report.shadow_index_count == 4
        and report.canonical_record_contract_clear is True
        and report.canonical_content_ref_rewritten is True
        and report.ev_retrieval_isolated is True
        and report.canonical_retrieval_regression_clear is True
        and report.negative_domain_isolation_clear is True
        and report.context_budget_clear is True
        and report.rollback_verified is True
        and report.repository_index_unchanged is True
        and report.repository_canonical_assets_absent is True
        and report.migration_contract_clear is True
        and report.genai_hold_preserved is True
        and report.repository_index_mutation_allowed is False
        and report.repository_canonical_assets_commit_allowed is False
        and report.auto_promotion_in_this_phase is False
        and report.vector_search_change_allowed is False
        and report.product_evidence is False
    )
    return 0 if expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
