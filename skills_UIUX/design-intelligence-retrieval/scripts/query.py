#!/usr/bin/env python3
"""Stable local adapter for the pinned vendored UI UX Pro Max search engine."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEARCH = ROOT / "vendor" / "ui-ux-pro-max" / "engine" / "scripts" / "search.py"


def main() -> int:
    if not SEARCH.exists():
        print(f"Vendored search engine not found: {SEARCH}", file=sys.stderr)
        return 2
    command = [sys.executable, "-B", str(SEARCH), *sys.argv[1:]]
    return subprocess.call(command, cwd=str(SEARCH.parent))


if __name__ == "__main__":
    raise SystemExit(main())
