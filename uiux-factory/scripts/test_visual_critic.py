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


from core.agents.visual_critic import VisualCritic
from core.contracts.visual_critic_schema import (
    VisualCriticResult,
)


def latest_browser_report() -> Path:
    reports = sorted(
        ROOT.glob(
            "runs/**/browser-report.json"
        ),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not reports:
        raise RuntimeError(
            "No browser-report.json found. "
            "Run BrowserQA first."
        )

    return reports[0]


async def main():
    report_path = latest_browser_report()

    print()
    print("=" * 68)
    print("UIUX FACTORY - VISUAL CRITIC")
    print("=" * 68)

    result = await VisualCritic().run(
        json.dumps(
            {
                "browser_report_path": str(
                    report_path
                )
            },
            ensure_ascii=False,
        )
    )

    critic = (
        VisualCriticResult
        .model_validate_json(
            result.content
        )
    )

    output_path = (
        report_path.parent
        / "visual-critic.json"
    )

    output_path.write_text(
        critic.model_dump_json(
            indent=2
        ),
        encoding="utf-8",
    )

    print()
    print(f"[Status] {critic.status}")
    print(
        f"[Overall] {critic.score.overall}"
    )
    print(
        f"[Visual] {critic.score.visual}"
    )
    print(
        f"[Hierarchy] {critic.score.hierarchy}"
    )
    print(
        f"[Typography] {critic.score.typography}"
    )
    print(
        f"[Spacing] {critic.score.spacing}"
    )
    print(
        f"[Responsive] {critic.score.responsive}"
    )
    print(
        "[Brand Fidelity] "
        f"{critic.score.brand_fidelity}"
    )
    print(
        "[Accessibility] "
        f"{critic.score.accessibility}"
    )
    print(
        "[Generic AI Feel] "
        f"{critic.score.generic_ai_feel}"
    )
    print(
        f"[Issues] {len(critic.issues)}"
    )
    print(
        "[Repair Directives] "
        f"{len(critic.repair_directives)}"
    )
    print(
        "[Ready for RepairAgent] "
        f"{critic.gates.ready_for_repair_agent}"
    )
    print(f"[Artifact] {output_path}")
    print()
    print("=" * 68)


if __name__ == "__main__":
    asyncio.run(main())
