#!/usr/bin/env python3
"""Install a curated skills_UIUX profile into a project .claude/skills directory.

Standard-library only. Design-intelligence resources are installed only when
the bridge skill is selected.

Example:
  python scripts/install-profile.py education --target ../my-project
  python scripts/install-profile.py redesign --target . --dry-run
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "profiles"
DESIGN_INTELLIGENCE_SKILL = "design-intelligence-retrieval"
DESIGN_INTELLIGENCE_RESOURCE = "vendor/ui-ux-pro-max"


def load_profile(name: str, seen: set[str] | None = None) -> list[str]:
    seen = seen or set()
    if name in seen:
        raise ValueError(f"profile inheritance cycle: {name}")
    seen.add(name)

    path = PROFILES / f"{name}.json"
    if not path.exists():
        available = ", ".join(sorted(p.stem for p in PROFILES.glob("*.json")))
        raise ValueError(f"unknown profile '{name}'. Available: {available}")

    data = json.loads(path.read_text(encoding="utf-8"))
    skills: list[str] = []
    parent = data.get("extends")
    if parent:
        skills.extend(load_profile(parent, seen))
    skills.extend(data.get("skills", []))
    return list(dict.fromkeys(skills))


def resolve_resources(skills: list[str]) -> list[str]:
    if DESIGN_INTELLIGENCE_SKILL not in skills:
        return []
    resource = ROOT / DESIGN_INTELLIGENCE_RESOURCE
    if not resource.exists():
        raise ValueError(
            f"{DESIGN_INTELLIGENCE_SKILL} requires missing resource: "
            f"{DESIGN_INTELLIGENCE_RESOURCE}"
        )
    return [DESIGN_INTELLIGENCE_RESOURCE]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("profile")
    parser.add_argument("--target", default=".", help="Project root")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--clean", action="store_true", help="Remove destination skills first")
    args = parser.parse_args()

    project = Path(args.target).resolve()
    destination = project / ".claude" / "skills"
    skills = load_profile(args.profile)
    resources = resolve_resources(skills)

    missing = [s for s in skills if not (ROOT / s / "SKILL.md").exists()]
    if missing:
        raise SystemExit(f"Profile references missing skills: {', '.join(missing)}")

    print(f"Profile: {args.profile}")
    print(f"Destination: {destination}")
    print(f"Skills ({len(skills)}): {', '.join(skills)}")
    if resources:
        print("Managed resources: " + ", ".join(resources))

    if args.dry_run:
        return 0

    if args.clean and destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    for skill in skills:
        src = ROOT / skill
        dst = destination / skill
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

    for resource_name in resources:
        src = ROOT / resource_name
        dst = destination / resource_name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))

    print("Installed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
