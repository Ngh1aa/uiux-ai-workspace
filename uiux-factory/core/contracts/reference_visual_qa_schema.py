from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ReferenceVisualMode = Literal[
    "strict_reference",
    "protected_surfaces",
    "reference_advisory",
    "spec_only",
]
ReferenceVisualStatus = Literal["passed", "failed", "cantTell", "inapplicable"]


class ReferenceVisualComparison(BaseModel):
    model_config = ConfigDict(extra="forbid")

    route: str = "/"
    viewport: str = ""
    reference_url: str = ""
    reference_screenshot: str = ""
    target_screenshot: str = ""
    reference_sha256: str = ""
    target_sha256: str = ""
    normalized_mae: float | None = Field(default=None, ge=0, le=1)
    differing_pixel_ratio: float | None = Field(default=None, ge=0, le=1)
    tolerance_per_channel: int = Field(default=24, ge=0, le=255)
    status: ReferenceVisualStatus
    blocking: bool = False
    evidence: str = ""


class ReferenceVisualQAResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["reference-visual-qa.v1"] = "reference-visual-qa.v1"
    spec_profile: Literal[
        "pixel_faithful",
        "preserve_and_extend",
        "redesign",
        "original_design",
    ]
    mode: ReferenceVisualMode
    status: ReferenceVisualStatus
    blocking: bool = False
    policy_id: str
    comparisons: list[ReferenceVisualComparison] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    generated_by: str = "ReferenceAwareVisualQA"
