#!/usr/bin/env python3
"""Vendor drift diff report for pinned ui-ux-pro-max upstream.

Compares the pinned vendor commit against upstream HEAD to produce a
structured diff report with 4-level risk classification.

Risk levels:
  LOW      — docs/license/non-runtime changes
  MEDIUM   — data row/content changes, schema preserved
  HIGH     — schema/search API/SKILL structure changes
  CRITICAL — license/provenance incompatibility or runtime contract removed
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
PINNED_COMMIT = "314307f156aeab0c6b567bbaa1ce4e7aabd5a636"
UPSTREAM_REPO = "nextlevelbuilder/ui-ux-pro-max-skill"

CRITICAL_PATHS = {"LICENSE", "NOTICE", "COPYING"}
HIGH_PATHS_PATTERNS = [
    "src/ui-ux-pro-max/scripts/",
    ".claude/skills/",
    "src/ui-ux-pro-max/data/catalog-summary.json",
    "src/ui-ux-pro-max/data/data-provenance.json",
]
MEDIUM_PATHS_PATTERNS = [
    "src/ui-ux-pro-max/data/",
]
LOW_PATHS_PATTERNS = [
    "README",
    "docs/",
    ".github/",
    "CHANGELOG",
    ".gitignore",
]


def classify_file_risk(path: str) -> str:
    """Classify a changed file into a risk level."""
    basename = Path(path).name

    if basename.upper() in CRITICAL_PATHS:
        return "CRITICAL"

    for pattern in HIGH_PATHS_PATTERNS:
        if pattern in path:
            return "HIGH"

    for pattern in MEDIUM_PATHS_PATTERNS:
        if pattern in path:
            return "MEDIUM"

    for pattern in LOW_PATHS_PATTERNS:
        if pattern.lower() in path.lower():
            return "LOW"

    return "MEDIUM"


def get_upstream_head(clone_dir: Path) -> str | None:
    """Get the HEAD commit of the upstream repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=clone_dir,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def revision_exists(clone_dir: Path, revision: str) -> bool:
    """Return True only when revision resolves to a commit in the checkout."""
    try:
        subprocess.run(
            ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
            capture_output=True,
            text=True,
            cwd=clone_dir,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_commits_between(clone_dir: Path, old_commit: str, new_commit: str) -> int:
    """Count commits between two revisions."""
    try:
        result = subprocess.run(
            ["git", "rev-list", "--count", f"{old_commit}..{new_commit}"],
            capture_output=True,
            text=True,
            cwd=clone_dir,
            check=True,
        )
        return int(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return -1


def get_changed_files(clone_dir: Path, old_commit: str, new_commit: str) -> list[str]:
    """Get list of files changed between two commits."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", old_commit, new_commit],
            capture_output=True,
            text=True,
            cwd=clone_dir,
            check=True,
        )
        return [f for f in result.stdout.strip().split("\n") if f]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def get_diff_stat(clone_dir: Path, old_commit: str, new_commit: str) -> str:
    """Get diffstat between two commits."""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", old_commit, new_commit],
            capture_output=True,
            text=True,
            cwd=clone_dir,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def generate_report(
    clone_dir: Path,
    pinned: str = PINNED_COMMIT,
) -> dict[str, Any]:
    """Generate a vendor drift diff report."""
    upstream_head = get_upstream_head(clone_dir)
    if not upstream_head:
        return {"error": "cannot determine upstream HEAD"}

    if not revision_exists(clone_dir, pinned):
        return {
            "error": (
                f"pinned commit {pinned} is not available in the upstream checkout; "
                "fetch full history before classifying drift"
            )
        }

    if upstream_head == pinned:
        return {
            "pinned_commit": pinned,
            "upstream_head": upstream_head,
            "status": "current",
            "commits_behind": 0,
            "message": "Vendor pin is current with upstream HEAD",
        }

    commits_behind = get_commits_between(clone_dir, pinned, upstream_head)
    changed_files = get_changed_files(clone_dir, pinned, upstream_head)
    diff_stat = get_diff_stat(clone_dir, pinned, upstream_head)

    if commits_behind < 0:
        return {"error": "cannot compute commit distance between pinned commit and upstream HEAD"}
    if commits_behind > 0 and not changed_files:
        return {
            "error": (
                "upstream is ahead but changed-file diff is empty; refusing to classify "
                "an incomplete drift report"
            )
        }

    file_risks: dict[str, str] = {}
    risk_counts: dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in changed_files:
        risk = classify_file_risk(f)
        file_risks[f] = risk
        risk_counts[risk] += 1

    data_schema_changed = any(
        "catalog-summary.json" in f or "data-provenance.json" in f
        for f in changed_files
    )
    search_api_changed = any("scripts/search.py" in f for f in changed_files)
    skill_changes = [f for f in changed_files if ".claude/skills/" in f]
    skills_added = [f for f in skill_changes if "SKILL.md" in f]
    skills_removed: list[str] = []
    license_changed = any(Path(f).name.upper() in CRITICAL_PATHS for f in changed_files)

    if risk_counts["CRITICAL"] > 0:
        overall_risk = "CRITICAL"
    elif risk_counts["HIGH"] > 0:
        overall_risk = "HIGH"
    elif risk_counts["MEDIUM"] > 0:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    recommendations = {
        "CRITICAL": "License or provenance change detected. Review IMMEDIATELY before any update.",
        "HIGH": "Schema, search API, or skill structure changed. Full test suite + manual review required before updating pin.",
        "MEDIUM": "Data content changes detected. Run validation + spot-check data integrity before updating pin.",
        "LOW": "Documentation/config changes only. Low risk — review and update at convenience.",
    }

    return {
        "pinned_commit": pinned,
        "upstream_head": upstream_head,
        "status": "behind",
        "commits_behind": commits_behind,
        "files_changed": changed_files,
        "file_risks": file_risks,
        "risk_counts": risk_counts,
        "overall_risk": overall_risk,
        "data_schema_changed": data_schema_changed,
        "search_api_changed": search_api_changed,
        "license_changed": license_changed,
        "skill_changes": skill_changes,
        "skills_added": skills_added,
        "skills_removed": skills_removed,
        "diff_stat": diff_stat,
        "recommendation": recommendations[overall_risk],
    }


def format_issue_body(report: dict[str, Any]) -> str:
    """Format the report as a GitHub issue body."""
    if report.get("status") == "current":
        return "Vendor pin is current. No action needed."

    risk = report["overall_risk"]
    risk_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}

    lines = [
        f"## {risk_emoji.get(risk, '⚪')} Vendor Drift Detected — Risk: {risk}",
        "",
        f"**Pinned commit:** `{report['pinned_commit'][:12]}`",
        f"**Upstream HEAD:** `{report['upstream_head'][:12]}`",
        f"**Commits behind:** {report['commits_behind']}",
        "",
        "### Recommendation",
        f"> {report['recommendation']}",
        "",
        "### Risk Breakdown",
        "| Level | Count |",
        "|---|---|",
    ]
    for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        count = report["risk_counts"].get(level, 0)
        if count > 0:
            lines.append(f"| {risk_emoji.get(level, '')} {level} | {count} |")

    lines.extend([
        "",
        "### Key Changes",
        f"- Data schema changed: {'✅ YES' if report['data_schema_changed'] else '❌ No'}",
        f"- Search API changed: {'✅ YES' if report['search_api_changed'] else '❌ No'}",
        f"- License changed: {'🔴 YES' if report['license_changed'] else '❌ No'}",
        f"- Skill changes: {len(report['skill_changes'])} files",
    ])

    if report.get("diff_stat"):
        lines.extend(["", "### Diff Summary", "```", report["diff_stat"], "```"])

    lines.extend([
        "",
        "### Action Required",
        "1. Review changed files and their risk levels",
        "2. Run `python scripts/validate-vendor-uiux-pro-max.py` on updated snapshot",
        "3. Run `python scripts/eval-harness.py smoke`",
        "4. If all pass, update pinned commit in workflow + validation script",
        "",
        "⚠️ **Do NOT auto-update.** Manual review required.",
    ])

    return "\n".join(lines)


def cmd_report(args: argparse.Namespace) -> int:
    clone_dir = Path(args.clone_dir)
    if not clone_dir.exists():
        print(f"ERROR: clone directory not found: {clone_dir}", file=sys.stderr)
        return 1

    report = generate_report(clone_dir, args.pinned or PINNED_COMMIT)

    if "error" in report:
        print(f"ERROR: {report['error']}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.issue_body:
        print(format_issue_body(report))
    else:
        status = report["status"]
        if status == "current":
            print("✅ Vendor pin is current with upstream HEAD")
            return 0

        risk = report["overall_risk"]
        print("Vendor Drift Report")
        print(f"{'=' * 50}")
        print(f"Status:           {report['commits_behind']} commits behind")
        print(f"Overall risk:     {risk}")
        print(f"Files changed:    {len(report['files_changed'])}")
        print(f"Schema changed:   {report['data_schema_changed']}")
        print(f"Search API:       {report['search_api_changed']}")
        print(f"License:          {report['license_changed']}")
        print()
        print(f"Recommendation:   {report['recommendation']}")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "clone_dir",
        help="Path to a local clone/checkout of the upstream repository",
    )
    parser.add_argument("--pinned", help=f"Pinned commit (default: {PINNED_COMMIT})")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--issue-body", action="store_true", help="Output GitHub issue body markdown")
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return cmd_report(args)
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
