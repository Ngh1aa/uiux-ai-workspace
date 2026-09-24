from typing import Literal

from pydantic import BaseModel, Field


class SectionSpec(BaseModel):
    type: str
    purpose: str
    priority: Literal["P0", "P1", "P2"] = "P1"
    composition: str
    visual_anchor: str
    density: Literal["low", "medium", "high"] = "medium"
    mobile_behavior: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class PageSpec(BaseModel):
    path: str
    page_role: str
    composition_family: str
    first_visual_anchor: str
    sections: list[SectionSpec] = Field(default_factory=list)
    anti_monotony_rules: list[str] = Field(default_factory=list)


class VisualCompositionGate(BaseModel):
    page_roles_mapped: bool = False
    composition_families_diverse: bool = False
    mobile_transformations_defined: bool = False
    visual_anchors_defined: bool = False
    ready_for_frontend_engineer: bool = False


class VisualComposition(BaseModel):
    schema_version: str = "0.1.0"
    status: Literal["provisional", "approved", "blocked"] = "provisional"

    domain: str
    project_slug: str
    visual_signature: str

    composition_principles: list[str] = Field(default_factory=list)
    pages: list[PageSpec] = Field(default_factory=list)
    unresolved_items: list[str] = Field(default_factory=list)

    gates: VisualCompositionGate
    generated_by: str = "VisualComposer"
