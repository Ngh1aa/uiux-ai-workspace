import asyncio
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )


from core.agents.frontend_engineer import (
    FrontendEngineer,
)
from core.agents.visual_composer import (
    VisualComposer,
)
from core.contracts.frontend_result_schema import (
    FrontendResult,
)
from core.contracts.visual_composition_schema import (
    VisualComposition,
)


def latest_run_with_inputs() -> Path:
    runs_root = ROOT / "runs"

    candidates = sorted(
        [
            path
            for path
            in runs_root.iterdir()
            if path.is_dir()
        ],
        key=lambda path: (
            path.stat().st_mtime
        ),
        reverse=True,
    )

    for run_dir in candidates:
        required = [
            run_dir
            / "design-contract.json",
            run_dir
            / "design-system.json",
            run_dir
            / "implementation-plan.json",
        ]

        if all(
            path.exists()
            for path in required
        ):
            return run_dir

    raise RuntimeError(
        "No run with required frontend inputs found."
    )


async def ensure_visual_composition(
    run_dir: Path,
) -> Path:
    path = (
        run_dir
        / "visual-composition.json"
    )

    if path.exists():
        return path

    payload = {
        "design_contract_content": (
            run_dir
            / "design-contract.json"
        ).read_text(
            encoding="utf-8"
        ),
        "design_system_content": (
            run_dir
            / "design-system.json"
        ).read_text(
            encoding="utf-8"
        ),
        "implementation_plan_content": (
            run_dir
            / "implementation-plan.json"
        ).read_text(
            encoding="utf-8"
        ),
    }

    result = await VisualComposer().run(
        json.dumps(
            payload,
            ensure_ascii=False,
        )
    )

    composition = (
        VisualComposition
        .model_validate_json(
            result.content
        )
    )

    path.write_text(
        composition.model_dump_json(
            indent=2
        ),
        encoding="utf-8",
    )

    return path


async def main():
    run_dir = latest_run_with_inputs()

    visual_path = (
        await ensure_visual_composition(
            run_dir
        )
    )

    payload = {
        "factory_root": str(ROOT),
        "design_contract_content": (
            run_dir
            / "design-contract.json"
        ).read_text(
            encoding="utf-8"
        ),
        "design_system_content": (
            run_dir
            / "design-system.json"
        ).read_text(
            encoding="utf-8"
        ),
        "implementation_plan_content": (
            run_dir
            / "implementation-plan.json"
        ).read_text(
            encoding="utf-8"
        ),
        "visual_composition_content": (
            visual_path.read_text(
                encoding="utf-8"
            )
        ),
    }

    print()
    print("=" * 64)
    print(
        "UIUX FACTORY - FRONTEND ENGINEER V2"
    )
    print("=" * 64)

    result = await FrontendEngineer().run(
        json.dumps(
            payload,
            ensure_ascii=False,
        )
    )

    frontend = (
        FrontendResult
        .model_validate_json(
            result.content
        )
    )

    print()
    print(
        "[FrontendEngineerV2] COMPLETED"
    )
    print(
        f"[Project] {frontend.project_slug}"
    )
    print(
        "[GitHub Pages] "
        f"{frontend.github_pages_entry}"
    )
    print(
        f"[Skills Used] "
        f"{len(frontend.skills_used)}"
    )
    print(
        f"[Policy Checks] "
        f"{frontend.policy_checks}"
    )
    print(
        "[Visual Composition] "
        f"{frontend.gates.visual_composition_consumed}"
    )
    print(
        "[Required Skills] "
        f"{frontend.gates.required_skills_loaded}"
    )
    print(
        "[Semantic HTML] "
        f"{frontend.gates.semantic_html_passed}"
    )
    print(
        "[Responsive] "
        f"{frontend.gates.responsive_contract_passed}"
    )
    print(
        "[Focus] "
        f"{frontend.gates.focus_contract_passed}"
    )
    print(
        "[Build Verified] "
        f"{frontend.gates.build_verified}"
    )
    print()
    print("=" * 64)


if __name__ == "__main__":
    asyncio.run(
        main()
    )
