"""Read configuration without exposing credentials; optional explicit live smoke request."""
import argparse
import asyncio
from pathlib import Path

from core.runtime.free_provider import FreeProvider, ProviderError


async def main(live: bool):
    try:
        provider = FreeProvider.from_env(Path(__file__).resolve().parents[1])
        print("Configured:", ", ".join(f"{p.name}/{p.model}" for p in provider.configs))
        if live:
            await provider.complete("ux_ia", "Reply with a short acknowledgement.", "Connection smoke test.")
            print("PASS: live model response received.")
        else:
            print("No API request sent. Use --live to verify the configured account.")
    except ProviderError as error:
        print("NOT READY:", error)
        raise SystemExit(2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    asyncio.run(main(parser.parse_args().live))
