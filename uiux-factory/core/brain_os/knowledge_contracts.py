from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import Field, field_validator, model_validator

from core.brain_os.contracts import BrainContractModel


class KnowledgeCategory(str, Enum):
    FOUNDATIONS = "foundations"
    PRODUCT = "product"
    RESEARCH = "research"
    MANAGEMENT = "management"
    DOMAIN = "domain"
    PATTERN = "pattern"
    PLATFORM = "platform"


class KnowledgeSourceKind(str, Enum):
    REPO_REFERENCE = "repo_reference"
    EXTERNAL_REFERENCE = "external_reference"
    STANDARD = "standard"
    HUMAN_CURATED = "human_curated"


class KnowledgeFreshness(str, Enum):
    EVERGREEN = "evergreen"
    VERSIONED = "versioned"
    TIME_SENSITIVE = "time_sensitive"


def _clean_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


class KnowledgeRecord(BrainContractModel):
    """Immutable Brain view of one canonical declarative knowledge record.

    The record is advisory metadata/context only. It does not own skill methodology,
    project memory, current-run evidence, routing, gates or release authority.
    """

    schema_version: Literal["knowledge-record.v1"] = "knowledge-record.v1"
    id: str = Field(min_length=1, max_length=128)
    title: str = Field(min_length=1, max_length=300)
    category: KnowledgeCategory
    topic: str = Field(min_length=1, max_length=256)
    summary: str = Field(min_length=1, max_length=4000)
    content_ref: str = Field(min_length=1, max_length=512)
    source_ref: str = Field(min_length=1, max_length=1024)
    source_kind: KnowledgeSourceKind
    version: str = Field(min_length=1, max_length=128)
    updated_at: str = Field(min_length=1, max_length=128)
    freshness: KnowledgeFreshness
    confidence: float = Field(ge=0.0, le=1.0)
    applicable_domains: list[str] = Field(default_factory=list, max_length=50)
    applicable_stages: list[str] = Field(default_factory=list, max_length=30)
    tags: list[str] = Field(default_factory=list, max_length=50)
    advisory_only: Literal[True] = True
    current_run_evidence: Literal[False] = False
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"

    @field_validator("applicable_domains", "applicable_stages", "tags")
    @classmethod
    def _normalize_lists(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)

    @model_validator(mode="after")
    def _validate_reference_boundaries(self) -> "KnowledgeRecord":
        if self.content_ref.startswith("BM-") or self.source_ref.startswith("BM-"):
            raise ValueError("knowledge records cannot use Brain-memory IDs as content/source ownership")
        if self.content_ref.startswith("EVID-"):
            raise ValueError("knowledge content_ref cannot be a current-run evidence ID")
        return self


class KnowledgeArchitecture(BrainContractModel):
    """Read-only declaration of A50 Knowledge OS ownership boundaries."""

    schema_version: Literal["knowledge-architecture.v1"] = "knowledge-architecture.v1"
    declarative_owner: Literal["skills_UIUX/knowledge"] = "skills_UIUX/knowledge"
    schema_owner: Literal["skills_UIUX/schemas/knowledge-record.schema.json"] = (
        "skills_UIUX/schemas/knowledge-record.schema.json"
    )
    methodology_owner: Literal["skills_UIUX/<skill>/SKILL.md"] = "skills_UIUX/<skill>/SKILL.md"
    memory_owner: Literal["core/brain_os/memory_contracts.py + core/memory/"] = (
        "core/brain_os/memory_contracts.py + core/memory/"
    )
    evidence_owner: Literal["core/runtime/flow_os/evidence.py + core/provenance/ + uiux-factory/qa/"] = (
        "core/runtime/flow_os/evidence.py + core/provenance/ + uiux-factory/qa/"
    )
    categories: tuple[KnowledgeCategory, ...] = (
        KnowledgeCategory.FOUNDATIONS,
        KnowledgeCategory.PRODUCT,
        KnowledgeCategory.RESEARCH,
        KnowledgeCategory.MANAGEMENT,
        KnowledgeCategory.DOMAIN,
        KnowledgeCategory.PATTERN,
        KnowledgeCategory.PLATFORM,
    )
    retrieval_implemented: Literal[False] = False
    vector_database_required: Literal[False] = False
    skill_body_duplication_allowed: Literal[False] = False
    advisory_only: Literal[True] = True
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"


def current_knowledge_architecture() -> KnowledgeArchitecture:
    return KnowledgeArchitecture()
