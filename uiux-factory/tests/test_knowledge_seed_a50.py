from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from core.brain_os.knowledge_retrieval import KnowledgeIndex


ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_ROOT = ROOT / "skills_UIUX/knowledge"
SKILLS_ROOT = ROOT / "skills_UIUX"
EXPECTED_IDS = {
    "knowledge.domain.financial-currency-locale-formatting.v1",
    "knowledge.domain.cultural-object-metadata-rights-iiif.v1",
    "knowledge.domain.industrial-motor-system-claims-doe.v1",
    "knowledge.domain.ev-charging-ocpp-transaction-semantics.v1",
    "knowledge.domain.edtech-lti-context-roles-services.v2",
}
EXPECTED_SOURCE_HOSTS = {
    "www.unicode.org",
    "iiif.io",
    "www.energy.gov",
    "openchargealliance.org",
    "www.1edtech.org",
}


def test_a50_canonical_corpus_is_small_traceable_and_domain_scoped() -> None:
    indexed, digest = KnowledgeIndex(KNOWLEDGE_ROOT).load()

    assert len(indexed) == len(EXPECTED_IDS)
    assert len(digest) == 64
    assert {item.record.id for item in indexed} == EXPECTED_IDS
    assert {urlparse(item.record.source_ref).hostname for item in indexed} == EXPECTED_SOURCE_HOSTS
    assert all(item.record.category.value == "domain" for item in indexed)
    assert all(len(item.record.applicable_domains) == 1 for item in indexed)
    assert len({item.record.applicable_domains[0] for item in indexed}) == len(EXPECTED_IDS)
    assert all(item.record.current_run_evidence is False for item in indexed)
    assert all(item.record.authority_effect == "none" for item in indexed)
    assert all(item.record.gate_effect == "none" for item in indexed)
    assert all(item.record.release_effect == "none" for item in indexed)


def test_a50_canonical_content_does_not_fork_skill_methodology_structure() -> None:
    indexed, _ = KnowledgeIndex(KNOWLEDGE_ROOT).load()
    forbidden_headings = {
        "## workflow",
        "## acceptance criteria",
        "## decision rules",
        "## step 1",
        "## step 2",
        "## step 3",
    }

    for item in indexed:
        content_path = (ROOT / item.record.content_ref).resolve()
        text = content_path.read_text(encoding="utf-8").lower()
        assert not any(heading in text for heading in forbidden_headings), item.record.id

    assert not list(KNOWLEDGE_ROOT.rglob("SKILL.md"))
    assert list(SKILLS_ROOT.glob("*/SKILL.md")), "expected canonical skill methodology to remain separate"
