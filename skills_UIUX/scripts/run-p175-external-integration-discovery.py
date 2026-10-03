#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[2]
FACTORY = WORKSPACE / "uiux-factory"
if str(FACTORY) not in sys.path:
    sys.path.insert(0, str(FACTORY))

from core.dogfood.p175_external_integration_discovery import (
    build_external_integration_matrix,
    run_p175_external_integration_discovery,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run P1.7.5 external integration discovery.")
    parser.add_argument("--matrix", action="store_true")
    parser.add_argument("--repository")
    parser.add_argument("--repo-root")
    parser.add_argument("--output-dir")
    parser.add_argument("--max-age-days", type=int, default=90)
    args = parser.parse_args()

    if args.matrix:
        print(json.dumps(build_external_integration_matrix(), ensure_ascii=False, separators=(",", ":")))
        return 0

    if not args.repository or not args.repo_root or not args.output_dir:
        parser.error("--repository, --repo-root and --output-dir are required unless --matrix is used")

    report = run_p175_external_integration_discovery(
        repository=args.repository,
        repo_root=Path(args.repo_root),
        output_dir=Path(args.output_dir),
        token=os.environ.get("P175_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN"),
        max_age_days=args.max_age_days,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
