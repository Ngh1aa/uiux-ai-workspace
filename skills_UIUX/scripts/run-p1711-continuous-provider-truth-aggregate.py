#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = SKILLS_ROOT.parent
FACTORY_ROOT = WORKSPACE_ROOT / "uiux-factory"
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from core.dogfood.p1711_continuous_provider_truth_aggregate import (
    run_p1711_continuous_provider_truth_aggregate,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="P1.7.11 aggregate scheduled provider truth artifacts into one fleet decision."
    )
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-matrix-json")
    args = parser.parse_args()

    raw_matrix = args.expected_matrix_json or os.environ.get("P1711_EXPECTED_MATRIX") or ""
    try:
        expected_matrix = json.loads(raw_matrix) if raw_matrix.strip() else {}
    except json.JSONDecodeError as exc:
        expected_matrix = {"invalid_json": str(exc)}

    report = run_p1711_continuous_provider_truth_aggregate(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        expected_matrix=expected_matrix,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
