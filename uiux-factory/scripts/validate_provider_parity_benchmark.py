from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SKILLS = WORKSPACE / "skills_UIUX"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.provider_parity_regression import evaluate_provider_parity_benchmark
from core.runtime.flow_os.flow import FlowPlanner


DEFAULT_BENCHMARK = ROOT / "benchmarks" / "provider-parity-v1.json"
DEFAULT_POLICY = SKILLS / "runtime" / "runtime-policy.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate offline provider compatibility parity")
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    try:
        raw = args.benchmark.read_bytes()
        payload = json.loads(raw.decode("utf-8"))
        policy = json.loads(DEFAULT_POLICY.read_text(encoding="utf-8"))
        planner = FlowPlanner(SKILLS, policy)
        results = evaluate_provider_parity_benchmark(
            args.benchmark,
            factory_root=ROOT,
            planner=planner,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"provider parity benchmark FAILED: {exc}")
        return 1

    failures = [item for item in results if not item.passed]
    digest = hashlib.sha256(raw).hexdigest()[:16]
    version = str(payload.get("version", ""))
    status = "PASSED" if not failures else "FAILED"
    print(
        f"provider parity benchmark {status}: {len(results) - len(failures)}/{len(results)} cases, "
        f"hash={digest}, version={version}"
    )
    for item in results:
        print(f"- {'PASS' if item.passed else 'FAIL'} {item.case_id} [{item.kind}]: {item.detail}")

    if args.report is not None:
        report = {
            "schema_version": 1,
            "benchmark_version": version,
            "benchmark_hash": digest,
            "scope": payload.get("scope"),
            "passed": not failures,
            "case_count": len(results),
            "pass_count": len(results) - len(failures),
            "results": [
                {
                    "case_id": item.case_id,
                    "kind": item.kind,
                    "passed": item.passed,
                    "detail": item.detail,
                }
                for item in results
            ],
            "truth_boundary": (
                "Offline provider parity and project-profile smoke are regression evidence only; "
                "they are not live-provider, rendered UI, user-validation or product-outcome evidence."
            ),
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
