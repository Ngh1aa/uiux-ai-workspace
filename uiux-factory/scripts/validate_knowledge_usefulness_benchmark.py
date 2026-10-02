from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_usefulness_regression import evaluate_knowledge_usefulness


def main() -> int:
    report = evaluate_knowledge_usefulness(
        ROOT / "benchmarks/knowledge-usefulness-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=WORKSPACE / "skills_UIUX/knowledge",
    )
    status = "PASSED" if report.passed == report.total else "FAILED"
    print(
        f"knowledge usefulness benchmark {status}: {report.passed}/{report.total} cases, "
        f"corpus_hash={report.corpus_hash}, index_hash={report.index_hash[:16]}, version={report.version}"
    )
    for case in report.cases:
        print(
            f"- {'PASS' if case.passed else 'FAIL'} {case.case_id}: decision={case.decision}; "
            f"actionable={case.actionable_delta} specific={case.domain_specificity} "
            f"duplication_clear={case.skill_duplication_clear} noise_clear={case.retrieval_noise_clear} "
            f"provenance={case.provenance_clear} chars={case.context_chars}; {case.message}"
        )
    print(f"expand_allowed={report.expand_allowed}")
    print(f"expand_blocker={report.expand_blocker}")
    print(f"scope={report.scope}")
    return 0 if report.passed == report.total and report.expand_allowed is False else 1


if __name__ == "__main__":
    raise SystemExit(main())
