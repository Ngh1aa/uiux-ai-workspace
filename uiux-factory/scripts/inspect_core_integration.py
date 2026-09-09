import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def latest_run() -> Path:
    runs = ROOT / "runs"

    candidates = sorted(
        [
            path
            for path in runs.iterdir()
            if path.is_dir() and (path / "run.json").exists()
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not candidates:
        raise RuntimeError("No run directory found.")

    return candidates[0]


def main():
    run_dir = latest_run()
    events = run_dir / "events.jsonl"

    skill_root = run_dir / "skill-context"
    contexts = (
        sorted(skill_root.glob("*/skill-context.json"))
        if skill_root.exists()
        else []
    )

    print()
    print("=" * 72)
    print("UIUX FACTORY - CORE INTEGRATION EVIDENCE")
    print("=" * 72)
    print(f"[Run] {run_dir.name}")
    print(f"[Events] {events}")
    print(f"[Skill Context Stages] {len(contexts)}")

    for context_path in contexts:
        payload = json.loads(
            context_path.read_text(encoding="utf-8")
        )

        print()
        print(
            f"[{payload['stage']}] "
            f"domain={payload['domain']}"
        )

        for source in payload["sources"]:
            print(
                "  - "
                f"{source['relative_path']} "
                f"{source['sha256'][:12]}"
            )

    if events.exists():
        lines = [
            line
            for line in events.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]

        print()
        print(f"[Event Count] {len(lines)}")

        for line in lines[-12:]:
            event = json.loads(line)
            print(
                f"  #{event['seq']} "
                f"{event['type']} "
                f"stage={event.get('stage')} "
                f"agent={event.get('agent')}"
            )


if __name__ == "__main__":
    main()
