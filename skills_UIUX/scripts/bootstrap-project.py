#!/usr/bin/env python3
"""Bootstrap profile-based skills_UIUX sync for a consumer project."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "project-sync-uiux-skills.yml"


def default_profile(project: Path, profile: str) -> dict:
    return {
        "schema_version": 2,
        "profile": profile,
        "packs": [],
        "additional_skills": [],
        "exclude_skills": [],
        "project": {"name": project.name, "mode": "website", "domain": "unspecified"},
        "source_of_truth": [],
        "constraints": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Consumer project root")
    parser.add_argument("--profile", default="uiux-corporate", help="skills_UIUX profile")
    parser.add_argument("--force-workflow", action="store_true", help="Replace an existing sync workflow")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project = args.project.resolve()
    profile_path = project / ".uiux-profile.json"
    workflow_path = project / ".github" / "workflows" / "sync-uiux-skills.yml"
    actions: list[str] = []
    if not profile_path.exists():
        actions.append(f"create {profile_path}")
    if not workflow_path.exists() or args.force_workflow:
        actions.append(f"install {workflow_path}")
    actions.append("install selected skills")
    print("Planned actions:")
    for action in actions:
        print(f"- {action}")
    if args.dry_run:
        return 0

    project.mkdir(parents=True, exist_ok=True)
    if not profile_path.exists():
        profile_path.write_text(json.dumps(default_profile(project, args.profile), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    if not workflow_path.exists() or args.force_workflow:
        shutil.copyfile(TEMPLATE, workflow_path)
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "install-project.py"), str(project)]).returncode


if __name__ == "__main__":
    raise SystemExit(main())
