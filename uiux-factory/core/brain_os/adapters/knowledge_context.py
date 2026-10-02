from __future__ import annotations

from datetime import date
from typing import Any, Iterable, Literal

from pydantic import Field

from core.brain_os.adapters.flow_selection import FlowSelectionDecision
from core.brain_os.contracts import BrainContractModel
from core.brain_os.knowledge_contracts import KnowledgeCategory
from core.brain_os.knowledge_retrieval import (
    DEFAULT_MAX_ITEM_CHARS,
    DEFAULT_MAX_TOTAL_CHARS,
    DEFAULT_RETRIEVAL_LIMIT,
    DEFAULT_TIME_SENSITIVE_MAX_AGE_DAYS,
    KnowledgeQuery,
    KnowledgeRetrievalResult,
    KnowledgeRetriever,
)


def _values(raw: object) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        value = raw.strip()
        return [value] if value else []
    if isinstance(raw, (list, tuple, set)):
        return [str(item).strip() for item in raw if str(item).strip()]
    value = str(raw).strip()
    return [value] if value else []


def _clean_unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


class KnowledgeReasoningContext(BrainContractModel):
    """Reusable advisory knowledge attached only after canonical flow selection."""

    schema_version: Literal["brain-knowledge-context.v1"] = "brain-knowledge-context.v1"
    flow_selection: FlowSelectionDecision
    stage_id: str = Field(min_length=1, max_length=256)
    retrieval: KnowledgeRetrievalResult
    attached_after_flow_selection: Literal[True] = True
    advisory_only: Literal[True] = True
    current_run_evidence: Literal[False] = False
    flow_effect: Literal["none"] = "none"
    skill_activation_effect: Literal["none"] = "none"
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"
    release_effect: Literal["none"] = "none"


def attach_knowledge_after_flow_selection(
    *,
    retriever: KnowledgeRetriever,
    flow_selection: FlowSelectionDecision,
    stage_id: str,
    task_context: dict[str, Any],
    categories: Iterable[KnowledgeCategory | str] = (),
    tags: Iterable[str] = (),
    terms: Iterable[str] = (),
    as_of: str | None = None,
    limit: int = DEFAULT_RETRIEVAL_LIMIT,
    max_item_chars: int = DEFAULT_MAX_ITEM_CHARS,
    max_total_chars: int = DEFAULT_MAX_TOTAL_CHARS,
    time_sensitive_max_age_days: int = DEFAULT_TIME_SENSITIVE_MAX_AGE_DAYS,
) -> KnowledgeReasoningContext:
    """Retrieve bounded reusable context after routing, without changing routing.

    Requiring a `FlowSelectionDecision` makes the ordering explicit. The adapter has
    no API to select/replan a flow, activate a skill, satisfy a gate or write evidence.
    """

    stage = str(stage_id).strip()
    if not stage:
        raise ValueError("stage_id is required for knowledge retrieval")

    normalized_categories: list[KnowledgeCategory] = []
    for raw in categories:
        normalized_categories.append(
            raw if isinstance(raw, KnowledgeCategory) else KnowledgeCategory(str(raw).strip())
        )

    domains = _clean_unique(_values(task_context.get("domain")))
    context_tags = _clean_unique(
        [
            *_values(task_context.get("website_type")),
            *_values(task_context.get("product_archetype")),
            *_values(task_context.get("features")),
        ]
    )
    query_tags = _clean_unique([*context_tags, *[str(item) for item in tags]])
    query_terms = _clean_unique(
        [
            *_values(task_context.get("intent")),
            *_values(task_context.get("website_type")),
            *_values(task_context.get("product_archetype")),
            *_values(task_context.get("features")),
            *[str(item) for item in terms],
        ]
    )

    query = KnowledgeQuery(
        as_of=as_of or date.today().isoformat(),
        categories=normalized_categories,
        domains=domains,
        stages=[stage],
        tags=query_tags,
        terms=query_terms,
        limit=limit,
        max_item_chars=max_item_chars,
        max_total_chars=max_total_chars,
        time_sensitive_max_age_days=time_sensitive_max_age_days,
    )
    result = retriever.retrieve(query)
    return KnowledgeReasoningContext(
        flow_selection=flow_selection,
        stage_id=stage,
        retrieval=result,
    )
