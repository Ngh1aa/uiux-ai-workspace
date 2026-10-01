from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SKILLS = WORKSPACE / "skills_UIUX"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.routing_regression import (
    RoutingBenchmarkCorpus,
    RoutingBenchmarkError,
    build_routing_report,
)
from core.runtime.flow_os.flow import FlowPlanner


DEFAULT_BENCHMARK = ROOT / "benchmarks" / "routing-v1.json"
DEFAULT_POLICY = SKILLS / "runtime" / "runtime-policy.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate deterministic UIUX Factory routing behavior")
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    try:
        corpus = RoutingBenchmarkCorpus.load(args.benchmark)
        policy = json.loads(DEFAULT_POLICY.read_text(encoding="utf-8"))
        planner = FlowPlanner(SKILLS, policy)
        report = build_routing_report(
            corpus,
            planner=planner,
            policy_doc=policy,
            run_label="routing-validation",
        )
    except (OSError, json.JSONDecodeError, RoutingBenchmarkError, ValueError) as exc:
        print(f"routing benchmark validation FAILED: {exc}")
        return 1

    print(
        "routing benchmark "
        + ("passed" if report["passed"] else "FAILED")
        + f": {report['pass_count']}/{report['case_count']} cases, "
        + f"hash={report['benchmark_hash'][:16]}, version={report['benchmark_version']}"
    )
    for row in report["cases"]:
        status = "PASS" if row["passed"] else "FAIL"
        actual = row["actual"]
        print(
            f"- {status} {row['case_id']}: "
            f"surface={actual['surface']} flow={actual['flow']} "
            f"domain={actual['domain']} website={actual['website_type']}"
        )
        if not row["passed"]:
            failed_checks = [name for name, passed in row["checks"].items() if not passed]
            print("  failed checks: " + ", ".join(failed_checks))

    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
