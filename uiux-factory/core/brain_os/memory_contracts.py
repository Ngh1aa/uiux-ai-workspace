from __future__ import annotations

import hashlib
from enum import Enum
from typing import Literal

from pydantic import Field, field_validator

from core.brain_os.contracts import BrainContractModel, Decision, Hypothesis


class BrainMemoryKind(str, Enum):
    RATIONALE = "rationale"
    HYPOTHESIS = "hypothesis"
    DECISION = "decision"


def _clean_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


def memory_id(*, project_scope: str, kind: BrainMemoryKind, source_ref: str) -> str:
    raw = f"{project_scope.strip()}\n{kind.value}\n{source_ref.strip()}".encode("utf-8")
    return f"BM-{hashlib.sha256(raw).hexdigest()[:20]}"


class BrainMemoryBase(BrainContractModel):
    schema_version: Literal["brain-memory.v1"] = "brain-memory.v1"
    id: str = Field(min_length=1, max_length=128)
    kind: BrainMemoryKind
    project_scope: str = Field(min_length=1, max_length=512)
    source_run_id: str = Field(min_length=1, max_length=128)
    source_ref: str = Field(min_length=1, max_length=256)
    evidence_refs: list[str] = Field(default_factory=list, max_length=100)
    tags: list[str] = Field(default_factory=list, max_length=50)
    created_at: str = Field(min_length=1, max_length=128)
    advisory_only: Literal[True] = True
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"
    current_run_evidence: Literal[False] = False

    @field_validator("evidence_refs", "tags")
    @classmethod
    def _normalize_lists(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)


class RationaleMemoryRecord(BrainMemoryBase):
    kind: Literal[BrainMemoryKind.RATIONALE] = BrainMemoryKind.RATIONALE
    subject: str = Field(min_length=1, max_length=2000)
    rationale: str = Field(min_length=1, max_length=6000)
    hypothesis_refs: list[str] = Field(default_factory=list, max_length=100)
    decision_refs: list[str] = Field(default_factory=list, max_length=100)

    @field_validator("hypothesis_refs", "decision_refs")
    @classmethod
    def _normalize_refs(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)


class HypothesisMemoryRecord(BrainMemoryBase):
    kind: Literal[BrainMemoryKind.HYPOTHESIS] = BrainMemoryKind.HYPOTHESIS
    hypothesis: Hypothesis


class DecisionMemoryRecord(BrainMemoryBase):
    kind: Literal[BrainMemoryKind.DECISION] = BrainMemoryKind.DECISION
    decision: Decision


BrainMemoryRecord = RationaleMemoryRecord | HypothesisMemoryRecord | DecisionMemoryRecord


def hypothesis_memory(
    hypothesis: Hypothesis,
    *,
    project_scope: str,
    source_run_id: str,
    created_at: str,
    tags: list[str] | None = None,
) -> HypothesisMemoryRecord:
    return HypothesisMemoryRecord(
        id=memory_id(
            project_scope=project_scope,
            kind=BrainMemoryKind.HYPOTHESIS,
            source_ref=hypothesis.id,
        ),
        project_scope=project_scope,
        source_run_id=source_run_id,
        source_ref=hypothesis.id,
        evidence_refs=list(hypothesis.evidence_refs),
        tags=tags or [],
        created_at=created_at,
        hypothesis=hypothesis,
    )


def decision_memory(
    decision: Decision,
    *,
    project_scope: str,
    source_run_id: str,
    created_at: str,
    tags: list[str] | None = None,
) -> DecisionMemoryRecord:
    return DecisionMemoryRecord(
        id=memory_id(
            project_scope=project_scope,
            kind=BrainMemoryKind.DECISION,
            source_ref=decision.id,
        ),
        project_scope=project_scope,
        source_run_id=source_run_id,
        source_ref=decision.id,
        evidence_refs=list(decision.evidence_refs),
        tags=tags or [],
        created_at=created_at,
        decision=decision,
    )


def rationale_memory(
    *,
    source_ref: str,
    subject: str,
    rationale: str,
    project_scope: str,
    source_run_id: str,
    created_at: str,
    evidence_refs: list[str] | None = None,
    hypothesis_refs: list[str] | None = None,
    decision_refs: list[str] | None = None,
    tags: list[str] | None = None,
) -> RationaleMemoryRecord:
    return RationaleMemoryRecord(
        id=memory_id(
            project_scope=project_scope,
            kind=BrainMemoryKind.RATIONALE,
            source_ref=source_ref,
        ),
        project_scope=project_scope,
        source_run_id=source_run_id,
        source_ref=source_ref,
        evidence_refs=evidence_refs or [],
        hypothesis_refs=hypothesis_refs or [],
        decision_refs=decision_refs or [],
        tags=tags or [],
        created_at=created_at,
        subject=subject,
        rationale=rationale,
    )
