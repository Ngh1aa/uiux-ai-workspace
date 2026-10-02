from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.brain_os.knowledge_contracts import KnowledgeRecord
from core.brain_os.knowledge_retrieval import KnowledgeIndex, KnowledgeQuery, KnowledgeRetriever


class KnowledgeEdtechCanonicalApplyError(ValueError):
    pass


@dataclass(frozen=True)
class EdtechCanonicalApplyReport:
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
        raise KnowledgeEdtechCanonicalApplyError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeEdtechCanonicalApplyError(f"expected object: {path}")
    return payload


def evaluate_knowledge_edtech_canonical_apply(
    state_path: Path,
    *,
    workspace_root: Path,
    knowledge_root: Path,
    expansion_proposal_path: Path,
    owner_delegation_path: Path,
    workflow_path: Path,
    conftest_path: Path,
) -> EdtechCanonicalApplyReport:
    state = _load_json(state_path)
    if state.get("schema_version") != 1 or state.get("phase") != "A50.13":
        raise KnowledgeEdtechCanonicalApplyError("A50.13 canonical-state contract drifted")
    if state.get("scope") != "post_edtech_promotion_canonical_truth":
        raise KnowledgeEdtechCanonicalApplyError("A50.13 scope drifted")

    governance = state.get("governance", {})
    if governance.get("canonical_record_count") != 5:
        raise KnowledgeEdtechCanonicalApplyError("A50.13 must define five canonical records")
    if governance.get("vector_search_change_allowed") is not False or governance.get("product_evidence") is not False:
        raise KnowledgeEdtechCanonicalApplyError("A50.13 may not enable vector search or product evidence")
    if governance.get("genai_candidate_status") != "HOLD_FRESHNESS_REVIEW":
        raise KnowledgeEdtechCanonicalApplyError("A50.13 must preserve GenAI/NIST HOLD")
    if governance.get("final_owner_review_status") != "DEFERRED_UNTIL_UPGRADE_COMPLETE":
        raise KnowledgeEdtechCanonicalApplyError("A50.13 final owner review boundary drifted")

    expected_records = state.get("expected_records")
    if not isinstance(expected_records, list) or len(expected_records) != 5:
        raise KnowledgeEdtechCanonicalApplyError("A50.13 expected_records must contain five entries")
    expected_refs = [str(item["ref"]) for item in expected_records]
    expected_ids = [str(item["id"]) for item in expected_records]
    expected_domains = [str(item["domain"]) for item in expected_records]
    if len(set(expected_refs)) != 5 or len(set(expected_ids)) != 5 or len(set(expected_domains)) != 5:
        raise KnowledgeEdtechCanonicalApplyError("A50.13 canonical identities must be unique")

    index_payload = _load_json(knowledge_root / "index.json")
    exact_record_set_clear = bool(index_payload.get("schema_version") == "knowledge-index.v1" and index_payload.get("records") == expected_refs)
    if not exact_record_set_clear:
        raise KnowledgeEdtechCanonicalApplyError("A50.13 canonical index does not match approved five-record set")

    index = KnowledgeIndex(knowledge_root)
    indexed, _digest = index.load()
    canonical_index_count = len(indexed)
    if [item.record.id for item in indexed] != expected_ids:
        raise KnowledgeEdtechCanonicalApplyError("A50.13 loaded ids drifted")
    if [item.record.applicable_domains for item in indexed] != [[domain] for domain in expected_domains]:
        raise KnowledgeEdtechCanonicalApplyError("A50.13 loaded domains drifted")

    promoted = state.get("promoted_record", {})
    canonical_record_path = workspace_root / str(promoted.get("canonical_record_path"))
    canonical_content_path = workspace_root / str(promoted.get("canonical_content_path"))
    revision_record_path = workspace_root / str(promoted.get("revision_record_path"))
    revision_content_path = workspace_root / str(promoted.get("revision_content_path"))
    for path in (canonical_record_path, canonical_content_path, revision_record_path, revision_content_path):
        if not path.is_file():
            raise KnowledgeEdtechCanonicalApplyError(f"A50.13 required asset missing: {path}")

    canonical_payload = _load_json(canonical_record_path)
    revision_payload = _load_json(revision_record_path)
    canonical_record = KnowledgeRecord.model_validate(canonical_payload)
    revision_record = KnowledgeRecord.model_validate(revision_payload)
    promoted_record_contract_clear = bool(
        canonical_record.id == promoted.get("id") == revision_record.id
        and canonical_record.content_ref == promoted.get("canonical_content_path")
        and canonical_record.applicable_domains == ["education-edtech"]
    )
    canonical_semantic = dict(canonical_payload)
    revision_semantic = dict(revision_payload)
    canonical_semantic.pop("content_ref", None)
    revision_semantic.pop("content_ref", None)
    promoted_record_semantic_copy = canonical_semantic == revision_semantic
    promoted_content_exact_copy = canonical_content_path.read_bytes() == revision_content_path.read_bytes()
    source_freshness_metadata_clear = bool(
        canonical_record.version == promoted.get("source_version")
        and promoted.get("source_freshness_checked_on") == state.get("checked_on")
        and canonical_record.source_ref == "https://www.1edtech.org/standards/lti"
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
    cases = state.get("active_regression_cases")
    if not isinstance(cases, list) or len(cases) != 5:
        raise KnowledgeEdtechCanonicalApplyError("A50.13 requires five active regression cases")
    retrieval_regression_clear = True
    context_budget_clear = True
    vector_search_disabled = True
    for case in cases:
        result = retriever.retrieve(KnowledgeQuery(
            as_of=str(state["checked_on"]),
            domains=[str(case["domain"])],
            stages=[str(case["stage"])],
            terms=[str(term) for term in case["terms"]],
            limit=5,
            max_item_chars=5500,
            max_total_chars=7000,
        ))
        expected_id = str(case["expected_record_id"])
        if [hit.record.id for hit in result.hits] != [expected_id]:
            retrieval_regression_clear = False
        if sum(item.reason == "domain_mismatch" for item in result.exclusions) != 4 or result.indexed_record_count != 5:
            retrieval_regression_clear = False
        if result.vector_search_used:
            vector_search_disabled = False
        hit = next((item for item in result.hits if item.record.id == expected_id), None)
        if hit is None or not (250 <= hit.delivered_content_chars <= 5500):
            context_budget_clear = False

    if state.get("negative_isolation_domains") != ["ai-software"]:
        raise KnowledgeEdtechCanonicalApplyError("A50.13 negative-isolation contract drifted")
    ai_result = retriever.retrieve(KnowledgeQuery(
        as_of=str(state["checked_on"]), domains=["ai-software"], stages=["design"],
        terms=["risk", "ai", "integration"], limit=5,
    ))
    negative_domain_isolation_clear = bool(
        not ai_result.hits
        and sum(item.reason == "domain_mismatch" for item in ai_result.exclusions) == 5
        and ai_result.indexed_record_count == 5
    )
    if ai_result.vector_search_used:
        vector_search_disabled = False

    expansion = _load_json(expansion_proposal_path)
    genai = next((item for item in expansion.get("candidates", []) if item.get("candidate_id") == "a50-6-genai-nist"), None)
    genai_hold_preserved = bool(isinstance(genai, dict) and genai.get("proposal_status") == governance["genai_candidate_status"])

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
    )
    final_owner_review_deferred = bool(
        final_review.get("status") == governance["final_owner_review_status"]
        and final_review.get("reviewer") == "Haign12"
    )

    conftest_text = conftest_path.read_text(encoding="utf-8")
    workflow_text = workflow_path.read_text(encoding="utf-8")
    historical_tests = [str(x) for x in state.get("historical_pre_edtech_promotion_test_modules", [])]
    historical_validators = [str(x) for x in state.get("historical_pre_edtech_promotion_validators", [])]
    historical_tests_frozen = all(name in conftest_text for name in historical_tests)
    historical_validators_removed_from_active_ci = all(f"python scripts/{name}" not in workflow_text for name in historical_validators)
    post_promotion_validator_active = "python scripts/validate_knowledge_edtech_canonical_apply.py" in workflow_text

    rollback = state.get("rollback", {})
    rollback_contract_clear = bool(
        rollback.get("restore_index_refs") == expected_refs[:4]
        and rollback.get("remove_only") == [str(promoted.get("canonical_record_path")), str(promoted.get("canonical_content_path"))]
        and rollback.get("preserve_revision_history") is True
        and rollback.get("preserve_governance_history") is True
        and rollback.get("preserve_ev_canonical_record") is True
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
    return EdtechCanonicalApplyReport(
        state_id=str(state["state_id"]), decision=decision, canonical_index_count=canonical_index_count,
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
