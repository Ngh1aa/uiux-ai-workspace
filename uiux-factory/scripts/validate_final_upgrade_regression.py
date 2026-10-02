#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.final_upgrade_regression import evaluate_final_upgrade_regression


PASS_DECISION = "WORKSPACE_UPGRADE_FINAL_REGRESSION_PASS"
HOLD_DECISION = "HOLD_FINAL_REGRESSION_EVIDENCE_REQUIRED"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Flow 4 final upgrade regression")
    parser.add_argument("--report-root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    contract = ROOT / "benchmarks" / "final-upgrade-regression-v1.json"
    report = evaluate_final_upgrade_regression(contract, report_root=args.report_root)

    print(f"Flow 4 final regression: decision={report.decision}")
    print(f"scope={report.scope}")
    print(f"flow3_clear={report.flow3_clear}")
    print(f"contract_clear={report.contract_clear}")
    print(f"governance_boundary_clear={report.governance_boundary_clear}")
    print(f"evidence_complete={report.evidence_complete}")
    print(f"release_audit_present={report.release_audit_present}")
    print(f"release_audit_passed={report.release_audit_passed}")
    print(f"projects={report.project_pass_count}/{report.required_project_count}")
    print(f"final_owner_review_allowed={report.final_owner_review_allowed}")
    for item in report.project_results:
        print(
            f"- {item.project_id}: present={item.report_present} passed={item.report_passed} "
            f"contract_clear={item.contract_clear} truth_boundary_clear={item.truth_boundary_clear} "
            f"sha={item.expected_target_sha}"
        )

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    forbidden = (
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

    if args.report_root is None:
        ok = all(
            (
                report.decision == HOLD_DECISION,
                report.flow3_clear,
                report.contract_clear,
                report.governance_boundary_clear,
                report.evidence_complete is False,
                report.final_owner_review_allowed is False,
                not any(forbidden),
                effects_clear,
            )
        )
    else:
        ok = all(
            (
                report.decision == PASS_DECISION,
                report.flow3_clear,
                report.contract_clear,
                report.governance_boundary_clear,
                report.evidence_complete,
                report.release_audit_passed,
                report.project_pass_count == report.required_project_count == 4,
                report.final_owner_review_allowed,
                not any(forbidden),
                effects_clear,
            )
        )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
