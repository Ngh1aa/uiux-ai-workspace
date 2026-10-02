#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.architecture_debt_closure_audit import (
    evaluate_architecture_debt_closure_audit,
)


EXPECTED_DECISION = "ARCHITECTURE_DEBT_LEDGER_CLOSED_FOR_UPGRADE"


def main() -> int:
    audit_path = ROOT / "benchmarks/architecture-debt-closure-audit-v1.json"
    report = evaluate_architecture_debt_closure_audit(audit_path)

    print(f"Flow 3 architecture debt closure: decision={report.decision}")
    print(f"scope={report.scope}")
    print(f"source_contract_clear={report.source_contract_clear}")
    print(f"area_contract_clear={report.area_contract_clear}")
    print(f"governance_boundary_clear={report.governance_boundary_clear}")
    print(f"closed={report.closed_count}")
    print(f"intentional_holds={report.intentional_hold_count}")
    print(f"new_actionable_debt={report.actionable_debt_count}")
    print(f"flow4_allowed={report.flow4_allowed}")
    for item in report.areas:
        suffix = f" trigger={item.trigger}" if item.trigger else ""
        print(
            f"- {item.id}: classification={item.classification} "
            f"evidence_clear={item.evidence_clear} upgrade_blocker={item.upgrade_blocker}{suffix}"
        )

    forbidden = (
        report.runtime_mutation_allowed,
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
    effects = (
        report.execution_effect,
        report.authority_effect,
        report.gate_effect,
        report.evidence_effect,
        report.release_effect,
    )
    clear = all(
        (
            report.decision == EXPECTED_DECISION,
            report.source_contract_clear,
            report.area_contract_clear,
            report.governance_boundary_clear,
            report.closed_count == 4,
            report.intentional_hold_count == 5,
            report.actionable_debt_count == 0,
            report.flow4_allowed,
            all(item.evidence_clear for item in report.areas),
            not any(forbidden),
            all(item == "none" for item in effects),
        )
    )
    return 0 if clear else 1


if __name__ == "__main__":
    raise SystemExit(main())
