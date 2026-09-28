from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


FACTORY_ROOT = Path(__file__).resolve().parents[1]
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from core.dogfood.cross_project import evaluate_cross_project_contract, project_profile  # noqa: E402


def _git_sha(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=15,
        shell=False,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value if len(value) == 40 else None


def _visible_files(root: Path) -> list[str]:
    output: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if ".git" in relative.parts:
            continue
        output.append(relative.as_posix())
    return sorted(output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run A13 cross-project source/contract dogfood")
    parser.add_argument("--project-id", choices=("lumen", "cennext"), required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--expected-target-sha", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    root = args.project_root.resolve()
    if not root.is_dir():
        raise SystemExit(f"project root does not exist: {root}")

    actual_sha = _git_sha(root)
    if actual_sha != args.expected_target_sha:
        raise SystemExit(
            f"target SHA mismatch for {args.project_id}: expected {args.expected_target_sha}, "
            f"got {actual_sha or '(not a git checkout)'}"
        )

    profile = project_profile(args.project_id)
    report = evaluate_cross_project_contract(
        profile,
        available_paths=_visible_files(root),
        change_surface=profile.expected_change_surface,
    )
    report["target_sha"] = actual_sha
    report["expected_target_sha"] = args.expected_target_sha
    report["target_sha_bound"] = actual_sha == args.expected_target_sha
    report["passed"] = bool(report["passed"] and report["target_sha_bound"])

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
