from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.brain_os.knowledge_contracts import KnowledgeRecord
from core.brain_os.knowledge_retrieval import KnowledgeIndex, KnowledgeQuery, KnowledgeRetriever


class KnowledgeEdtechPromotionProposalError(ValueError):
    pass


@dataclass(frozen=True)
class EdtechCanonicalPromotionProposalReport:
    proposal_id: str
    decision: str
    historical_canary_clear: bool
    current_baseline_clear: bool
    source_freshness_clear: bool
    candidate_unindexed: bool
    candidate_authority_boundary_clear: bool
    retrieval_regression_clear: bool
    negative_domain_isolation_clear: bool
    rollback_contract_clear: bool
    genai_hold_preserved: bool
    owner_delegation_clear: bool
    review_status: str
    review_verdict: str | None
    separate_promotion_task_allowed: bool
    index_mutation_allowed: bool
    canonical_promotion_in_this_proposal: bool
    auto_promotion_allowed: bool
    vector_search_change_allowed: bool
    product_evidence: bool


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeEdtechPromotionProposalError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeEdtechPromotionProposalError(f"expected object: {path}")
    return payload


def evaluate_knowledge_edtech_canonical_promotion_proposal(
    *,
    proposal_path: Path,
    review_path: Path,
    canonical_state_path: Path,
    expansion_proposal_path: Path,
    owner_delegation_path: Path,
    workspace_root: Path,
    knowledge_root: Path,
) -> EdtechCanonicalPromotionProposalReport:
    proposal = _load_json(proposal_path)
    expected_top = {
        "schema_version", "proposal_id", "version", "checked_on", "phase", "scope",
        "candidate", "historical_canary_evidence", "current_baseline", "source_freshness",
        "rollback", "required_execution_controls", "governance",
    }
    if set(proposal) != expected_top or proposal.get("schema_version") != 1:
        raise KnowledgeEdtechPromotionProposalError("A50.11 proposal contract drifted")
    if proposal["phase"] != "A50.11" or proposal["scope"] != "governance_review_only_no_index_mutation":
        raise KnowledgeEdtechPromotionProposalError("A50.11 phase/scope drifted")

    governance = proposal["governance"]
    allowed = {"APPROVE_PROMOTION_TASK", "REVISE_PROPOSAL", "HOLD", "REJECT"}
    if set(governance.get("allowed_review_verdicts", [])) != allowed:
        raise KnowledgeEdtechPromotionProposalError("A50.11 verdict vocabulary drifted")
    for field in (
        "index_mutation_in_this_proposal", "canonical_promotion_in_this_proposal",
        "auto_promotion_allowed", "vector_search_change_allowed", "product_evidence",
    ):
        if governance.get(field) is not False:
            raise KnowledgeEdtechPromotionProposalError(f"A50.11 must keep {field}=false")
    if governance.get("promotion_execution_requires_separate_task") is not True:
        raise KnowledgeEdtechPromotionProposalError("A50.11 approval must require a separate task")
    if governance.get("final_owner_review_status") != "DEFERRED_UNTIL_UPGRADE_COMPLETE":
        raise KnowledgeEdtechPromotionProposalError("A50.11 final owner review boundary drifted")

    historical = proposal["historical_canary_evidence"]
    historical_canary_clear = bool(
        historical.get("source_pr") == 119
        and historical.get("head_sha") == "d25af8fe25b69a7fe3460acff323ffe6083d5aa9"
        and historical.get("merge_commit_sha") == "335e2aefd03a5404493391823c33d10a1626e747"
        and historical.get("decision") == "CANARY_PASS"
        and historical.get("prior_verdict") == "ACCEPT_FOR_INDEX_TRIAL"
        and all(historical.get(name) is True for name in (
            "promotion_proposal_allowed", "retrieval_isolated", "canonical_regression_clear",
            "negative_domain_isolation_clear", "context_budget_clear", "rollback_verified",
            "genai_hold_preserved",
        ))
    )
    if not historical_canary_clear:
        raise KnowledgeEdtechPromotionProposalError("A50.11 historical A50.9C evidence is incomplete")

    state = _load_json(canonical_state_path)
    baseline = proposal["current_baseline"]
    expected_records = state.get("expected_records")
    if not isinstance(expected_records, list):
        raise KnowledgeEdtechPromotionProposalError("A50.11 current canonical state is missing")
    expected_refs = [str(item["ref"]) for item in expected_records]
    expected_ids = [str(item["id"]) for item in expected_records]
    current_baseline_clear = bool(
        state.get("state_id") == baseline.get("state_id") == "knowledge-canonical-state-v2"
        and state.get("phase") == "A50.10C"
        and baseline.get("canonical_index_expected_count") == 4
        and len(expected_refs) == 4
        and state.get("governance", {}).get("canonical_record_count") == 4
    )
    if not current_baseline_clear:
        raise KnowledgeEdtechPromotionProposalError("A50.11 requires the EV-inclusive four-record baseline")

    index_path = knowledge_root / "index.json"
    before = index_path.read_bytes()
    index_payload = _load_json(index_path)
    if index_payload.get("schema_version") != "knowledge-index.v1" or index_payload.get("records") != expected_refs:
        raise KnowledgeEdtechPromotionProposalError("A50.11 canonical index drifted from state v2")
    index = KnowledgeIndex(knowledge_root)
    indexed, _digest = index.load()
    if [item.record.id for item in indexed] != expected_ids:
        raise KnowledgeEdtechPromotionProposalError("A50.11 canonical ids drifted")

    candidate = proposal["candidate"]
    source_record_path = workspace_root / str(candidate["source_record_path"])
    source_content_path = workspace_root / str(candidate["source_content_path"])
    if not source_record_path.is_file() or not source_content_path.is_file():
        raise KnowledgeEdtechPromotionProposalError("A50.11 EdTech revision assets are missing")
    record = KnowledgeRecord.model_validate(_load_json(source_record_path))
    candidate_unindexed = bool(
        baseline.get("candidate_must_be_unindexed") is True
        and record.id == candidate.get("record_id")
        and record.id not in expected_ids
        and candidate.get("proposed_index_ref") not in expected_refs
        and not (workspace_root / str(candidate["proposed_record_path"])).exists()
        and not (workspace_root / str(candidate["proposed_content_path"])).exists()
    )
    if not candidate_unindexed:
        raise KnowledgeEdtechPromotionProposalError("A50.11 requires EdTech v2 to remain unindexed/unpromoted")

    candidate_authority_boundary_clear = bool(
        record.applicable_domains == ["education-edtech"]
        and record.advisory_only is True
        and record.current_run_evidence is False
        and record.authority_effect == "none"
        and record.gate_effect == "none"
        and record.evidence_effect == "none"
        and record.release_effect == "none"
    )
    if not candidate_authority_boundary_clear:
        raise KnowledgeEdtechPromotionProposalError("A50.11 candidate authority boundary drifted")

    freshness = proposal["source_freshness"]
    source_freshness_clear = bool(
        freshness.get("status") == "RECHECKED"
        and freshness.get("checked_on") == proposal["checked_on"] == "2026-10-02"
        and freshness.get("official_source") == "1EdTech"
        and freshness.get("current_core") == "LTI 1.3"
        and freshness.get("required_advantage_services") == [
            "Assignment and Grade Services 2.0",
            "Names and Role Provisioning Services 2.0",
            "Deep Linking 2.0",
        ]
        and freshness.get("candidate_metadata_matches") is True
        and record.source_ref == candidate.get("expected_source_ref")
        and record.version == candidate.get("expected_source_version")
    )
    if not source_freshness_clear:
        raise KnowledgeEdtechPromotionProposalError("A50.11 source freshness receipt/metadata drifted")

    retriever = KnowledgeRetriever(index)
    retrieval_regression_clear = True
    vector_search_disabled = True
    for case in state.get("active_regression_cases", []):
        result = retriever.retrieve(KnowledgeQuery(
            as_of=proposal["checked_on"],
            domains=[str(case["domain"])],
            stages=[str(case["stage"])],
            terms=[str(term) for term in case["terms"]],
            limit=5,
            max_item_chars=5500,
            max_total_chars=7000,
        ))
        if [hit.record.id for hit in result.hits] != [str(case["expected_record_id"])]:
            retrieval_regression_clear = False
        if result.indexed_record_count != 4 or result.vector_search_used:
            retrieval_regression_clear = False
            vector_search_disabled = False
    if not retrieval_regression_clear:
        raise KnowledgeEdtechPromotionProposalError("A50.11 current canonical retrieval regression detected")

    negative_domain_isolation_clear = True
    for domain in ("education-edtech", "ai-software"):
        result = retriever.retrieve(KnowledgeQuery(
            as_of=proposal["checked_on"], domains=[domain], stages=["design"],
            terms=["lti", "integration", "state"], limit=5,
        ))
        if result.hits or sum(item.reason == "domain_mismatch" for item in result.exclusions) != 4:
            negative_domain_isolation_clear = False
        if result.vector_search_used:
            vector_search_disabled = False
    if not negative_domain_isolation_clear or not vector_search_disabled:
        raise KnowledgeEdtechPromotionProposalError("A50.11 negative isolation/vector boundary failed")

    rollback = proposal["rollback"]
    rollback_contract_clear = bool(
        rollback.get("restore_index_from_current_four_record_baseline") is True
        and rollback.get("remove_only_future_edtech_canonical_assets") == [
            str(candidate["proposed_record_path"]), str(candidate["proposed_content_path"]),
        ]
        and rollback.get("preserve_ev_canonical_record") is True
        and rollback.get("preserve_revision_and_governance_history") is True
        and index_path.read_bytes() == before
    )
    if not rollback_contract_clear:
        raise KnowledgeEdtechPromotionProposalError("A50.11 rollback/no-mutation contract failed")

    expansion = _load_json(expansion_proposal_path)
    genai = next((item for item in expansion.get("candidates", []) if item.get("candidate_id") == "a50-6-genai-nist"), None)
    genai_hold_preserved = bool(isinstance(genai, dict) and genai.get("proposal_status") == "HOLD_FRESHNESS_REVIEW")
    if not genai_hold_preserved:
        raise KnowledgeEdtechPromotionProposalError("A50.11 must preserve GenAI/NIST HOLD")

    delegation = _load_json(owner_delegation_path)
    permissions = delegation.get("permissions", {})
    boundaries = delegation.get("governance_boundaries", {})
    final_review = delegation.get("final_review", {})
    owner_delegation_clear = bool(
        delegation.get("delegation_id") == "governance-owner-delegation-2026-10-02"
        and delegation.get("owner_login") == "Haign12"
        and permissions.get("continue_to_next_task_when_required_checks_pass") is True
        and permissions.get("bypass_failed_or_missing_checks") is False
        and permissions.get("fabricate_independent_human_review") is False
        and boundaries.get("each_step_requires_auditable_evidence") is True
        and final_review.get("status") == governance["final_owner_review_status"]
    )
    if not owner_delegation_clear:
        raise KnowledgeEdtechPromotionProposalError("A50.11 owner delegation boundary is not clear")

    review_payload = _load_json(review_path)
    policy = review_payload.get("review_policy", {})
    review = review_payload.get("review", {})
    review_status = str(review.get("status"))
    review_verdict = review.get("verdict")
    if (
        review_payload.get("proposal_id") != proposal["proposal_id"]
        or review_payload.get("review_status") != "COMPLETE"
        or policy.get("reviewer_type") != "owner_delegated_governance"
        or policy.get("delegation_id") != delegation.get("delegation_id")
        or policy.get("explicit_approval_required") is not True
        or set(policy.get("allowed_verdicts", [])) != allowed
        or review_status != "REVIEWED"
        or review_verdict not in allowed
        or not str(review.get("rationale") or "").strip()
        or not str(review.get("reviewer") or "").strip()
    ):
        raise KnowledgeEdtechPromotionProposalError("A50.11 delegated review contract drifted")

    separate_promotion_task_allowed = False
    if review_verdict == "APPROVE_PROMOTION_TASK":
        if not all(review.get(name) is True for name in (
            "source_freshness_rechecked", "rollback_plan_accepted",
            "cross_domain_risk_accepted", "current_four_record_baseline_accepted",
        )):
            raise KnowledgeEdtechPromotionProposalError("A50.11 approval requires all explicit checks")
        decision = "APPROVED_FOR_EXPLICIT_PROMOTION_TASK"
        separate_promotion_task_allowed = True
    else:
        decision = str(review_verdict)

    return EdtechCanonicalPromotionProposalReport(
        proposal_id=str(proposal["proposal_id"]),
        decision=decision,
        historical_canary_clear=historical_canary_clear,
        current_baseline_clear=current_baseline_clear,
        source_freshness_clear=source_freshness_clear,
        candidate_unindexed=candidate_unindexed,
        candidate_authority_boundary_clear=candidate_authority_boundary_clear,
        retrieval_regression_clear=retrieval_regression_clear,
        negative_domain_isolation_clear=negative_domain_isolation_clear,
        rollback_contract_clear=rollback_contract_clear,
        genai_hold_preserved=genai_hold_preserved,
        owner_delegation_clear=owner_delegation_clear,
        review_status=review_status,
        review_verdict=review_verdict,
        separate_promotion_task_allowed=separate_promotion_task_allowed,
        index_mutation_allowed=False,
        canonical_promotion_in_this_proposal=False,
        auto_promotion_allowed=False,
        vector_search_change_allowed=False,
        product_evidence=False,
    )
