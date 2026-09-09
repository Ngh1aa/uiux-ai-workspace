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
from core.contracts.browser_qa_schema import BrowserQAResult


def latest_generated_project() -> Path:
    generated_root = ROOT / "generated"

    candidates = sorted(
        [
            path
            for path in generated_root.iterdir()
            if (
                path.is_dir()
                and (path / "index.html").exists()
            )
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not candidates:
        raise RuntimeError(
            "No generated project with root index.html found."
        )

    return candidates[0]


async def main():
    project_dir = latest_generated_project()

    timestamp = datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )

    output_dir = (
        ROOT
        / "runs"
        / f"browserqa-{timestamp}"
    )

    print()
    print("=" * 68)
    print("UIUX FACTORY - BROWSER QA / PLAYWRIGHT")
    print("=" * 68)

    result = await BrowserQAAgent().run(
        json.dumps(
            {
                "project_dir": str(project_dir),
                "project_slug": project_dir.name,
                "output_dir": str(output_dir),
            },
            ensure_ascii=False,
        )
    )

    qa = BrowserQAResult.model_validate_json(
        result.content
    )

    report_path = (
        output_dir
        / "browser-report.json"
    )

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path.write_text(
        qa.model_dump_json(
            indent=2
        ),
        encoding="utf-8",
    )

    print()
    print(f"[Status] {qa.status}")
    print(f"[Project] {qa.project_slug}")
    print(f"[Routes] {len(qa.routes)}")
    print(f"[Viewports] {len(qa.viewports)}")
    print(
        "[Screenshots] "
        f"{qa.summary.get('screenshots', 0)}"
    )
    print(
        "[Console Errors] "
        f"{qa.summary.get('console_error_count', 0)}"
    )
    print(
        "[Page Errors] "
        f"{qa.summary.get('page_error_count', 0)}"
    )
    print(
        "[Overflow] "
        f"{qa.summary.get('overflow_count', 0)}"
    )
    print(
        "[Broken Links] "
        f"{qa.summary.get('broken_link_count', 0)}"
    )
    print(
        "[Ready for VisualCritic] "
        f"{qa.gates.ready_for_visual_critic}"
    )
    print(f"[Report] {report_path}")
    print()
    print("=" * 68)


if __name__ == "__main__":
    asyncio.run(main())
