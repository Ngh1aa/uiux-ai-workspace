from typing import Literal

from pydantic import BaseModel, Field


class ArtifactSource(BaseModel):
    path: str
    sha256: str


class EvidenceStatus(BaseModel):
    research: str = "UNKNOWN"
    ux_ia: str = "UNKNOWN"
    art_direction: str = "UNKNOWN"


class ProjectContract(BaseModel):
    goal: str

    domain: str = "UNKNOWN"

    requested_primary_color: str = "UNKNOWN"

    evidence_level: Literal[
        "verified",
        "provisional",
        "unknown",
    ] = "unknown"


class UXPageRole(BaseModel):
    name: str
    role: str


class UXContract(BaseModel):
    principles: list[str] = Field(
        default_factory=list
    )

    page_roles: list[UXPageRole] = Field(
        default_factory=list
    )

    primary_journey: list[str] = Field(
        default_factory=list
    )

    assumptions: list[str] = Field(
        default_factory=list
    )


class VisualContract(BaseModel):
    signature: str = ""

    attributes: list[str] = Field(
        default_factory=list
    )

    layout_rules: list[str] = Field(
        default_factory=list
    )

    color_roles: list[str] = Field(
        default_factory=list
    )

    typography_rules: list[str] = Field(
        default_factory=list
    )

    media_rules: list[str] = Field(
        default_factory=list
    )

    motion_rules: list[str] = Field(
        default_factory=list
    )

    composition_matrix: list[str] = Field(
        default_factory=list
    )


class ImplementationConstraints(BaseModel):
    preserve_page_role_diversity: bool = True

    avoid_generic_card_grid: bool = True

    avoid_shared_hero_everywhere: bool = True

    mobile_requires_explicit_transformation: bool = True

    do_not_invent_evidence: bool = True

    unresolved_items: list[str] = Field(
        default_factory=list
    )


class DesignContract(BaseModel):
    schema_version: str = "0.1.0"

    status: Literal[
        "provisional",
        "approved",
        "blocked",
    ] = "provisional"

    project: ProjectContract

    ux: UXContract

    visual: VisualContract

    constraints: ImplementationConstraints

    gates: EvidenceStatus

    sources: dict[str, ArtifactSource]

    generated_by: str = (
        "DesignContractAgent"
    )