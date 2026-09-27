from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


EvidenceStatus = Literal[
    "VERIFIED",
    "INFERRED",
    "ASSUMED",
    "UNKNOWN",
    "PROPOSED",
    "N/A_JUSTIFIED",
]


class EvidenceProvenanceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(pattern=r"^EVID-[0-9a-f]{16}$")
    status: EvidenceStatus
    kind: str = Field(min_length=1, max_length=120)
    source_type: str = Field(min_length=1, max_length=160)
    source_url: str = Field(default="", max_length=4000)
    source_artifact: str = Field(default="", max_length=2000)
    source_artifact_sha256: str = Field(default="", max_length=64)
    captured_at: str = Field(default="", max_length=120)
    viewport: str = Field(default="", max_length=160)
    state: str = Field(default="", max_length=240)
    selector: str = Field(default="", max_length=1200)
    property_name: str = Field(default="", max_length=300)
    value: str = Field(default="", max_length=6000)
    locator: str = Field(min_length=1, max_length=4000)


class SpecEvidenceLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    line_number: int = Field(gt=0)
    statement: str = Field(min_length=1, max_length=6000)
    evidence_ids: list[str] = Field(default_factory=list, max_length=64)


class EvidenceProvenanceManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["evidence-provenance.v1"] = "evidence-provenance.v1"
    spec_profile: str = Field(min_length=1, max_length=120)
    source_artifact: str = Field(default="", max_length=2000)
    source_sha256: str = Field(default="", max_length=64)
    catalog_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    spec_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    records: list[EvidenceProvenanceRecord] = Field(default_factory=list)
    spec_links: list[SpecEvidenceLink] = Field(default_factory=list)
    downstream_consumers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
