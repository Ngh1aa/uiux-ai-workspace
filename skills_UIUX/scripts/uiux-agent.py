#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTORY_ROOT = ROOT.parent / "uiux-factory"
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.browser_evidence import PlaywrightBrowserEvidenceAdapter
from core.runtime.flow_os.managed import ManagedFlowController, ManagedWebsiteRun
from core.runtime.flow_os.provider import create_provider
from core.runtime.flow_os.provider_routing import StageProviderRouter
from core.runtime.flow_os.provider_runner import ProviderManagedRunner, ProviderRunResult
from core.runtime.flow_os.release import ProductionReleaseController


def _managed_overrides(args: argparse.Namespace) -> dict[str, object]:
    return {
        "intent": args.intent,
        "change_surface": args.change_surface,
        "website_type": args.website_type,
        "domain": args.domain,
        "product_archetype": args.product_archetype,
        "validation_lane": args.validation_lane,
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


def _active_stage(managed: ManagedWebsiteRun):
    return next(stage for stage in managed.flow.stages if stage.id == managed.active_stage)


def _persist_provider_route(
    harness: ProviderNeutralAgentHarness,
    managed: ManagedWebsiteRun,
    record: dict[str, object],
) -> None:
    manager_state = harness.resume(managed.manager_run_id)
    history = list(manager_state.context.get("provider_routing_history", []))
    history.append(dict(record))
    manager_state.context["provider_routing_history"] = history[-64:]
    manager_state.context["provider_route_last"] = dict(record)
    harness.checkpoints.save(manager_state.run_id, manager_state.to_dict())

    stage_runs = managed.stage_runs.get(str(record.get("stage_id", "")), [])
    if stage_runs:
        stage_state = harness.resume(stage_runs[-1])
        stage_state.context["provider_route"] = dict(record)
        harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())


def _run_provider_cycles(
    manager: ManagedFlowController,
    managed: ManagedWebsiteRun,
    args: argparse.Namespace,
) -> tuple[ProviderRunResult, list[dict[str, object]]]:
    router = StageProviderRouter(manager.harness.policy_doc)
    route_records: list[dict[str, object]] = []
    last: ProviderRunResult | None = None

    for cycle in range(1, args.max_provider_cycles + 1):
        if managed.state in {"COMPLETED", "AWAITING_APPROVAL", "BLOCKED", "FAILED"}:
            if last is None:
                last = ProviderRunResult(
                    managed.state,
                    managed.active_stage,
                    0,
                    str(args.provider or ""),
                    str(args.model or "provider-default"),
                )
            return last, route_records

        stage = _active_stage(managed)
        selection = router.resolve(
            stage_id=stage.id,
            agent=stage.agent,
            default_provider=str(args.provider or ""),
            default_model=args.model,
            requested_max_turns=args.max_provider_turns,
        )
        provider = create_provider(
            selection.provider,
            model=selection.model,
            command=args.provider_command,
        )
        route_record: dict[str, object] = selection.to_dict()
        route_record["resolved_model"] = provider.model
        route_record["cycle"] = cycle

        runner = ProviderManagedRunner(manager, provider)
        try:
            stage_result = runner.run_active_stage(
                managed,
                max_turns=selection.max_turns,
                auto_replan=not args.no_auto_replan,
                dry_run=args.dry_run,
            )
        finally:
            _persist_provider_route(manager.harness, managed, route_record)
            route_records.append(dict(route_record))

        last = ProviderRunResult(
            managed.state if managed.state == "COMPLETED" else stage_result.state,
            managed.active_stage,
            cycle,
            provider.name,
            provider.model,
            stage_result.message,
        )
        if (
            stage_result.state in {"AWAITING_APPROVAL", "BLOCKED", "FAILED", "FAIL", "DRY_RUN"}
            or managed.state == "COMPLETED"
        ):
            return last, route_records

    managed.state = "FAILED"
    manager._checkpoint_managed(managed)
    if last is None:
        last = ProviderRunResult(
            "FAILED",
            managed.active_stage,
            args.max_provider_cycles,
            str(args.provider or ""),
            str(args.model or "provider-default"),
            "managed provider cycle budget exhausted",
        )
    else:
        last = ProviderRunResult(
            "FAILED",
            managed.active_stage,
            args.max_provider_cycles,
            last.provider,
            last.model,
            "managed provider cycle budget exhausted",
        )
    return last, route_records


def main() -> int:
    parser = argparse.ArgumentParser(description="Provider-neutral UIUX Factory Flow OS harness")
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

    parser.add_argument("--managed", action="store_true", help="Use the canonical declarative Factory Flow OS")
    parser.add_argument("--managed-run-id", help="Resume an existing managed website run")
    parser.add_argument("--intent", choices=["build", "redesign", "rebuild", "improve", "fix", "polish"], help="Optional override; otherwise inferred from --task")
    parser.add_argument("--change-surface", choices=["MICRO", "FOCUSED", "PAGE", "REDESIGN", "PRODUCT"], help="Optional A3 change-size override; otherwise inferred from Task Contract scope")
    parser.add_argument("--website-type", help="Optional override; otherwise inferred from --task")
    parser.add_argument("--domain", help="Optional business-domain override, e.g. financial-services")
    parser.add_argument("--product-archetype", help="Optional product/workflow archetype override, e.g. payments-infrastructure")
    parser.add_argument("--validation-lane", choices=["prototype", "evidence-led", "production-learning"], help="Optional lifecycle rigor override; otherwise inferred from mode/risk/features")
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
    parser.add_argument("--max-provider-turns", type=int, default=12, help="Maximum model→tool→observation turns per stage and hard ceiling for routed stage budgets")
    parser.add_argument("--no-auto-replan", action="store_true", help="Stop on provider FAIL/BLOCKED/tool failure instead of applying declarative replanning")

    parser.add_argument("--browser-artifacts", help="Ingest Playwright browser-evidence artifacts below uiux-factory/qa")
    parser.add_argument("--capture-browser-evidence", action="store_true", help="Run the Playwright browser evidence test against --browser-base-url")
    parser.add_argument("--browser-base-url", help="Browser evidence target URL; localhost only by default")
    parser.add_argument("--browser-route", action="append", default=[], help="Route to capture; repeat for multiple routes")
    parser.add_argument("--finalize-worktree", action="store_true", help="Commit, fast-forward merge and optionally clean the isolated worktree; requires external_write")
    parser.add_argument("--keep-worktree", action="store_true", help="Keep the worktree after successful finalize")
    parser.add_argument("--commit-message", default="uiux-agent: finalize managed run", help="Commit message used by --finalize-worktree")
    parser.add_argument("--deploy-production", action="store_true", help="Execute the configured production deploy adapter; requires release authority")
    parser.add_argument("--confirm-production-release", help="Must equal PRODUCTION for --deploy-production")
    args = parser.parse_args()

    harness = ProviderNeutralAgentHarness(ROOT, Path(args.project))

    if args.managed or args.managed_run_id:
        manager = ManagedFlowController(harness)
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

        output: dict[str, object] = {"managed": managed.to_dict()}
        approved_gate: str | None = None
        if args.approve_gate:
            manager.approve_gate(managed, args.approve_gate)
            approved_gate = args.approve_gate
            manager.complete_stage(managed)
            output["approved_gate"] = approved_gate

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
            result, provider_routes = _run_provider_cycles(manager, managed, args)
            output["provider_run"] = result.to_dict()
            output["provider_routes"] = provider_routes
            output["managed"] = managed.to_dict()
            if result.state not in {"COMPLETED", "AWAITING_APPROVAL", "READY", "RUNNING", "REPLANNED"}:
                print(json.dumps(output, ensure_ascii=False, indent=2))
                return 2

        release = ProductionReleaseController(harness)
        if args.browser_artifacts or args.capture_browser_evidence:
            adapter = PlaywrightBrowserEvidenceAdapter(FACTORY_ROOT / "qa", harness.policy_doc)
            if args.capture_browser_evidence:
                if not args.browser_base_url or not args.browser_route:
                    raise ValueError("--capture-browser-evidence requires --browser-base-url and at least one --browser-route")
                records = adapter.capture(args.browser_base_url, args.browser_route)
            else:
                records = adapter.collect(Path(args.browser_artifacts))
            release.attach_release_evidence(managed, records)
            output["browser_evidence"] = [record.to_dict() for record in records]

        if args.finalize_worktree:
            finalized = release.finalize_workspace(
                managed,
                authority=args.authority,
                commit_message=args.commit_message,
                cleanup=not args.keep_worktree,
            )
            output["workspace_finalize"] = finalized.to_dict()

        if args.deploy_production:
            deployed = release.deploy_production(
                managed,
                authority=args.authority,
                confirmation=args.confirm_production_release or "",
            )
            output["production_deploy"] = deployed.to_dict()

        if any(
            [
                args.provider,
                approved_gate,
                args.browser_artifacts,
                args.capture_browser_evidence,
                args.finalize_worktree,
                args.deploy_production,
            ]
        ):
            output["managed"] = managed.to_dict()
            print(json.dumps(output, ensure_ascii=False, indent=2))
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
