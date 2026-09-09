import asyncio
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from core.agents.ux_strategist import (
    UXStrategist,
)


async def main():
    goal = (
        "Thiết kế website ecommerce hiện đại, "
        "sang trọng, thân thiện, "
        "màu chủ đạo là màu tím."
    )

    research = """
Research stage completed in mock mode.

Evidence status:
PENDING

No external competitor claims have been verified yet.
"""

    instruction = f"""
## GOAL

{goal}

## RESEARCH

{research}
"""

    print()
    print("=" * 60)
    print("UIUX FACTORY - UX STRATEGIST")
    print("=" * 60)

    agent = UXStrategist()

    result = await agent.run(
        instruction
    )

    if not result:
        raise RuntimeError(
            "UXStrategist returned no result."
        )

    print(
        "\n[UXStrategist] COMPLETED"
    )

    print(
        result.content[:1500]
    )

    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())