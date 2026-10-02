from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from core.benchmarks.lifecycle_event_interop_regression import evaluate_lifecycle_event_interop_corpus
from core.runtime.lifecycle_event_interop import (
    assert_receipts_non_authoritative,
    project_factory_event_receipts,
    project_managed_transition_receipts,
)


FACTORY = Path(__file__).resolve().parents[1]
CORPUS = FACTORY / "benchmarks" / "lifecycle-event-interop-v1.json"


def _managed_checkpoint(
    run_id: str,
    *,
    state: str = "READY",
    revision: int = 1,
    active_stage: str = "design",
    completed_stages: list[str] | None = None,
    stage_runs: dict[str, list[str]] | None = None,
    approved_gates: list[str] | None = None,
    replan_count: int = 0,
) -> dict:
    return {
        "manager_run_id": run_id,
        "flow": {
            "id": "flow",
            "revision": revision,
            "stages": [
                {
                    "id": "design",
                    "agent": "development",
                    "gates": [{"id": "signoff", "approval": "human"}],
                }
            ],
        },
        "task_context": {"approval_mode": "manual"},
        "authority": "branch_write",
        "active_stage": active_stage,
        "state": state,
        "replan_count": replan_count,
        "completed_stages": list(completed_stages or []),
        "stage_runs": deepcopy(stage_runs or {}),
        "replan_history": [],
        "approved_gates": list(approved_gates or []),
    }


def test_a52_2_interop_corpus_passes() -> None:
    report = evaluate_lifecycle_event_interop_corpus(CORPUS)
    assert report.total == 8
    assert report.passed == report.total
    assert report.source_inputs_unchanged is True
    assert report.authority_boundaries_clear is True
    assert report.scope == "observation_only_no_lifecycle_mutation"


def test_factory_receipt_preserves_native_seq_and_timestamp_without_checkpoint_claims() -> None:
    event = {
        "seq": 7,
        "type": "stage.started",
        "run_id": "factory-run",
        "timestamp": "2026-10-02T00:00:00+00:00",
        "stage": "implementation",
        "agent": "implementation",
        "data": {},
    }
    before = deepcopy(event)
    receipts = project_factory_event_receipts([event])
    assert event == before
    assert len(receipts) == 1
    receipt = receipts[0]
    assert receipt.kind == "stage_started"
    assert receipt.phase == "IMPLEMENT"
    assert receipt.chronology_strength == "durable_append_only"
    assert receipt.source_seq == 7
    assert receipt.source_timestamp == "2026-10-02T00:00:00+00:00"
    assert receipt.previous_checkpoint_hash is None
    assert receipt.checkpoint_hash is None
    assert_receipts_non_authoritative(receipts)


def test_unknown_factory_event_fails_safe_as_native_observation() -> None:
    receipts = project_factory_event_receipts(
        [
            {
                "seq": 1,
                "type": "future.lifecycle.event",
                "run_id": "factory-run",
                "timestamp": "2026-10-02T00:00:00+00:00",
                "stage": "mystery",
                "agent": None,
                "data": {"candidate": "do-not-guess"},
            }
        ]
    )
    assert receipts[0].kind == "native_event_observed"
    assert receipts[0].phase is None
    assert receipts[0].authority_effect == "none"
    assert receipts[0].evidence_effect == "none"


def test_initial_managed_checkpoint_does_not_fabricate_run_start_or_native_chronology() -> None:
    current = _managed_checkpoint("managed-run")
    before = deepcopy(current)
    receipts = project_managed_transition_receipts(None, current)
    assert current == before
    assert [item.kind for item in receipts] == ["native_event_observed"]
    receipt = receipts[0]
    assert receipt.chronology_strength == "derived_checkpoint_delta"
    assert receipt.source_seq is None
    assert receipt.source_timestamp is None
    assert receipt.previous_checkpoint_hash is None
    assert receipt.checkpoint_hash
    assert receipt.details["projection_order_only"] is True


def test_managed_approval_receipt_never_satisfies_gate_or_becomes_evidence() -> None:
    previous = _managed_checkpoint("managed-run", state="AWAITING_APPROVAL")
    current = _managed_checkpoint(
        "managed-run",
        state="AWAITING_APPROVAL",
        approved_gates=["signoff"],
    )
    receipts = project_managed_transition_receipts(previous, current)
    assert [item.kind for item in receipts] == ["approval_granted"]
    receipt = receipts[0]
    assert receipt.details["gate_id"] == "signoff"
    assert receipt.gate_effect == "none"
    assert receipt.evidence_effect == "none"
    assert receipt.release_effect == "none"
    assert_receipts_non_authoritative(receipts)


def test_managed_completion_does_not_claim_finalize_or_release() -> None:
    previous = _managed_checkpoint(
        "managed-run",
        state="RUNNING",
        stage_runs={"design": ["stage-run-1"]},
    )
    current = _managed_checkpoint(
        "managed-run",
        state="COMPLETED",
        completed_stages=["design"],
        stage_runs={"design": ["stage-run-1"]},
    )
    receipts = project_managed_transition_receipts(previous, current)
    assert [item.kind for item in receipts] == ["stage_completed", "run_completed"]
    run_receipt = receipts[-1]
    assert run_receipt.phase is None
    assert run_receipt.details["managed_completion_is_not_finalize_or_release"] is True
    assert run_receipt.release_effect == "none"


def test_managed_checkpoint_run_ids_must_match() -> None:
    previous = _managed_checkpoint("managed-a")
    current = _managed_checkpoint("managed-b")
    with pytest.raises(ValueError, match="same manager_run_id"):
        project_managed_transition_receipts(previous, current)


def test_managed_stage_run_lineage_cannot_shrink_or_rewrite() -> None:
    previous = _managed_checkpoint(
        "managed-run",
        state="RUNNING",
        stage_runs={"design": ["stage-run-1", "stage-run-2"]},
    )
    current = _managed_checkpoint(
        "managed-run",
        state="RUNNING",
        stage_runs={"design": ["stage-run-2"]},
    )
    with pytest.raises(ValueError, match="stage_run lineage is not append-only"):
        project_managed_transition_receipts(previous, current)
