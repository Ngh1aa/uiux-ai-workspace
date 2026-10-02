from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_ev_canonical_promotion_proposal import evaluate_knowledge_ev_canonical_promotion_proposal


def main() -> int:
    benchmarks = ROOT / "benchmarks"
    report = evaluate_knowledge_ev_canonical_promotion_proposal(
        proposal_review_path=benchmarks / "knowledge-ev-canonical-promotion-proposal-v1.json",
        review_path=benchmarks / "knowledge-ev-canonical-promotion-review-v1.json",
        canary_trial_path=benchmarks / "knowledge-ev-controlled-index-trial-v1.json",
        acceptance_trial_path=benchmarks / "knowledge-candidate-acceptance-trial-v1.json",
        acceptance_mapping_path=benchmarks / "knowledge-candidate-acceptance-mapping-v1.json",
        acceptance_reviews_path=benchmarks / "knowledge-candidate-acceptance-human-reviews-v1.json",
        draft_corpus_path=benchmarks / "knowledge-ready-candidate-drafts-v1.json",
        expansion_proposal_path=benchmarks / "knowledge-expansion-proposal-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=WORKSPACE / "skills_UIUX/knowledge",
        benchmarks_root=benchmarks,
    )
    print(
        "A50.10A EV canonical promotion proposal: "
        f"decision={report.decision} canary={report.canary_decision} "
        f"review={report.review_status} canonical={report.canonical_index_count}"
    )
    print(f"proposal_preconditions_clear={report.proposal_preconditions_clear}")
    print(f"candidate_unindexed={report.candidate_unindexed}")
    print(f"separate_promotion_task_allowed={report.separate_promotion_task_allowed}")
    print(f"index_mutation_allowed={report.index_mutation_allowed}")
    print(f"canonical_promotion_in_this_proposal={report.canonical_promotion_in_this_proposal}")
    print(f"auto_promotion_allowed={report.auto_promotion_allowed}")
    print(f"vector_search_change_allowed={report.vector_search_change_allowed}")
    print(f"product_evidence={report.product_evidence}")

    expected = (
        report.decision == "APPROVED_FOR_EXPLICIT_PROMOTION_TASK"
        and report.canary_decision == "CANARY_PASS"
        and report.canary_promotion_proposal_allowed is True
        and report.proposal_preconditions_clear is True
        and report.candidate_unindexed is True
        and report.canonical_index_count == 3
        and report.review_status == "REVIEWED"
        and report.review_verdict == "APPROVE_PROMOTION_TASK"
        and report.source_freshness_rechecked is True
        and report.rollback_plan_accepted is True
        and report.cross_domain_risk_accepted is True
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
