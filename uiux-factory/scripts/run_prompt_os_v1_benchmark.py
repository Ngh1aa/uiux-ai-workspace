from __future__ import annotations

import json
from pathlib import Path

from core.benchmarks.prompt_os_v1 import PromptOSProfileBenchmark


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "benchmarks" / "prompt_os_v1_profiles.json"
OUTPUT = ROOT / "benchmark-results" / "prompt-os-v1-profile-benchmark.json"


def main() -> int:
    result = PromptOSProfileBenchmark(FIXTURE).run(OUTPUT)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
