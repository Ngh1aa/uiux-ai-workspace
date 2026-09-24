#!/usr/bin/env python3
"""Validate the pinned UI UX Pro Max vendor snapshot and local integration assumptions."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor" / "ui-ux-pro-max"
PINNED = "314307f156aeab0c6b567bbaa1ce4e7aabd5a636"
EXPECTED_SKILLS = {
    "banner-design",
    "brand",
    "design-system",
    "design",
    "slides",
    "ui-styling",
    "ui-ux-pro-max",
}
REQUIRED = [
    VENDOR / "LICENSE",
    VENDOR / "UPSTREAM.md",
    VENDOR / "engine" / "scripts" / "search.py",
    VENDOR / "engine" / "scripts" / "core.py",
    VENDOR / "engine" / "scripts" / "design_system.py",
    VENDOR / "engine" / "scripts" / "reasoning_contract.py",
    VENDOR / "engine" / "data" / "catalog-summary.json",
    VENDOR / "engine" / "data" / "data-provenance.json",
    VENDOR / "engine" / "data" / "styles.csv",
    VENDOR / "engine" / "data" / "colors.csv",
    VENDOR / "engine" / "data" / "products.csv",
    VENDOR / "engine" / "data" / "typography.csv",
    VENDOR / "engine" / "data" / "ui-reasoning.csv",
    VENDOR / "engine" / "data" / "ux-guidelines.csv",
]


def main() -> int:
    errors: list[str] = []

    for path in REQUIRED:
        if not path.exists():
            errors.append(f"missing required vendor file: {path.relative_to(ROOT)}")

    skills_dir = VENDOR / "skills"
    actual_skills = (
        {path.name for path in skills_dir.iterdir() if path.is_dir()}
        if skills_dir.exists()
        else set()
    )
    missing = EXPECTED_SKILLS - actual_skills
    if missing:
        errors.append(f"missing upstream skill packages: {sorted(missing)}")

    for skill in EXPECTED_SKILLS & actual_skills:
        if not (skills_dir / skill / "SKILL.md").exists():
            errors.append(f"missing SKILL.md for upstream skill: {skill}")

    generated = [
        path.relative_to(ROOT)
        for path in VENDOR.rglob("*")
        if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}
    ] if VENDOR.exists() else []
    if generated:
        errors.append(f"generated Python cache found in vendor snapshot: {generated[:8]}")

    upstream = VENDOR / "UPSTREAM.md"
    if upstream.exists() and PINNED not in upstream.read_text(encoding="utf-8"):
        errors.append("UPSTREAM.md does not contain pinned upstream commit")

    summary_path = VENDOR / "engine" / "data" / "catalog-summary.json"
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            counts = summary.get("counts", {})
            for key in (
                "styles",
                "products",
                "palettes",
                "reasoningProfiles",
                "fontPairings",
                "googleFonts",
                "curatedIcons",
                "upstreamPhosphorIcons",
                "uxGuidelines",
                "motionPresets",
                "chartTypes",
                "stacks",
                "stackGuidelines",
            ):
                if key not in counts:
                    errors.append(f"catalog summary missing count key: {key}")
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"invalid catalog-summary.json: {exc}")

    if errors:
        print("Vendor validation errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Vendor integrity passed: "
        f"{len(EXPECTED_SKILLS)} upstream skills + full pinned search/data contract"
    )
    return 0


def check_upstream() -> int:
    """Check if the pinned commit is current with upstream HEAD."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "ls-remote", f"https://github.com/{UPSTREAM_REPO}.git", "HEAD"],
            capture_output=True, text=True, check=True, timeout=30,
        )
        upstream_head = result.stdout.split()[0] if result.stdout.strip() else None
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
        print(f"WARNING: cannot fetch upstream HEAD: {exc}", file=sys.stderr)
        return 0  # informational, don't block CI

    if not upstream_head:
        print("WARNING: empty response from upstream", file=sys.stderr)
        return 0

    if upstream_head == PINNED:
        print(f"Vendor pin is current: {PINNED[:12]}")
        return 0
    else:
        print(f"Vendor pin is BEHIND upstream")
        print(f"  Pinned:   {PINNED[:12]}")
        print(f"  Upstream: {upstream_head[:12]}")
        print(f"  Action:   run vendor-drift-diff.py for detailed risk analysis")
        return 0  # informational exit — does not block CI


UPSTREAM_REPO = "nextlevelbuilder/ui-ux-pro-max-skill"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-upstream",
        action="store_true",
        help="Check if pinned commit is current with upstream HEAD (informational)",
    )
    args = parser.parse_args()

    if args.check_upstream:
        raise SystemExit(check_upstream())
    raise SystemExit(main())
