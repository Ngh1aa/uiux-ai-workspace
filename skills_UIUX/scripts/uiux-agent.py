#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.agent import ProviderNeutralAgentHarness
from runtime.manager import DevelopmentManagerAgent
from runtime.provider import create_provider
from runtime.provider_runner import ProviderManagedRunner


def _managed_overrides(args: argparse.Namespace) -> dict[str, object]:
    return {
        "intent": args.intent,
        "website_type": args.website_type,
        "mode": args.mode,
        "risk": args.risk,
        "features": args.feature,
        "approval_mode": args.approval_mode,
    }


def _actions_from_plan(path: str | None) -> list[dict[str, object]]:
    if not path:
        return []
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return list(payload.get("actions", []))


def main() -> int:
    parser = argparse.ArgumentParser(description="Provider-neutral skills_UIUX agent harness")
    parser.add_argument("--project", required=True)
    parser.add_argument("--task", default="UIUX task")
    parser.add_argument("--agent", choices=["development", "research", "implementation", "qa"], default="research")
    parser.add_argument("--authority", choices=["read_only", "branch_write", "external_write", "release"], default="read_only")
    parser.add_argument("--skill", action="append", default=[])
    parser.add_argument("--exclude-skill", action="append", default=[])
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--plan", help="Legacy/manual JSON file containing an actions array")
    parser.add_argument("--run-id")
    parser.add_argument("--resume")
    parser.add_argument("--dry-run", action="store_true")

    parser.add_argument("--managed", action="store_true", help="Use the Development Manager declarative Flow OS")
    parser.add_argument("--managed-run-id", help="Resume an existing managed website run")
    parser.add_argument("--intent", choices=["build", "redesign", "rebuild"], help="Optional override; otherwise inferred from --task")
    parser.add_argument("--website-type", help="Optional override; otherwise inferred from --task")
    parser.add_argument("--mode", choices=["visual-prototype", "interactive-prototype", "production-candidate", "production"], help="Optional override; otherwise inferred from --task")
    parser.add_argument("--risk", help="Optional override; otherwise inferred from --task")
    parser.add_argument("--feature", action="append", default=[], help="Optional feature override(s); otherwise inferred from --task")
    parser.add_argument("--approval-mode", choices=["auto", "manual"], default="auto", help="Require explicit human approval for human-marked gates when set to manual")
    parser.add_argument("--approve-gate", help="Approve a human gate on the active managed stage")
    parser.add_argument("--stage", help="Start or complete a resolved specialist stage; defaults to active stage")
    parser.add_argument("--complete-stage", action="store_true", help="Mark the selected/active managed stage gate as complete and advance")
    parser.add_argument("--advance-on-success", action="store_true", help="After a successfully executed legacy managed stage plan, mark it complete and advance")
    parser.add_argument("--replan-signal")
    parser.add_argument("--current-stage")
    parser.add_argument("--replan-count", type=int, help="Override persisted replan count for diagnostics")
    parser.add_argument("--no-apply-replan", action="store_true", help="Return a replan decision without mutating the managed run")

    parser.add_argument("--provider", choices=["auto", "openai", "anthropic", "command"], help="Run active managed stages automatically with a model provider")
    parser.add_argument("--model", help="Provider model override; otherwise provider/env default is used")
    parser.add_argument("--provider-command", help="Command adapter executable; receives JSON on stdin and returns stage JSON on stdout")
    parser.add_argument("--max-provider-cycles", type=int, default=16, help="Maximum managed stage/replan cycles per invocation")
    parser.add_argument("--max-provider-turns", type=int, default=12, help="Maximum model→tool→observation turns per stage")
    parser.add_argument("--no-auto-replan", action="store_true", help="Stop on provider FAIL/BLOCKED/tool failure instead of applying declarative replanning")
    args = parser.parse_args()

    harness = ProviderNeutralAgentHarness(ROOT, Path(args.project))

    if args.managed or args.managed_run_id:
        manager = DevelopmentManagerAgent(harness)
        if args.managed_run_id:
            managed = manager.resume(args.managed_run_id)
        else:
            managed = manager.start_from_goal(
                args.task,
                authority=args.authority,
                overrides=_managed_overrides(args),
                additional_skills=args.skill,
                exclude_skills=args.exclude_skill,
            )

        approved_gate: str | None = None
        if args.approve_gate:
            manager.approve_gate(managed, args.approve_gate)
            approved_gate = args.approve_gate
            manager.complete_stage(managed)

        if args.replan_signal:
            decision = manager.replan(
                managed,
                signal=args.replan_signal,
                current_stage=args.current_stage,
                replan_count=args.replan_count,
                apply=not args.no_apply_replan,
            )
            print(json.dumps({"managed": managed.to_dict(), "replan": decision.to_dict()}, ensure_ascii=False, indent=2))
            return 0 if decision.accepted else 2

        if args.complete_stage:
            next_stage = manager.complete_stage(managed, args.stage)
            print(json.dumps({"managed": managed.to_dict(), "next_stage": next_stage}, ensure_ascii=False, indent=2))
            return 0

        if args.provider:
            provider = create_provider(args.provider, model=args.model, command=args.provider_command)
            runner = ProviderManagedRunner(manager, provider)
            result = runner.run_to_boundary(
                managed,
                max_cycles=args.max_provider_cycles,
                max_turns_per_stage=args.max_provider_turns,
                auto_replan=not args.no_auto_replan,
                dry_run=args.dry_run,
            )
            output: dict[str, object] = {"managed": managed.to_dict(), "provider_run": result.to_dict()}
            if approved_gate:
                output["approved_gate"] = approved_gate
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return 0 if result.state in {"COMPLETED", "AWAITING_APPROVAL", "READY", "RUNNING", "REPLANNED"} else 2

        if approved_gate:
            print(json.dumps({"managed": managed.to_dict(), "approved_gate": approved_gate}, ensure_ascii=False, indent=2))
            return 0

        if not args.stage and not args.plan:
            print(json.dumps(managed.to_dict(), ensure_ascii=False, indent=2))
            return 0

        state = manager.start_stage(managed, args.stage, explicit_sources=args.source)
        state = harness.execute_plan(state, _actions_from_plan(args.plan), dry_run=args.dry_run)
        if state.state == "COMPLETED" and args.advance_on_success:
            manager.complete_stage(managed, state.context.get("stage_id"))
        print(json.dumps({"managed": managed.to_dict(), "stage_state": state.to_dict()}, ensure_ascii=False, indent=2))
        return 0 if state.state == "COMPLETED" else 2

    if args.resume:
        state = harness.resume(args.resume)
    else:
        state = harness.create_run(
            args.task,
            args.agent,
            args.authority,
            selected_skills=args.skill,
            explicit_sources=args.source,
            run_id=args.run_id,
        )
    state = harness.execute_plan(state, _actions_from_plan(args.plan), dry_run=args.dry_run)
    print(json.dumps(state.to_dict(), ensure_ascii=False, indent=2))
    return 0 if state.state == "COMPLETED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
