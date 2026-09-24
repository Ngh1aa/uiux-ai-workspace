from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BenchmarkReference(BaseModel):
    url: str
    label: str
    domain: str
    role: Literal[
        "visual-craft",
        "information-architecture",
        "product-storytelling",
        "conversion",
        "service-journey",
        "trust-accessibility",
        "editorial",
    ]
    rationale: str
    provenance: str = "curated-public-production-site"
    transfer_policy: str = (
        "Extract principles only. Do not copy proprietary copy, assets, brand tokens, "
        "illustrations, photography, page composition or interaction choreography."
    )


class BenchmarkPlan(BaseModel):
    schema_version: str = "1.1.0"
    website_type: str
    vertical: str = "generic"
    auto_inspiration_enabled: bool = True
    target_reference_count: int = 4
    user_reference_count: int = 0
    selected: list[BenchmarkReference] = Field(default_factory=list)
    final_reference_urls: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    generated_by: str = "ReferenceIntelligencePlanner"
