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

from core.dogfood.p173_repository_policy_registry import run_p173_live_dogfood


def main() -> int:
    parser = argparse.ArgumentParser(description="Run P1.7.3 read-only multi-repository policy-registry dogfood.")
    parser.add_argument("--target-root", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    token = os.environ.get("UIUX_TARGET_REPO_TOKEN") or os.environ.get("GH_TOKEN") or ""
    report = run_p173_live_dogfood(
        github_token=token,
        target_root=Path(args.target_root),
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
