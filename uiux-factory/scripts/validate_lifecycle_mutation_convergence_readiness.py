from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.benchmarks.lifecycle_mutation_convergence_readiness import (
    LifecycleMutationReadinessError,
    evaluate_lifecycle_mutation_convergence_readiness,
)


DEFAULT_READINESS = ROOT / "benchmarks" / "lifecycle-mutation-convergence-readiness-v1.json"
DEFAULT_PARITY = ROOT / "benchmarks" / "lifecycle-parity-v1.json"
EXPECTED_DECISION = "KEEP_SEPARATE_STATE_OWNERS_EVENT_INTEROP_REQUIRED"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate A52.1 lifecycle mutation convergence readiness")
    parser.add_argument("--readiness", type=Path, default=DEFAULT_READINESS)
    parser.add_argument("--parity", type=Path, default=DEFAULT_PARITY)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    try:
        report = evaluate_lifecycle_mutation_convergence_readiness(
            args.readiness,
            lifecycle_parity_path=args.parity,
        )
    except (LifecycleMutationReadinessError, OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"A52.1 lifecycle mutation readiness FAILED: {exc}")
        return 1

    print(f"A52.1 lifecycle mutation readiness: decision={report.decision}")
    print(f"lifecycle_projection_parity_clear={report.lifecycle_projection_parity_clear}")
    print(f"reconciliation_read_only={report.reconciliation_read_only}")
    print(f"source_contract_clear={report.source_contract_clear}")
    print(f"semantic_blockers_match_contract={report.semantic_blockers_match_contract}")
    print(
        "semantic_blockers="
        + (",".join(report.semantic_blockers) if report.semantic_blockers else "-")
    )
    print(f"event_interop_proposal_allowed={report.event_interop_proposal_allowed}")
    print(f"mutation_governance_allowed={report.mutation_governance_allowed}")
    print(f"state_owner_replacement_allowed={report.state_owner_replacement_allowed}")
    print(f"shared_mutable_state_allowed={report.shared_mutable_state_allowed}")
    print(f"runtime_transition_change_allowed={report.runtime_transition_change_allowed}")
    print(f"routing_change_allowed={report.routing_change_allowed}")
    print(f"provider_default_change_allowed={report.provider_default_change_allowed}")
    print(f"evidence_authority_change_allowed={report.evidence_authority_change_allowed}")
    print(f"gate_authority_change_allowed={report.gate_authority_change_allowed}")
    print(f"finalize_release_authority_change_allowed={report.finalize_release_authority_change_allowed}")
    print(f"product_evidence={report.product_evidence}")

    if args.report is not None:
        payload = {
            "decision": report.decision,
            "lifecycle_projection_parity_clear": report.lifecycle_projection_parity_clear,
            "reconciliation_read_only": report.reconciliation_read_only,
            "source_contract_clear": report.source_contract_clear,
            "semantic_blockers": list(report.semantic_blockers),
            "semantic_blockers_match_contract": report.semantic_blockers_match_contract,
            "event_interop_proposal_allowed": report.event_interop_proposal_allowed,
            "mutation_governance_allowed": report.mutation_governance_allowed,
            "state_owner_replacement_allowed": report.state_owner_replacement_allowed,
            "shared_mutable_state_allowed": report.shared_mutable_state_allowed,
            "runtime_transition_change_allowed": report.runtime_transition_change_allowed,
            "routing_change_allowed": report.routing_change_allowed,
            "provider_default_change_allowed": report.provider_default_change_allowed,
            "evidence_authority_change_allowed": report.evidence_authority_change_allowed,
            "gate_authority_change_allowed": report.gate_authority_change_allowed,
            "finalize_release_authority_change_allowed": report.finalize_release_authority_change_allowed,
            "product_evidence": report.product_evidence,
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    forbidden = (
        report.mutation_governance_allowed,
        report.state_owner_replacement_allowed,
        report.shared_mutable_state_allowed,
        report.runtime_transition_change_allowed,
        report.routing_change_allowed,
        report.provider_default_change_allowed,
        report.evidence_authority_change_allowed,
        report.gate_authority_change_allowed,
        report.finalize_release_authority_change_allowed,
        report.product_evidence,
    )
    if any(forbidden):
        return 1
    if report.decision != EXPECTED_DECISION:
        return 1
    if not all(
        (
            report.lifecycle_projection_parity_clear,
            report.reconciliation_read_only,
            report.source_contract_clear,
            report.semantic_blockers_match_contract,
            report.event_interop_proposal_allowed,
        )
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
