from typing import Literal

from pydantic import BaseModel, Field


class ViewportSpec(BaseModel):
    name: str
    width: int
    height: int


class RouteViewportEvidence(BaseModel):
    route: str
    viewport: ViewportSpec
    screenshot: str
    status: Literal["passed", "failed"]

    console_errors: list[str] = Field(default_factory=list)
    page_errors: list[str] = Field(default_factory=list)

    horizontal_overflow: bool = False
    overflow_amount_px: int = 0

    h1_count: int = 0
    main_count: int = 0
    nav_count: int = 0

    broken_internal_links: list[str] = Field(default_factory=list)

    # Automated smoke evidence only; these fields do not claim WCAG conformance.
    missing_alt_count: int = 0
    unlabeled_control_count: int = 0
    small_control_target_count: int = 0
    focus_obscured_count: int = 0
    catastrophic_contrast_count: int = 0


class BrowserQAGate(BaseModel):
    routes_discovered: bool = False
    screenshots_created: bool = False
    no_page_errors: bool = False
    no_console_errors: bool = False
    no_horizontal_overflow: bool = False
    internal_links_valid: bool = False
    semantic_smoke_passed: bool = False

    image_alt_smoke_passed: bool = False
    accessible_name_smoke_passed: bool = False
    control_target_smoke_passed: bool = False
    focus_visibility_smoke_passed: bool = False
    elementary_visual_sanity_passed: bool = False

    ready_for_visual_critic: bool = False


class BrowserQAResult(BaseModel):
    schema_version: str = "0.2.0"
    status: Literal["passed", "failed", "partial"]

    project_slug: str
    project_dir: str
    base_url: str

    routes: list[str] = Field(default_factory=list)
    viewports: list[ViewportSpec] = Field(default_factory=list)
    evidence: list[RouteViewportEvidence] = Field(default_factory=list)

    skills_used: list[str] = Field(default_factory=list)
    gates: BrowserQAGate

    summary: dict[str, int | bool] = Field(default_factory=dict)
    limitations: list[str] = Field(default_factory=list)

    generated_by: str = "BrowserQAAgent"
