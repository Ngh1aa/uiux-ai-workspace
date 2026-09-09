import asyncio
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from core.agents.design_system_agent import (
    DesignSystemAgent,
)
from core.contracts.design_system_schema import (
    DesignSystemContract,
)


def latest_run_with_contract() -> Path:
    runs_root = ROOT / "runs"

    if not runs_root.exists():
        raise RuntimeError(
            "runs directory does not exist."
        )

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
        contract_path = (
            run_dir / "design-contract.json"
        )

        if contract_path.exists():
            return run_dir

    raise RuntimeError(
        "No run with design-contract.json found."
    )


async def main():
    run_dir = latest_run_with_contract()

    contract_path = (
        run_dir / "design-contract.json"
    )

    payload = {
        "design_contract_path": str(
            contract_path.resolve()
        ),
        "design_contract_content": (
            contract_path.read_text(
                encoding="utf-8"
            )
        ),
    }

    print()
    print("=" * 60)
    print("UIUX FACTORY - DESIGN SYSTEM AGENT")
    print("=" * 60)

    agent = DesignSystemAgent()

    result = await agent.run(
        json.dumps(
            payload,
            ensure_ascii=False,
        )
    )

    if not result:
        raise RuntimeError(
            "DesignSystemAgent returned no result."
        )

    system = (
        DesignSystemContract.model_validate_json(
            result.content
        )
    )

    print(
        "\n[DesignSystemAgent] COMPLETED"
    )

    print(
        f"[Status] {system.status}"
    )

    print(
        f"[Domain] {system.domain}"
    )

    print(
        f"[Components] {len(system.components)}"
    )

    print(
        f"[Patterns] {len(system.patterns)}"
    )

    print(
        f"[Relevant Skills] "
        f"{len(system.relevant_skills)}"
    )

    print(
        f"[Implementation Ready With Fallbacks] "
        f"{system.gates.implementation_ready_with_fallbacks}"
    )

    print(
        f"[Final Visual Lock] "
        f"{system.gates.final_visual_lock}"
    )

    print(
        f"[Unresolved] "
        f"{len(system.unresolved_items)}"
    )

    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
