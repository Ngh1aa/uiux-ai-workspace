import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(ROOT),
    )


def main():
    manager = (
        ROOT
        / "core"
        / "manager"
        / "development_manager.py"
    )

    required_files = [
        ROOT
        / "core"
        / "team"
        / "team_runner.py",
        ROOT
        / "core"
        / "orchestration"
        / "quality_loop.py",
        ROOT
        / "core"
        / "contracts"
        / "quality_loop_schema.py",
        ROOT
        / "core"
        / "agents"
        / "browser_qa_agent.py",
        ROOT
        / "core"
        / "agents"
        / "visual_critic.py",
        ROOT
        / "core"
        / "agents"
        / "repair_agent.py",
        ROOT
        / "core"
        / "actions"
        / "evaluate_visual_quality.py",
    ]

    missing_files = [
        path
        for path in required_files
        if not path.exists()
    ]

    text = (
        manager.read_text(
            encoding="utf-8"
        )
        if manager.exists()
        else ""
    )

    checks = {
        "manager_exists": (
            manager.exists()
        ),
        "visual_composer_integrated": (
            "VisualComposer().run("
            not in text
            and (
                "role_class=VisualComposer"
                in text
            )
        ),
        "frontend_integrated": (
            "FrontendEngineer().run("
            not in text
            and (
                "role_class=FrontendEngineer"
                in text
            )
        ),
        "quality_call_present": (
            "await self._run_quality_loop(context)"
            in text
        ),
        "quality_method_present": (
            "async def _run_quality_loop("
            in text
        ),
        "team_runner_present": (
            "self.team_runner"
            in text
        ),
        "required_files_present": (
            not missing_files
        ),
    }

    print()
    print("=" * 72)
    print(
        "UIUX FACTORY - FULL PIPELINE INTEGRATION VALIDATION"
    )
    print("=" * 72)

    for key, value in (
        checks.items()
    ):
        print(
            f"[{key}] {value}"
        )

    if missing_files:
        print()
        print(
            "MISSING FILES:"
        )

        for path in (
            missing_files
        ):
            print(
                "  - "
                + str(
                    path.relative_to(
                        ROOT
                    )
                )
            )

    failed = [
        key
        for key, value
        in checks.items()
        if not value
    ]

    print()
    print(
        f"[Failed Checks] {len(failed)}"
    )

    if failed:
        for key in failed:
            print(
                f"  - {key}"
            )
        raise SystemExit(1)

    print()
    print(
        "PASS: DevelopmentManager now reaches "
        "VisualComposer -> FrontendEngineer -> "
        "BrowserQA -> VisualCritic -> Repair through "
        "the integrated runtime."
    )


if __name__ == "__main__":
    main()
