from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.benchmarks.lifecycle_mutation_convergence_readiness import (
    LifecycleMutationReadinessError,
    _derive_decision,
    evaluate_lifecycle_mutation_convergence_readiness,
)


ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "benchmarks" / "lifecycle-mutation-convergence-readiness-v1.json"
PARITY = ROOT / "benchmarks" / "lifecycle-parity-v1.json"


def _evaluate(path: Path = READINESS):
    return evaluate_lifecycle_mutation_convergence_readiness(
        path,
        lifecycle_parity_path=PARITY,
    )


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "readiness.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def test_a52_current_repo_keeps_separate_state_owners() -> None:
    report = _evaluate()

    assert report.decision == "KEEP_SEPARATE_STATE_OWNERS_EVENT_INTEROP_REQUIRED"
    assert report.lifecycle_projection_parity_clear is True
    assert report.reconciliation_read_only is True
    assert report.source_contract_clear is True
    assert report.semantic_blockers_match_contract is True
    assert report.semantic_blockers == (
        "distinct_state_models",
        "factory_append_only_chronology",
        "managed_checkpoint_and_stage_lineage",
        "managed_human_gate_semantics",
        "replan_invalidation_semantics_non_parity",
        "finalize_release_semantics_non_parity",
    )
    assert report.event_interop_proposal_allowed is True
    assert report.mutation_governance_allowed is False
    assert report.state_owner_replacement_allowed is False
    assert report.shared_mutable_state_allowed is False
    assert report.runtime_transition_change_allowed is False
    assert report.routing_change_allowed is False
    assert report.provider_default_change_allowed is False
    assert report.evidence_authority_change_allowed is False
    assert report.gate_authority_change_allowed is False
    assert report.finalize_release_authority_change_allowed is False
    assert report.product_evidence is False


def test_a52_governance_contract_rejects_runtime_mutation_authority(tmp_path: Path) -> None:
    payload = json.loads(READINESS.read_text(encoding="utf-8"))
    payload["governance"]["runtime_transition_change_allowed_in_this_task"] = True

    with pytest.raises(LifecycleMutationReadinessError, match="cannot change lifecycle/authority/runtime semantics"):
        _evaluate(_write(tmp_path, payload))


def test_a52_cannot_self_opt_into_mutation_governance(tmp_path: Path) -> None:
    payload = json.loads(READINESS.read_text(encoding="utf-8"))
    payload["governance"]["explicit_mutation_governance_opt_in"] = True

    with pytest.raises(LifecycleMutationReadinessError, match="cannot opt into mutation governance"):
        _evaluate(_write(tmp_path, payload))


def test_a52_decision_derivation_fails_closed_before_semantic_hold() -> None:
    policy = {
        "prerequisite_regression": "HOLD_LIFECYCLE_CONVERGENCE_EVIDENCE_REQUIRED",
        "semantic_blockers_present": "KEEP_SEPARATE_STATE_OWNERS_EVENT_INTEROP_REQUIRED",
        "blockers_cleared_without_explicit_governance": "HOLD_EXPLICIT_MUTATION_GOVERNANCE_REQUIRED",
        "blockers_cleared_with_explicit_governance": "READY_FOR_SEPARATE_MUTATION_GOVERNANCE",
    }

    assert _derive_decision(
        parity_clear=False,
        source_contract_clear=True,
        reconciliation_read_only=True,
        blockers=("distinct_state_models",),
        explicit_mutation_governance_opt_in=False,
        policy=policy,
    ) == "HOLD_LIFECYCLE_CONVERGENCE_EVIDENCE_REQUIRED"
    assert _derive_decision(
        parity_clear=True,
        source_contract_clear=True,
        reconciliation_read_only=True,
        blockers=("distinct_state_models",),
        explicit_mutation_governance_opt_in=False,
        policy=policy,
    ) == "KEEP_SEPARATE_STATE_OWNERS_EVENT_INTEROP_REQUIRED"
    assert _derive_decision(
        parity_clear=True,
        source_contract_clear=True,
        reconciliation_read_only=True,
        blockers=(),
        explicit_mutation_governance_opt_in=False,
        policy=policy,
    ) == "HOLD_EXPLICIT_MUTATION_GOVERNANCE_REQUIRED"
    assert _derive_decision(
        parity_clear=True,
        source_contract_clear=True,
        reconciliation_read_only=True,
        blockers=(),
        explicit_mutation_governance_opt_in=True,
        policy=policy,
    ) == "READY_FOR_SEPARATE_MUTATION_GOVERNANCE"
