from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_edtech_controlled_index_trial import evaluate_knowledge_edtech_controlled_index_trial


def main() -> int:
    benchmarks = ROOT / "benchmarks"
    report = evaluate_knowledge_edtech_controlled_index_trial(
        benchmarks / "knowledge-edtech-controlled-index-trial-v1.json",
        revision_trial_path=benchmarks / "knowledge-edtech-revision-trial-v1.json",
        revision_mapping_path=benchmarks / "knowledge-edtech-revision-mapping-v1.json",
        revision_reviews_path=benchmarks / "knowledge-edtech-revision-human-review-v1.json",
        prior_trial_path=benchmarks / "knowledge-candidate-acceptance-trial-v1.json",
        prior_mapping_path=benchmarks / "knowledge-candidate-acceptance-mapping-v1.json",
        prior_reviews_path=benchmarks / "knowledge-candidate-acceptance-human-reviews-v1.json",
        draft_corpus_path=benchmarks / "knowledge-ready-candidate-drafts-v1.json",
        proposal_path=benchmarks / "knowledge-expansion-proposal-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=WORKSPACE / "skills_UIUX/knowledge",
        benchmarks_root=benchmarks,
    )
    print(
        "A50.9C EdTech controlled index trial: "
        f"decision={report.decision} prior={report.prior_revision_verdict} "
        f"canonical={report.canonical_index_count} canary={report.canary_index_count}"
    )
    print(f"usefulness_evidence_clear={report.usefulness_evidence_clear}")
    print(f"revision_record_unindexed={report.revision_record_unindexed}")
    print(f"edtech_retrieval_isolated={report.edtech_retrieval_isolated}")
    print(f"canonical_retrieval_regression_clear={report.canonical_retrieval_regression_clear}")
    print(f"negative_domain_isolation_clear={report.negative_domain_isolation_clear}")
    print(f"context_budget_clear={report.context_budget_clear}")
    print(f"rollback_verified={report.rollback_verified}")
    print(f"genai_hold_preserved={report.genai_hold_preserved}")
    print(f"promotion_proposal_allowed={report.promotion_proposal_allowed}")
    print(f"index_mutation_allowed={report.index_mutation_allowed}")
    print(f"canonical_promotion_allowed={report.canonical_promotion_allowed}")
    print(f"auto_promotion_allowed={report.auto_promotion_allowed}")
    print(f"vector_search_change_allowed={report.vector_search_change_allowed}")
    print(f"product_evidence={report.product_evidence}")

    expected = (
        report.decision == "CANARY_PASS"
        and report.prior_revision_verdict == "ACCEPT_FOR_INDEX_TRIAL"
        and report.usefulness_evidence_clear is True
        and report.revision_record_unindexed is True
        and report.canonical_index_count == 3
        and report.canary_index_count == 4
        and report.edtech_retrieval_isolated is True
        and report.canonical_retrieval_regression_clear is True
        and report.negative_domain_isolation_clear is True
        and report.context_budget_clear is True
        and report.rollback_verified is True
        and report.genai_hold_preserved is True
        and report.promotion_proposal_allowed is True
        and report.index_mutation_allowed is False
        and report.canonical_promotion_allowed is False
        and report.auto_promotion_allowed is False
        and report.vector_search_change_allowed is False
        and report.product_evidence is False
        and report.canonical_index_hash_before == report.canonical_index_hash_after
    )
    return 0 if expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
