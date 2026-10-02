from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_genai_nist_freshness_review import evaluate_knowledge_genai_nist_freshness_review


def main() -> int:
    benchmarks = ROOT / "benchmarks"
    report = evaluate_knowledge_genai_nist_freshness_review(
        benchmarks / "knowledge-genai-nist-freshness-review-v1.json",
        expansion_proposal_path=benchmarks / "knowledge-expansion-proposal-v1.json",
        canonical_state_path=benchmarks / "knowledge-canonical-state-v3.json",
        owner_delegation_path=benchmarks / "governance-owner-delegation-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=WORKSPACE / "skills_UIUX/knowledge",
    )
    print(f"A50.14 GenAI/NIST freshness: decision={report.decision}")
    for name in (
        "source_receipts_clear", "candidate_hold_preserved", "candidate_unindexed",
        "canonical_five_record_baseline_clear", "no_genai_canonical_assets",
        "revision_caveat_accurate", "active_revision_blocks_drafting",
        "re_review_trigger_clear", "mutation_boundaries_clear",
        "final_owner_review_deferred", "product_evidence",
    ):
        print(f"{name}={getattr(report, name)}")
    expected = (
        report.decision == "KEEP_HOLD_FRESHNESS_REVIEW"
        and report.source_receipts_clear
        and report.candidate_hold_preserved
        and report.candidate_unindexed
        and report.canonical_five_record_baseline_clear
        and report.no_genai_canonical_assets
        and report.revision_caveat_accurate
        and report.active_revision_blocks_drafting
        and report.re_review_trigger_clear
        and report.mutation_boundaries_clear
        and report.final_owner_review_deferred
        and report.product_evidence is False
    )
    return 0 if expected else 1


if __name__ == "__main__":
    raise SystemExit(main())
