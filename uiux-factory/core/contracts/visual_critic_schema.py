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


class VisualRouteSemanticReview(BaseModel):
    route: str
    page_role: str = "unknown"
    domain_fit: int = Field(ge=0, le=100)
    page_role_fit: int = Field(ge=0, le=100)
    decision_object_dominance: int = Field(ge=0, le=100)
    media_relevance: int = Field(ge=0, le=100)
    hierarchy: int = Field(ge=0, le=100)
    distinctiveness: int = Field(ge=0, le=100)
    generic_ai_feel: int = Field(ge=0, le=100)
    blocking_generic: bool = False
    generic_tells: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class SemanticVisualReview(BaseModel):
    reviewed: bool = True
    site_summary: str = ""
    website_type: str = "generic"
    vertical: str = "generic"
    blocking_generic: bool = False
    cross_route_variety: int = Field(default=100, ge=0, le=100)
    brand_distinctiveness: int = Field(default=70, ge=0, le=100)
    routes: list[VisualRouteSemanticReview] = Field(default_factory=list)


class VisualCriticGate(BaseModel):
    screenshots_consumed: bool = False
    browser_report_consumed: bool = False
    skills_loaded: bool = False
    score_generated: bool = False
    repair_directives_generated: bool = False
    ready_for_repair_agent: bool = False

    semantic_visual_review_attempted: bool = False
    semantic_visual_review_passed: bool = False
    domain_page_roles_reviewed: bool = False
    no_blocking_generic_pattern: bool = False
    proxy_only_mode: bool = True


class VisualCriticResult(BaseModel):
    schema_version: str = "0.2.0"

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

    semantic_review: SemanticVisualReview | None = None
    review_mode: Literal["vision", "proxy"] = "proxy"

    notes: list[str] = Field(
        default_factory=list
    )

    generated_by: str = "VisualCritic"
