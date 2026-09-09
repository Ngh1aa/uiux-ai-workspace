import argparse
import asyncio
import json
import os
from pathlib import Path

from core.contracts.creative_review_schema import CreativeDirective
from core.manager.creative_director_manager import CreativeDirectorDevelopmentManager
from core.runtime.run_lock import RunLock


ROOT = Path(__file__).resolve().parent


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as error:
        raise ValueError(f"{name} must be a number, got {raw!r}") from error


def _resolve_goal(goal: str | None, goal_file: str | None) -> str:
    if goal and goal_file:
        raise ValueError("Provide either goal or --goal-file, not both.")
    if goal_file:
        resolved = Path(goal_file).read_text(encoding="utf-8-sig").strip()
    else:
        resolved = (goal or "").strip()
    if not resolved:
        raise ValueError("A non-empty product goal is required.")
    return resolved


async def main(
    goal: str | None,
    context_path: str | None = None,
    run_id: str | None = None,
    intelligence_only: bool = False,
    engine: str = "template",
    source_run_id: str | None = None,
    creative_directive_path: str | None = None,
    runtime_preset: str | None = None,
) -> None:
    print()
    print("=" * 64)
    print("UIUX FACTORY")
    print("=" * 64)

    lock = RunLock(
        ROOT,
        timeout_seconds=_env_float("UIUX_RUN_LOCK_TIMEOUT_SECONDS", 7200.0),
        stale_seconds=_env_float("UIUX_RUN_LOCK_STALE_SECONDS", 14400.0),
    )

    print("[Queue] Waiting for local Factory run slot...")
    lock.acquire()
    print("[Queue] Factory run slot acquired.")

    try:
        manager = CreativeDirectorDevelopmentManager(root=ROOT)

        if source_run_id or creative_directive_path:
            if not (source_run_id and creative_directive_path and run_id):
                raise ValueError(
                    "Creative review revision requires --source-run-id, --creative-directive and --run-id."
                )
            if runtime_preset:
                raise ValueError(
                    "Creative review revisions inherit the source run runtime preset; "
                    "do not supply --runtime-preset."
                )
            directive = CreativeDirective.model_validate_json(
                Path(creative_directive_path).read_text(encoding="utf-8-sig")
            )
            run_context = await manager.run_revision(
                source_run_id=source_run_id,
                directive=directive,
                run_id=run_id,
                engine=engine,
            )
        else:
            from core.contracts.design_context_schema import DesignContext

            resolved_goal = _resolve_goal(goal, None)
            design_context = (
                DesignContext.model_validate(
                    json.loads(Path(context_path).read_text(encoding="utf-8-sig"))
                )
                if context_path
                else DesignContext()
            )
            run_context = await manager.run(
                resolved_goal,
                design_context,
                run_id,
                intelligence_only,
                engine,
                runtime_preset or "standard",
            )

        print()
        print("=" * 64)
        print(f"[Run] {run_context.run_id}")
        print(f"[Status] {run_context.status.upper()}")
        print(f"[Runtime Preset] {run_context.runtime_preset}")
        print("[Completed Stages] " + ", ".join(run_context.completed_stages))
        print(f"[Run State] {run_context.state_path}")
        print("=" * 64)
        print()
    finally:
        lock.release()
        print("[Queue] Factory run slot released.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UIUX Factory")

    parser.add_argument(
        "goal",
        nargs="?",
        help="Natural language product goal",
    )
    parser.add_argument(
        "--goal-file",
        help="Read the natural language product goal from a UTF-8 text file",
    )
    parser.add_argument(
        "--context",
        help="Path to a V3 design-context JSON file",
    )
    parser.add_argument(
        "--run-id",
        help="Stable job/run ID used by the Workbench bridge",
    )
    parser.add_argument(
        "--intelligence-only",
        action="store_true",
        help="Analyze references and build design-system.json before frontend generation",
    )
    parser.add_argument(
        "--engine",
        choices=["template", "ai"],
        default="template",
        help="AI cloud generates custom static pages; requires explicit free-tier configuration",
    )
    parser.add_argument(
        "--runtime-preset",
        help=(
            "Per-run plugin/tool/skill composition. Shipped presets: standard, "
            "visual-first, research-heavy, creator. User presets may be created with creator.py."
        ),
    )
    parser.add_argument(
        "--source-run-id",
        help="Completed source run to revise from an imported creative review",
    )
    parser.add_argument(
        "--creative-directive",
        help="Path to a CreativeDirective JSON file used for stage-aware revision",
    )
    args = parser.parse_args()

    if args.source_run_id or args.creative_directive:
        resolved_goal = None
        if args.goal or args.goal_file:
            raise ValueError("Creative review revision resumes the source goal; do not provide a new goal.")
    else:
        resolved_goal = _resolve_goal(args.goal, args.goal_file)

    asyncio.run(
        main(
            resolved_goal,
            args.context,
            args.run_id,
            args.intelligence_only,
            args.engine,
            args.source_run_id,
            args.creative_directive,
            args.runtime_preset,
        )
    )
