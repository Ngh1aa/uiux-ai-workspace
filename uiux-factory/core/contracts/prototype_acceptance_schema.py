from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


VerificationOutcome = Literal[
    "passed",
    "failed",
    "inapplicable",
    "cantTell",
    "untested",
]

VerificationMode = Literal[
    "artifact",
    "browser",
    "vision",
    "interaction",
    "performance",
    "hybrid",
    "manual",
]

AutomationStatus = Literal[
    "implemented",
    "planned",
    "manual",
]


class PrototypeRequirement(BaseModel):
    id: str
    stage: int = Field(ge=1, le=7)
    title: str
    requirement: str
    source: str = "checklist-prototype-ui-ux.md"
    verification_mode: VerificationMode
    evaluator: str
    automation_status: AutomationStatus = "planned"
    machine_required: bool = False
    final_required: bool = True
    severity: Literal["P0", "P1", "P2"] = "P1"
    applicability: str = "Applies when the described UI, state, flow or design decision exists."
    expectations: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    owner_stage: str = "visual_qa"


class EvidenceRef(BaseModel):
    kind: str
    path: str
    sha256: str
    evaluator: str
    source_digest: str
    route: str | None = None
    viewport: str | None = None


class RequirementResult(BaseModel):
    requirement_id: str
    outcome: VerificationOutcome
    rationale: str
    evidence: list[EvidenceRef] = Field(default_factory=list)
    stale_evidence: bool = False


class AcceptanceSummary(BaseModel):
    total: int
    passed: int = 0
    failed: int = 0
    inapplicable: int = 0
    cantTell: int = 0
    untested: int = 0
    implemented: int = 0
    planned: int = 0
    manual: int = 0


class PrototypeAcceptanceReport(BaseModel):
    schema_version: str = "1.0.0"
    checklist_version: str = "prototype-ui-ux-56-v1"
    run_id: str
    project_dir: str
    project_digest: str
    browser_report_path: str
    visual_critic_path: str
    requirements: list[PrototypeRequirement]
    results: list[RequirementResult]
    summary: AcceptanceSummary
    machine_status: Literal["passed", "blocked"]
    final_status: Literal[
        "approved",
        "human_review_required",
        "blocked",
    ]
    blocking_requirement_ids: list[str] = Field(default_factory=list)
    human_review_requirement_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    generated_by: str = "PrototypeAcceptanceEvaluatorV1"
