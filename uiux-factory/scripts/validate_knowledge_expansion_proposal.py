from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_expansion_proposal import evaluate_knowledge_expansion_proposal


BENCHMARKS = ROOT / "benchmarks"
KNOWLEDGE = WORKSPACE / "skills_UIUX" / "knowledge"


def main() -> int:
    report = evaluate_knowledge_expansion_proposal(
        proposal_path=BENCHMARKS / "knowledge-expansion-proposal-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=KNOWLEDGE,
        benchmarks_root=BENCHMARKS,
    )
    if report.current_index_count != 3:
        raise SystemExit("A50.6 proposal must preserve the three-record canonical index")
    if report.candidate_count != 3:
        raise SystemExit("A50.6 v1 must stay bounded to three candidates")
    if report.ready_count != 2 or report.hold_count != 1 or report.reject_count != 0:
        raise SystemExit("A50.6 expected candidate status mix is 2 READY / 1 HOLD / 0 REJECT")
    if report.trigger_recommendation != "CONSIDER_EXPANSION":
        raise SystemExit("A50.6 must be triggered by canonical CONSIDER_EXPANSION")
    if report.index_mutation_allowed or report.record_creation_allowed or report.vector_search_change_allowed:
        raise SystemExit("A50.6 proposal may not mutate index/records or enable vector search")

    print(
        "knowledge expansion proposal PASSED: "
        f"candidates={report.candidate_count} ready={report.ready_count} "
        f"hold={report.hold_count} reject={report.reject_count} "
        f"index={report.current_index_count} hash={report.proposal_hash}"
    )
    for candidate in report.candidates:
        print(
            f"- {candidate.status} {candidate.candidate_id}: "
            f"domain={candidate.domain} source={candidate.source_host} "
            f"freshness={candidate.freshness} duplication={candidate.duplication_risk} "
            f"freshness_risk={candidate.freshness_risk}"
        )
    print("scope=proposal_only_no_index_or_record_mutation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
