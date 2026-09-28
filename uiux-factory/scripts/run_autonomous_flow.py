from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FACTORY_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = FACTORY_ROOT.parent
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from core.runtime.flow_os.autonomous import AutonomousFlowRunner
from core.runtime.flow_os.provider import create_provider
from core.runtime.flow_os.resilience import RunRecoveryController


def _goal(args: argparse.Namespace) -> str | None:
    if args.goal and args.goal_file:
        raise ValueError("provide either --goal or --goal-file, not both")
    if args.goal_file:
        value = Path(args.goal_file).read_text(encoding="utf-8-sig").strip()
        if not value:
            raise ValueError("--goal-file is empty")
        return value
    value = str(args.goal or "").strip()
    return value or None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the canonical provider-neutral Flow Agent OS from one natural-language goal. "
            "Writes stay in an isolated Git worktree; merge/deploy/release are never automatic."
        )
    )
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--goal")
    parser.add_argument("--goal-file")
    parser.add_argument("--resume-run-id")
    parser.add_argument(
        "--recover-snapshot",
        help=(
            "Explicitly restore this hash-verified manager snapshot before resuming. "
            "Any recorded isolated worktree is rolled back first."
        ),
    )
    parser.add_argument("--source", action="append", default=None)
    parser.add_argument(
        "--authority",
        choices=["read_only", "branch_write"],
        default="branch_write",
    )
    parser.add_argument(
        "--provider",
        choices=["auto", "openai", "anthropic", "command"],
        default="auto",
    )
    parser.add_argument("--model")
    parser.add_argument("--provider-command")
    parser.add_argument("--max-cycles", type=int, default=16)
    parser.add_argument("--max-turns-per-stage", type=int, default=12)
    parser.add_argument("--no-auto-replan", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    goal = _goal(args)
    if bool(goal) == bool(args.resume_run_id):
        raise ValueError("provide exactly one of a goal or --resume-run-id")
    if args.recover_snapshot and not args.resume_run_id:
        raise ValueError("--recover-snapshot requires --resume-run-id")
    if args.max_cycles < 1 or args.max_cycles > 64:
        raise ValueError("--max-cycles must be between 1 and 64")
    if args.max_turns_per_stage < 1 or args.max_turns_per_stage > 64:
        raise ValueError("--max-turns-per-stage must be between 1 and 64")

    project_root = args.project_root.resolve()
    if args.recover_snapshot:
        recovery = RunRecoveryController(project_root).recover(
            args.resume_run_id,
            args.recover_snapshot,
            rollback_workspace=True,
        )
        print(json.dumps({"recovery": recovery}, indent=2, ensure_ascii=False))

    provider = create_provider(
        args.provider,
        model=args.model,
        command=args.provider_command,
    )
    runner = AutonomousFlowRunner(
        skills_root=REPO_ROOT / "skills_UIUX",
        project_root=project_root,
        provider=provider,
    )
    if goal is not None:
        result = runner.start(
            goal,
            authority=args.authority,
            explicit_sources=args.source,
            max_cycles=args.max_cycles,
            max_turns_per_stage=args.max_turns_per_stage,
            auto_replan=not args.no_auto_replan,
            dry_run=args.dry_run,
        )
    else:
        result = runner.resume(
            args.resume_run_id,
            explicit_sources=args.source,
            max_cycles=args.max_cycles,
            max_turns_per_stage=args.max_turns_per_stage,
            auto_replan=not args.no_auto_replan,
            dry_run=args.dry_run,
        )

    payload = result.to_dict()
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    print(text)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text + "\n", encoding="utf-8")
    return 0 if result.state in {"COMPLETED", "AWAITING_APPROVAL"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
