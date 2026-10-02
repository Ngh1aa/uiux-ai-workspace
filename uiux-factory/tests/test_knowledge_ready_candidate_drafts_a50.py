from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.benchmarks.knowledge_ready_candidate_drafts import (
    KnowledgeReadyCandidateDraftError,
    evaluate_knowledge_ready_candidate_drafts,
)
from core.brain_os.knowledge_contracts import KnowledgeRecord


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
CORPUS = ROOT / "benchmarks/knowledge-ready-candidate-drafts-v1.json"
PROPOSAL = ROOT / "benchmarks/knowledge-expansion-proposal-v1.json"
KNOWLEDGE = WORKSPACE / "skills_UIUX/knowledge"
BENCHMARKS = ROOT / "benchmarks"


def _evaluate(corpus: Path = CORPUS):
    return evaluate_knowledge_ready_candidate_drafts(
        corpus,
        proposal_path=PROPOSAL,
        workspace_root=WORKSPACE,
        knowledge_root=KNOWLEDGE,
        benchmarks_root=BENCHMARKS,
    )


def test_a50_7_ready_drafts_pass_without_canonical_acceptance() -> None:
    report = _evaluate()

    assert report.passed == report.total == 2
    assert report.canonical_index_count == 3
    assert report.draft_record_count == 2
    assert report.shadow_index_count == 5
    assert report.keep_draft_count == 2
    assert report.revise_draft_count == 0
    assert report.genai_hold_preserved is True
    assert report.index_mutation_allowed is False
    assert report.canonical_acceptance_allowed is False
    assert report.vector_search_change_allowed is False
    assert report.human_usefulness_claimed is False
    assert all(case.decision == "KEEP_DRAFT" for case in report.cases)
    assert all(case.retrieval_noise_clear for case in report.cases)
    assert all(case.skill_duplication_clear for case in report.cases)
    assert all(case.canonical_unindexed for case in report.cases)


def test_a50_7_draft_records_are_valid_knowledge_records_but_not_indexed() -> None:
    index = json.loads((KNOWLEDGE / "index.json").read_text(encoding="utf-8"))
    assert len(index["records"]) == 3
    assert all(not str(ref).startswith("drafts/") for ref in index["records"])

    draft_paths = sorted((KNOWLEDGE / "drafts/records").glob("*.json"))
    assert len(draft_paths) == 2
    draft_records = [KnowledgeRecord.model_validate_json(path.read_text(encoding="utf-8")) for path in draft_paths]
    indexed_ids = {
        json.loads((KNOWLEDGE / ref).read_text(encoding="utf-8"))["id"]
        for ref in index["records"]
    }
    assert {record.id for record in draft_records}.isdisjoint(indexed_ids)
    assert {record.applicable_domains[0] for record in draft_records} == {"education-edtech", "mobility-ev"}
    assert all(record.advisory_only is True for record in draft_records)
    assert all(record.current_run_evidence is False for record in draft_records)


def test_a50_7_genai_nist_stays_hold_and_has_no_draft_record() -> None:
    proposal = json.loads(PROPOSAL.read_text(encoding="utf-8"))
    genai = next(item for item in proposal["candidates"] if item["candidate_id"] == "a50-6-genai-nist")
    assert genai["proposal_status"] == "HOLD_FRESHNESS_REVIEW"

    draft_ids = {
        json.loads(path.read_text(encoding="utf-8"))["id"]
        for path in (KNOWLEDGE / "drafts/records").glob("*.json")
    }
    assert genai["proposed_record_id"] not in draft_ids


def test_a50_7_refuses_human_usefulness_claim(tmp_path: Path) -> None:
    payload = json.loads(CORPUS.read_text(encoding="utf-8"))
    payload["governance"]["human_usefulness_claim_allowed"] = True
    tampered = tmp_path / "tampered.json"
    tampered.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(KnowledgeReadyCandidateDraftError, match="human_usefulness_claim_allowed"):
        _evaluate(tampered)


def test_a50_7_refuses_domain_drift(tmp_path: Path) -> None:
    payload = json.loads(CORPUS.read_text(encoding="utf-8"))
    payload["cases"][0]["domain"] = "financial-services"
    tampered = tmp_path / "tampered-domain.json"
    tampered.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(KnowledgeReadyCandidateDraftError, match="draft domain is not isolated|proposal domain mismatch"):
        _evaluate(tampered)


def test_a50_7_refuses_source_host_drift(tmp_path: Path) -> None:
    payload = json.loads(CORPUS.read_text(encoding="utf-8"))
    payload["cases"][1]["expected_source_host"] = "example.com"
    tampered = tmp_path / "tampered-source.json"
    tampered.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(KnowledgeReadyCandidateDraftError, match="unexpected source host"):
        _evaluate(tampered)
