from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

from core.benchmarks.knowledge_expansion_proposal import (
    KnowledgeExpansionProposalError,
    evaluate_knowledge_expansion_proposal,
)


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
BENCHMARKS = ROOT / "benchmarks"
PROPOSAL = BENCHMARKS / "knowledge-expansion-proposal-v1.json"
KNOWLEDGE = WORKSPACE / "skills_UIUX" / "knowledge"


def _evaluate(*, proposal_path: Path = PROPOSAL, knowledge_root: Path = KNOWLEDGE):
    return evaluate_knowledge_expansion_proposal(
        proposal_path=proposal_path,
        workspace_root=WORKSPACE,
        knowledge_root=knowledge_root,
        benchmarks_root=BENCHMARKS,
    )


def _proposal_payload() -> dict:
    return json.loads(PROPOSAL.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def test_a50_6_canonical_proposal_is_bounded_and_non_mutating() -> None:
    report = _evaluate()

    assert report.trigger_recommendation == "CONSIDER_EXPANSION"
    assert report.current_index_count == 3
    assert report.candidate_count == 3
    assert report.ready_count == 2
    assert report.hold_count == 1
    assert report.reject_count == 0
    assert report.index_mutation_allowed is False
    assert report.record_creation_allowed is False
    assert report.vector_search_change_allowed is False
    assert {item.domain for item in report.candidates} == {
        "education-edtech",
        "mobility-ev",
        "ai-software",
    }
    assert {item.status for item in report.candidates} == {
        "READY_FOR_CONTENT_DRAFT",
        "HOLD_FRESHNESS_REVIEW",
    }


def test_a50_6_current_index_remains_exactly_three_records() -> None:
    index = json.loads((KNOWLEDGE / "index.json").read_text(encoding="utf-8"))
    assert len(index["records"]) == 3
    proposal = _proposal_payload()
    proposed_ids = {candidate["proposed_record_id"] for candidate in proposal["candidates"]}
    current_ids = {
        json.loads((KNOWLEDGE / relative).read_text(encoding="utf-8"))["id"]
        for relative in index["records"]
    }
    assert proposed_ids.isdisjoint(current_ids)


def test_a50_6_time_sensitive_candidate_must_hold_for_freshness_review(tmp_path: Path) -> None:
    payload = _proposal_payload()
    ai = next(item for item in payload["candidates"] if item["domain"] == "ai-software")
    ai["proposal_status"] = "READY_FOR_CONTENT_DRAFT"
    path = _write(tmp_path / "proposal.json", payload)

    with pytest.raises(KnowledgeExpansionProposalError, match="time-sensitive candidate must HOLD"):
        _evaluate(proposal_path=path)


def test_a50_6_trigger_cannot_overstate_round_two_verdict(tmp_path: Path) -> None:
    payload = _proposal_payload()
    payload["trigger"]["required_joint_usefulness_win_count"] = 2
    path = _write(tmp_path / "proposal.json", payload)

    with pytest.raises(KnowledgeExpansionProposalError, match="joint-usefulness trigger drifted"):
        _evaluate(proposal_path=path)


def test_a50_6_source_must_be_https(tmp_path: Path) -> None:
    payload = _proposal_payload()
    payload["candidates"][0]["source_ref"] = "http://example.invalid/spec"
    path = _write(tmp_path / "proposal.json", payload)

    with pytest.raises(KnowledgeExpansionProposalError, match="source_ref must be an HTTPS source"):
        _evaluate(proposal_path=path)


def test_a50_6_related_skill_owner_paths_must_exist(tmp_path: Path) -> None:
    payload = _proposal_payload()
    payload["candidates"][0]["related_skill_paths"] = ["skills_UIUX/not-a-real-skill/SKILL.md"]
    path = _write(tmp_path / "proposal.json", payload)

    with pytest.raises(KnowledgeExpansionProposalError, match="related skill path is invalid"):
        _evaluate(proposal_path=path)


def test_a50_6_candidate_cannot_claim_gate_or_release_authority(tmp_path: Path) -> None:
    payload = _proposal_payload()
    payload["candidates"][1]["gate_effect"] = "pass"
    path = _write(tmp_path / "proposal.json", payload)

    with pytest.raises(KnowledgeExpansionProposalError, match="gate_effect must remain none"):
        _evaluate(proposal_path=path)


def test_a50_6_proposal_cannot_enable_index_or_record_mutation(tmp_path: Path) -> None:
    payload = _proposal_payload()
    payload["governance"]["record_creation_allowed"] = True
    path = _write(tmp_path / "proposal.json", payload)

    with pytest.raises(KnowledgeExpansionProposalError, match="record_creation_allowed=false"):
        _evaluate(proposal_path=path)


def test_a50_6_fails_if_canonical_index_is_expanded_inside_proposal_phase(tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    shutil.copytree(KNOWLEDGE, knowledge)
    index_path = knowledge / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    index["records"].append("records/not-allowed-yet.json")
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

    with pytest.raises(KnowledgeExpansionProposalError, match="must not mutate the three-record canonical index"):
        _evaluate(knowledge_root=knowledge)


def test_a50_6_high_risk_candidate_cannot_be_ready(tmp_path: Path) -> None:
    payload = _proposal_payload()
    payload["candidates"][0]["duplication_risk"] = "HIGH"
    path = _write(tmp_path / "proposal.json", payload)

    with pytest.raises(KnowledgeExpansionProposalError, match="high-risk candidate cannot be READY"):
        _evaluate(proposal_path=path)
