import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )


from core.agents.browser_qa_agent import BrowserQAAgent
from core.agents.visual_critic import VisualCritic
from core.contracts.browser_qa_schema import BrowserQAResult
from core.contracts.visual_critic_schema import VisualCriticResult


def latest_repair_result() -> Path:
    reports = sorted(
        ROOT.glob(
            "runs/**/repair-result.json"
        ),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not reports:
        raise RuntimeError(
            "No repair-result.json found."
        )

    return reports[0]


async def main():
    repair_path = latest_repair_result()

    repair_payload = json.loads(
        repair_path.read_text(
            encoding="utf-8"
        )
    )

    project_dir = Path(
        repair_payload["project_dir"]
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )

    regression_dir = (
        ROOT
        / "runs"
        / f"regression-{timestamp}"
    )

    print()
    print("=" * 68)
    print("UIUX FACTORY - FINAL REGRESSION LOOP")
    print("=" * 68)

    browser_message = await BrowserQAAgent().run(
        json.dumps(
            {
                "project_dir": str(
                    project_dir
                ),
                "project_slug": (
                    repair_payload[
                        "project_slug"
                    ]
                ),
                "output_dir": str(
                    regression_dir
                ),
            },
            ensure_ascii=False,
        )
    )

    qa = BrowserQAResult.model_validate_json(
        browser_message.content
    )

    browser_report = (
        regression_dir
        / "browser-report.json"
    )

    browser_report.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    browser_report.write_text(
        qa.model_dump_json(
            indent=2
        ),
        encoding="utf-8",
    )

    critic_message = await VisualCritic().run(
        json.dumps(
            {
                "browser_report_path": str(
                    browser_report
                )
            },
            ensure_ascii=False,
        )
    )

    critic = VisualCriticResult.model_validate_json(
        critic_message.content
    )

    critic_path = (
        regression_dir
        / "visual-critic.json"
    )

    critic_path.write_text(
        critic.model_dump_json(
            indent=2
        ),
        encoding="utf-8",
    )

    print()
    print(
        f"[Browser QA] {qa.status}"
    )
    print(
        "[Ready for VisualCritic] "
        f"{qa.gates.ready_for_visual_critic}"
    )
    print(
        f"[Visual Critic] {critic.status}"
    )
    print(
        f"[Overall Score] {critic.score.overall}"
    )
    print(
        f"[Issues] {len(critic.issues)}"
    )
    print(
        "[Repair Again] "
        f"{critic.gates.ready_for_repair_agent}"
    )
    print(
        f"[Regression Dir] {regression_dir}"
    )
    print()
    print("=" * 68)


if __name__ == "__main__":
    asyncio.run(main())
