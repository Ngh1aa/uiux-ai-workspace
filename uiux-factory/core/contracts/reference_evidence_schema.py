from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


MeasuredEvidenceStatus = Literal["VERIFIED", "INFERRED", "UNKNOWN"]
ReferenceRole = Literal["reference", "existing_website"]
ReferenceStatus = Literal["observed", "partial", "unavailable"]
AssetKind = Literal[
    "image",
    "video",
    "font",
    "stylesheet",
    "script",
    "icon",
    "background-image",
]


class EvidenceRect(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float
    y: float
    width: float
    height: float


class EvidenceViewport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1, max_length=80)
    width: int = Field(gt=0, le=10000)
    height: int = Field(gt=0, le=10000)
    device_scale_factor: float = Field(default=1.0, gt=0, le=8)


class DOMNodeEvidence(BaseModel):
    """A bounded sequential DOM record. `index` preserves source traversal order."""

    model_config = ConfigDict(extra="forbid")

    index: int = Field(ge=0)
    parent_index: int | None = Field(default=None, ge=0)
    tag: str = Field(min_length=1, max_length=80)
    selector: str = Field(min_length=1, max_length=1200)
    id: str = Field(default="", max_length=500)
    classes: list[str] = Field(default_factory=list, max_length=64)
    attributes: dict[str, str] = Field(default_factory=dict)
    text: str = Field(default="", max_length=600)
    visible: bool = False
    rect: EvidenceRect
    evidence: Literal["VERIFIED"] = "VERIFIED"


class ComputedStyleEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_index: int = Field(ge=0)
    selector: str = Field(min_length=1, max_length=1200)
    properties: dict[str, str] = Field(default_factory=dict)
    custom_properties: dict[str, str] = Field(default_factory=dict)
    evidence: Literal["VERIFIED"] = "VERIFIED"


class AssetEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: AssetKind
    url: str = Field(default="", max_length=4000)
    declared_url: str = Field(default="", max_length=4000)
    selector: str = Field(default="", max_length=1200)
    family: str = Field(default="", max_length=500)
    natural_width: int | None = Field(default=None, ge=0)
    natural_height: int | None = Field(default=None, ge=0)
    status: str = Field(default="", max_length=120)
    evidence: Literal["VERIFIED"] = "VERIFIED"


class MediaQueryEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    condition: str = Field(min_length=1, max_length=2000)
    matches: bool
    source: str = Field(default="cssom", max_length=120)
    evidence: Literal["VERIFIED"] = "VERIFIED"


class PaletteColorEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: str = Field(min_length=1, max_length=120)
    weight: float | None = Field(default=None, ge=0, le=1)
    evidence: MeasuredEvidenceStatus
    source: str = Field(min_length=1, max_length=200)


class ScreenshotEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(min_length=1, max_length=2000)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    full_page: bool = False
    evidence: Literal["VERIFIED"] = "VERIFIED"


class ReferenceCaptureEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    viewport: EvidenceViewport
    page_url: str = Field(min_length=1, max_length=4000)
    scroll_width: int = Field(ge=0)
    scroll_height: int = Field(ge=0)
    horizontal_overflow: bool
    dom_truncated: bool = False
    style_truncated: bool = False
    dom: list[DOMNodeEvidence] = Field(default_factory=list)
    computed_styles: list[ComputedStyleEvidence] = Field(default_factory=list)
    root_custom_properties: dict[str, str] = Field(default_factory=dict)
    assets: list[AssetEvidence] = Field(default_factory=list)
    media_queries: list[MediaQueryEvidence] = Field(default_factory=list)
    css_colors: list[PaletteColorEvidence] = Field(default_factory=list)
    visual_palette: list[PaletteColorEvidence] = Field(default_factory=list)
    screenshot: ScreenshotEvidence | None = None
    warnings: list[str] = Field(default_factory=list)


class DocumentEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(default="", max_length=500)
    lang: str = Field(default="", max_length=120)
    description: str = Field(default="", max_length=2000)
    canonical: str = Field(default="", max_length=4000)
    theme_color: str = Field(default="", max_length=120)
    doctype: str = Field(default="", max_length=200)


class ReferencePageEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str = Field(min_length=1, max_length=4000)
    role: ReferenceRole = "reference"
    status: ReferenceStatus = "unavailable"
    captured_at: str = Field(default="", max_length=120)
    document: DocumentEvidence = Field(default_factory=DocumentEvidence)
    captures: list[ReferenceCaptureEvidence] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ReferenceEvidenceBundle(BaseModel):
    """Machine-readable reference evidence consumed by Spec Writer and QA.

    The extractor measures public, unauthenticated browser state only. It never upgrades
    screenshot-derived palette clusters or later motion inference to source truth.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["reference-evidence.v1"] = "reference-evidence.v1"
    generated_by: str = "ReferenceEvidenceExtractor"
    references: list[ReferencePageEvidence] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
