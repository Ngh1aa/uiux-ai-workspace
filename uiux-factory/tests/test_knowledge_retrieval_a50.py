from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.brain_os.adapters.flow_selection import FlowSelectionDecision, SurfaceSource
from core.brain_os.adapters.knowledge_context import attach_knowledge_after_flow_selection
from core.brain_os.knowledge_retrieval import KnowledgeIndex, KnowledgeQuery, KnowledgeRetrievalError, KnowledgeRetriever


REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_KNOWLEDGE = REPO_ROOT / "skills_UIUX/knowledge"
INDEX_SCHEMA = REPO_ROOT / "skills_UIUX/schemas/knowledge-index.schema.json"
EXPECTED_SEED = {
    "knowledge.domain.financial-currency-locale-formatting.v1",
    "knowledge.domain.cultural-object-metadata-rights-iiif.v1",
    "knowledge.domain.industrial-motor-system-claims-doe.v1",
}


def _flow() -> FlowSelectionDecision:
    return FlowSelectionDecision(
        change_surface="PAGE",
        surface_source=SurfaceSource.TASK_CONTRACT,
        flow_id="page-ui-work",
        flow_source="skills_UIUX/flows/page-ui-work.json",
        score=100,
        rationale="Canonical flow selected before knowledge retrieval.",
    )


def _workspace(tmp_path: Path) -> tuple[Path, Path]:
    workspace = tmp_path / "workspace"
    knowledge = workspace / "skills_UIUX/knowledge"
    (knowledge / "records").mkdir(parents=True)
    (knowledge / "content").mkdir(parents=True)
    return workspace, knowledge


def _write_record(
    workspace: Path,
    knowledge: Path,
    *,
    record_id: str,
    category: str = "pattern",
    domain: list[str] | None = None,
    stages: list[str] | None = None,
    tags: list[str] | None = None,
    freshness: str = "versioned",
    updated_at: str = "2026-10-01",
    confidence: float = 0.8,
    content: str = "Reusable product design knowledge.",
) -> str:
    slug = record_id.replace(".", "-")
    content_path = knowledge / "content" / f"{slug}.md"
    content_path.write_text(content, encoding="utf-8")
    record_ref = f"records/{slug}.json"
    payload = {
        "schema_version": "knowledge-record.v1",
        "id": record_id,
        "title": record_id,
        "category": category,
        "topic": record_id.split(".")[-1],
        "summary": f"Summary for {record_id}",
        "content_ref": str(content_path.relative_to(workspace)).replace("\\", "/"),
        "source_ref": f"https://example.invalid/{slug}",
        "source_kind": "external_reference",
        "version": "1.0.0",
        "updated_at": updated_at,
        "freshness": freshness,
        "confidence": confidence,
        "applicable_domains": domain or [],
        "applicable_stages": stages or [],
        "tags": tags or [],
        "advisory_only": True,
        "current_run_evidence": False,
        "authority_effect": "none",
        "gate_effect": "none",
        "evidence_effect": "none",
        "release_effect": "none",
    }
    (knowledge / record_ref).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return record_ref


def _manifest(knowledge: Path, refs: list[str]) -> None:
    (knowledge / "index.json").write_text(
        json.dumps({"schema_version": "knowledge-index.v1", "records": refs}, indent=2), encoding="utf-8"
    )


def test_a50_canonical_index_has_exact_curated_seed_and_valid_shape() -> None:
    manifest = json.loads((CANONICAL_KNOWLEDGE / "index.json").read_text(encoding="utf-8"))
    schema = json.loads(INDEX_SCHEMA.read_text(encoding="utf-8"))
    indexed, _ = KnowledgeIndex(CANONICAL_KNOWLEDGE).load()

    assert manifest["schema_version"] == "knowledge-index.v1"
    assert len(manifest["records"]) == 3
    assert {item.record.id for item in indexed} == EXPECTED_SEED
    assert schema["properties"]["records"]["maxItems"] == 5000
    assert schema["properties"]["records"]["uniqueItems"] is True


def test_a50_canonical_seed_remains_advisory_and_cross_domain_isolated() -> None:
    result = KnowledgeRetriever(KnowledgeIndex(CANONICAL_KNOWLEDGE)).retrieve(
        KnowledgeQuery(as_of="2026-10-02", domains=["financial-services"], stages=["implementation"])
    )

    assert result.indexed_record_count == 3
    assert [hit.record.id for hit in result.hits] == [
        "knowledge.domain.financial-currency-locale-formatting.v1"
    ]
    assert sum(item.reason == "domain_mismatch" for item in result.exclusions) == 2
    assert result.vector_search_used is False
    assert result.current_run_evidence is False
    assert result.flow_effect == "none"
    assert result.skill_activation_effect == "none"
    assert result.gate_effect == "none"
    assert result.release_effect == "none"


def test_a50_retrieval_ranks_specific_domain_stage_before_universal(tmp_path: Path) -> None:
    workspace, knowledge = _workspace(tmp_path)
    universal = _write_record(workspace, knowledge, record_id="knowledge.foundation.general", category="foundations", confidence=0.99)
    fintech = _write_record(workspace, knowledge, record_id="knowledge.pattern.fintech-error", domain=["financial-services"], stages=["qa"], tags=["error", "trust"], confidence=0.7)
    ecommerce = _write_record(workspace, knowledge, record_id="knowledge.pattern.ecommerce-error", domain=["ecommerce"], stages=["qa"], tags=["error"], confidence=0.95)
    _manifest(knowledge, [universal, fintech, ecommerce])

    result = KnowledgeRetriever(KnowledgeIndex(knowledge)).retrieve(
        KnowledgeQuery(as_of="2026-10-02", domains=["financial-services"], stages=["qa"], tags=["error"], terms=["trust"])
    )
    assert [hit.record.id for hit in result.hits] == ["knowledge.pattern.fintech-error", "knowledge.foundation.general"]
    assert any(item.reason == "domain_mismatch" for item in result.exclusions)


def test_a50_time_sensitive_stale_knowledge_is_excluded(tmp_path: Path) -> None:
    workspace, knowledge = _workspace(tmp_path)
    stale = _write_record(workspace, knowledge, record_id="knowledge.domain.market-rule", freshness="time_sensitive", updated_at="2026-08-01")
    fresh = _write_record(workspace, knowledge, record_id="knowledge.domain.current-rule", freshness="time_sensitive", updated_at="2026-09-25")
    _manifest(knowledge, [stale, fresh])
    result = KnowledgeRetriever(KnowledgeIndex(knowledge)).retrieve(KnowledgeQuery(as_of="2026-10-02", time_sensitive_max_age_days=30))
    assert [hit.record.id for hit in result.hits] == ["knowledge.domain.current-rule"]
    assert {item.record_ref: item.reason for item in result.exclusions}[stale] == "stale_time_sensitive"


def test_a50_context_budget_is_bounded_and_truncation_is_explicit(tmp_path: Path) -> None:
    workspace, knowledge = _workspace(tmp_path)
    first = _write_record(workspace, knowledge, record_id="knowledge.pattern.long-one", content="A" * 1000, confidence=0.9)
    second = _write_record(workspace, knowledge, record_id="knowledge.pattern.long-two", content="B" * 1000, confidence=0.8)
    _manifest(knowledge, [first, second])
    result = KnowledgeRetriever(KnowledgeIndex(knowledge)).retrieve(
        KnowledgeQuery(as_of="2026-10-02", limit=2, max_item_chars=400, max_total_chars=600)
    )
    assert [hit.delivered_content_chars for hit in result.hits] == [400, 200]
    assert result.delivered_content_chars == 600
    assert all(hit.truncated and len(hit.content_sha256) == 64 for hit in result.hits)


def test_a50_index_and_content_paths_fail_closed_on_escape(tmp_path: Path) -> None:
    workspace, knowledge = _workspace(tmp_path)
    _manifest(knowledge, ["../outside.json"])
    with pytest.raises(KnowledgeRetrievalError, match="escapes knowledge root"):
        KnowledgeIndex(knowledge).load()

    bad_ref = "records/bad.json"
    (knowledge / bad_ref).write_text(json.dumps({
        "schema_version": "knowledge-record.v1", "id": "knowledge.bad", "title": "Bad", "category": "pattern",
        "topic": "bad", "summary": "Bad path", "content_ref": "../outside.md", "source_ref": "https://example.invalid/bad",
        "source_kind": "external_reference", "version": "1", "updated_at": "2026-10-02", "freshness": "versioned",
        "confidence": 0.5, "advisory_only": True, "current_run_evidence": False, "authority_effect": "none",
        "gate_effect": "none", "evidence_effect": "none", "release_effect": "none"
    }), encoding="utf-8")
    _manifest(knowledge, [bad_ref])
    with pytest.raises(KnowledgeRetrievalError, match="must stay inside"):
        KnowledgeIndex(knowledge).load()


def test_a50_adapter_attaches_after_flow_selection_without_mutating_flow(tmp_path: Path) -> None:
    workspace, knowledge = _workspace(tmp_path)
    ref = _write_record(workspace, knowledge, record_id="knowledge.domain.fintech-trust", category="domain", domain=["financial-services"], stages=["research"], tags=["trust"])
    _manifest(knowledge, [ref])
    flow = _flow()
    before = flow.model_dump(mode="json")
    context = attach_knowledge_after_flow_selection(
        retriever=KnowledgeRetriever(KnowledgeIndex(knowledge)), flow_selection=flow, stage_id="research",
        task_context={"domain": "financial-services", "intent": "redesign", "website_type": "saas", "features": ["trust"]},
        as_of="2026-10-02"
    )
    assert flow.model_dump(mode="json") == before
    assert context.flow_selection == flow
    assert context.flow_effect == "none"
    assert context.skill_activation_effect == "none"
    assert context.current_run_evidence is False
