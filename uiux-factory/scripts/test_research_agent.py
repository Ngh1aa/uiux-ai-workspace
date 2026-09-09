import asyncio
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from core.agents.research_agent import ResearchAgent


async def main():
    goal = (
        "Thiết kế website ecommerce hiện đại, "
        "sang trọng, thân thiện, "
        "màu chủ đạo là màu tím."
    )

    print()
    print("=" * 60)
    print("UIUX FACTORY - RESEARCH AGENT")
    print("=" * 60)

    print(f"\n[Goal]\n{goal}")

    agent = ResearchAgent()

    print("\n[ResearchAgent] Starting MOCK mode...")

    result = await agent.run(goal)

    if not result:
        raise RuntimeError(
            "ResearchAgent returned no result."
        )

    run_id = datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )

    run_dir = ROOT / "runs" / run_id

    run_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    artifact_path = run_dir / "research.md"

    artifact_path.write_text(
        result.content,
        encoding="utf-8",
    )

    print("\n[ResearchAgent] COMPLETED")
    print(f"[Artifact] {artifact_path}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())