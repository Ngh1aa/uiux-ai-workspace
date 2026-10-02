from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.brain_os.knowledge_contracts import KnowledgeRecord
from core.brain_os.knowledge_retrieval import KnowledgeIndex, KnowledgeQuery, KnowledgeRetriever


class KnowledgeEvCanonicalApplyError(ValueError):
    pass


@dataclass(frozen=True)
class EvCanonicalApplyReport:
    state_id: str
    decision: str
    canonical_index_count: int
    exact_record_set_clear: bool
    promoted_record_contract_clear: bool
    promoted_content_exact_copy: bool
    promoted_record_semantic_copy: bool
    source_freshness_metadata_clear: bool
    authority_boundary_clear: bool
    retrieval_regression_clear: bool
    negative_domain_isolation_clear: bool
    context_budget_clear: bool
    vector_search_disabled: bool
    genai_hold_preserved: bool
    owner_delegation_clear: bool
    historical_tests_frozen: bool
    historical_validators_removed_from_active_ci: bool
    post_promotion_validator_active: bool
    rollback_contract_clear: bool
    final_owner_review_deferred: bool
    product_evidence: bool


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeEvCanonicalApplyError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeEvCanonicalApplyError(f"expected object: {path}")
    return payload


def evaluate_knowledge_ev_canonical_apply(
    state_path: Path,
    *,
    workspace_root: Path,
    knowledge_root: Path,
    expansion_proposal_path: Path,
    owner_delegation_path: Path,
    workflow_path: Path,
    conftest_path: Path,
) -> EvCanonicalApplyReport:
    state = _load_json(state_path)
    expected_top = {
        "schema_version",
        "state_id",
        "version",
        "checked_on",
        "phase",
        "scope",
        "expected_records",
        "promoted_record",
        "active_regression_cases",
        "negative_isolation_domains",
        "historical_pre_promotion_test_modules",
        "historical_pre_promotion_validators",
        "governance",
        "rollback",
    }
    if set(state) != expected_top or state.get("schema_version") != 1:
        raise KnowledgeEvCanonicalApplyError("A50.10C canonical-state contract drifted")
    if state["phase"] != "A50.10C" or state["scope"] != "post_ev_promotion_canonical_truth":
        raise KnowledgeEvCanonicalApplyError("A50.10C identity/scope drifted")

    governance = state["governance"]
    expected_governance = {
        "canonical_record_count",
        "vector_search_change_allowed",
        "product_evidence",
        "genai_candidate_status",
        "final_owner_review_status",
    }
    if not isinstance(governance, dict) or set(governance) != expected_governance:
        raise KnowledgeEvCanonicalApplyError("A50.10C governance contract drifted")
    if governance["canonical_record_count"] != 4:
        raise KnowledgeEvCanonicalApplyError("A50.10C must define exactly four canonical records")
    if governance["vector_search_change_allowed"] is not False or governance["product_evidence"] is not False:
        raise KnowledgeEvCanonicalApplyError("A50.10C may not enable vector search or claim product evidence")
    if governance["genai_candidate_status"] != "HOLD_FRESHNESS_REVIEW":
        raise KnowledgeEvCanonicalApplyError("A50.10C must preserve GenAI/NIST freshness HOLD")
    if governance["final_owner_review_status"] != "DEFERRED_UNTIL_UPGRADE_COMPLETE":
        raise KnowledgeEvCanonicalApplyError("A50.10C must preserve deferred final owner review")

    expected_records = state["expected_records"]
    if not isinstance(expected_records, list) or len(expected_records) != 4:
        raise KnowledgeEvCanonicalApplyError("A50.10C expected_records must contain four entries")
    expected_refs = [str(item["ref"]) for item in expected_records]
    expected_ids = [str(item["id"]) for item in expected_records]
    expected_domains = [str(item["domain"]) for item in expected_records]
    if len(set(expected_refs)) != 4 or len(set(expected_ids)) != 4 or len(set(expected_domains)) != 4:
        raise KnowledgeEvCanonicalApplyError("A50.10C canonical record identity must be unique")

    index_payload = _load_json(knowledge_root / "index.json")
    refs = index_payload.get("records")
    exact_record_set_clear = bool(
        index_payload.get("schema_version") == "knowledge-index.v1"
        and refs == expected_refs
    )
    if not exact_record_set_clear:
        raise KnowledgeEvCanonicalApplyError("A50.10C canonical index does not match the exact approved record set")

    index = KnowledgeIndex(knowledge_root)
    indexed, _index_hash = index.load()
    canonical_index_count = len(indexed)
    loaded_ids = [item.record.id for item in indexed]
    loaded_domains = [item.record.applicable_domains for item in indexed]
    if canonical_index_count != 4 or loaded_ids != expected_ids:
        raise KnowledgeEvCanonicalApplyError("A50.10C loaded canonical record ids drifted")
    if loaded_domains != [[domain] for domain in expected_domains]:
        raise KnowledgeEvCanonicalApplyError("A50.10C loaded canonical domains drifted")

    promoted = state["promoted_record"]
    expected_promoted_keys = {
        "id",
        "canonical_record_path",
        "canonical_content_path",
        "draft_record_path",
        "draft_content_path",
        "source_version",
        "source_freshness_checked_on",
    }
    if not isinstance(promoted, dict) or set(promoted) != expected_promoted_keys:
        raise KnowledgeEvCanonicalApplyError("A50.10C promoted-record contract drifted")

    canonical_record_path = workspace_root / str(promoted["canonical_record_path"])
    canonical_content_path = workspace_root / str(promoted["canonical_content_path"])
    draft_record_path = workspace_root / str(promoted["draft_record_path"])
    draft_content_path = workspace_root / str(promoted["draft_content_path"])
    for path in (canonical_record_path, canonical_content_path, draft_record_path, draft_content_path):
        if not path.is_file():
            raise KnowledgeEvCanonicalApplyError(f"A50.10C required asset missing: {path}")

    canonical_payload = _load_json(canonical_record_path)
    draft_payload = _load_json(draft_record_path)
    canonical_record = KnowledgeRecord.model_validate(canonical_payload)
    draft_record = KnowledgeRecord.model_validate(draft_payload)
    promoted_record_contract_clear = bool(
        canonical_record.id == promoted["id"]
        and canonical_record.id == draft_record.id
        and canonical_record.content_ref == promoted["canonical_content_path"]
        and canonical_record.applicable_domains == ["mobility-ev"]
    )

    canonical_copy_compare = dict(canonical_payload)
    draft_copy_compare = dict(draft_payload)
    canonical_copy_compare.pop("content_ref", None)
    draft_copy_compare.pop("content_ref", None)
    promoted_record_semantic_copy = canonical_copy_compare == draft_copy_compare
    promoted_content_exact_copy = canonical_content_path.read_bytes() == draft_content_path.read_bytes()
    source_freshness_metadata_clear = bool(
        canonical_record.version == promoted["source_version"]
        and promoted["source_freshness_checked_on"] == state["checked_on"]
        and canonical_record.source_ref == "https://openchargealliance.org/my-oca/ocpp/"
    )
    authority_boundary_clear = bool(
        canonical_record.advisory_only is True
        and canonical_record.current_run_evidence is False
        and canonical_record.authority_effect == "none"
        and canonical_record.gate_effect == "none"
        and canonical_record.evidence_effect == "none"
        and canonical_record.release_effect == "none"
    )

    retriever = KnowledgeRetriever(index)
    regression_cases = state["active_regression_cases"]
    if not isinstance(regression_cases, list) or len(regression_cases) != 4:
        raise KnowledgeEvCanonicalApplyError("A50.10C requires four active regression cases")
    retrieval_regression_clear = True
    context_budget_clear = True
    vector_search_disabled = True
    seen_case_ids: set[str] = set()
    for case in regression_cases:
        case_id = str(case["id"])
        if case_id in seen_case_ids:
            raise KnowledgeEvCanonicalApplyError(f"duplicate A50.10C regression case: {case_id}")
        seen_case_ids.add(case_id)
        result = retriever.retrieve(
            KnowledgeQuery(
                as_of=str(state["checked_on"]),
                domains=[str(case["domain"])],
                stages=[str(case["stage"])],
                terms=[str(term) for term in case["terms"]],
                limit=5,
                max_item_chars=5_500,
                max_total_chars=7_000,
            )
        )
        actual_ids = [hit.record.id for hit in result.hits]
        expected_id = str(case["expected_record_id"])
        if actual_ids != [expected_id]:
            retrieval_regression_clear = False
        if sum(item.reason == "domain_mismatch" for item in result.exclusions) != 3:
            retrieval_regression_clear = False
        if result.indexed_record_count != 4:
            retrieval_regression_clear = False
        if result.vector_search_used:
            vector_search_disabled = False
        hit = next((item for item in result.hits if item.record.id == expected_id), None)
        if hit is None or not (250 <= hit.delivered_content_chars <= 5_500):
            context_budget_clear = False

    if state["negative_isolation_domains"] != ["education-edtech", "ai-software"]:
        raise KnowledgeEvCanonicalApplyError("A50.10C negative-isolation domain contract drifted")
    negative_domain_isolation_clear = True
    for domain in state["negative_isolation_domains"]:
        result = retriever.retrieve(
            KnowledgeQuery(
                as_of=str(state["checked_on"]),
                domains=[str(domain)],
                stages=["design"],
                terms=["knowledge", "integration", "state"],
                limit=5,
            )
        )
        if result.hits or sum(item.reason == "domain_mismatch" for item in result.exclusions) != 4:
            negative_domain_isolation_clear = False
        if result.vector_search_used:
            vector_search_disabled = False

    expansion = _load_json(expansion_proposal_path)
    candidates = expansion.get("candidates")
    if not isinstance(candidates, list):
        raise KnowledgeEvCanonicalApplyError("A50.6 expansion candidate history is missing")
    genai = next((item for item in candidates if item.get("candidate_id") == "a50-6-genai-nist"), None)
    genai_hold_preserved = bool(
        isinstance(genai, dict)
        and genai.get("proposal_status") == governance["genai_candidate_status"]
    )

    delegation = _load_json(owner_delegation_path)
    permissions = delegation.get("permissions")
    boundaries = delegation.get("governance_boundaries")
    final_review = delegation.get("final_review")
    owner_delegation_clear = bool(
        delegation.get("delegation_id") == "governance-owner-delegation-2026-10-02"
        and delegation.get("owner_login") == "Haign12"
        and delegation.get("mode") == "preauthorized_continuation_after_required_gates_pass"
        and isinstance(permissions, dict)
        and permissions.get("continue_to_next_task_when_required_checks_pass") is True
        and permissions.get("bypass_failed_or_missing_checks") is False
        and permissions.get("fabricate_independent_human_review") is False
        and isinstance(boundaries, dict)
        and boundaries.get("each_step_requires_auditable_evidence") is True
        and boundaries.get("final_retrospective_owner_review_required") is True
    )
    final_owner_review_deferred = bool(
        isinstance(final_review, dict)
        and final_review.get("status") == governance["final_owner_review_status"]
        and final_review.get("reviewer") == "Haign12"
    )

    historical_tests = set(str(item) for item in state["historical_pre_promotion_test_modules"])
    historical_validators = set(str(item) for item in state["historical_pre_promotion_validators"])
    conftest_text = conftest_path.read_text(encoding="utf-8")
    workflow_text = workflow_path.read_text(encoding="utf-8")
    historical_tests_frozen = all(name in conftest_text for name in historical_tests)
    historical_validators_removed_from_active_ci = all(
        f"python scripts/{name}" not in workflow_text for name in historical_validators
    )
    post_promotion_validator_active = "python scripts/validate_knowledge_ev_canonical_apply.py" in workflow_text

    rollback = state["rollback"]
    expected_rollback_keys = {"restore_index_refs", "remove_only", "preserve_drafts", "preserve_governance_history"}
    rollback_contract_clear = bool(
        isinstance(rollback, dict)
        and set(rollback) == expected_rollback_keys
        and rollback["restore_index_refs"] == expected_refs[:3]
        and rollback["remove_only"] == [
            str(promoted["canonical_record_path"]),
            str(promoted["canonical_content_path"]),
        ]
        and rollback["preserve_drafts"] is True
        and rollback["preserve_governance_history"] is True
    )

    checks = (
        exact_record_set_clear,
        promoted_record_contract_clear,
        promoted_content_exact_copy,
        promoted_record_semantic_copy,
        source_freshness_metadata_clear,
        authority_boundary_clear,
        retrieval_regression_clear,
        negative_domain_isolation_clear,
        context_budget_clear,
        vector_search_disabled,
        genai_hold_preserved,
        owner_delegation_clear,
        historical_tests_frozen,
        historical_validators_removed_from_active_ci,
        post_promotion_validator_active,
        rollback_contract_clear,
        final_owner_review_deferred,
    )
    decision = "CANONICAL_APPLY_PASS" if all(checks) else "CANONICAL_APPLY_FAIL"

    return EvCanonicalApplyReport(
        state_id=str(state["state_id"]),
        decision=decision,
        canonical_index_count=canonical_index_count,
        exact_record_set_clear=exact_record_set_clear,
        promoted_record_contract_clear=promoted_record_contract_clear,
        promoted_content_exact_copy=promoted_content_exact_copy,
        promoted_record_semantic_copy=promoted_record_semantic_copy,
        source_freshness_metadata_clear=source_freshness_metadata_clear,
        authority_boundary_clear=authority_boundary_clear,
        retrieval_regression_clear=retrieval_regression_clear,
        negative_domain_isolation_clear=negative_domain_isolation_clear,
        context_budget_clear=context_budget_clear,
        vector_search_disabled=vector_search_disabled,
        genai_hold_preserved=genai_hold_preserved,
        owner_delegation_clear=owner_delegation_clear,
        historical_tests_frozen=historical_tests_frozen,
        historical_validators_removed_from_active_ci=historical_validators_removed_from_active_ci,
        post_promotion_validator_active=post_promotion_validator_active,
        rollback_contract_clear=rollback_contract_clear,
        final_owner_review_deferred=final_owner_review_deferred,
        product_evidence=False,
    )
