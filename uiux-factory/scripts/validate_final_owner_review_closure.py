#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.final_owner_review_closure import (
    EXPECTED_HOLD_IDS,
    evaluate_final_owner_review_closure,
)


PASS_DECISION = "WORKSPACE_UPGRADE_CLOSED_WITH_INTENTIONAL_HOLDS"
HOLD_DECISION = "HOLD_FINAL_OWNER_REVIEW_EVIDENCE_REQUIRED"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Flow 5 final owner review closure")
    parser.add_argument("--flow4-report", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    contract = ROOT / "benchmarks" / "final-owner-review-closure-v1.json"
    report = evaluate_final_owner_review_closure(
        contract,
        flow4_report_path=args.flow4_report,
    )

    print(f"Flow 5 owner review closure: decision={report.decision}")
    print(f"scope={report.scope}")
    print(f"flow3_clear={report.flow3_clear}")
    print(f"flow4_report_present={report.flow4_report_present}")
    print(f"flow4_clear={report.flow4_clear}")
    print(f"intentional_holds_preserved={report.intentional_holds_preserved}")
    print(f"intentional_hold_ids={','.join(report.intentional_hold_ids)}")
    print(f"owner_delegation_clear={report.owner_delegation_clear}")
    print(f"owner_review_source_clear={report.owner_review_source_clear}")
    print(f"repository_hygiene_receipt_clear={report.repository_hygiene_receipt_clear}")
    print(f"governance_boundary_clear={report.governance_boundary_clear}")
    print(f"final_owner_review_completed={report.final_owner_review_completed}")
    print(f"upgrade_closed={report.upgrade_closed}")
    print(f"future_hold_triggers_preserved={report.future_hold_triggers_preserved}")
    print(f"independent_human_review_claimed={report.independent_human_review_claimed}")

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    forbidden = (
        report.independent_human_review_claimed,
        report.provider_default_change_allowed,
        report.lifecycle_state_owner_change_allowed,
        report.routing_change_allowed,
        report.knowledge_index_mutation_allowed,
        report.vector_search_change_allowed,
        report.compatibility_shim_deletion_allowed,
        report.evidence_authority_change_allowed,
        report.gate_authority_change_allowed,
        report.release_authority_change_allowed,
        report.product_evidence,
    )
    effects_clear = all(
        value == "none"
        for value in (
            report.execution_effect,
            report.authority_effect,
            report.gate_effect,
            report.evidence_effect,
            report.release_effect,
        )
    )
    base_clear = all(
        (
            report.flow3_clear,
            report.intentional_holds_preserved,
            report.intentional_hold_ids == EXPECTED_HOLD_IDS,
            report.owner_delegation_clear,
            report.owner_review_source_clear,
            report.repository_hygiene_receipt_clear,
            report.governance_boundary_clear,
            report.future_hold_triggers_preserved,
            not any(forbidden),
            effects_clear,
        )
    )

    if args.flow4_report is None:
        ok = all(
            (
                base_clear,
                report.decision == HOLD_DECISION,
                report.flow4_report_present is False,
                report.flow4_clear is False,
                report.final_owner_review_completed is False,
                report.upgrade_closed is False,
            )
        )
    else:
        ok = all(
            (
                base_clear,
                report.decision == PASS_DECISION,
                report.flow4_report_present,
                report.flow4_clear,
                report.final_owner_review_completed,
                report.upgrade_closed,
            )
        )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
