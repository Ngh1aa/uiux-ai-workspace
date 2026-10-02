from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.knowledge_retrieval_regression import evaluate_knowledge_retrieval_corpus


def main() -> int:
    corpus = ROOT / "benchmarks/knowledge-retrieval-v1.json"
    report = evaluate_knowledge_retrieval_corpus(corpus)
    status = "PASSED" if report.passed == report.total else "FAILED"
    print(
        f"knowledge retrieval benchmark {status}: {report.passed}/{report.total} cases, "
        f"hash={report.corpus_hash}, version={report.version}"
    )
    for case in report.cases:
        print(
            f"- {'PASS' if case.passed else 'FAIL'} {case.case_id}: {case.message}; "
            f"ids={','.join(case.actual_ids)} exclusions={','.join(case.exclusion_reasons)}"
        )
    print(f"scope={report.scope}")
    return 0 if report.passed == report.total else 1


if __name__ == "__main__":
    raise SystemExit(main())
