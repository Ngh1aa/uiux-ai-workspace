import asyncio
import sys
import tempfile
from pathlib import Path
from typing import ClassVar

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from metagpt.actions import Action
from metagpt.roles.role import Role

from core.team.team_runner import UIUXTeamRunner


class CoreIntegrationSmokeAction(Action):
    name: str = "CoreIntegrationSmokeAction"

    MARKER: ClassVar[str] = "UIUX SKILL EXECUTION CONTEXT"

    async def run(self, history) -> str:
        if not history:
            raise RuntimeError("No MetaGPT role history received.")

        content = history[-1].content

        if self.MARKER not in content:
            raise RuntimeError(
                "Real skill execution context was not injected into MetaGPT Message."
            )

        return "CORE_INTEGRATION_SMOKE_PASS"


class CoreIntegrationSmokeRole(Role):
    name: str = "CoreSmoke"
    profile: str = "CoreIntegrationSmokeRole"
    goal: str = (
        "Prove MetaGPT Team + real skills_UIUX execution context are connected."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([CoreIntegrationSmokeAction])


class SmokeContext:
    run_id = "core-smoke"
    goal = "Thiết kế website ecommerce hiện đại màu tím"

    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.artifacts: dict[str, str] = {}

    def add_artifact(self, key, path):
        self.artifacts[key] = str(path)


async def main():
    with tempfile.TemporaryDirectory(
        prefix="uiux-core-integration-"
    ) as temp:
        run_dir = Path(temp) / "run"
        run_dir.mkdir(parents=True, exist_ok=True)

        context = SmokeContext(run_dir)
        runner = UIUXTeamRunner(root=ROOT)

        result = await runner.run_role(
            role_class=CoreIntegrationSmokeRole,
            stage="implementation",
            instruction="SMOKE TEST",
            context=context,
        )

        event_path = run_dir / "events.jsonl"
        skill_context = (
            run_dir
            / "skill-context"
            / "implementation"
            / "skill-context.json"
        )
        copied_sources = list(
            (
                run_dir
                / "skill-context"
                / "implementation"
                / "sources"
            ).glob("*.md")
        )

        print()
        print("=" * 72)
        print("UIUX FACTORY - CORE INTEGRATION SMOKE TEST")
        print("=" * 72)
        print(
            "[MetaGPT Team] "
            f"{type(runner.meta_team.team).__name__}"
        )
        print(f"[Team Roles] {runner.meta_team.role_names()}")
        print(f"[Result] {result.content}")
        print(f"[Skill Context] {skill_context.exists()}")
        print(f"[Copied Real Skills] {len(copied_sources)}")
        print(f"[Events JSONL] {event_path.exists()}")
        print(f"[Artifact Keys] {sorted(context.artifacts)}")

        if result.content != "CORE_INTEGRATION_SMOKE_PASS":
            raise SystemExit(1)
        if not skill_context.exists():
            raise SystemExit(1)
        if not copied_sources:
            raise SystemExit(1)
        if not event_path.exists():
            raise SystemExit(1)

        print()
        print(
            "PASS: MetaGPT Team received a Message containing "
            "compiled, copied real skills_UIUX execution context."
        )


if __name__ == "__main__":
    asyncio.run(main())
