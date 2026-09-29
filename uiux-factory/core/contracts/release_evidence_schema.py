from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

EvidenceState = Literal["VERIFIED", "FAILED", "UNKNOWN", "PLANNED", "N/A_JUSTIFIED"]


class ReleaseEvidenceArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(pattern=r"^REL-[0-9a-f]{16}$")
    kind: str = Field(min_length=1, max_length=120)
    path: str = Field(min_length=1, max_length=2000)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    size_bytes: int = Field(ge=0)
    state: EvidenceState = "VERIFIED"
    claims: list[str] = Field(default_factory=list, max_length=32)


class ReleaseEvidenceClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim: str = Field(min_length=1, max_length=160)
    state: EvidenceState
    evidence_ids: list[str] = Field(default_factory=list, max_length=64)
    detail: str = Field(default="", max_length=2000)


class ReleaseEvidenceManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["uiux-release-evidence.v1"] = "uiux-release-evidence.v1"
    target_repository: str = Field(min_length=1, max_length=500)
    target_sha: str = Field(min_length=7, max_length=64)
    generated_at: str = Field(min_length=1, max_length=120)
    release_classification: str = Field(min_length=1, max_length=120)
    artifacts: list[ReleaseEvidenceArtifact] = Field(default_factory=list)
    claims: list[ReleaseEvidenceClaim] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
