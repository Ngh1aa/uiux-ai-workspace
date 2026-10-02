from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.lifecycle_event_interop_regression import evaluate_lifecycle_event_interop_corpus


CORPUS = ROOT / "benchmarks" / "lifecycle-event-interop-v1.json"
EXPECTED_CASES = 8


def main() -> int:
    report = evaluate_lifecycle_event_interop_corpus(CORPUS)
    print(
        "A52.2 lifecycle event interoperability: "
        f"{report.passed}/{report.total} PASS hash={report.corpus_hash}"
    )
    print(f"scope={report.scope}")
    print(f"source_inputs_unchanged={report.source_inputs_unchanged}")
    print(f"authority_boundaries_clear={report.authority_boundaries_clear}")
    for case in report.cases:
        print(f"- {'PASS' if case.passed else 'FAIL'} {case.case_id}: {case.message}")

    if report.total != EXPECTED_CASES:
        print(f"expected {EXPECTED_CASES} A52.2 cases, got {report.total}")
        return 1
    if report.passed != report.total:
        return 1
    if report.source_inputs_unchanged is not True:
        return 1
    if report.authority_boundaries_clear is not True:
        return 1
    if report.scope != "observation_only_no_lifecycle_mutation":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
