import asyncio
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from core.agents.implementation_planner import (
    ImplementationPlanner,
)
from core.contracts.implementation_plan_schema import (
    ImplementationPlan,
)


def latest_run_with_inputs() -> Path:
    runs_root = ROOT / "runs"

    candidates = sorted(
        [
            path
            for path in runs_root.iterdir()
            if path.is_dir()
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    for run_dir in candidates:
        design_contract = (
            run_dir / "design-contract.json"
        )
        design_system = (
            run_dir / "design-system.json"
        )

        if (
            design_contract.exists()
            and design_system.exists()
        ):
            return run_dir

    raise RuntimeError(
        "No run with design-contract.json "
        "and design-system.json found."
    )


async def main():
    run_dir = latest_run_with_inputs()

    design_contract_path = (
        run_dir / "design-contract.json"
    )

    design_system_path = (
        run_dir / "design-system.json"
    )

    payload = {
        "design_contract_path": str(
            design_contract_path.resolve()
        ),
        "design_contract_content": (
            design_contract_path.read_text(
                encoding="utf-8"
            )
        ),
        "design_system_path": str(
            design_system_path.resolve()
        ),
        "design_system_content": (
            design_system_path.read_text(
                encoding="utf-8"
            )
        ),
    }

    print()
    print("=" * 60)
    print("UIUX FACTORY - IMPLEMENTATION PLANNER")
    print("=" * 60)

    agent = ImplementationPlanner()

    result = await agent.run(
        json.dumps(
            payload,
            ensure_ascii=False,
        )
    )

    if not result:
        raise RuntimeError(
            "ImplementationPlanner returned no result."
        )

    plan = (
        ImplementationPlan.model_validate_json(
            result.content
        )
    )

    print(
        "\n[ImplementationPlanner] COMPLETED"
    )

    print(
        f"[Project] {plan.project_slug}"
    )

    print(
        f"[Output] {plan.output_dir}"
    )

    print(
        f"[Routes] {len(plan.routes)}"
    )

    print(
        f"[Components] {len(plan.components)}"
    )

    print(
        f"[Ready] "
        f"{plan.gates.ready_for_frontend_engineer}"
    )

    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
