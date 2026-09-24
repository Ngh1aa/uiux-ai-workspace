from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class EvidenceOutcome(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    INAPPLICABLE = "inapplicable"
    CANT_TELL = "cantTell"
    UNTESTED = "untested"


class VerificationMode(str, Enum):
    ANALYSIS = "analysis"
    INSPECTION = "inspection"
    DEMONSTRATION = "demonstration"
    TEST = "test"
    VISION = "vision"
    HYBRID = "hybrid"
    MANUAL = "manual"


class RequirementDefinition(BaseModel):
    id: str
    category: str
    title: str
    requirement: str
    source: str = "prototype-output-checklist"
    source_version: str = "1.0"
    owner_stage: str
    severity: Literal["P0", "P1", "P2"] = "P1"
    verification_mode: VerificationMode
    machine_gate: bool = True
    final_gate: bool = True
    applicability: str
    expectations: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    evaluator: str | None = None


class EvidenceReference(BaseModel):
    kind: str
    path: str
    sha256: str | None = None
    run_id: str | None = None
    project_digest: str | None = None
    route: str | None = None
    viewport: str | None = None
    evaluator: str | None = None
    evaluator_version: str | None = None
    note: str | None = None


class RequirementResult(BaseModel):
    requirement_id: str
    outcome: EvidenceOutcome
    applicable: bool | None = None
    test_targets: list[str] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)
    rationale: str


class EvidenceSummary(BaseModel):
    total: int
    passed: int
    failed: int
    inapplicable: int
    cant_tell: int
    untested: int
    machine_blockers: int
    final_blockers: int


class PrototypeAcceptanceReport(BaseModel):
    schema_version: int = 2
    registry_version: str
    run_id: str
    project_dir: str
    project_digest: str
    generated_at: str
    requirements: list[RequirementResult]
    summary: EvidenceSummary
    machine_status: Literal["passed", "blocked"]
    final_status: Literal["approved", "human_review_required", "blocked"]
    stale_evidence_count: int = 0
    limitations: list[str] = Field(default_factory=list)
