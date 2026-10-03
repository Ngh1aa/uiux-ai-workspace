#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[2]
FACTORY = WORKSPACE / "uiux-factory"
if str(FACTORY) not in sys.path:
    sys.path.insert(0, str(FACTORY))

from core.dogfood.p174_policy_drift import build_policy_drift_matrix, run_p174_policy_drift


def main() -> int:
    parser = argparse.ArgumentParser(description="Run P1.7.4 repository policy drift detection.")
    parser.add_argument("--matrix", action="store_true", help="Print the monitored repository matrix from the canonical registry.")
    parser.add_argument("--repository")
    parser.add_argument("--repo-root")
    parser.add_argument("--output-dir")
    args = parser.parse_args()

    if args.matrix:
        print(json.dumps(build_policy_drift_matrix(), ensure_ascii=False, separators=(",", ":")))
        return 0

    if not args.repository or not args.repo_root or not args.output_dir:
        parser.error("--repository, --repo-root and --output-dir are required unless --matrix is used")

    report = run_p174_policy_drift(
        repository=args.repository,
        repo_root=Path(args.repo_root),
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
