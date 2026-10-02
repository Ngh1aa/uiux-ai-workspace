from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.post_interop_executable_debt_audit import (
    ExecutableDebtAuditError,
    evaluate_post_interop_executable_debt_audit,
)


DEFAULT_AUDIT = ROOT / "benchmarks" / "post-interop-executable-debt-audit-v1.json"
EXPECTED_DECISION = "SELECT_COMPAT_SHIM_RETIREMENT_READINESS"
EXPECTED_NEXT_PACKAGE = "A53.1 — Runtime Compatibility Shim Retirement Readiness"
EXPECTED_CONSUMER_FILE_COUNT = 8
EXPECTED_CONSUMER_IMPORT_COUNT = 19
EXPECTED_CONSUMERS = {
    "uiux-factory/tests/test_adaptive_flow.py": {"runtime.flow", "runtime.task_context"},
    "uiux-factory/tests/test_canonical_runtime_a4.py": {
        "runtime.flow",
        "runtime.manager",
        "runtime.task_context",
    },
    "uiux-factory/tests/test_runtime_lifecycle_context.py": {"runtime.flow", "runtime.task_context"},
    "uiux-factory/tests/test_task_contract.py": {
        "runtime.agent",
        "runtime.flow",
        "runtime.manager",
        "runtime.task_context",
    },
    "skills_UIUX/scripts/context-manifest.py": {"runtime.agent"},
    "skills_UIUX/scripts/validate-flows.py": {"runtime.flow"},
    "skills_UIUX/scripts/validate-provider-runtime.py": {
        "runtime.agent",
        "runtime.manager",
        "runtime.provider",
        "runtime.provider_runner",
    },
    "skills_UIUX/scripts/validate-runtime-foundation.py": {"runtime.agent", "runtime.manager"},
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate A52.3 post-interop executable debt audit")
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    try:
        report = evaluate_post_interop_executable_debt_audit(args.audit)
    except (ExecutableDebtAuditError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"A52.3 executable debt audit FAILED: {exc}")
        return 1

    print(f"A52.3 executable debt audit: decision={report.decision}")
    print(f"next_package={report.next_package or '-'}")
    print(f"scope={report.scope}")
    print(f"source_truth_clear={report.source_truth_clear}")
    print(f"provider_default_migration_blocked={report.provider_default_migration_blocked}")
    print(f"provider_live_receipts={report.provider_live_receipt_count}/8")
    print(f"lifecycle_mutation_blocked={report.lifecycle_mutation_blocked}")
    print("lifecycle_blockers=" + ",".join(report.lifecycle_blockers))
    print(f"lifecycle_interop_observation_only={report.lifecycle_interop_observation_only}")
    print(f"genai_nist_expansion_blocked={report.genai_nist_expansion_blocked}")
    print(f"vector_semantic_retrieval_deferred={report.vector_semantic_retrieval_deferred}")
    print(f"shim_count={report.shim_count}")
    print(f"shim_contract_clear={report.shim_contract_clear}")
    print(f"internal_consumer_files={report.internal_consumer_file_count}")
    print(f"internal_consumer_imports={report.internal_consumer_import_count}")
    for consumer in report.internal_consumers:
        print(f"- consumer {consumer.path}: {','.join(consumer.modules)}")
    print(f"known_consumer_contract_clear={report.known_consumer_contract_clear}")
    print(f"governance_boundary_clear={report.governance_boundary_clear}")
    print(f"runtime_mutation_allowed={report.runtime_mutation_allowed}")
    print(f"shim_deletion_allowed={report.shim_deletion_allowed}")
    print(f"provider_default_change_allowed={report.provider_default_change_allowed}")
    print(f"lifecycle_state_owner_change_allowed={report.lifecycle_state_owner_change_allowed}")
    print(f"genai_promotion_allowed={report.genai_promotion_allowed}")
    print(f"vector_search_change_allowed={report.vector_search_change_allowed}")
    print(f"product_evidence={report.product_evidence}")

    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    forbidden = (
        report.runtime_mutation_allowed,
        report.shim_deletion_allowed,
        report.provider_default_change_allowed,
        report.lifecycle_state_owner_change_allowed,
        report.genai_promotion_allowed,
        report.vector_search_change_allowed,
        report.product_evidence,
    )
    effects = (
        report.execution_effect,
        report.authority_effect,
        report.gate_effect,
        report.evidence_effect,
        report.release_effect,
    )
    actual_consumers = {item.path: set(item.modules) for item in report.internal_consumers}

    if report.decision != EXPECTED_DECISION:
        return 1
    if report.next_package != EXPECTED_NEXT_PACKAGE:
        return 1
    if report.scope != "architecture_debt_selection_only_no_runtime_mutation":
        return 1
    if not all(
        (
            report.source_truth_clear,
            report.provider_default_migration_blocked,
            report.lifecycle_mutation_blocked,
            report.lifecycle_interop_observation_only,
            report.genai_nist_expansion_blocked,
            report.vector_semantic_retrieval_deferred,
            report.shim_contract_clear,
            report.known_consumer_contract_clear,
            report.governance_boundary_clear,
        )
    ):
        return 1
    if report.provider_live_receipt_count != 0:
        return 1
    if len(report.lifecycle_blockers) != 6:
        return 1
    if report.shim_count != 8:
        return 1
    if report.internal_consumer_file_count != EXPECTED_CONSUMER_FILE_COUNT:
        return 1
    if report.internal_consumer_import_count != EXPECTED_CONSUMER_IMPORT_COUNT:
        return 1
    if actual_consumers != EXPECTED_CONSUMERS:
        return 1
    if any(forbidden):
        return 1
    if any(value != "none" for value in effects):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
