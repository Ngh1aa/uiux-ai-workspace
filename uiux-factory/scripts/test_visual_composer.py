import asyncio
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from core.agents.visual_composer import VisualComposer
from core.contracts.visual_composition_schema import VisualComposition


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
        required = [
            run_dir / "design-contract.json",
            run_dir / "design-system.json",
            run_dir / "implementation-plan.json",
        ]

        if all(path.exists() for path in required):
            return run_dir

    raise RuntimeError(
        "No run with design-contract.json, design-system.json "
        "and implementation-plan.json found."
    )


async def main():
    run_dir = latest_run_with_inputs()

    payload = {
        "design_contract_content": (
            run_dir / "design-contract.json"
        ).read_text(encoding="utf-8"),
        "design_system_content": (
            run_dir / "design-system.json"
        ).read_text(encoding="utf-8"),
        "implementation_plan_content": (
            run_dir / "implementation-plan.json"
        ).read_text(encoding="utf-8"),
    }

    print()
    print("=" * 60)
    print("UIUX FACTORY - VISUAL COMPOSER")
    print("=" * 60)

    result = await VisualComposer().run(
        json.dumps(
            payload,
            ensure_ascii=False,
        )
    )

    composition = VisualComposition.model_validate_json(
        result.content
    )

    families = {
        page.composition_family
        for page in composition.pages
    }

    print()
    print("[VisualComposer] COMPLETED")
    print(f"[Domain] {composition.domain}")
    print(f"[Pages] {len(composition.pages)}")
    print(f"[Composition Families] {len(families)}")
    print(
        "[Mobile Rules] "
        f"{composition.gates.mobile_transformations_defined}"
    )
    print(
        "[Ready] "
        f"{composition.gates.ready_for_frontend_engineer}"
    )
    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
