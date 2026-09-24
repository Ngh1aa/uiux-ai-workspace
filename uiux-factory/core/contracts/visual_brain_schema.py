from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class VisualBrainScore(BaseModel):
    brand_recognition: int = Field(ge=0, le=100)
    subject_fit: int = Field(ge=0, le=100)
    page_role_diversity: int = Field(ge=0, le=100)
    interaction_clarity: int = Field(ge=0, le=100)
    responsive_intent: int = Field(ge=0, le=100)
    anti_generic: int = Field(ge=0, le=100)
    overall: int = Field(ge=0, le=100)


class VisualBrainRouteDiagnostic(BaseModel):
    path: str
    page_role: str
    composition_family: str
    first_visual_anchor: str
    generic_tells: list[str] = Field(default_factory=list)
    interaction_requirements: list[str] = Field(default_factory=list)
    calibration_directives: list[str] = Field(default_factory=list)


class VisualBrainGate(BaseModel):
    five_core_skills_loaded: bool = False
    visual_signature_specific: bool = False
    page_roles_materially_distinct: bool = False
    decision_objects_specific: bool = False
    interaction_contracts_present: bool = False
    mobile_transformations_present: bool = False
    no_blocking_generic_pattern: bool = False
    ready_for_implementation: bool = False


class VisualBrainReport(BaseModel):
    schema_version: str = "1.0.0"
    status: Literal["passed", "calibrated", "blocked"] = "calibrated"
    domain: str
    memorable_commitment: str
    signature_cues: list[str] = Field(default_factory=list)
    generic_tells: list[str] = Field(default_factory=list)
    keep: list[str] = Field(default_factory=list)
    revise: list[str] = Field(default_factory=list)
    remove: list[str] = Field(default_factory=list)
    route_diagnostics: list[VisualBrainRouteDiagnostic] = Field(default_factory=list)
    skills: dict[str, str] = Field(default_factory=dict)
    score: VisualBrainScore
    gates: VisualBrainGate
    generated_by: str = "VisualBrainV1"
