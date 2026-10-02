from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.runtime_compatibility_convergence import (
    RuntimeCompatibilityConvergenceError,
    evaluate_runtime_compatibility_convergence,
)


DEFAULT_CONTRACT = ROOT / "benchmarks" / "runtime-compatibility-convergence-v1.json"
EXPECTED_DECISION = "FIRST_PARTY_RUNTIME_COMPAT_CONVERGENCE_PASS"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Flow 1 / A53.1 runtime compatibility convergence")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    try:
        report = evaluate_runtime_compatibility_convergence(args.contract)
    except (RuntimeCompatibilityConvergenceError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Flow 1 runtime compatibility convergence FAILED: {exc}")
        return 1

    print(f"Flow 1 runtime compatibility convergence: decision={report.decision}")
    print(f"scope={report.scope}")
    print(f"historical_baseline_clear={report.historical_baseline_clear}")
    print(f"historical_consumers={report.historical_consumer_files}/{report.historical_consumer_imports}")
    print(f"shim_count={report.shim_count}")
    print(f"shim_contract_clear={report.shim_contract_clear}")
    print(f"identity_checks_clear={report.identity_checks_clear}")
    print(f"migrated_consumer_contract_clear={report.migrated_consumer_contract_clear}")
    print(f"script_bootstrap_clear={report.script_bootstrap_clear}")
    print(f"internal_consumer_files={report.internal_consumer_file_count}")
    print(f"internal_consumer_imports={report.internal_consumer_import_count}")
    print(f"zero_internal_consumers={report.zero_internal_consumers}")
    print(f"governance_boundary_clear={report.governance_boundary_clear}")
    for check in report.identity_checks:
        status = "PASS" if check.identical else "FAIL"
        print(f"- {status} {check.shim_path}:{check.shim_symbol} is {check.canonical_module}:{check.canonical_symbol}")
    for consumer in report.internal_consumers:
        print(f"- remaining consumer {consumer.path}: {','.join(consumer.modules)}")

    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    forbidden = (
        report.shim_deletion_allowed,
        report.external_removal_safety_inferred,
        report.runtime_behavior_change_allowed,
        report.provider_default_change_allowed,
        report.lifecycle_state_owner_change_allowed,
        report.routing_change_allowed,
        report.evidence_authority_change_allowed,
        report.gate_authority_change_allowed,
        report.release_authority_change_allowed,
        report.product_evidence,
    )
    effects = (
        report.execution_effect,
        report.authority_effect,
        report.gate_effect,
        report.evidence_effect,
        report.release_effect,
    )

    if report.decision != EXPECTED_DECISION:
        return 1
    if report.scope != "first_party_import_convergence_no_shim_removal":
        return 1
    if report.historical_consumer_files != 8 or report.historical_consumer_imports != 19:
        return 1
    if report.shim_count != 8:
        return 1
    if report.internal_consumer_file_count != 0 or report.internal_consumer_import_count != 0:
        return 1
    if not all(
        (
            report.historical_baseline_clear,
            report.shim_contract_clear,
            report.identity_checks_clear,
            report.migrated_consumer_contract_clear,
            report.script_bootstrap_clear,
            report.zero_internal_consumers,
            report.governance_boundary_clear,
        )
    ):
        return 1
    if any(forbidden):
        return 1
    if any(value != "none" for value in effects):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
