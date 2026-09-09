import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def latest_run() -> Path:
    runs = ROOT / "runs"

    candidates = sorted(
        [
            path
            for path in runs.iterdir()
            if (
                path.is_dir()
                and (
                    path
                    / "run.json"
                ).exists()
            )
        ],
        key=lambda path: (
            path.stat().st_mtime
        ),
        reverse=True,
    )

    if not candidates:
        raise RuntimeError(
            "No run directory found."
        )

    return candidates[0]


def main():
    run_dir = latest_run()

    run_json = (
        run_dir
        / "run.json"
    )

    run = json.loads(
        run_json.read_text(
            encoding="utf-8"
        )
    )

    print()
    print("=" * 72)
    print(
        "UIUX FACTORY - FULL PIPELINE EVIDENCE"
    )
    print("=" * 72)
    print(
        f"[Run] {run_dir.name}"
    )
    print(
        f"[Status] {run.get('status')}"
    )
    print(
        "[Completed Stages] "
        + ", ".join(
            run.get(
                "completed_stages",
                [],
            )
        )
    )

    errors = run.get(
        "errors",
        []
    )

    print(
        f"[Errors] {len(errors)}"
    )

    for error in errors:
        print(
            f"  - {error}"
        )

    skill_root = (
        run_dir
        / "skill-context"
    )

    contexts = (
        sorted(
            skill_root.glob(
                "*/skill-context.json"
            )
        )
        if skill_root.exists()
        else []
    )

    print()
    print(
        "[Integrated Skill Stages] "
        f"{len(contexts)}"
    )

    for context_path in contexts:
        payload = json.loads(
            context_path.read_text(
                encoding="utf-8"
            )
        )

        print(
            f"  - {payload['stage']}: "
            f"{len(payload['sources'])} skills "
            f"({payload['domain']})"
        )

    event_path = (
        run_dir
        / "events.jsonl"
    )

    if event_path.exists():
        events = [
            json.loads(
                line
            )
            for line in event_path.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]

        print()
        print(
            f"[Event Count] {len(events)}"
        )

        stage_agents = []

        for event in events:
            if event.get(
                "type"
            ) == "agent.completed":
                stage_agents.append(
                    (
                        event.get(
                            "stage"
                        ),
                        event.get(
                            "agent"
                        ),
                    )
                )

        for stage, agent in (
            stage_agents
        ):
            print(
                f"  - {stage}: {agent}"
            )

    quality_path = (
        run_dir
        / "quality-loop.json"
    )

    print()
    print(
        "[Quality Loop Artifact] "
        f"{quality_path.exists()}"
    )

    if quality_path.exists():
        quality = json.loads(
            quality_path.read_text(
                encoding="utf-8"
            )
        )

        print(
            f"[Quality Status] "
            f"{quality.get('status')}"
        )
        print(
            f"[Final Score] "
            f"{quality.get('final_score')}"
        )
        print(
            f"[Stop Reason] "
            f"{quality.get('stop_reason')}"
        )
        print(
            "[Quality Iterations] "
            f"{len(quality.get('iterations', []))}"
        )

        for row in quality.get(
            "iterations",
            []
        ):
            print(
                "  - iteration "
                f"{row.get('iteration')}: "
                f"browser={row.get('browser_status')} "
                f"critic={row.get('critic_status')} "
                f"score={row.get('critic_score')} "
                f"repair={row.get('repair_status')}"
            )


if __name__ == "__main__":
    main()
