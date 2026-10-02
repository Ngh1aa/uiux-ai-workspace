from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator

from core.brain_os.contracts import BrainContractModel
from core.brain_os.knowledge_contracts import (
    KnowledgeCategory,
    KnowledgeFreshness,
    KnowledgeRecord,
)


KNOWLEDGE_INDEX_VERSION = "knowledge-index.v1"
DEFAULT_RETRIEVAL_LIMIT = 6
MAX_RETRIEVAL_LIMIT = 12
DEFAULT_MAX_ITEM_CHARS = 4_000
DEFAULT_MAX_TOTAL_CHARS = 12_000
DEFAULT_TIME_SENSITIVE_MAX_AGE_DAYS = 30


class KnowledgeRetrievalError(ValueError):
    """Raised when canonical knowledge metadata/index content is unsafe or malformed."""


def _clean_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


def _normalized_tokens(values: list[str]) -> list[str]:
    tokens: list[str] = []
    for raw in values:
        for token in re.split(r"[^a-zA-Z0-9_-]+", str(raw).lower()):
            value = token.strip("-_ ")
            if len(value) >= 2:
                tokens.append(value)
    return _clean_unique(tokens)


def _stable_hash(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(raw).hexdigest()


def _content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _parse_date(value: str, *, field: str) -> date:
    raw = str(value).strip()
    try:
        return date.fromisoformat(raw[:10])
    except ValueError as exc:
        raise KnowledgeRetrievalError(f"{field} must start with an ISO date: {value!r}") from exc


class KnowledgeQuery(BrainContractModel):
    schema_version: Literal["knowledge-query.v1"] = "knowledge-query.v1"
    as_of: str = Field(min_length=10, max_length=32)
    categories: list[KnowledgeCategory] = Field(default_factory=list, max_length=7)
    domains: list[str] = Field(default_factory=list, max_length=20)
    stages: list[str] = Field(default_factory=list, max_length=20)
    tags: list[str] = Field(default_factory=list, max_length=30)
    terms: list[str] = Field(default_factory=list, max_length=50)
    limit: int = Field(default=DEFAULT_RETRIEVAL_LIMIT, ge=1, le=MAX_RETRIEVAL_LIMIT)
    max_item_chars: int = Field(default=DEFAULT_MAX_ITEM_CHARS, ge=256, le=20_000)
    max_total_chars: int = Field(default=DEFAULT_MAX_TOTAL_CHARS, ge=256, le=50_000)
    time_sensitive_max_age_days: int = Field(
        default=DEFAULT_TIME_SENSITIVE_MAX_AGE_DAYS,
        ge=0,
        le=365,
    )

    @field_validator("domains", "stages", "tags", "terms")
    @classmethod
    def _normalize_lists(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)

    @field_validator("as_of")
    @classmethod
    def _validate_as_of(cls, value: str) -> str:
        _parse_date(value, field="as_of")
        return value

    @model_validator(mode="after")
    def _validate_budgets(self) -> "KnowledgeQuery":
        if self.max_total_chars < min(self.max_item_chars, 256):
            raise ValueError("max_total_chars is too small for the item budget")
        return self


class KnowledgeHit(BrainContractModel):
    record: KnowledgeRecord
    record_path: str = Field(min_length=1, max_length=1024)
    content: str = Field(min_length=1, max_length=20_000)
    content_sha256: str = Field(min_length=64, max_length=64)
    source_content_chars: int = Field(ge=1)
    delivered_content_chars: int = Field(ge=1)
    truncated: bool
    relevance_points: int = Field(ge=0)
    matched_domains: list[str] = Field(default_factory=list, max_length=20)
    matched_stages: list[str] = Field(default_factory=list, max_length=20)
    matched_tags: list[str] = Field(default_factory=list, max_length=30)
    matched_terms: list[str] = Field(default_factory=list, max_length=50)
    advisory_only: Literal[True] = True
    current_run_evidence: Literal[False] = False
    flow_effect: Literal["none"] = "none"
    skill_activation_effect: Literal["none"] = "none"
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"
    release_effect: Literal["none"] = "none"


class KnowledgeExclusion(BrainContractModel):
    record_ref: str = Field(min_length=1, max_length=1024)
    reason: str = Field(min_length=1, max_length=256)


class KnowledgeRetrievalResult(BrainContractModel):
    schema_version: Literal["knowledge-retrieval.v1"] = "knowledge-retrieval.v1"
    query: KnowledgeQuery
    index_ref: str = Field(min_length=1, max_length=1024)
    index_sha256: str = Field(min_length=64, max_length=64)
    indexed_record_count: int = Field(ge=0)
    hits: list[KnowledgeHit] = Field(default_factory=list, max_length=MAX_RETRIEVAL_LIMIT)
    exclusions: list[KnowledgeExclusion] = Field(default_factory=list, max_length=500)
    delivered_content_chars: int = Field(ge=0)
    deterministic_metadata_first: Literal[True] = True
    vector_search_used: Literal[False] = False
    advisory_only: Literal[True] = True
    current_run_evidence: Literal[False] = False
    flow_effect: Literal["none"] = "none"
    skill_activation_effect: Literal["none"] = "none"
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"
    release_effect: Literal["none"] = "none"


@dataclass(frozen=True)
class _IndexedRecord:
    record: KnowledgeRecord
    record_path: Path
    record_ref: str


class KnowledgeIndex:
    """Deterministic loader for the canonical skills_UIUX/knowledge index.

    The index is metadata only. It never selects/replans a flow, activates a skill,
    writes memory, creates trusted evidence or changes authority/release state.
    """

    def __init__(self, knowledge_root: Path, manifest_name: str = "index.json") -> None:
        self.knowledge_root = Path(knowledge_root).resolve()
        self.workspace_root = self.knowledge_root.parents[1]
        self.manifest_path = (self.knowledge_root / manifest_name).resolve()
        if not self.manifest_path.is_relative_to(self.knowledge_root):
            raise KnowledgeRetrievalError("knowledge manifest must stay inside knowledge root")

    def _safe_relative_path(self, raw: str, *, purpose: str) -> Path:
        value = str(raw).strip()
        if not value:
            raise KnowledgeRetrievalError(f"{purpose} path cannot be empty")
        candidate = Path(value)
        if candidate.is_absolute():
            raise KnowledgeRetrievalError(f"{purpose} path must be relative: {value}")
        resolved = (self.knowledge_root / candidate).resolve()
        if not resolved.is_relative_to(self.knowledge_root):
            raise KnowledgeRetrievalError(f"{purpose} path escapes knowledge root: {value}")
        return resolved

    def _safe_content_path(self, raw: str) -> Path:
        value = str(raw).strip()
        if not value:
            raise KnowledgeRetrievalError("content_ref cannot be empty")
        candidate = Path(value)
        if candidate.is_absolute():
            raise KnowledgeRetrievalError(f"content_ref must be workspace-relative: {value}")
        resolved = (self.workspace_root / candidate).resolve()
        if not resolved.is_relative_to(self.knowledge_root):
            raise KnowledgeRetrievalError(
                f"content_ref must stay inside skills_UIUX/knowledge: {value}"
            )
        return resolved

    def load(self) -> tuple[list[_IndexedRecord], str]:
        if not self.manifest_path.is_file():
            raise KnowledgeRetrievalError(f"knowledge index not found: {self.manifest_path}")
        try:
            payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise KnowledgeRetrievalError(f"cannot read knowledge index: {exc}") from exc
        if not isinstance(payload, dict) or set(payload) != {"schema_version", "records"}:
            raise KnowledgeRetrievalError("knowledge index must contain only schema_version and records")
        if payload.get("schema_version") != KNOWLEDGE_INDEX_VERSION:
            raise KnowledgeRetrievalError(
                f"knowledge index schema_version must be {KNOWLEDGE_INDEX_VERSION}"
            )
        raw_records = payload.get("records")
        if not isinstance(raw_records, list):
            raise KnowledgeRetrievalError("knowledge index records must be an array")
        refs = [str(item).strip() for item in raw_records]
        if any(not ref for ref in refs):
            raise KnowledgeRetrievalError("knowledge index record paths must be non-empty strings")
        if len(refs) != len(set(refs)):
            raise KnowledgeRetrievalError("knowledge index record paths must be unique")
        if len(refs) > 5_000:
            raise KnowledgeRetrievalError("knowledge index exceeds 5000 records")

        indexed: list[_IndexedRecord] = []
        ids: set[str] = set()
        normalized_records: list[dict[str, Any]] = []
        for ref in refs:
            record_path = self._safe_relative_path(ref, purpose="record")
            if record_path == self.manifest_path:
                raise KnowledgeRetrievalError("knowledge index cannot index itself")
            if record_path.suffix.lower() != ".json" or not record_path.is_file():
                raise KnowledgeRetrievalError(f"knowledge record is missing or not JSON: {ref}")
            try:
                raw = json.loads(record_path.read_text(encoding="utf-8"))
                record = KnowledgeRecord.model_validate(raw)
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                raise KnowledgeRetrievalError(f"invalid knowledge record {ref}: {exc}") from exc
            if record.id in ids:
                raise KnowledgeRetrievalError(f"duplicate knowledge record id: {record.id}")
            ids.add(record.id)
            content_path = self._safe_content_path(record.content_ref)
            if not content_path.is_file():
                raise KnowledgeRetrievalError(
                    f"knowledge content_ref does not exist for {record.id}: {record.content_ref}"
                )
            indexed.append(_IndexedRecord(record=record, record_path=record_path, record_ref=ref))
            normalized_records.append(
                {
                    "record_ref": ref,
                    "record": record.model_dump(mode="json"),
                    "content_sha256": _content_hash(content_path.read_text(encoding="utf-8")),
                }
            )

        digest = _stable_hash(
            {
                "schema_version": KNOWLEDGE_INDEX_VERSION,
                "records": normalized_records,
            }
        )
        return indexed, digest


class KnowledgeRetriever:
    def __init__(self, index: KnowledgeIndex) -> None:
        self.index = index

    @staticmethod
    def _eligible(
        record: KnowledgeRecord,
        query: KnowledgeQuery,
    ) -> tuple[bool, str | None, dict[str, list[str]], int]:
        categories = {item.value if isinstance(item, KnowledgeCategory) else str(item) for item in query.categories}
        if categories and record.category.value not in categories:
            return False, "category_mismatch", {}, 0

        query_domains = {item.lower() for item in query.domains}
        record_domains = {item.lower() for item in record.applicable_domains}
        matched_domains = sorted(query_domains.intersection(record_domains))
        if query_domains and record_domains and not matched_domains:
            return False, "domain_mismatch", {}, 0

        query_stages = {item.lower() for item in query.stages}
        record_stages = {item.lower() for item in record.applicable_stages}
        matched_stages = sorted(query_stages.intersection(record_stages))
        if query_stages and record_stages and not matched_stages:
            return False, "stage_mismatch", {}, 0

        as_of = _parse_date(query.as_of, field="as_of")
        if record.freshness is KnowledgeFreshness.TIME_SENSITIVE:
            try:
                updated = _parse_date(record.updated_at, field=f"updated_at[{record.id}]")
            except KnowledgeRetrievalError:
                return False, "invalid_updated_at", {}, 0
            age = (as_of - updated).days
            if age < 0:
                return False, "future_updated_at", {}, 0
            if age > query.time_sensitive_max_age_days:
                return False, "stale_time_sensitive", {}, 0

        query_tags = {item.lower() for item in query.tags}
        record_tags = {item.lower() for item in record.tags}
        matched_tags = sorted(query_tags.intersection(record_tags))

        terms = _normalized_tokens(query.terms)
        haystack = " ".join(
            [record.title, record.topic, record.summary, *record.tags, *record.applicable_domains]
        ).lower()
        matched_terms = [term for term in terms if term in haystack]

        points = 0
        points += len(matched_domains) * 12
        points += len(matched_stages) * 10
        points += len(matched_tags) * 6
        points += len(matched_terms) * 2
        if categories:
            points += 4

        matches = {
            "domains": matched_domains,
            "stages": matched_stages,
            "tags": matched_tags,
            "terms": matched_terms,
        }
        return True, None, matches, points

    def retrieve(self, query: KnowledgeQuery) -> KnowledgeRetrievalResult:
        indexed, digest = self.index.load()
        candidates: list[tuple[int, float, str, _IndexedRecord, dict[str, list[str]]]] = []
        exclusions: list[KnowledgeExclusion] = []

        for item in indexed:
            eligible, reason, matches, points = self._eligible(item.record, query)
            if not eligible:
                exclusions.append(
                    KnowledgeExclusion(record_ref=item.record_ref, reason=reason or "not_eligible")
                )
                continue
            candidates.append((points, item.record.confidence, item.record.id, item, matches))

        candidates.sort(key=lambda row: (-row[0], -row[1], row[2]))

        hits: list[KnowledgeHit] = []
        total_chars = 0
        for points, _confidence, _record_id, item, matches in candidates:
            if len(hits) >= query.limit:
                exclusions.append(KnowledgeExclusion(record_ref=item.record_ref, reason="limit_reached"))
                continue
            remaining = query.max_total_chars - total_chars
            if remaining <= 0:
                exclusions.append(
                    KnowledgeExclusion(record_ref=item.record_ref, reason="context_budget_exhausted")
                )
                continue

            content_path = self.index._safe_content_path(item.record.content_ref)
            try:
                source_content = content_path.read_text(encoding="utf-8").strip()
            except OSError as exc:
                raise KnowledgeRetrievalError(
                    f"cannot read knowledge content for {item.record.id}: {exc}"
                ) from exc
            if not source_content:
                exclusions.append(KnowledgeExclusion(record_ref=item.record_ref, reason="empty_content"))
                continue

            delivery_cap = min(query.max_item_chars, remaining)
            delivered = source_content[:delivery_cap]
            if not delivered:
                exclusions.append(
                    KnowledgeExclusion(record_ref=item.record_ref, reason="context_budget_exhausted")
                )
                continue
            total_chars += len(delivered)
            hits.append(
                KnowledgeHit(
                    record=item.record,
                    record_path=str(item.record_path),
                    content=delivered,
                    content_sha256=_content_hash(source_content),
                    source_content_chars=len(source_content),
                    delivered_content_chars=len(delivered),
                    truncated=len(delivered) < len(source_content),
                    relevance_points=points,
                    matched_domains=matches["domains"],
                    matched_stages=matches["stages"],
                    matched_tags=matches["tags"],
                    matched_terms=matches["terms"],
                )
            )

        return KnowledgeRetrievalResult(
            query=query,
            index_ref=str(self.index.manifest_path),
            index_sha256=digest,
            indexed_record_count=len(indexed),
            hits=hits,
            exclusions=exclusions,
            delivered_content_chars=total_chars,
        )
