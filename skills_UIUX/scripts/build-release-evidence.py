#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = SKILLS_ROOT.parent
FACTORY_ROOT = WORKSPACE_ROOT / "uiux-factory"
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from core.provenance.release_evidence_registry import build_release_evidence_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one integrity-hashed release evidence registry.")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--target-sha", required=True)
    parser.add_argument("--artifact", action="append", default=[], help="kind=path; repeat for every evidence artifact")
    parser.add_argument("--generated-at", default="")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    pairs: list[tuple[str, Path]] = []
    for raw in args.artifact:
        if "=" not in raw:
            raise SystemExit(f"Invalid --artifact {raw!r}; expected kind=path")
        kind, raw_path = raw.split("=", 1)
        if not kind.strip() or not raw_path.strip():
            raise SystemExit(f"Invalid --artifact {raw!r}; expected non-empty kind and path")
        pairs.append((kind.strip(), Path(raw_path).resolve()))

    manifest = build_release_evidence_manifest(
        target_repository=args.repository,
        target_sha=args.target_sha,
        artifacts=pairs,
        generated_at=args.generated_at or None,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(manifest.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n"
    output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
