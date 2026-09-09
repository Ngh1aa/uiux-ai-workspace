#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.agent import build_context_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a minimal skills_UIUX context manifest")
    parser.add_argument("--project", required=True)
    parser.add_argument("--skill", action="append", default=[])
    parser.add_argument("--source", action="append", default=[])
    args = parser.parse_args()

    manifest = build_context_manifest(
        Path(args.project).resolve(),
        ROOT,
        selected_skills=args.skill,
        explicit_sources=args.source,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
