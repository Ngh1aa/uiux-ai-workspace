from __future__ import annotations

import hashlib
import json
from pathlib import Path

from core.benchmarks.scorecard_regression import evaluate_scorecard_benchmark


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "benchmarks" / "scorecard-v1.json"


def main() -> int:
    payload = CORPUS.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()[:16]
    version = json.loads(payload.decode("utf-8"))["version"]
    results = evaluate_scorecard_benchmark(CORPUS)
    failures = [item for item in results if not item.passed]
    if failures:
        print(
            f"scorecard benchmark FAILED: {len(results) - len(failures)}/{len(results)} cases, "
            f"hash={digest}, version={version}"
        )
        for item in results:
            print(f"- {'PASS' if item.passed else 'FAIL'} {item.case_id}: {item.detail}")
        return 1

    print(f"scorecard benchmark PASSED: {len(results)}/{len(results)} cases, hash={digest}, version={version}")
    for item in results:
        print(f"- PASS {item.case_id}: {item.detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
