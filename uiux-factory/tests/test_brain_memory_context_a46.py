from __future__ import annotations

from pathlib import Path

import pytest

from core.brain_os.adapters.flow_selection import FlowSelectionDecision, SurfaceSource
from core.brain_os.adapters.memory_context import (
    MemoryReasoningContext,
    MemoryRecallItem,
    attach_memory_after_flow_selection,
)
from core.brain_os.contracts import Hypothesis
from core.brain_os.memory_contracts import hypothesis_memory, rationale_memory
from core.memory.brain_memory import BrainMemoryStore


def _flow() -> FlowSelectionDecision:
    return FlowSelectionDecision(
        change_surface="PAGE",
        surface_source=SurfaceSource.TASK_CONTRACT,
        flow_id="page-ui-work",
        flow_source="skills_UIUX/flows/page-ui-work.json",
        score=100,
        rationale="Canonical FlowPlanner already selected the page flow.",
    )


def _hypothesis() -> Hypothesis:
    return Hypothesis(
        id="h-old",
        statement="Task-first hierarchy improves comprehension",
        risk="normal",
        confidence=0.5,
        validation_method="Usability test",
    )


def test_a46_memory_context_requires_existing_flow_selection_and_preserves_it(tmp_path: Path) -> None:
    store = BrainMemoryStore(tmp_path)
    scope = str(tmp_path.resolve())
    store.record(
        hypothesis_memory(
            _hypothesis(),
            project_scope=scope,
            source_run_id="old-run",
            created_at="2026-10-01T00:00:00Z",
            tags=["product"],
        )
    )
    flow = _flow()
    before = flow.model_dump()

    context = attach_memory_after_flow_selection(
        store=store,
        flow_selection=flow,
        current_run_id="current-run",
        tags=["product"],
    )

    assert flow.model_dump() == before
    assert context.flow_selection == flow
    assert context.attached_after_flow_selection is True
    assert context.flow_effect == "none"
    assert len(context.memories) == 1
    assert context.memories[0].source_run_id == "old-run"


def test_a46_memory_context_excludes_current_run_records(tmp_path: Path) -> None:
    store = BrainMemoryStore(tmp_path)
    scope = str(tmp_path.resolve())
    store.record(
        rationale_memory(
            source_ref="old-rationale",
            subject="Old rationale",
            rationale="Historical context",
            project_scope=scope,
            source_run_id="old-run",
            created_at="2026-10-01T00:00:00Z",
        )
    )
    store.record(
        rationale_memory(
            source_ref="current-rationale",
            subject="Current rationale",
            rationale="Must not re-enter the same run as history",
            project_scope=scope,
            source_run_id="current-run",
            created_at="2026-10-02T00:00:00Z",
        )
    )

    context = attach_memory_after_flow_selection(
        store=store,
        flow_selection=_flow(),
        current_run_id="current-run",
    )

    assert [item.source_run_id for item in context.memories] == ["old-run"]
    assert all(item.current_run_evidence is False for item in context.memories)


def test_a46_memory_context_retains_no_authority_gate_or_evidence_effect(tmp_path: Path) -> None:
    store = BrainMemoryStore(tmp_path)
    context = attach_memory_after_flow_selection(
        store=store,
        flow_selection=_flow(),
        current_run_id="run-empty",
    )

    assert context.memories == []
    assert context.advisory_only is True
    assert context.flow_effect == "none"
    assert context.authority_effect == "none"
    assert context.gate_effect == "none"
    assert context.evidence_effect == "none"
    assert not hasattr(context, "passed")


def test_a46_context_rejects_current_run_memory_even_if_constructed_manually() -> None:
    item = MemoryRecallItem(
        memory_ref="BM-1",
        kind="rationale",
        source_run_id="same-run",
        source_ref="r1",
        created_at="2026-10-02T00:00:00Z",
        payload={"subject": "x", "rationale": "y"},
    )

    with pytest.raises(ValueError, match="current-run memory"):
        MemoryReasoningContext(
            current_run_id="same-run",
            flow_selection=_flow(),
            memories=[item],
        )


def test_a46_attach_requires_current_run_id(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="current_run_id"):
        attach_memory_after_flow_selection(
            store=BrainMemoryStore(tmp_path),
            flow_selection=_flow(),
            current_run_id=" ",
        )


def test_a46_memory_context_adapter_has_no_routing_execution_gate_or_release_owner() -> None:
    factory = Path(__file__).resolve().parents[1]
    source = (
        factory / "core" / "brain_os" / "adapters" / "memory_context.py"
    ).read_text(encoding="utf-8")
    forbidden = (
        "FlowPlanner(",
        "select_canonical_flow(",
        "propose_bounded_escalation(",
        "ManagedFlowController",
        "ProviderManagedRunner",
        "gate_evidence_errors",
        "run_target_command",
        "release_action",
        "ProductionReleaseController",
        "merge_pull_request",
    )
    for token in forbidden:
        assert token not in source
