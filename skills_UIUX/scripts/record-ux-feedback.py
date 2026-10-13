#!/usr/bin/env python3
"""Persist normalized local browser QA history through the canonical A5 store."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILLS_ROOT.parent / "uiux-factory"))
from core.memory.ux_feedback import record_browser_feedback


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--reports-dir", required=True)
    args = parser.parse_args()
    try:
        root = Path(args.project_root).resolve(strict=True)
        if not root.is_dir():
            raise ValueError("project-root must be a directory")
        policy = json.loads((SKILLS_ROOT / "runtime/runtime-policy.json").read_text(encoding="utf-8"))
        result = record_browser_feedback(root, Path(args.reports_dir), policy)
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"status": "UNKNOWN", "diagnostic": type(exc).__name__, "advisory_only": True}), file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
