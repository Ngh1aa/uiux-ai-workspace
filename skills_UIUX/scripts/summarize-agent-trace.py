#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a skills_UIUX JSONL agent trace")
    parser.add_argument("trace")
    args = parser.parse_args()

    path = Path(args.trace)
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    events = Counter(row.get("event") for row in rows)
    statuses = Counter(row.get("status") for row in rows)
    print(json.dumps({
        "events": len(rows),
        "event_counts": dict(events),
        "status_counts": dict(statuses),
        "run_ids": sorted({row.get("run_id") for row in rows}),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
