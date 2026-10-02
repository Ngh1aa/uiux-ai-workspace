from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_ready_candidate_drafts import evaluate_knowledge_ready_candidate_drafts


def main() -> int:
    report = evaluate_knowledge_ready_candidate_drafts(
        ROOT / "benchmarks/knowledge-ready-candidate-drafts-v1.json",
        proposal_path=ROOT / "benchmarks/knowledge-expansion-proposal-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=WORKSPACE / "skills_UIUX/knowledge",
        benchmarks_root=ROOT / "benchmarks",
    )
    status = "PASSED" if report.passed == report.total else "FAILED"
    print(
        f"A50.7 ready-candidate drafts {status}: {report.passed}/{report.total}; "
        f"canonical={report.canonical_index_count} drafts={report.draft_record_count} "
        f"shadow={report.shadow_index_count} keep={report.keep_draft_count} revise={report.revise_draft_count}"
    )
    for case in report.cases:
        print(
            f"- {'PASS' if case.passed else 'FAIL'} {case.case_id}: {case.decision}; "
            f"actionable={case.actionable_delta} proposal={case.proposal_alignment_clear} "
            f"unindexed={case.canonical_unindexed} domain={case.domain_specificity} "
            f"duplication={case.skill_duplication_clear} noise={case.retrieval_noise_clear} "
            f"provenance={case.provenance_clear} budget={case.context_budget_clear} "
            f"chars={case.context_chars}; {case.message}"
        )
    print(f"genai_hold_preserved={report.genai_hold_preserved}")
    print(f"index_mutation_allowed={report.index_mutation_allowed}")
    print(f"canonical_acceptance_allowed={report.canonical_acceptance_allowed}")
    print(f"human_usefulness_claimed={report.human_usefulness_claimed}")
    return 0 if (
        report.passed == report.total
        and report.keep_draft_count == 2
        and report.revise_draft_count == 0
        and report.genai_hold_preserved
        and report.canonical_index_count == 3
        and report.shadow_index_count == 5
        and report.index_mutation_allowed is False
        and report.canonical_acceptance_allowed is False
        and report.human_usefulness_claimed is False
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
