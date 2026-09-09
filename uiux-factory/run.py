import argparse
import asyncio
import json
import os
from pathlib import Path

from core.manager.visual_brain_manager import VisualBrainDevelopmentManager
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
    goal: str,
    context_path: str | None = None,
    run_id: str | None = None,
    intelligence_only: bool = False,
    engine: str = "template",
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
        manager = VisualBrainDevelopmentManager(root=ROOT)

        from core.contracts.design_context_schema import DesignContext

        design_context = (
            DesignContext.model_validate(
                json.loads(Path(context_path).read_text(encoding="utf-8-sig"))
            )
            if context_path
            else DesignContext()
        )
        run_context = await manager.run(
            goal,
            design_context,
            run_id,
            intelligence_only,
            engine,
        )

        print()
        print("=" * 64)
        print(f"[Run] {run_context.run_id}")
        print(f"[Status] {run_context.status.upper()}")
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
    args = parser.parse_args()

    resolved_goal = _resolve_goal(args.goal, args.goal_file)

    asyncio.run(
        main(
            resolved_goal,
            args.context,
            args.run_id,
            args.intelligence_only,
            args.engine,
        )
    )
