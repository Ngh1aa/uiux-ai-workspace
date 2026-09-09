import asyncio
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from core.agents.design_contract_agent import (
    DesignContractAgent,
)

from core.contracts.schema import (
    DesignContract,
)


def latest_run_with_artifacts() -> Path:
    candidates = sorted(
        [
            path
            for path in (ROOT / "runs").iterdir()
            if path.is_dir()
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    for run_dir in candidates:
        required = [
            run_dir / "research.md",
            run_dir / "ux-ia.md",
            run_dir / "art-direction.md",
        ]

        if all(path.exists() for path in required):
            return run_dir

    raise RuntimeError(
        "No completed run with research, "
        "ux-ia and art-direction artifacts found."
    )


async def main():
    run_dir = latest_run_with_artifacts()

    research_path = run_dir / "research.md"
    ux_path = run_dir / "ux-ia.md"
    art_path = run_dir / "art-direction.md"

    payload = {
        "goal": (
            "Thiết kế website ecommerce hiện đại "
            "sang trọng thân thiện màu tím"
        ),
        "artifacts": {
            "research": {
                "path": str(research_path),
                "content": research_path.read_text(
                    encoding="utf-8"
                ),
            },
            "ux_ia": {
                "path": str(ux_path),
                "content": ux_path.read_text(
                    encoding="utf-8"
                ),
            },
            "art_direction": {
                "path": str(art_path),
                "content": art_path.read_text(
                    encoding="utf-8"
                ),
            },
        },
    }

    print()
    print("=" * 60)
    print("UIUX FACTORY - DESIGN CONTRACT")
    print("=" * 60)

    agent = DesignContractAgent()

    result = await agent.run(
        json.dumps(
            payload,
            ensure_ascii=False,
        )
    )

    if not result:
        raise RuntimeError(
            "DesignContractAgent returned no result."
        )

    contract = DesignContract.model_validate_json(
        result.content
    )

    print(
        "\n[DesignContractAgent] COMPLETED"
    )

    print(
        f"[Schema] {contract.schema_version}"
    )

    print(
        f"[Status] {contract.status}"
    )

    print(
        f"[Domain] {contract.project.domain}"
    )

    print(
        f"[Primary Color] "
        f"{contract.project.requested_primary_color}"
    )

    print(
        f"[Pages] {len(contract.ux.page_roles)}"
    )

    print(
        f"[Visual Rules] "
        f"{len(contract.visual.layout_rules)}"
    )

    print(
        f"[Sources] {len(contract.sources)}"
    )

    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())