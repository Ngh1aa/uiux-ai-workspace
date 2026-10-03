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

from core.dogfood.p172_external_side_effect_governance import run_p172_live_dogfood


def main() -> int:
    parser = argparse.ArgumentParser(description="Run P1.7.2 read-only external side-effect governance dogfood.")
    parser.add_argument("--repository", default="Ngh1aa/LuxRoom")
    parser.add_argument("--pr-number", type=int, default=24)
    parser.add_argument("--base-branch", default="main")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    token = os.environ.get("UIUX_TARGET_REPO_TOKEN") or os.environ.get("GH_TOKEN") or ""
    report = run_p172_live_dogfood(
        repository=args.repository,
        pr_number=args.pr_number,
        github_token=token,
        output_dir=Path(args.output_dir),
        base_branch=args.base_branch,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
