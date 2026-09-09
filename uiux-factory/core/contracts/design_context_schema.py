"""Bounded, portable inputs and source-attributed evidence for V3."""

import base64
import binascii
import re
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator


def public_web_url(value: str) -> str:
    value = value.strip()
    if len(value) > 2000:
        raise ValueError("Reference URL must be at most 2000 characters.")
    parts = urlsplit(value)
    if (
        parts.scheme not in {"https", "http"}
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.port not in {None, 80, 443}
    ):
        raise ValueError("Use an HTTP(S) URL without credentials on port 80 or 443.")
    return value


class ContextAsset(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=200)
    kind: Literal["logo", "screenshot"]
    data_url: str = Field(max_length=2_800_000)

    @field_validator("data_url")
    @classmethod
    def validate_image(cls, value: str) -> str:
        if not re.match(r"^data:image/(png|jpeg|webp);base64,", value):
            raise ValueError("Upload a PNG, JPEG or WebP image (up to 2 MB).")
        try:
            raw = base64.b64decode(value.split(",", 1)[1], validate=True)
        except (ValueError, binascii.Error) as error:
            raise ValueError("Invalid image encoding.") from error
        if len(raw) > 2_000_000:
            raise ValueError("Each image must be at most 2 MB.")
        return value


class DesignContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    brand_name: str = Field(default="", max_length=120)
    personality: list[str] = Field(default_factory=list, max_length=12)
    avoid: list[str] = Field(default_factory=list, max_length=20)
    guideline: str = Field(default="", max_length=30_000)
    existing_code: str = Field(default="", max_length=100_000)
    # Accepts the brief's compact JSON or the existing canonical foundations.
    tokens: dict[str, JsonValue] = Field(default_factory=dict)
    reference_urls: list[str] = Field(default_factory=list, max_length=4)
    existing_website: str = Field(default="", max_length=2000)
    assets: list[ContextAsset] = Field(default_factory=list, max_length=4)
    # When fewer than target references are supplied, Factory may add curated
    # live production sites for measurable inspiration. User references win.
    # Four is the finalist cap for ReferenceAnalyzer; broader discovery belongs
    # to ResearchAgent and should normally inspect 10–20 candidates.
    auto_inspiration: bool = True
    inspiration_target: int = Field(default=4, ge=0, le=4)

    @field_validator("reference_urls")
    @classmethod
    def validate_urls(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(public_web_url(value) for value in values))

    @field_validator("existing_website")
    @classmethod
    def validate_website(cls, value: str) -> str:
        return public_web_url(value) if value.strip() else ""

    @field_validator("personality", "avoid")
    @classmethod
    def validate_labels(cls, values: list[str]) -> list[str]:
        if any(len(value) > 300 for value in values):
            raise ValueError("Each brand rule must be at most 300 characters.")
        return list(dict.fromkeys(value.strip() for value in values if value.strip()))


class DesignObservation(BaseModel):
    category: Literal["layout", "typography", "color", "motion", "ux", "asset"]
    subject: str
    value: str
    source: str
    certainty: Literal["FACT", "EVIDENCE_BACKED_INFERENCE", "UNKNOWN"] = "FACT"


class ReferenceDNA(BaseModel):
    url: str
    role: Literal["reference", "existing_website"] = "reference"
    status: Literal["observed", "partial", "unavailable"] = "unavailable"
    title: str = ""
    captured_at: str = ""
    observations: list[DesignObservation] = Field(default_factory=list)
    patterns: list[str] = Field(default_factory=list)
    screenshots: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(
        default_factory=lambda: [
            "Single-page evidence; unvisited pages and interaction states are unknown.",
            "Reference colors, assets and copy are not the project's brand tokens.",
            "Transfer principles only; do not copy proprietary assets or compositions.",
        ]
    )


class ReferenceBoard(BaseModel):
    schema_version: str = "0.3.0"
    references: list[ReferenceDNA] = Field(default_factory=list)
    generated_by: str = "ReferenceAnalyzer"


class BrandDNA(BaseModel):
    name: str = ""
    personality: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    source_status: Literal["supplied_guideline", "partial_assets", "no_brand_evidence"] = "no_brand_evidence"
    evidence: list[DesignObservation] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    source_context_sha256: str = ""
    reference_patterns: list[str] = Field(default_factory=list)
    policy: str = (
        "Explicit tokens > labeled guideline > existing CSS > existing website. "
        "References never override brand."
    )
