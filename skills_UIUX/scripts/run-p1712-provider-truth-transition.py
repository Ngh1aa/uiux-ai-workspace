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

from core.runtime.flow_os.provider_truth_transition import (
    write_provider_truth_transition_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare current and previous P1.7.11 fleet summaries and emit a read-only P1.7.12 transition artifact."
    )
    parser.add_argument("--current", required=True)
    parser.add_argument("--baseline")
    parser.add_argument("--baseline-selection")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    report = write_provider_truth_transition_report(
        current_summary_path=args.current,
        baseline_summary_path=args.baseline,
        baseline_source_path=args.baseline_selection,
        output_path=args.output,
    )
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))

    # P1.7.12 is detection/evidence only. NEW_BLOCKER is already enforced by
    # current P1.7.10/P1.7.11 truth; BASELINE_NOT_AVAILABLE is expected on first run.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
