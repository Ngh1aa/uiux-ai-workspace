from __future__ import annotations

from typing import Any, Iterable, Literal

from pydantic import Field, model_validator

from core.brain_os.adapters.flow_selection import FlowSelectionDecision
from core.brain_os.contracts import BrainContractModel
from core.brain_os.memory_contracts import BrainMemoryKind
from core.memory.brain_memory import BrainMemoryStore


class MemoryRecallItem(BrainContractModel):
    memory_ref: str = Field(min_length=1, max_length=128)
    kind: Literal["rationale", "hypothesis", "decision"]
    source_run_id: str = Field(min_length=1, max_length=128)
    source_ref: str = Field(min_length=1, max_length=256)
    evidence_refs: list[str] = Field(default_factory=list, max_length=100)
    tags: list[str] = Field(default_factory=list, max_length=50)
    created_at: str = Field(min_length=1, max_length=128)
    payload: dict[str, Any]
    advisory_only: Literal[True] = True
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"
    current_run_evidence: Literal[False] = False


class MemoryReasoningContext(BrainContractModel):
    """Historical advisory memory attached after canonical flow selection."""

    schema_version: Literal["brain-memory-context.v1"] = "brain-memory-context.v1"
    current_run_id: str = Field(min_length=1, max_length=128)
    flow_selection: FlowSelectionDecision
    memories: list[MemoryRecallItem] = Field(default_factory=list, max_length=500)
    attached_after_flow_selection: Literal[True] = True
    advisory_only: Literal[True] = True
    flow_effect: Literal["none"] = "none"
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"

    @model_validator(mode="after")
    def _validate_historical_only(self) -> "MemoryReasoningContext":
        current = self.current_run_id
        if any(item.source_run_id == current for item in self.memories):
            raise ValueError("memory reasoning context cannot include current-run memory")
        if any(item.current_run_evidence for item in self.memories):
            raise ValueError("memory reasoning context cannot contain current-run evidence")
        return self


def attach_memory_after_flow_selection(
    *,
    store: BrainMemoryStore,
    flow_selection: FlowSelectionDecision,
    current_run_id: str,
    kinds: Iterable[BrainMemoryKind | str] = (),
    tags: Iterable[str] = (),
    source_refs: Iterable[str] = (),
    limit: int | None = None,
) -> MemoryReasoningContext:
    """Recall project memory only after a canonical flow decision already exists.

    Requiring a `FlowSelectionDecision` makes the ordering explicit: historical memory
    can enrich reasoning after routing, but this adapter has no API to select/replan a
    flow or change task authority.
    """

    run_id = str(current_run_id).strip()
    if not run_id:
        raise ValueError("current_run_id is required for historical memory isolation")

    raw = store.recall(
        kinds=kinds,
        tags=tags,
        source_refs=source_refs,
        exclude_run_id=run_id,
        limit=limit,
    )
    memories = [MemoryRecallItem.model_validate(item) for item in raw]
    return MemoryReasoningContext(
        current_run_id=run_id,
        flow_selection=flow_selection,
        memories=memories,
    )
