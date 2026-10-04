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

from core.dogfood.p177_multi_provider_attestation_truth import (
    build_multi_provider_attestation_matrix,
    run_p177_multi_provider_attestation_truth,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="P1.7.7 read-only multi-provider attestation and canonical integration truth."
    )
    parser.add_argument("--matrix", action="store_true")
    parser.add_argument("--repository")
    parser.add_argument("--repo-root")
    parser.add_argument("--output-dir")
    parser.add_argument("--max-age-days", type=int, default=90)
    args = parser.parse_args()

    if args.matrix:
        print(json.dumps(build_multi_provider_attestation_matrix(), ensure_ascii=False))
        return 0

    if not args.repository or not args.repo_root or not args.output_dir:
        parser.error("--repository, --repo-root and --output-dir are required unless --matrix is used")

    report = run_p177_multi_provider_attestation_truth(
        repository=args.repository,
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        github_token=os.environ.get("P177_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN"),
        vercel_token=os.environ.get("P177_VERCEL_TOKEN"),
        vercel_team_id=os.environ.get("P177_VERCEL_TEAM_ID") or os.environ.get("VERCEL_ORG_ID"),
        netlify_token=os.environ.get("P177_NETLIFY_TOKEN"),
        render_token=os.environ.get("P177_RENDER_TOKEN"),
        cloudflare_token=os.environ.get("P177_CLOUDFLARE_API_TOKEN"),
        cloudflare_account_id=os.environ.get("P177_CLOUDFLARE_ACCOUNT_ID"),
        railway_token=os.environ.get("P179_RAILWAY_TOKEN"),
        railway_workspace_id=os.environ.get("P179_RAILWAY_WORKSPACE_ID"),
        max_age_days=args.max_age_days,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
