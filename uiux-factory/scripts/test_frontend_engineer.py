import asyncio
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from core.agents.frontend_engineer import FrontendEngineer
from core.contracts.frontend_result_schema import FrontendResult


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
        "factory_root": str(ROOT),
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
    print("UIUX FACTORY - FRONTEND ENGINEER")
    print("=" * 60)

    result = await FrontendEngineer().run(
        json.dumps(
            payload,
            ensure_ascii=False,
        )
    )

    frontend = FrontendResult.model_validate_json(
        result.content
    )

    print(
        "\n[FrontendEngineer] COMPLETED"
    )
    print(
        f"[Project] {frontend.project_slug}"
    )
    print(
        f"[Project Dir] {frontend.project_dir}"
    )
    print(
        f"[GitHub Pages index] "
        f"{frontend.github_pages_entry}"
    )
    print(
        f"[Next App] {frontend.next_app_dir}"
    )
    print(
        f"[Files] {len(frontend.files)}"
    )
    print(
        f"[Guardrail] "
        f"{frontend.gates.workspace_guardrail_passed}"
    )
    print(
        f"[Root index] "
        f"{frontend.gates.root_index_created}"
    )
    print(
        f"[Next source] "
        f"{frontend.gates.next_source_created}"
    )
    print(
        f"[Build verified] "
        f"{frontend.gates.build_verified}"
    )
    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
