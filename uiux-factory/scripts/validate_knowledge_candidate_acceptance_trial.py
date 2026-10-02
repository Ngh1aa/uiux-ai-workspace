from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_candidate_acceptance_trial import evaluate_knowledge_candidate_acceptance_trial


def main() -> int:
    report = evaluate_knowledge_candidate_acceptance_trial(
        trial_path=ROOT / "benchmarks/knowledge-candidate-acceptance-trial-v1.json",
        mapping_path=ROOT / "benchmarks/knowledge-candidate-acceptance-mapping-v1.json",
        reviews_path=ROOT / "benchmarks/knowledge-candidate-acceptance-human-reviews-v1.json",
        draft_corpus_path=ROOT / "benchmarks/knowledge-ready-candidate-drafts-v1.json",
        proposal_path=ROOT / "benchmarks/knowledge-expansion-proposal-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=WORKSPACE / "skills_UIUX/knowledge",
        benchmarks_root=ROOT / "benchmarks",
    )
    print(
        "A50.8 candidate acceptance trial PASSED: "
        f"reviewed={report.reviewed_case_count}/{len(report.cases)} "
        f"accept={report.accepted_for_index_trial_count} revise={report.revise_draft_count} "
        f"hold={report.hold_count} reject={report.reject_count} "
        f"human_complete={report.human_review_complete}"
    )
    for case in report.cases:
        print(
            f"- {case.case_id}: verdict={case.verdict} knowledge={case.knowledge_condition} "
            f"baseline={case.baseline_condition} reviewed={case.human_review_complete}; {case.rationale}"
        )
    print(f"index_mutation_allowed={report.index_mutation_allowed}")
    print(f"canonical_acceptance_allowed={report.canonical_acceptance_allowed}")
    print(f"auto_promotion_allowed={report.auto_promotion_allowed}")
    print(f"vector_search_change_allowed={report.vector_search_change_allowed}")
    print(f"product_evidence={report.product_evidence}")

    expected_pending = (
        report.reviewed_case_count == 0
        and report.accepted_for_index_trial_count == 0
        and report.revise_draft_count == 0
        and report.hold_count == 2
        and report.reject_count == 0
        and report.human_review_complete is False
    )
    boundaries = (
        report.index_mutation_allowed is False
        and report.canonical_acceptance_allowed is False
        and report.auto_promotion_allowed is False
        and report.vector_search_change_allowed is False
        and report.product_evidence is False
    )
    return 0 if expected_pending and boundaries else 1


if __name__ == "__main__":
    raise SystemExit(main())
