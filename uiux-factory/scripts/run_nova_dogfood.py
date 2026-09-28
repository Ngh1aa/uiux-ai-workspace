from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


FACTORY_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = FACTORY_ROOT.parent
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from core.dogfood.real_project import RealProjectDogfoodError, RealProjectDogfoodRunner  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the A13 deterministic real-project dogfood lane against Nova")
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--route", default="/app.html?screen=home")
    parser.add_argument("--expected-target-sha", default=None)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    runner = RealProjectDogfoodRunner(
        skills_root=REPO_ROOT / "skills_UIUX",
        factory_root=FACTORY_ROOT,
        project_root=args.project_root,
    )
    try:
        report = runner.run(
            base_url=args.base_url,
            route=args.route,
            expected_target_sha=args.expected_target_sha,
            report_path=args.report,
        )
    except (OSError, ValueError, RealProjectDogfoodError) as exc:
        print(f"A13 Nova dogfood FAILED: {exc}")
        return 1

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report.get("passed") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
