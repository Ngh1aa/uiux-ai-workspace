from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.brain_os.knowledge_retrieval import KnowledgeIndex


class KnowledgeGenaiFreshnessReviewError(ValueError):
    pass


@dataclass(frozen=True)
class GenaiFreshnessReviewReport:
    review_id: str
    decision: str
    source_receipts_clear: bool
    candidate_hold_preserved: bool
    candidate_unindexed: bool
    canonical_five_record_baseline_clear: bool
    no_genai_canonical_assets: bool
    revision_caveat_accurate: bool
    active_revision_blocks_drafting: bool
    re_review_trigger_clear: bool
    mutation_boundaries_clear: bool
    final_owner_review_deferred: bool
    product_evidence: bool


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeGenaiFreshnessReviewError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeGenaiFreshnessReviewError(f"expected object: {path}")
    return payload


def evaluate_knowledge_genai_nist_freshness_review(
    review_path: Path,
    *,
    expansion_proposal_path: Path,
    canonical_state_path: Path,
    owner_delegation_path: Path,
    workspace_root: Path,
    knowledge_root: Path,
) -> GenaiFreshnessReviewReport:
    review = _load_json(review_path)
    expected_top = {
        "schema_version", "review_id", "version", "checked_on", "phase", "scope",
        "candidate_id", "candidate_record_id", "source_receipts", "freshness_assessment",
        "decision", "rationale", "re_review_trigger", "governance",
    }
    if set(review) != expected_top or review.get("schema_version") != 1:
        raise KnowledgeGenaiFreshnessReviewError("A50.14 review contract drifted")
    if review.get("phase") != "A50.14" or review.get("scope") != "freshness_governance_only_no_draft_or_index_mutation":
        raise KnowledgeGenaiFreshnessReviewError("A50.14 phase/scope drifted")
    if review.get("decision") != "KEEP_HOLD_FRESHNESS_REVIEW":
        raise KnowledgeGenaiFreshnessReviewError("A50.14 must fail closed while AI RMF revision remains active")

    receipts = review.get("source_receipts")
    source_receipts_clear = bool(
        isinstance(receipts, list)
        and len(receipts) == 3
        and all(isinstance(item, dict) for item in receipts)
        and all(str(item.get("source", "")).startswith("https://") for item in receipts)
        and all(str(item.get("publisher", "")).strip() for item in receipts)
        and all(str(item.get("finding", "")).strip() for item in receipts)
        and {item.get("publisher") for item in receipts} <= {"NIST", "NIST AIRC"}
    )
    if not source_receipts_clear:
        raise KnowledgeGenaiFreshnessReviewError("A50.14 official source receipts are incomplete")

    assessment = review.get("freshness_assessment")
    expected_assessment = {
        "ai_600_1_official_and_current_resource",
        "ai_rmf_1_0_revision_in_progress",
        "candidate_revision_caveat_still_accurate",
        "framework_dependency_stable_enough_for_drafting",
        "freshness_risk",
    }
    if not isinstance(assessment, dict) or set(assessment) != expected_assessment:
        raise KnowledgeGenaiFreshnessReviewError("A50.14 freshness assessment drifted")
    revision_caveat_accurate = bool(
        assessment["ai_600_1_official_and_current_resource"] is True
        and assessment["ai_rmf_1_0_revision_in_progress"] is True
        and assessment["candidate_revision_caveat_still_accurate"] is True
        and assessment["freshness_risk"] == "HIGH"
    )
    active_revision_blocks_drafting = assessment["framework_dependency_stable_enough_for_drafting"] is False
    if not revision_caveat_accurate or not active_revision_blocks_drafting:
        raise KnowledgeGenaiFreshnessReviewError("A50.14 active revision must keep candidate held")

    expansion = _load_json(expansion_proposal_path)
    candidate = next(
        (item for item in expansion.get("candidates", []) if item.get("candidate_id") == review["candidate_id"]),
        None,
    )
    candidate_hold_preserved = bool(
        isinstance(candidate, dict)
        and candidate.get("proposal_status") == "HOLD_FRESHNESS_REVIEW"
        and candidate.get("proposed_record_id") == review["candidate_record_id"]
        and candidate.get("source_version") == "NIST-AI-600-1-2024-with-2026-framework-revision-caveat"
        and candidate.get("freshness_risk") == "HIGH"
    )
    if not candidate_hold_preserved:
        raise KnowledgeGenaiFreshnessReviewError("A50.14 historical GenAI HOLD/caveat drifted")

    state = _load_json(canonical_state_path)
    expected_records = state.get("expected_records")
    if not isinstance(expected_records, list):
        raise KnowledgeGenaiFreshnessReviewError("A50.14 canonical state v3 missing")
    expected_refs = [str(item["ref"]) for item in expected_records]
    expected_ids = [str(item["id"]) for item in expected_records]
    governance = review["governance"]
    canonical_five_record_baseline_clear = bool(
        state.get("state_id") == "knowledge-canonical-state-v3"
        and state.get("phase") == "A50.13"
        and len(expected_refs) == governance.get("canonical_index_expected_count") == 5
    )
    if not canonical_five_record_baseline_clear:
        raise KnowledgeGenaiFreshnessReviewError("A50.14 requires exact five-record A50.13 baseline")

    index_path = knowledge_root / "index.json"
    index_before = index_path.read_bytes()
    indexed, _digest = KnowledgeIndex(knowledge_root).load()
    canonical_ids = [item.record.id for item in indexed]
    index_payload = _load_json(index_path)
    candidate_unindexed = bool(
        governance.get("candidate_must_remain_unindexed") is True
        and index_payload.get("records") == expected_refs
        and canonical_ids == expected_ids
        and review["candidate_record_id"] not in canonical_ids
    )
    if not candidate_unindexed:
        raise KnowledgeGenaiFreshnessReviewError("A50.14 candidate must remain unindexed")

    genai_named_assets = [
        path for path in (knowledge_root / "records").glob("*genai*")
    ] + [
        path for path in (knowledge_root / "content").glob("*genai*")
    ]
    no_genai_canonical_assets = not genai_named_assets
    if not no_genai_canonical_assets:
        raise KnowledgeGenaiFreshnessReviewError("A50.14 must not create canonical GenAI assets")

    trigger = review.get("re_review_trigger")
    re_review_trigger_clear = bool(
        isinstance(trigger, dict)
        and trigger.get("type") == "official_nist_framework_status_change"
        and "NIST" in str(trigger.get("condition", ""))
        and "revised AI RMF" in str(trigger.get("condition", ""))
    )
    if not re_review_trigger_clear:
        raise KnowledgeGenaiFreshnessReviewError("A50.14 requires explicit future re-review trigger")

    expected_false = (
        "draft_creation_allowed", "canonical_record_creation_allowed", "index_mutation_allowed",
        "acceptance_trial_allowed", "canary_allowed", "promotion_allowed",
        "vector_search_change_allowed", "product_evidence",
    )
    mutation_boundaries_clear = all(governance.get(field) is False for field in expected_false)
    if not mutation_boundaries_clear or index_path.read_bytes() != index_before:
        raise KnowledgeGenaiFreshnessReviewError("A50.14 freshness review must be non-mutating")

    delegation = _load_json(owner_delegation_path)
    final_owner_review_deferred = bool(
        delegation.get("owner_login") == "Haign12"
        and delegation.get("permissions", {}).get("bypass_failed_or_missing_checks") is False
        and delegation.get("final_review", {}).get("status") == governance.get("final_owner_review_status") == "DEFERRED_UNTIL_UPGRADE_COMPLETE"
    )
    if not final_owner_review_deferred:
        raise KnowledgeGenaiFreshnessReviewError("A50.14 owner review/delegation boundary drifted")

    return GenaiFreshnessReviewReport(
        review_id=str(review["review_id"]),
        decision=str(review["decision"]),
        source_receipts_clear=source_receipts_clear,
        candidate_hold_preserved=candidate_hold_preserved,
        candidate_unindexed=candidate_unindexed,
        canonical_five_record_baseline_clear=canonical_five_record_baseline_clear,
        no_genai_canonical_assets=no_genai_canonical_assets,
        revision_caveat_accurate=revision_caveat_accurate,
        active_revision_blocks_drafting=active_revision_blocks_drafting,
        re_review_trigger_clear=re_review_trigger_clear,
        mutation_boundaries_clear=mutation_boundaries_clear,
        final_owner_review_deferred=final_owner_review_deferred,
        product_evidence=False,
    )
