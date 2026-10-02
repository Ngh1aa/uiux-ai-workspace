from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_project_dogfood import evaluate_knowledge_project_dogfood


def main() -> int:
    report = evaluate_knowledge_project_dogfood(
        ROOT / "benchmarks/knowledge-project-dogfood-v1.json",
        knowledge_root=WORKSPACE / "skills_UIUX/knowledge",
    )
    status = "PASSED" if report.passed == report.total else "FAILED"
    print(
        f"knowledge project dogfood {status}: {report.passed}/{report.total} cases, "
        f"corpus_hash={report.corpus_hash}, index_hash={report.index_hash[:16]}, version={report.version}"
    )
    for case in report.cases:
        print(
            f"- {'PASS' if case.passed else 'FAIL'} {case.case_id}: {case.message}; "
            f"repo={case.repository} ids={','.join(case.actual_ids)}"
        )
    print(f"scope={report.scope}")
    return 0 if report.passed == report.total else 1


if __name__ == "__main__":
    raise SystemExit(main())
