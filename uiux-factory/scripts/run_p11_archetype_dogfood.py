from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


FACTORY_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = FACTORY_ROOT.parent
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from core.dogfood.archetype_matrix import (  # noqa: E402
    ArchetypeDogfoodError,
    evaluate_project,
    project_ids,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run P1.1 real-task archetype dogfood")
    parser.add_argument("--project-id", choices=project_ids(), required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--expected-target-sha", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    policy_path = REPO_ROOT / "skills_UIUX" / "runtime" / "runtime-policy.json"
    policy_doc = json.loads(policy_path.read_text(encoding="utf-8"))

    try:
        report = evaluate_project(
            skills_root=REPO_ROOT / "skills_UIUX",
            policy_doc=policy_doc,
            project_root=args.project_root,
            project_id=args.project_id,
            expected_target_sha=args.expected_target_sha,
        )
    except (OSError, ValueError, ArchetypeDogfoodError, json.JSONDecodeError) as exc:
        print(f"P1.1 {args.project_id} archetype dogfood FAILED: {exc}")
        return 1

    output = Path(args.report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report.get("passed") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
