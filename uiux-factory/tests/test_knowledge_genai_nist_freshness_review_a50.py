from __future__ import annotations

from pathlib import Path

from core.benchmarks.knowledge_genai_nist_freshness_review import evaluate_knowledge_genai_nist_freshness_review

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
BENCHMARKS = ROOT / "benchmarks"
KNOWLEDGE = WORKSPACE / "skills_UIUX/knowledge"


def test_a50_14_genai_freshness_review_keeps_hold_without_mutation() -> None:
    before = (KNOWLEDGE / "index.json").read_bytes()
    report = evaluate_knowledge_genai_nist_freshness_review(
        BENCHMARKS / "knowledge-genai-nist-freshness-review-v1.json",
        expansion_proposal_path=BENCHMARKS / "knowledge-expansion-proposal-v1.json",
        canonical_state_path=BENCHMARKS / "knowledge-canonical-state-v3.json",
        owner_delegation_path=BENCHMARKS / "governance-owner-delegation-v1.json",
        workspace_root=WORKSPACE,
        knowledge_root=KNOWLEDGE,
    )
    after = (KNOWLEDGE / "index.json").read_bytes()
    assert report.decision == "KEEP_HOLD_FRESHNESS_REVIEW"
    assert report.source_receipts_clear is True
    assert report.candidate_hold_preserved is True
    assert report.candidate_unindexed is True
    assert report.canonical_five_record_baseline_clear is True
    assert report.no_genai_canonical_assets is True
    assert report.revision_caveat_accurate is True
    assert report.active_revision_blocks_drafting is True
    assert report.re_review_trigger_clear is True
    assert report.mutation_boundaries_clear is True
    assert report.final_owner_review_deferred is True
    assert report.product_evidence is False
    assert before == after


def test_a50_14_genai_candidate_remains_out_of_canonical_namespace() -> None:
    import json
    payload = json.loads((KNOWLEDGE / "index.json").read_text(encoding="utf-8"))
    assert len(payload["records"]) == 5
    assert all("genai" not in ref.lower() and "nist-ai-600" not in ref.lower() for ref in payload["records"])
    assert not list((KNOWLEDGE / "records").glob("*genai*"))
    assert not list((KNOWLEDGE / "content").glob("*genai*"))
