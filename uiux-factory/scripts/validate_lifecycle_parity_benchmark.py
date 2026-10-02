from __future__ import annotations

from pathlib import Path

from core.benchmarks.lifecycle_parity_regression import evaluate_lifecycle_parity_corpus


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    corpus = root / "benchmarks/lifecycle-parity-v1.json"
    report = evaluate_lifecycle_parity_corpus(corpus)

    print(
        f"lifecycle parity benchmark {'PASSED' if report.passed == report.total else 'FAILED'}: "
        f"{report.passed}/{report.total} cases, hash={report.corpus_hash}, version={report.schema_version}"
    )
    for case in report.cases:
        print(f"- {'PASS' if case.passed else 'FAIL'} {case.case_id}: {case.message}")
    print(f"scope={report.scope}")
    return 0 if report.passed == report.total else 1


if __name__ == "__main__":
    raise SystemExit(main())
