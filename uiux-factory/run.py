import argparse
import asyncio
import json
from pathlib import Path

from core.manager.development_manager import (
    DevelopmentManager,
)


ROOT = Path(__file__).resolve().parent


async def main(goal: str, context_path: str | None = None, run_id: str | None = None,
               intelligence_only: bool = False, engine: str = "template") -> None:
    print()
    print("=" * 64)
    print("UIUX FACTORY")
    print("=" * 64)

    manager = DevelopmentManager(
        root=ROOT
    )

    from core.contracts.design_context_schema import DesignContext
    design_context = DesignContext.model_validate(json.loads(Path(context_path).read_text(encoding="utf-8-sig"))) if context_path else DesignContext()
    run_context = await manager.run(goal, design_context, run_id, intelligence_only, engine)

    print()
    print("=" * 64)

    print(
        f"[Run] {run_context.run_id}"
    )

    print(
        f"[Status] {run_context.status.upper()}"
    )

    print(
        "[Completed Stages] "
        + ", ".join(
            run_context.completed_stages
        )
    )

    print(
        f"[Run State] "
        f"{run_context.state_path}"
    )

    print("=" * 64)
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UIUX Factory"
    )

    parser.add_argument(
        "goal",
        type=str,
        help="Natural language product goal",
    )

    parser.add_argument("--context", help="Path to a V3 design-context JSON file")
    parser.add_argument("--run-id", help="Stable job/run ID used by the Workbench bridge")
    parser.add_argument("--intelligence-only", action="store_true", help="Analyze references and build design-system.json before frontend generation")
    parser.add_argument("--engine", choices=["template", "ai"], default="template", help="AI cloud generates custom static pages; requires explicit free-tier configuration")
    args = parser.parse_args()

    asyncio.run(
        main(args.goal, args.context, args.run_id, args.intelligence_only, args.engine)
    )
