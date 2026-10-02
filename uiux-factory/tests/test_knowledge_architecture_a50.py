from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from core.brain_os.knowledge_contracts import (
    KnowledgeArchitecture,
    KnowledgeCategory,
    KnowledgeRecord,
    current_knowledge_architecture,
)


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SCHEMA_PATH = WORKSPACE / "skills_UIUX/schemas/knowledge-record.schema.json"
KNOWLEDGE_ROOT = WORKSPACE / "skills_UIUX/knowledge"


def _record(**overrides):
    payload = {
        "id": "knowledge.pattern.empty-state.v1",
        "title": "Empty-state principles",
        "category": "pattern",
        "topic": "empty-states",
        "summary": "Reusable empty-state design principles.",
        "content_ref": "skills_UIUX/knowledge/patterns/empty-states.md",
        "source_ref": "https://example.invalid/reference/empty-states",
        "source_kind": "external_reference",
        "version": "1.0.0",
        "updated_at": "2026-10-02",
        "freshness": "versioned",
        "confidence": 0.8,
        "applicable_domains": ["generic", "generic", "financial-services"],
        "applicable_stages": ["design", "qa"],
        "tags": ["states", "states", "empty"],
    }
    payload.update(overrides)
    return KnowledgeRecord(**payload)


def test_a50_architecture_preserves_owner_and_non_authority_boundaries() -> None:
    architecture = current_knowledge_architecture()

    assert isinstance(architecture, KnowledgeArchitecture)
    assert architecture.declarative_owner == "skills_UIUX/knowledge"
    assert architecture.index_owner == "skills_UIUX/knowledge/index.json"
    assert architecture.retrieval_owner == "core/brain_os/knowledge_retrieval.py"
    assert architecture.context_adapter_owner == "core/brain_os/adapters/knowledge_context.py"
    assert architecture.methodology_owner == "skills_UIUX/<skill>/SKILL.md"
    assert architecture.retrieval_implemented is True
    assert architecture.deterministic_metadata_first is True
    assert architecture.vector_database_required is False
    assert architecture.skill_body_duplication_allowed is False
    assert architecture.advisory_only is True
    assert architecture.authority_effect == "none"
    assert architecture.gate_effect == "none"
    assert architecture.evidence_effect == "none"
    assert architecture.release_effect == "none"


def test_a50_python_taxonomy_matches_canonical_json_schema() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    schema_categories = set(schema["properties"]["category"]["enum"])
    python_categories = {item.value for item in KnowledgeCategory}

    assert python_categories == schema_categories
    assert schema["properties"]["advisory_only"]["const"] is True
    assert schema["properties"]["current_run_evidence"]["const"] is False
    for field in ("authority_effect", "gate_effect", "evidence_effect", "release_effect"):
        assert schema["properties"][field]["const"] == "none"
        assert field in schema["required"]


def test_a50_knowledge_record_is_not_project_memory_or_current_evidence() -> None:
    record = _record()

    assert record.advisory_only is True
    assert record.current_run_evidence is False
    assert record.applicable_domains == ["generic", "financial-services"]
    assert record.tags == ["states", "empty"]
    assert "project_scope" not in KnowledgeRecord.model_fields
    assert "source_run_id" not in KnowledgeRecord.model_fields
    assert "evidence_refs" not in KnowledgeRecord.model_fields


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("content_ref", "BM-123456"),
        ("source_ref", "BM-123456"),
        ("content_ref", "EVID-current-run"),
        ("source_ref", "EVID-current-run"),
    ],
)
def test_a50_knowledge_rejects_memory_and_current_evidence_ownership(field: str, value: str) -> None:
    with pytest.raises(ValidationError, match="cannot use"):
        _record(**{field: value})


def test_a50_knowledge_directory_does_not_fork_skill_methodology() -> None:
    assert (KNOWLEDGE_ROOT / "README.md").is_file()
    assert (KNOWLEDGE_ROOT / "index.json").is_file()
    assert not list(KNOWLEDGE_ROOT.rglob("SKILL.md"))
