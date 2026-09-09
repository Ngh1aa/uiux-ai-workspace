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


from core.agents.repair_agent import RepairAgent
from core.contracts.repair_result_schema import RepairResult


def latest_visual_critic() -> Path:
    reports = sorted(
        ROOT.glob(
            "runs/**/visual-critic.json"
        ),
        key=lambda path: (
            path.stat().st_mtime
        ),
        reverse=True,
    )

    if not reports:
        raise RuntimeError(
            "No visual-critic.json found."
        )

    return reports[0]


async def main():
    critic_path = latest_visual_critic()

    browser_report = (
        critic_path.parent
        / "browser-report.json"
    )

    print()
    print("=" * 68)
    print("UIUX FACTORY - REPAIR AGENT")
    print("=" * 68)

    result = await RepairAgent().run(
        json.dumps(
            {
                "visual_critic_path": str(
                    critic_path
                ),
                "browser_report_path": str(
                    browser_report
                ),
                "output_dir": str(
                    critic_path.parent
                ),
            },
            ensure_ascii=False,
        )
    )

    repair = RepairResult.model_validate_json(
        result.content
    )

    output_path = (
        critic_path.parent
        / "repair-result.json"
    )

    output_path.write_text(
        repair.model_dump_json(
            indent=2
        ),
        encoding="utf-8",
    )

    print()
    print(f"[Status] {repair.status}")
    print(
        "[Applied Directives] "
        f"{repair.applied_directives}"
    )
    print(
        "[Deferred Directives] "
        f"{repair.deferred_directives}"
    )
    print(
        "[Modified Files] "
        f"{len(repair.modified_files)}"
    )
    print(
        "[Backups] "
        f"{len(repair.backup_files)}"
    )
    print(
        "[Skills Used] "
        f"{len(repair.skills_used)}"
    )
    print(
        "[Regression Required] "
        f"{repair.gates.regression_required}"
    )
    print(
        f"[Artifact] {output_path}"
    )
    print()
    print("=" * 68)


if __name__ == "__main__":
    asyncio.run(main())
