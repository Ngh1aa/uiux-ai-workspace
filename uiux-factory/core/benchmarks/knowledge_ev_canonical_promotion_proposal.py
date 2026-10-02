from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.benchmarks.knowledge_ev_controlled_index_trial import evaluate_knowledge_ev_controlled_index_trial
from core.brain_os.knowledge_contracts import KnowledgeRecord
from core.brain_os.knowledge_retrieval import KnowledgeIndex


class KnowledgeEvPromotionProposalError(ValueError):
    pass


@dataclass(frozen=True)
class EvCanonicalPromotionProposalReport:
    proposal_id: str
    decision: str
    canary_decision: str
    canary_promotion_proposal_allowed: bool
    proposal_preconditions_clear: bool
    candidate_unindexed: bool
    canonical_index_count: int
    review_status: str
    review_verdict: str | None
    source_freshness_rechecked: bool | None
    rollback_plan_accepted: bool | None
    cross_domain_risk_accepted: bool | None
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
        raise KnowledgeEvPromotionProposalError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeEvPromotionProposalError(f"expected object: {path}")
    return payload


def evaluate_knowledge_ev_canonical_promotion_proposal(
    *,
    proposal_review_path: Path,
    review_path: Path,
    canary_trial_path: Path,
    acceptance_trial_path: Path,
    acceptance_mapping_path: Path,
    acceptance_reviews_path: Path,
    draft_corpus_path: Path,
    expansion_proposal_path: Path,
    workspace_root: Path,
    knowledge_root: Path,
    benchmarks_root: Path,
) -> EvCanonicalPromotionProposalReport:
    proposal = _load_json(proposal_review_path)
    expected_top = {
        "schema_version",
        "proposal_id",
        "version",
        "checked_on",
        "scope",
        "candidate",
        "required_preconditions",
        "required_execution_controls",
        "governance",
    }
    if set(proposal) != expected_top or proposal.get("schema_version") != 1:
        raise KnowledgeEvPromotionProposalError("A50.10A proposal contract drifted")
    if proposal["scope"] != "governance_review_only_no_index_mutation":
        raise KnowledgeEvPromotionProposalError("A50.10A scope drifted")

    governance = proposal["governance"]
    expected_governance = {
        "allowed_review_verdicts",
        "index_mutation_in_this_proposal",
        "canonical_promotion_in_this_proposal",
        "auto_promotion_allowed",
        "promotion_execution_requires_separate_task",
        "vector_search_change_allowed",
        "product_evidence",
    }
    if not isinstance(governance, dict) or set(governance) != expected_governance:
        raise KnowledgeEvPromotionProposalError("A50.10A governance contract drifted")
    allowed_verdicts = {"APPROVE_PROMOTION_TASK", "REVISE_PROPOSAL", "HOLD", "REJECT"}
    if set(governance["allowed_review_verdicts"]) != allowed_verdicts:
        raise KnowledgeEvPromotionProposalError("A50.10A review verdict vocabulary drifted")
    for field in (
        "index_mutation_in_this_proposal",
        "canonical_promotion_in_this_proposal",
        "auto_promotion_allowed",
        "vector_search_change_allowed",
        "product_evidence",
    ):
        if governance[field] is not False:
            raise KnowledgeEvPromotionProposalError(f"A50.10A must keep {field}=false")
    if governance["promotion_execution_requires_separate_task"] is not True:
        raise KnowledgeEvPromotionProposalError("A50.10A approval must require a separate promotion task")

    canary = evaluate_knowledge_ev_controlled_index_trial(
        canary_trial_path,
        acceptance_trial_path=acceptance_trial_path,
        acceptance_mapping_path=acceptance_mapping_path,
        acceptance_reviews_path=acceptance_reviews_path,
        draft_corpus_path=draft_corpus_path,
        proposal_path=expansion_proposal_path,
        workspace_root=workspace_root,
        knowledge_root=knowledge_root,
        benchmarks_root=benchmarks_root,
    )

    preconditions = proposal["required_preconditions"]
    expected_preconditions = {
        "canary_decision",
        "promotion_proposal_allowed",
        "canonical_index_expected_count",
        "candidate_must_be_unindexed",
        "genai_candidate_status",
    }
    if not isinstance(preconditions, dict) or set(preconditions) != expected_preconditions:
        raise KnowledgeEvPromotionProposalError("A50.10A precondition contract drifted")
    if preconditions["canary_decision"] != "CANARY_PASS" or preconditions["promotion_proposal_allowed"] is not True:
        raise KnowledgeEvPromotionProposalError("A50.10A must require verified CANARY_PASS proposal eligibility")
    if preconditions["canonical_index_expected_count"] != 3 or preconditions["candidate_must_be_unindexed"] is not True:
        raise KnowledgeEvPromotionProposalError("A50.10A canonical preconditions drifted")
    if preconditions["genai_candidate_status"] != "HOLD_FRESHNESS_REVIEW":
        raise KnowledgeEvPromotionProposalError("GenAI/NIST HOLD boundary drifted")

    candidate = proposal["candidate"]
    expected_candidate_keys = {
        "candidate_id",
        "record_id",
        "source_record_path",
        "source_content_path",
        "proposed_record_path",
        "proposed_content_path",
        "proposed_index_ref",
        "domain",
    }
    if not isinstance(candidate, dict) or set(candidate) != expected_candidate_keys:
        raise KnowledgeEvPromotionProposalError("A50.10A candidate contract drifted")
    if candidate["candidate_id"] != "a50-6-ev-ocpp":
        raise KnowledgeEvPromotionProposalError("A50.10A must target the accepted EV/OCPP candidate")
    if candidate["record_id"] != "knowledge.domain.ev-charging-ocpp-transaction-semantics.v1" or candidate["domain"] != "mobility-ev":
        raise KnowledgeEvPromotionProposalError("A50.10A EV identity drifted")
    if candidate["proposed_index_ref"] != "records/ev-charging-ocpp-transaction-semantics.json":
        raise KnowledgeEvPromotionProposalError("A50.10A proposed canonical index ref drifted")

    source_record_path = (workspace_root / str(candidate["source_record_path"])).resolve()
    source_content_path = (workspace_root / str(candidate["source_content_path"])).resolve()
    if not source_record_path.is_file() or not source_content_path.is_file():
        raise KnowledgeEvPromotionProposalError("A50.10A source draft assets are missing")
    record = KnowledgeRecord.model_validate(_load_json(source_record_path))
    if record.id != candidate["record_id"] or record.applicable_domains != ["mobility-ev"]:
        raise KnowledgeEvPromotionProposalError("A50.10A source draft metadata drifted")

    canonical_index_path = knowledge_root / "index.json"
    index_payload = _load_json(canonical_index_path)
    canonical_refs = index_payload.get("records")
    if index_payload.get("schema_version") != "knowledge-index.v1" or not isinstance(canonical_refs, list):
        raise KnowledgeEvPromotionProposalError("canonical Knowledge OS index contract drifted")
    canonical_records, _digest = KnowledgeIndex(knowledge_root).load()
    canonical_ids = {item.record.id for item in canonical_records}
    candidate_unindexed = (
        len(canonical_refs) == 3
        and record.id not in canonical_ids
        and str(candidate["proposed_index_ref"]) not in canonical_refs
    )
    if not candidate_unindexed:
        raise KnowledgeEvPromotionProposalError("A50.10A requires EV to remain unindexed during proposal review")

    proposed_record_path = (workspace_root / str(candidate["proposed_record_path"])).resolve()
    proposed_content_path = (workspace_root / str(candidate["proposed_content_path"])).resolve()
    if proposed_record_path.exists() or proposed_content_path.exists():
        raise KnowledgeEvPromotionProposalError("A50.10A proposal must not create canonical EV files")

    required_controls = proposal["required_execution_controls"]
    expected_controls = {
        "explicit_human_governance_approval",
        "fresh_source_version_recheck",
        "copy_content_to_canonical_namespace",
        "rewrite_record_content_ref_to_canonical_path",
        "validate_record_contract_before_index_change",
        "add_exactly_one_canonical_index_ref",
        "rerun_retrieval_cross_domain_regression",
        "verify_context_budget",
        "verify_rollback_plan",
        "preserve_vector_search_disabled",
    }
    if not isinstance(required_controls, list) or set(required_controls) != expected_controls:
        raise KnowledgeEvPromotionProposalError("A50.10A execution controls drifted")

    proposal_preconditions_clear = bool(
        canary.decision == preconditions["canary_decision"]
        and canary.promotion_proposal_allowed is True
        and canary.rollback_verified is True
        and canary.canonical_retrieval_regression_clear is True
        and canary.negative_domain_isolation_clear is True
        and canary.genai_hold_preserved is True
        and len(canonical_refs) == preconditions["canonical_index_expected_count"]
        and candidate_unindexed
    )
    if not proposal_preconditions_clear:
        raise KnowledgeEvPromotionProposalError("A50.10A promotion proposal preconditions are not clear")

    review_payload = _load_json(review_path)
    if review_payload.get("proposal_id") != proposal["proposal_id"] or review_payload.get("review_status") not in {"PENDING", "COMPLETE"}:
        raise KnowledgeEvPromotionProposalError("A50.10A review ledger contract drifted")
    policy = review_payload.get("review_policy")
    if not isinstance(policy, dict):
        raise KnowledgeEvPromotionProposalError("A50.10A review policy is required")
    if policy.get("reviewer_type") != "independent_human" or policy.get("explicit_approval_required") is not True:
        raise KnowledgeEvPromotionProposalError("A50.10A requires explicit independent human governance")
    if set(policy.get("allowed_verdicts", [])) != allowed_verdicts:
        raise KnowledgeEvPromotionProposalError("A50.10A review policy verdicts drifted")

    review = review_payload.get("review")
    if not isinstance(review, dict):
        raise KnowledgeEvPromotionProposalError("A50.10A review entry is required")
    expected_review_keys = {
        "status",
        "verdict",
        "rationale",
        "reviewer",
        "reviewed_at",
        "source_freshness_rechecked",
        "rollback_plan_accepted",
        "cross_domain_risk_accepted",
    }
    if set(review) != expected_review_keys:
        raise KnowledgeEvPromotionProposalError("A50.10A review entry drifted")

    separate_promotion_task_allowed = False
    if review["status"] == "PENDING":
        if review_payload["review_status"] != "PENDING":
            raise KnowledgeEvPromotionProposalError("pending A50.10A review requires PENDING ledger status")
        for field in (
            "verdict",
            "rationale",
            "reviewer",
            "reviewed_at",
            "source_freshness_rechecked",
            "rollback_plan_accepted",
            "cross_domain_risk_accepted",
        ):
            if review[field] is not None:
                raise KnowledgeEvPromotionProposalError(f"pending A50.10A review cannot fabricate {field}")
        decision = "GOVERNANCE_REVIEW_REQUIRED"
    elif review["status"] == "REVIEWED":
        if review_payload["review_status"] != "COMPLETE":
            raise KnowledgeEvPromotionProposalError("reviewed A50.10A entry requires COMPLETE ledger status")
        verdict = review.get("verdict")
        if verdict not in allowed_verdicts:
            raise KnowledgeEvPromotionProposalError("invalid A50.10A governance verdict")
        if not str(review.get("rationale") or "").strip() or not str(review.get("reviewer") or "").strip() or not str(review.get("reviewed_at") or "").strip():
            raise KnowledgeEvPromotionProposalError("reviewed A50.10A rationale/reviewer/date are required")
        if verdict == "APPROVE_PROMOTION_TASK":
            approvals = (
                review.get("source_freshness_rechecked") is True,
                review.get("rollback_plan_accepted") is True,
                review.get("cross_domain_risk_accepted") is True,
            )
            if not all(approvals):
                raise KnowledgeEvPromotionProposalError("A50.10A approval requires all explicit governance checks")
            separate_promotion_task_allowed = True
            decision = "APPROVED_FOR_EXPLICIT_PROMOTION_TASK"
        else:
            decision = str(verdict)
    else:
        raise KnowledgeEvPromotionProposalError("A50.10A review status must be PENDING or REVIEWED")

    return EvCanonicalPromotionProposalReport(
        proposal_id=str(proposal["proposal_id"]),
        decision=decision,
        canary_decision=canary.decision,
        canary_promotion_proposal_allowed=canary.promotion_proposal_allowed,
        proposal_preconditions_clear=proposal_preconditions_clear,
        candidate_unindexed=candidate_unindexed,
        canonical_index_count=len(canonical_refs),
        review_status=str(review["status"]),
        review_verdict=review.get("verdict"),
        source_freshness_rechecked=review.get("source_freshness_rechecked"),
        rollback_plan_accepted=review.get("rollback_plan_accepted"),
        cross_domain_risk_accepted=review.get("cross_domain_risk_accepted"),
        separate_promotion_task_allowed=separate_promotion_task_allowed,
        index_mutation_allowed=False,
        canonical_promotion_in_this_proposal=False,
        auto_promotion_allowed=False,
        vector_search_change_allowed=False,
        product_evidence=False,
    )
