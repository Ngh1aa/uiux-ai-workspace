from __future__ import annotations

from enum import Enum

from pydantic import Field, field_validator, model_validator

from core.brain_os.contracts import BrainContractModel


CRITIQUE_REPAIR_CONTRACT_VERSION = "1.0"


class CritiqueSeverity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class CritiqueIssueStatus(str, Enum):
    OBSERVED = "OBSERVED"
    CONFIRMED = "CONFIRMED"
    BLOCKED = "BLOCKED"
    RESOLVED = "RESOLVED"


class RootCauseStatus(str, Enum):
    PROPOSED = "PROPOSED"
    SUPPORTED = "SUPPORTED"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


class RepairDirectiveStatus(str, Enum):
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    DEFERRED = "DEFERRED"
    BLOCKED = "BLOCKED"


class RetestStatus(str, Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


def _clean_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


class CritiqueIssue(BrainContractModel):
    """One evidence-grounded critique finding.

    OBSERVED may represent an early critic observation. CONFIRMED and RESOLVED are
    stronger claims and therefore require evidence. RESOLVED additionally requires a
    retest reference so model prose alone can never close an issue.
    """

    schema_version: str = CRITIQUE_REPAIR_CONTRACT_VERSION
    id: str = Field(min_length=1, max_length=128)
    critic: str = Field(min_length=1, max_length=256)
    category: str = Field(min_length=1, max_length=256)
    severity: CritiqueSeverity
    status: CritiqueIssueStatus = CritiqueIssueStatus.OBSERVED
    summary: str = Field(min_length=1, max_length=4000)
    rationale: str = Field(min_length=1, max_length=8000)
    evidence_refs: list[str] = Field(default_factory=list, max_length=100)
    affected_artifacts: list[str] = Field(default_factory=list, max_length=100)
    blockers: list[str] = Field(default_factory=list, max_length=50)
    retest_refs: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("evidence_refs", "affected_artifacts", "blockers", "retest_refs")
    @classmethod
    def _normalize_lists(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)

    @model_validator(mode="after")
    def _validate_status_requirements(self) -> "CritiqueIssue":
        if self.status in {CritiqueIssueStatus.CONFIRMED, CritiqueIssueStatus.RESOLVED} and not self.evidence_refs:
            raise ValueError(f"{self.status.value} critique issue requires at least one evidence reference")
        if self.status is CritiqueIssueStatus.BLOCKED and not self.blockers:
            raise ValueError("BLOCKED critique issue requires at least one blocker")
        if self.status is CritiqueIssueStatus.RESOLVED and not self.retest_refs:
            raise ValueError("RESOLVED critique issue requires at least one retest reference")
        return self


class RootCause(BrainContractModel):
    """A bounded causal explanation linking one or more critique issues."""

    schema_version: str = CRITIQUE_REPAIR_CONTRACT_VERSION
    id: str = Field(min_length=1, max_length=128)
    issue_ids: list[str] = Field(min_length=1, max_length=100)
    statement: str = Field(min_length=1, max_length=6000)
    status: RootCauseStatus = RootCauseStatus.PROPOSED
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_refs: list[str] = Field(default_factory=list, max_length=100)
    assumptions: list[str] = Field(default_factory=list, max_length=100)
    blockers: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("issue_ids", "evidence_refs", "assumptions", "blockers")
    @classmethod
    def _normalize_lists(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)

    @model_validator(mode="after")
    def _validate_status_requirements(self) -> "RootCause":
        if not self.issue_ids:
            raise ValueError("RootCause requires at least one critique issue reference")
        if self.status in {RootCauseStatus.SUPPORTED, RootCauseStatus.REJECTED} and not self.evidence_refs:
            raise ValueError(f"{self.status.value} root cause requires at least one evidence reference")
        if self.status is RootCauseStatus.BLOCKED and not self.blockers:
            raise ValueError("BLOCKED root cause requires at least one blocker")
        return self


class RepairDirective(BrainContractModel):
    """A proposed or accepted repair instruction, never proof that repair executed."""

    schema_version: str = CRITIQUE_REPAIR_CONTRACT_VERSION
    id: str = Field(min_length=1, max_length=128)
    issue_ids: list[str] = Field(min_length=1, max_length=100)
    root_cause_ids: list[str] = Field(min_length=1, max_length=100)
    target_stage: str = Field(min_length=1, max_length=128)
    instruction: str = Field(min_length=1, max_length=8000)
    rationale: str = Field(min_length=1, max_length=8000)
    expected_outcome: str = Field(min_length=1, max_length=4000)
    priority: CritiqueSeverity = CritiqueSeverity.P1
    status: RepairDirectiveStatus = RepairDirectiveStatus.PROPOSED
    constraints: list[str] = Field(default_factory=list, max_length=100)
    evidence_refs: list[str] = Field(default_factory=list, max_length=100)
    blockers: list[str] = Field(default_factory=list, max_length=50)
    accepted_by: str | None = Field(default=None, max_length=256)
    defer_reason: str | None = Field(default=None, max_length=2000)
    requires_human_approval: bool = False

    @field_validator("issue_ids", "root_cause_ids", "constraints", "evidence_refs", "blockers")
    @classmethod
    def _normalize_lists(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)

    @field_validator("accepted_by", "defer_reason")
    @classmethod
    def _normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @model_validator(mode="after")
    def _validate_status_requirements(self) -> "RepairDirective":
        if not self.issue_ids:
            raise ValueError("RepairDirective requires at least one critique issue reference")
        if not self.root_cause_ids:
            raise ValueError("RepairDirective requires at least one root cause reference")
        if self.status is RepairDirectiveStatus.ACCEPTED and not self.accepted_by:
            raise ValueError("ACCEPTED repair directive requires accepted_by provenance")
        if self.status is RepairDirectiveStatus.DEFERRED and not self.defer_reason:
            raise ValueError("DEFERRED repair directive requires defer_reason")
        if self.status is RepairDirectiveStatus.BLOCKED and not self.blockers:
            raise ValueError("BLOCKED repair directive requires at least one blocker")
        return self


class RetestRequirement(BrainContractModel):
    """Defines what evidence is required after a repair before an issue may close."""

    schema_version: str = CRITIQUE_REPAIR_CONTRACT_VERSION
    id: str = Field(min_length=1, max_length=128)
    repair_directive_id: str = Field(min_length=1, max_length=128)
    stage: str = Field(min_length=1, max_length=128)
    evidence_types: list[str] = Field(min_length=1, max_length=50)
    acceptance_criteria: list[str] = Field(min_length=1, max_length=100)
    status: RetestStatus = RetestStatus.PENDING
    evidence_refs: list[str] = Field(default_factory=list, max_length=100)
    blockers: list[str] = Field(default_factory=list, max_length=50)

    @field_validator("evidence_types", "acceptance_criteria", "evidence_refs", "blockers")
    @classmethod
    def _normalize_lists(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)

    @model_validator(mode="after")
    def _validate_status_requirements(self) -> "RetestRequirement":
        if not self.evidence_types:
            raise ValueError("RetestRequirement requires at least one evidence type")
        if not self.acceptance_criteria:
            raise ValueError("RetestRequirement requires at least one acceptance criterion")
        if self.status in {RetestStatus.PASSED, RetestStatus.FAILED} and not self.evidence_refs:
            raise ValueError(f"{self.status.value} retest requires at least one evidence reference")
        if self.status is RetestStatus.BLOCKED and not self.blockers:
            raise ValueError("BLOCKED retest requires at least one blocker")
        return self


class RepairLink(BrainContractModel):
    """Traceable lineage bundle connecting critique to repair and required retest."""

    schema_version: str = CRITIQUE_REPAIR_CONTRACT_VERSION
    id: str = Field(min_length=1, max_length=128)
    issue_ids: list[str] = Field(min_length=1, max_length=100)
    root_cause_ids: list[str] = Field(min_length=1, max_length=100)
    repair_directive_ids: list[str] = Field(min_length=1, max_length=100)
    retest_requirement_ids: list[str] = Field(min_length=1, max_length=100)
    rationale: str = Field(min_length=1, max_length=6000)

    @field_validator(
        "issue_ids",
        "root_cause_ids",
        "repair_directive_ids",
        "retest_requirement_ids",
    )
    @classmethod
    def _normalize_lists(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)

    @model_validator(mode="after")
    def _validate_lineage(self) -> "RepairLink":
        if not self.issue_ids:
            raise ValueError("RepairLink requires at least one critique issue reference")
        if not self.root_cause_ids:
            raise ValueError("RepairLink requires at least one root cause reference")
        if not self.repair_directive_ids:
            raise ValueError("RepairLink requires at least one repair directive reference")
        if not self.retest_requirement_ids:
            raise ValueError("RepairLink requires at least one retest requirement reference")
        return self
