from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.repair_proposal_regression import (
    RepairProposalBenchmarkError,
    RepairProposalCorpus,
    run_repair_proposal_benchmark,
)


DEFAULT_CORPUS = ROOT / "benchmarks" / "repair-proposals-v1.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate deterministic repair proposal policy")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    try:
        corpus = RepairProposalCorpus.load(args.corpus)
        report = run_repair_proposal_benchmark(corpus)
    except (OSError, json.JSONDecodeError, RepairProposalBenchmarkError, ValueError) as exc:
        print(f"repair proposal benchmark FAILED: {exc}")
        return 1

    status = "PASSED" if report["passed"] else "FAILED"
    print(
        f"repair proposal benchmark {status}: "
        f"{report['pass_count']}/{report['case_count']} cases, "
        f"hash={report['content_hash'][:16]}, version={report['version']}"
    )
    for row in report["cases"]:
        failed = [name for name, ok in row["checks"].items() if not ok]
        suffix = "" if not failed else " failed=" + ",".join(failed)
        print(
            f"- {'PASS' if row['passed'] else 'FAIL'} {row['case_id']}: "
            f"critic={row['critic']} stage={row['actual_target_stage']} "
            f"evidence={','.join(row['actual_evidence_types'])}{suffix}"
        )

    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
