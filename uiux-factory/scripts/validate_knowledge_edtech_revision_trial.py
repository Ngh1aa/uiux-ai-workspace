from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_edtech_revision_trial import evaluate_knowledge_edtech_revision_trial


def main() -> int:
    benchmarks = ROOT / "benchmarks"
    report = evaluate_knowledge_edtech_revision_trial(
        trial_path=benchmarks / "knowledge-edtech-revision-trial-v1.json",
        mapping_path=benchmarks / "knowledge-edtech-revision-mapping-v1.json",
        reviews_path=benchmarks / "knowledge-edtech-revision-human-review-v1.json",
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
        "A50.9A EdTech revision trial PASSED: "
        f"prior={report.prior_verdict} revised={report.revised_record_id} "
        f"reviewed={report.human_review_complete} verdict={report.verdict} "
        f"canonical={report.canonical_index_count}"
    )
    print(f"revised_record_unindexed={report.revised_record_unindexed}")
    print(f"shadow_retrieval_isolated={report.shadow_retrieval_isolated}")
    print(f"required_state_guidance_present={report.required_state_guidance_present}")
    print(f"joint_usefulness_win={report.joint_usefulness_win}")
    print(f"correctness_guard_clear={report.correctness_guard_clear}")
    print(f"unsupported_claim_risk_guard_clear={report.unsupported_claim_risk_guard_clear}")
    print(f"index_mutation_allowed={report.index_mutation_allowed}")
    print(f"canonical_acceptance_allowed={report.canonical_acceptance_allowed}")
    print(f"auto_promotion_allowed={report.auto_promotion_allowed}")
    print(f"vector_search_change_allowed={report.vector_search_change_allowed}")
    print(f"product_evidence={report.product_evidence}")

    expected = (
        report.prior_verdict == "REVISE_DRAFT"
        and report.revised_record_unindexed is True
        and report.shadow_retrieval_isolated is True
        and report.required_state_guidance_present is True
        and report.human_review_complete is True
        and report.preferred_output == "B"
        and report.knowledge_condition == "B"
        and report.baseline_condition == "A"
        and report.material_regression is False
        and report.verdict == "ACCEPT_FOR_INDEX_TRIAL"
        and report.joint_usefulness_win is True
        and report.correctness_guard_clear is True
        and report.unsupported_claim_risk_guard_clear is True
        and report.canonical_index_count == 3
        and report.index_mutation_allowed is False
        and report.canonical_acceptance_allowed is False
        and report.auto_promotion_allowed is False
        and report.vector_search_change_allowed is False
        and report.product_evidence is False
    )
    return 0 if expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
