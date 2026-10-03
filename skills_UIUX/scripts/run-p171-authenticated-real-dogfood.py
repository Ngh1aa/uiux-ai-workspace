#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = SKILLS_ROOT.parent
FACTORY_ROOT = WORKSPACE_ROOT / "uiux-factory"
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from core.dogfood.p171_authenticated_real_runner import DOGFOOD_PROFILES, run_authenticated_dogfood


def main() -> int:
    parser = argparse.ArgumentParser(description="Run P1.7.1 authenticated GitHubProductionRunner dogfood against one opted-in real repository.")
    parser.add_argument("--profile", default="luxroom-cart-total-live-region", choices=sorted(DOGFOOD_PROFILES))
    parser.add_argument("--transaction-id", required=True)
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--github-output", default="")
    args = parser.parse_args()

    token = os.environ.get("UIUX_TARGET_REPO_TOKEN") or os.environ.get("GH_TOKEN") or ""
    report = run_authenticated_dogfood(
        profile_id=args.profile,
        transaction_id=args.transaction_id,
        github_token=token,
        workspace_root=Path(args.workspace_root),
        output_dir=Path(args.output_dir),
    )
    summary = {
        "passed": report["passed"],
        "profile": args.profile,
        "transaction_branch": report["transaction_branch"],
        "main_unchanged": report["main_unchanged"],
        "changed_files": report["changed_files"],
        "pr_state": report["pr_state"],
        "pr_url": report["pr_url"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.github_output:
        output = Path(args.github_output)
        with output.open("a", encoding="utf-8") as handle:
            handle.write(f"passed={'true' if report['passed'] else 'false'}\n")
            handle.write(f"transaction_branch={report['transaction_branch']}\n")
            handle.write(f"pr_url={report['pr_url'] or ''}\n")
            handle.write(f"pr_state={report['pr_state'] or ''}\n")
            handle.write(f"main_unchanged={'true' if report['main_unchanged'] else 'false'}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
