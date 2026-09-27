from __future__ import annotations

import json
from pathlib import Path

from core.verification.prompt_os_release import PromptOSV1ReleaseVerifier


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "benchmark-results" / "prompt-os-v1-release-verification.json"


def main() -> int:
    result = PromptOSV1ReleaseVerifier(ROOT).verify()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
