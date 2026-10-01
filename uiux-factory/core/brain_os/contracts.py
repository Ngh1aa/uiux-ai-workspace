from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


BRAIN_CONTRACT_VERSION = "1.0"

ChangeSurface = Literal["MICRO", "FOCUSED", "PAGE", "REDESIGN", "PRODUCT"]
AuthorityLevel = Literal["unspecified", "read_only", "branch_write", "external_write", "release"]
DecisionOwner = Literal["brain_advisory", "human", "runtime_contract", "joint"]


class UncertaintyState(str, Enum):
    KNOWN = "KNOWN"
    INFERRED = "INFERRED"
    PROPOSED = "PROPOSED"
    VALIDATED = "VALIDATED"
    BLOCKED = "BLOCKED"
    CONFLICTED = "CONFLICTED"


class HypothesisStatus(str, Enum):
    PROPOSED = "PROPOSED"
    TESTING = "TESTING"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


class DecisionStatus(str, Enum):
    PROPOSED = "PROPOSED"
    SELECTED = "SELECTED"
    DEFERRED = "DEFERRED"
    SUPERSEDED = "SUPERSEDED"
    BLOCKED = "BLOCKED"


class Reversibility(str, Enum):
    REVERSIBLE = "REVERSIBLE"
    COSTLY = "COSTLY"
    IRREVERSIBLE = "IRREVERSIBLE"


def _clean_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


class BrainContractModel(BaseModel):
    """Strict immutable base for Brain OS control-plane data contracts."""

    model_config = ConfigDict(extra="forbid", frozen=True, use_enum_values=False)


class Uncertainty(BrainContractModel):
    id: str = Field(min_length=1, max_length=128)
    subject: str = Field(min_length=1, max_length=2000)
    state: UncertaintyState
    rationale: str = Field(min_length=1, max_length=6000)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_refs: list[str] = Field(default_factory=list, max_length=100)
    blockers: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("evidence_refs", "blockers")
    @classmethod
    def _normalize_lists(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)

    @model_validator(mode="after")
    def _validate_state_requirements(self) -> "Uncertainty":
        if self.state is UncertaintyState.VALIDATED and not self.evidence_refs:
            raise ValueError("VALIDATED uncertainty requires at least one evidence reference")
        if self.state is UncertaintyState.BLOCKED and not self.blockers:
            raise ValueError("BLOCKED uncertainty requires at least one blocker")
        return self


class Hypothesis(BrainContractModel):
    id: str = Field(min_length=1, max_length=128)
    statement: str = Field(min_length=1, max_length=6000)
    risk: str = Field(min_length=1, max_length=128)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    validation_method: str = Field(min_length=1, max_length=2000)
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    assumptions: list[str] = Field(default_factory=list, max_length=100)
    evidence_refs: list[str] = Field(default_factory=list, max_length=100)
    blockers: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("assumptions", "evidence_refs", "blockers")
    @classmethod
    def _normalize_lists(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)

    @model_validator(mode="after")
    def _validate_status_requirements(self) -> "Hypothesis":
        if self.status in {HypothesisStatus.VALIDATED, HypothesisStatus.REJECTED} and not self.evidence_refs:
            raise ValueError(f"{self.status.value} hypothesis requires at least one evidence reference")
        if self.status is HypothesisStatus.BLOCKED and not self.blockers:
            raise ValueError("BLOCKED hypothesis requires at least one blocker")
        return self


class Decision(BrainContractModel):
    id: str = Field(min_length=1, max_length=128)
    question: str = Field(min_length=1, max_length=4000)
    chosen: str = Field(min_length=1, max_length=4000)
    alternatives: list[str] = Field(default_factory=list, max_length=50)
    evidence_refs: list[str] = Field(default_factory=list, max_length=100)
    tradeoff: str = Field(min_length=1, max_length=6000)
    reversibility: Reversibility
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    status: DecisionStatus = DecisionStatus.PROPOSED
    owner: DecisionOwner = "brain_advisory"
    selected_by: str | None = Field(default=None, max_length=256)
    blockers: list[str] = Field(default_factory=list, max_length=50)
    supersedes: str | None = Field(default=None, max_length=128)

    @field_validator("alternatives", "evidence_refs", "blockers")
    @classmethod
    def _normalize_lists(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)

    @field_validator("selected_by", "supersedes")
    @classmethod
    def _normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @model_validator(mode="after")
    def _validate_status_requirements(self) -> "Decision":
        if self.status is DecisionStatus.SELECTED and not self.selected_by:
            raise ValueError("SELECTED decision requires selected_by provenance")
        if self.status is DecisionStatus.BLOCKED and not self.blockers:
            raise ValueError("BLOCKED decision requires at least one blocker")
        if self.status is DecisionStatus.SUPERSEDED and not self.supersedes:
            raise ValueError("SUPERSEDED decision requires supersedes reference")
        return self


class BrainTaskFrame(BrainContractModel):
    """Reasoning frame derived from, but not replacing, the canonical Task Contract.

    `authority` is descriptive context inherited from the canonical runtime contract. The
    frame does not grant, elevate or enforce execution authority.
    """

    schema_version: str = BRAIN_CONTRACT_VERSION
    frame_id: str = Field(min_length=1, max_length=128)
    goal: str = Field(min_length=1, max_length=12000)
    intent: str = Field(min_length=1, max_length=256)
    domain: str = Field(min_length=1, max_length=256)
    product_archetype: str = Field(min_length=1, max_length=256)
    change_surface: ChangeSurface
    validation_lane: str = Field(min_length=1, max_length=256)
    authority: AuthorityLevel = "unspecified"
    risk: str = Field(min_length=1, max_length=128)
    constraints: list[str] = Field(default_factory=list, max_length=200)
    preserve: list[str] = Field(default_factory=list, max_length=100)
    forbidden: list[str] = Field(default_factory=list, max_length=100)
    success_criteria: list[str] = Field(default_factory=list, max_length=100)
    evidence_refs: list[str] = Field(default_factory=list, max_length=100)
    uncertainties: list[Uncertainty] = Field(default_factory=list, max_length=100)
    source_task_contract_version: str = Field(min_length=1, max_length=64)
    source_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    source_inference_evidence: list[str] = Field(default_factory=list, max_length=100)

    @field_validator(
        "constraints",
        "preserve",
        "forbidden",
        "success_criteria",
        "evidence_refs",
        "source_inference_evidence",
    )
    @classmethod
    def _normalize_string_lists(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)

    @model_validator(mode="after")
    def _validate_frame_requirements(self) -> "BrainTaskFrame":
        uncertainty_ids = [item.id for item in self.uncertainties]
        if len(uncertainty_ids) != len(set(uncertainty_ids)):
            raise ValueError("BrainTaskFrame uncertainty ids must be unique")
        return self
