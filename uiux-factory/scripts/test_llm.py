import asyncio

from metagpt.config2 import config
from metagpt.provider.llm_provider_registry import create_llm_instance


async def main():
    print(f"[Provider] {config.llm.api_type}")
    print(f"[Model] {config.llm.model}")

    llm = create_llm_instance(config.llm)

    response = await llm.aask(
        "Reply with exactly: UIUX Factory LLM OK"
    )

    print(f"[Response] {response}")


if __name__ == "__main__":
    asyncio.run(main())