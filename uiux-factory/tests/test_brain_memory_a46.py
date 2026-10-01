from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.brain_os.contracts import (
    Decision,
    DecisionStatus,
    Hypothesis,
    HypothesisStatus,
    Reversibility,
)
from core.brain_os.memory_contracts import (
    BrainMemoryKind,
    decision_memory,
    hypothesis_memory,
    rationale_memory,
)
from core.memory.brain_memory import BrainMemoryError, BrainMemoryStore


def _hypothesis(*, status: HypothesisStatus = HypothesisStatus.PROPOSED) -> Hypothesis:
    return Hypothesis(
        id="h-memory",
        statement="A clearer hierarchy improves task confidence",
        risk="normal",
        confidence=0.6,
        validation_method="Usability test",
        status=status,
        evidence_refs=["ev-h"] if status is HypothesisStatus.VALIDATED else [],
    )


def _decision(*, chosen: str = "Primary task first") -> Decision:
    return Decision(
        id="d-memory",
        question="Which hierarchy should lead?",
        chosen=chosen,
        alternatives=["Feature-first"],
        evidence_refs=["ev-d"],
        tradeoff="Secondary features are less prominent",
        reversibility=Reversibility.REVERSIBLE,
        confidence=0.8,
        status=DecisionStatus.SELECTED,
        owner="human",
        selected_by="product-owner",
    )


def test_a46_typed_memory_adapters_preserve_source_contracts_and_provenance(tmp_path: Path) -> None:
    scope = str(tmp_path.resolve())
    hypothesis = _hypothesis(status=HypothesisStatus.VALIDATED)
    decision = _decision()

    h_record = hypothesis_memory(
        hypothesis,
        project_scope=scope,
        source_run_id="run-1",
        created_at="2026-10-02T00:00:00Z",
        tags=["nova", "product"],
    )
    d_record = decision_memory(
        decision,
        project_scope=scope,
        source_run_id="run-1",
        created_at="2026-10-02T00:00:01Z",
    )
    r_record = rationale_memory(
        source_ref="rationale-nav",
        subject="Navigation hierarchy",
        rationale="Prioritize the primary task because direct user evidence supports it.",
        project_scope=scope,
        source_run_id="run-1",
        created_at="2026-10-02T00:00:02Z",
        evidence_refs=["ev-r"],
        hypothesis_refs=[hypothesis.id],
        decision_refs=[decision.id],
    )

    assert h_record.hypothesis == hypothesis
    assert d_record.decision == decision
    assert r_record.hypothesis_refs == [hypothesis.id]
    assert r_record.decision_refs == [decision.id]
    for record in (h_record, d_record, r_record):
        assert record.advisory_only is True
        assert record.authority_effect == "none"
        assert record.gate_effect == "none"
        assert record.evidence_effect == "none"
        assert record.current_run_evidence is False


def test_a46_store_round_trip_upserts_same_identity_and_preserves_project_scope(tmp_path: Path) -> None:
    store = BrainMemoryStore(tmp_path, {"brain_memory": {"max_records": 10}})
    scope = str(tmp_path.resolve())
    first = decision_memory(
        _decision(chosen="Primary task first"),
        project_scope=scope,
        source_run_id="run-1",
        created_at="2026-10-02T00:00:00Z",
    )
    second = decision_memory(
        _decision(chosen="Primary workflow first"),
        project_scope=scope,
        source_run_id="run-2",
        created_at="2026-10-02T00:01:00Z",
    )

    assert first.id == second.id
    assert store.record(first) is True
    assert store.record(second) is True

    loaded = store.load()
    assert len(loaded) == 1
    assert loaded[0].source_run_id == "run-2"
    assert loaded[0].project_scope == scope
    assert loaded[0].decision.chosen == "Primary workflow first"


def test_a46_recall_is_bounded_advisory_and_excludes_current_run(tmp_path: Path) -> None:
    store = BrainMemoryStore(
        tmp_path,
        {"brain_memory": {"max_records": 10, "max_recall_records": 3}},
    )
    scope = str(tmp_path.resolve())
    store.record(
        hypothesis_memory(
            _hypothesis(),
            project_scope=scope,
            source_run_id="old-run",
            created_at="2026-10-01T00:00:00Z",
            tags=["fintech"],
        )
    )
    store.record(
        rationale_memory(
            source_ref="r-current",
            subject="Current thought",
            rationale="Current-run rationale must not be recalled as historical context.",
            project_scope=scope,
            source_run_id="current-run",
            created_at="2026-10-02T00:00:00Z",
            tags=["fintech"],
        )
    )

    recalled = store.recall(
        tags=["fintech"],
        exclude_run_id="current-run",
        limit=2,
    )

    assert len(recalled) == 1
    assert recalled[0]["kind"] == BrainMemoryKind.HYPOTHESIS.value
    assert recalled[0]["source_run_id"] == "old-run"
    assert recalled[0]["advisory_only"] is True
    assert recalled[0]["current_run_evidence"] is False
    assert recalled[0]["authority_effect"] == "none"
    assert recalled[0]["gate_effect"] == "none"
    assert recalled[0]["evidence_effect"] == "none"


def test_a46_store_rejects_cross_project_record(tmp_path: Path) -> None:
    store = BrainMemoryStore(tmp_path)
    record = hypothesis_memory(
        _hypothesis(),
        project_scope=str((tmp_path / "other").resolve()),
        source_run_id="run-1",
        created_at="2026-10-02T00:00:00Z",
    )

    with pytest.raises(BrainMemoryError, match="project_scope"):
        store.record(record)


def test_a46_store_fails_closed_on_unknown_or_malformed_persisted_record(tmp_path: Path) -> None:
    store = BrainMemoryStore(tmp_path)
    store.memory_dir.mkdir(parents=True)
    store.path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "records": [
                    {
                        "kind": "mystery",
                        "id": "x",
                        "project_scope": str(tmp_path.resolve()),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(BrainMemoryError, match="unsupported brain memory kind"):
        store.load()


def test_a46_recall_limit_is_policy_bounded(tmp_path: Path) -> None:
    store = BrainMemoryStore(tmp_path, {"brain_memory": {"max_records": 5, "max_recall_records": 2}})
    with pytest.raises(ValueError, match="max_recall_records"):
        store.recall(limit=3)


def test_a46_store_refuses_symlink_memory_path(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    runs = tmp_path / ".uiux-agent-runs"
    runs.mkdir()
    (runs / "memory").symlink_to(outside, target_is_directory=True)

    store = BrainMemoryStore(tmp_path)
    with pytest.raises(BrainMemoryError, match="symlink"):
        store.load()


def test_a46_memory_source_has_no_flow_gate_execution_or_release_authority() -> None:
    factory = Path(__file__).resolve().parents[1]
    contract_source = (factory / "core" / "brain_os" / "memory_contracts.py").read_text(encoding="utf-8")
    store_source = (factory / "core" / "memory" / "brain_memory.py").read_text(encoding="utf-8")
    combined = contract_source + "\n" + store_source
    forbidden = (
        "FlowPlanner(",
        "ManagedFlowController",
        "ProviderManagedRunner",
        "gate_evidence_errors",
        "run_target_command",
        "release_action",
        "ProductionReleaseController",
        "merge_pull_request",
    )
    for token in forbidden:
        assert token not in combined
