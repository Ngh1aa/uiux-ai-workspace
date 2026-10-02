from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SKILLS = WORKSPACE / "skills_UIUX"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.provider_default_migration_readiness import (
    ProviderMigrationReadinessError,
    evaluate_provider_default_migration_readiness,
)


DEFAULT_READINESS = ROOT / "benchmarks" / "provider-default-migration-readiness-v1.json"
DEFAULT_RECEIPTS = ROOT / "benchmarks" / "provider-live-trial-receipts-v1.json"
DEFAULT_PARITY = ROOT / "benchmarks" / "provider-parity-v1.json"
DEFAULT_POLICY = SKILLS / "runtime" / "runtime-policy.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate A51.1 provider default migration readiness")
    parser.add_argument("--readiness", type=Path, default=DEFAULT_READINESS)
    parser.add_argument("--receipts", type=Path, default=DEFAULT_RECEIPTS)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    try:
        report = evaluate_provider_default_migration_readiness(
            args.readiness,
            args.receipts,
            parity_benchmark_path=DEFAULT_PARITY,
            factory_root=ROOT,
            skills_root=SKILLS,
            runtime_policy_path=DEFAULT_POLICY,
        )
    except (ProviderMigrationReadinessError, OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"A51.1 provider migration readiness FAILED: {exc}")
        return 1

    print(
        "A51.1 provider migration readiness: "
        f"decision={report.decision} "
        f"receipts={report.observed_receipt_count}/{report.required_receipt_count}"
    )
    print(f"offline_provider_parity_clear={report.offline_provider_parity_clear}")
    print(f"default_lane_contract_clear={report.default_lane_contract_clear}")
    print(f"live_receipt_contract_clear={report.live_receipt_contract_clear}")
    print(f"live_matrix_complete={report.live_matrix_complete}")
    print(f"live_matrix_all_passed={report.live_matrix_all_passed}")
    print(f"missing_matrix={','.join(report.missing_matrix) if report.missing_matrix else '-'}")
    print(f"failed_matrix={','.join(report.failed_matrix) if report.failed_matrix else '-'}")
    print(f"migration_governance_allowed={report.migration_governance_allowed}")
    print(f"default_change_allowed={report.default_change_allowed}")
    print(f"provider_migration_allowed={report.provider_migration_allowed}")
    print(f"auto_migration_allowed={report.auto_migration_allowed}")
    print(f"product_evidence={report.product_evidence}")

    if args.report is not None:
        payload = {
            "decision": report.decision,
            "offline_provider_parity_clear": report.offline_provider_parity_clear,
            "default_lane_contract_clear": report.default_lane_contract_clear,
            "live_receipt_contract_clear": report.live_receipt_contract_clear,
            "live_matrix_complete": report.live_matrix_complete,
            "live_matrix_all_passed": report.live_matrix_all_passed,
            "required_receipt_count": report.required_receipt_count,
            "observed_receipt_count": report.observed_receipt_count,
            "missing_matrix": list(report.missing_matrix),
            "failed_matrix": list(report.failed_matrix),
            "migration_governance_allowed": report.migration_governance_allowed,
            "default_change_allowed": False,
            "provider_migration_allowed": False,
            "auto_migration_allowed": False,
            "product_evidence": False,
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    expected = "KEEP_LEGACY_DEFAULT_LIVE_EVIDENCE_REQUIRED"
    if report.decision not in {expected, "READY_FOR_DEFAULT_MIGRATION_GOVERNANCE"}:
        return 1
    if report.default_change_allowed or report.provider_migration_allowed or report.auto_migration_allowed:
        return 1
    if report.product_evidence:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
