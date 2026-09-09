from typing import Literal

from pydantic import BaseModel, Field


class VisualScore(BaseModel):
    visual: int
    hierarchy: int
    typography: int
    spacing: int
    responsive: int
    brand_fidelity: int
    accessibility: int
    generic_ai_feel: int
    overall: int


class VisualIssue(BaseModel):
    severity: Literal["P0", "P1", "P2"]
    category: str
    route: str
    viewport: str
    evidence: str
    recommendation: str


class RepairDirective(BaseModel):
    priority: int
    route: str
    target: str
    instruction: str
    success_criteria: str


class VisualCriticGate(BaseModel):
    screenshots_consumed: bool = False
    browser_report_consumed: bool = False
    skills_loaded: bool = False
    score_generated: bool = False
    repair_directives_generated: bool = False
    ready_for_repair_agent: bool = False


class VisualCriticResult(BaseModel):
    schema_version: str = "0.1.0"

    status: Literal[
        "passed",
        "repair_required",
        "blocked",
    ]

    project_slug: str
    score: VisualScore

    issues: list[VisualIssue] = Field(
        default_factory=list
    )

    repair_directives: list[RepairDirective] = Field(
        default_factory=list
    )

    skills_used: list[str] = Field(
        default_factory=list
    )

    gates: VisualCriticGate

    notes: list[str] = Field(
        default_factory=list
    )

    generated_by: str = "VisualCritic"
