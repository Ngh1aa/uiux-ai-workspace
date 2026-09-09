import asyncio
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from core.agents.art_director import (
    ArtDirector,
)


async def main():
    goal = (
        "Thiết kế website ecommerce hiện đại, "
        "sang trọng, thân thiện, "
        "màu chủ đạo là màu tím."
    )

    research = (
        "Research completed in mock mode. "
        "External reference evidence is still pending."
    )

    ux_ia = (
        "Detected domain: ecommerce. "
        "Primary page roles include Home, Category, Search, "
        "Product Detail, Cart and Checkout."
    )

    instruction = (
        "## GOAL\n\n"
        + goal
        + "\n\n## RESEARCH\n\n"
        + research
        + "\n\n## UX_IA\n\n"
        + ux_ia
    )

    print()
    print("=" * 60)
    print("UIUX FACTORY - ART DIRECTOR")
    print("=" * 60)

    agent = ArtDirector()

    result = await agent.run(
        instruction
    )

    if not result:
        raise RuntimeError(
            "ArtDirector returned no result."
        )

    print(
        "\n[ArtDirector] COMPLETED"
    )

    print(
        result.content[:1800]
    )

    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())