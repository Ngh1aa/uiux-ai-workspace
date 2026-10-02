from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from core.benchmarks.knowledge_ev_controlled_index_trial import evaluate_knowledge_ev_controlled_index_trial
from core.brain_os.knowledge_contracts import KnowledgeRecord
from core.brain_os.knowledge_retrieval import KnowledgeIndex, KnowledgeQuery, KnowledgeRetriever


class KnowledgeEvPromotionShadowError(ValueError):
    pass


@dataclass(frozen=True)
class EvCanonicalPromotionShadowReport:
    implementation_id: str
    decision: str
    canary_decision: str
    owner_delegation_clear: bool
    source_freshness_clear: bool
    candidate_unindexed_before: bool
    canonical_index_count_before: int
    shadow_index_count: int
    canonical_record_contract_clear: bool
    canonical_content_ref_rewritten: bool
    ev_retrieval_isolated: bool
    canonical_retrieval_regression_clear: bool
    negative_domain_isolation_clear: bool
    context_budget_clear: bool
    rollback_verified: bool
    repository_index_unchanged: bool
    repository_canonical_assets_absent: bool
    migration_contract_clear: bool
    genai_hold_preserved: bool
    repository_index_mutation_allowed: bool
    repository_canonical_assets_commit_allowed: bool
    auto_promotion_in_this_phase: bool
    vector_search_change_allowed: bool
    product_evidence: bool


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeEvPromotionShadowError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeEvPromotionShadowError(f"expected object: {path}")
    return payload


def _query(*, as_of: str, domain: str, stage: str, terms: list[str], max_item_chars: int = 4000, max_total_chars: int = 8000) -> KnowledgeQuery:
    return KnowledgeQuery(
        as_of=as_of,
        domains=[domain],
        stages=[stage],
        terms=terms,
        limit=5,
        max_item_chars=max_item_chars,
        max_total_chars=max_total_chars,
    )


def evaluate_knowledge_ev_canonical_promotion_shadow(
    shadow_contract_path: Path,
    *,
    canary_trial_path: Path,
    acceptance_trial_path: Path,
    acceptance_mapping_path: Path,
    acceptance_reviews_path: Path,
    draft_corpus_path: Path,
    expansion_proposal_path: Path,
    promotion_proposal_path: Path,
    owner_delegation_path: Path,
    workspace_root: Path,
    knowledge_root: Path,
    benchmarks_root: Path,
) -> EvCanonicalPromotionShadowReport:
    contract = _load_json(shadow_contract_path)
    expected_top = {
        "schema_version",
        "implementation_id",
        "version",
        "checked_on",
        "scope",
        "candidate",
        "source_freshness_evidence",
        "required_preconditions",
        "canonical_regression_cases",
        "negative_isolation_domains",
        "post_promotion_migration",
        "governance",
    }
    if set(contract) != expected_top or contract.get("schema_version") != 1:
        raise KnowledgeEvPromotionShadowError("A50.10B contract drifted")
    if contract["scope"] != "shadow_apply_only_no_repository_canonical_mutation":
        raise KnowledgeEvPromotionShadowError("A50.10B must remain shadow-only")

    governance = contract["governance"]
    expected_governance = {
        "pass_decision",
        "fail_decision",
        "repository_index_mutation_allowed",
        "repository_canonical_assets_commit_allowed",
        "auto_promotion_in_this_phase",
        "vector_search_change_allowed",
        "product_evidence",
        "final_owner_review_deferred",
    }
    if not isinstance(governance, dict) or set(governance) != expected_governance:
        raise KnowledgeEvPromotionShadowError("A50.10B governance contract drifted")
    if governance["pass_decision"] != "READY_FOR_CANONICAL_APPLY" or governance["fail_decision"] != "SHADOW_APPLY_FAIL":
        raise KnowledgeEvPromotionShadowError("A50.10B decision vocabulary drifted")
    for field in (
        "repository_index_mutation_allowed",
        "repository_canonical_assets_commit_allowed",
        "auto_promotion_in_this_phase",
        "vector_search_change_allowed",
        "product_evidence",
    ):
        if governance[field] is not False:
            raise KnowledgeEvPromotionShadowError(f"A50.10B must keep {field}=false")
    if governance["final_owner_review_deferred"] is not True:
        raise KnowledgeEvPromotionShadowError("A50.10B must preserve deferred final owner review")

    preconditions = contract["required_preconditions"]
    if preconditions != {
        "canary_decision": "CANARY_PASS",
        "promotion_proposal_id": "knowledge-ev-canonical-promotion-proposal-v1",
        "owner_delegation_id": "governance-owner-delegation-2026-10-02",
        "canonical_index_expected_count": 3,
        "candidate_must_be_unindexed": True,
        "genai_candidate_status": "HOLD_FRESHNESS_REVIEW",
    }:
        raise KnowledgeEvPromotionShadowError("A50.10B preconditions drifted")

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
    if canary.decision != "CANARY_PASS" or canary.promotion_proposal_allowed is not True:
        raise KnowledgeEvPromotionShadowError("A50.10B requires verified EV CANARY_PASS")

    proposal = _load_json(promotion_proposal_path)
    if proposal.get("proposal_id") != preconditions["promotion_proposal_id"]:
        raise KnowledgeEvPromotionShadowError("A50.10B promotion proposal identity drifted")
    proposal_governance = proposal.get("governance")
    if not isinstance(proposal_governance, dict) or proposal_governance.get("promotion_execution_requires_separate_task") is not True:
        raise KnowledgeEvPromotionShadowError("A50.10B must remain the separate bounded implementation task")
    if proposal_governance.get("auto_promotion_allowed") is not False:
        raise KnowledgeEvPromotionShadowError("A50.10A auto-promotion boundary drifted")

    delegation = _load_json(owner_delegation_path)
    permissions = delegation.get("permissions")
    boundaries = delegation.get("governance_boundaries")
    owner_delegation_clear = bool(
        delegation.get("delegation_id") == preconditions["owner_delegation_id"]
        and delegation.get("owner_login") == "Haign12"
        and delegation.get("mode") == "preauthorized_continuation_after_required_gates_pass"
        and isinstance(permissions, dict)
        and permissions.get("continue_to_next_task_when_required_checks_pass") is True
        and permissions.get("create_follow_up_implementation_tasks") is True
        and permissions.get("bypass_failed_or_missing_checks") is False
        and permissions.get("fabricate_independent_human_review") is False
        and isinstance(boundaries, dict)
        and boundaries.get("each_step_requires_auditable_evidence") is True
        and boundaries.get("final_retrospective_owner_review_required") is True
    )
    if not owner_delegation_clear:
        raise KnowledgeEvPromotionShadowError("A50.10B owner delegation is incomplete or unsafe")

    candidate = contract["candidate"]
    expected_candidate_keys = {
        "record_id",
        "source_record_path",
        "source_content_path",
        "canonical_record_path",
        "canonical_content_path",
        "canonical_index_ref",
        "domain",
        "stage",
        "terms",
        "max_item_chars",
        "max_total_chars",
    }
    if not isinstance(candidate, dict) or set(candidate) != expected_candidate_keys:
        raise KnowledgeEvPromotionShadowError("A50.10B candidate contract drifted")
    if candidate["record_id"] != "knowledge.domain.ev-charging-ocpp-transaction-semantics.v1" or candidate["domain"] != "mobility-ev":
        raise KnowledgeEvPromotionShadowError("A50.10B EV identity drifted")

    source_record_path = (workspace_root / str(candidate["source_record_path"])).resolve()
    source_content_path = (workspace_root / str(candidate["source_content_path"])).resolve()
    if not source_record_path.is_file() or not source_content_path.is_file():
        raise KnowledgeEvPromotionShadowError("A50.10B EV draft assets are missing")
    source_record_payload = _load_json(source_record_path)
    source_record = KnowledgeRecord.model_validate(source_record_payload)

    freshness = contract["source_freshness_evidence"]
    expected_freshness_keys = {"source_url", "observed_version", "observed_label", "checked_on", "evidence_kind"}
    if not isinstance(freshness, dict) or set(freshness) != expected_freshness_keys:
        raise KnowledgeEvPromotionShadowError("A50.10B source freshness evidence drifted")
    source_freshness_clear = bool(
        freshness["source_url"] == source_record.source_ref
        and freshness["observed_version"] == source_record.version
        and freshness["observed_label"] == "OCPP 2.1 Edition 2 Errata 2026-06"
        and freshness["checked_on"] == contract["checked_on"]
        and freshness["evidence_kind"] == "official_source_web_recheck"
    )
    if not source_freshness_clear:
        raise KnowledgeEvPromotionShadowError("A50.10B source freshness evidence does not match the candidate")

    canonical_index_path = knowledge_root / "index.json"
    real_index_before = canonical_index_path.read_bytes()
    real_index_hash_before = hashlib.sha256(real_index_before).hexdigest()
    index_payload = json.loads(real_index_before.decode("utf-8"))
    canonical_refs = index_payload.get("records")
    if index_payload.get("schema_version") != "knowledge-index.v1" or not isinstance(canonical_refs, list):
        raise KnowledgeEvPromotionShadowError("canonical index contract drifted")
    canonical_records, _ = KnowledgeIndex(knowledge_root).load()
    canonical_ids = [item.record.id for item in canonical_records]
    candidate_unindexed_before = bool(
        len(canonical_refs) == preconditions["canonical_index_expected_count"]
        and candidate["canonical_index_ref"] not in canonical_refs
        and source_record.id not in set(canonical_ids)
    )
    if not candidate_unindexed_before:
        raise KnowledgeEvPromotionShadowError("A50.10B requires EV to remain unindexed before shadow apply")

    real_canonical_record_path = (workspace_root / str(candidate["canonical_record_path"])).resolve()
    real_canonical_content_path = (workspace_root / str(candidate["canonical_content_path"])).resolve()
    repository_canonical_assets_absent = not real_canonical_record_path.exists() and not real_canonical_content_path.exists()
    if not repository_canonical_assets_absent:
        raise KnowledgeEvPromotionShadowError("A50.10B shadow phase must not begin with committed EV canonical assets")

    regression_cases = contract["canonical_regression_cases"]
    if not isinstance(regression_cases, list) or len(regression_cases) != 3:
        raise KnowledgeEvPromotionShadowError("A50.10B requires three canonical regression cases")
    if contract["negative_isolation_domains"] != ["education-edtech", "ai-software"]:
        raise KnowledgeEvPromotionShadowError("A50.10B negative-domain contract drifted")

    migration = contract["post_promotion_migration"]
    expected_historical = {
        "validate_knowledge_ev_controlled_index_trial.py",
        "validate_knowledge_edtech_controlled_index_trial.py",
        "validate_knowledge_ev_canonical_promotion_proposal.py",
    }
    migration_contract_clear = bool(
        isinstance(migration, dict)
        and migration.get("next_phase") == "A50.10C"
        and migration.get("historical_three_record_validators_must_transition_before_repository_apply") is True
        and set(migration.get("historical_validators", [])) == expected_historical
    )
    if not migration_contract_clear:
        raise KnowledgeEvPromotionShadowError("A50.10B post-promotion migration contract drifted")

    canonical_record_contract_clear = False
    canonical_content_ref_rewritten = False
    ev_retrieval_isolated = False
    canonical_retrieval_regression_clear = True
    negative_domain_isolation_clear = True
    context_budget_clear = False
    rollback_verified = False
    shadow_index_count = 0

    with TemporaryDirectory(prefix="a50-10b-shadow-") as temp_dir:
        shadow_workspace = Path(temp_dir) / "workspace"
        shadow_knowledge = shadow_workspace / "skills_UIUX/knowledge"
        shutil.copytree(knowledge_root, shadow_knowledge)

        shadow_content_path = shadow_workspace / str(candidate["canonical_content_path"])
        shadow_record_path = shadow_workspace / str(candidate["canonical_record_path"])
        shadow_content_path.parent.mkdir(parents=True, exist_ok=True)
        shadow_record_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_content_path, shadow_content_path)

        canonical_payload = dict(source_record_payload)
        canonical_payload["content_ref"] = str(candidate["canonical_content_path"])
        shadow_record_path.write_text(json.dumps(canonical_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        canonical_record = KnowledgeRecord.model_validate(canonical_payload)
        canonical_record_contract_clear = canonical_record.id == source_record.id and canonical_record.advisory_only is True and canonical_record.current_run_evidence is False
        canonical_content_ref_rewritten = canonical_record.content_ref == candidate["canonical_content_path"]

        shadow_index_path = shadow_knowledge / "index.json"
        shadow_index_before = shadow_index_path.read_bytes()
        promoted_refs = [*canonical_refs, str(candidate["canonical_index_ref"])]
        shadow_index_path.write_text(
            json.dumps({"schema_version": "knowledge-index.v1", "records": promoted_refs}, indent=2) + "\n",
            encoding="utf-8",
        )
        promoted_index = KnowledgeIndex(shadow_knowledge)
        promoted_records, _ = promoted_index.load()
        shadow_index_count = len(promoted_records)
        if shadow_index_count != 4 or len({item.record.id for item in promoted_records}) != 4:
            raise KnowledgeEvPromotionShadowError("A50.10B shadow promotion must produce exactly four unique canonical records")
        retriever = KnowledgeRetriever(promoted_index)

        ev_result = retriever.retrieve(
            _query(
                as_of=contract["checked_on"],
                domain=str(candidate["domain"]),
                stage=str(candidate["stage"]),
                terms=[str(term) for term in candidate["terms"]],
                max_item_chars=int(candidate["max_item_chars"]),
                max_total_chars=int(candidate["max_total_chars"]),
            )
        )
        ev_ids = [hit.record.id for hit in ev_result.hits]
        ev_hit = next((hit for hit in ev_result.hits if hit.record.id == source_record.id), None)
        ev_retrieval_isolated = ev_ids == [source_record.id] and sum(item.reason == "domain_mismatch" for item in ev_result.exclusions) == 3 and ev_result.vector_search_used is False
        context_budget_clear = bool(ev_hit and 250 <= ev_hit.delivered_content_chars <= int(candidate["max_item_chars"]))

        baseline_retriever = KnowledgeRetriever(KnowledgeIndex(knowledge_root))
        for raw in regression_cases:
            query = _query(
                as_of=contract["checked_on"],
                domain=str(raw["domain"]),
                stage=str(raw["stage"]),
                terms=[str(term) for term in raw["terms"]],
            )
            baseline = baseline_retriever.retrieve(query)
            promoted = retriever.retrieve(query)
            expected_id = str(raw["expected_record_id"])
            if [hit.record.id for hit in baseline.hits] != [expected_id] or [hit.record.id for hit in promoted.hits] != [expected_id]:
                canonical_retrieval_regression_clear = False
            if not any(item.record_ref == candidate["canonical_index_ref"] and item.reason == "domain_mismatch" for item in promoted.exclusions):
                canonical_retrieval_regression_clear = False
            if baseline.vector_search_used or promoted.vector_search_used:
                canonical_retrieval_regression_clear = False

        for domain in contract["negative_isolation_domains"]:
            result = retriever.retrieve(
                _query(
                    as_of=contract["checked_on"],
                    domain=str(domain),
                    stage="design",
                    terms=["knowledge", "integration", "state"],
                )
            )
            if result.hits or sum(item.reason == "domain_mismatch" for item in result.exclusions) != 4 or result.vector_search_used:
                negative_domain_isolation_clear = False

        shadow_index_path.write_bytes(shadow_index_before)
        shadow_record_path.unlink()
        shadow_content_path.unlink()
        rollback_records, _ = KnowledgeIndex(shadow_knowledge).load()
        rollback_verified = bool(
            shadow_index_path.read_bytes() == shadow_index_before
            and [item.record.id for item in rollback_records] == canonical_ids
            and not shadow_record_path.exists()
            and not shadow_content_path.exists()
        )

    real_index_after = canonical_index_path.read_bytes()
    repository_index_unchanged = bool(
        real_index_before == real_index_after
        and real_index_hash_before == hashlib.sha256(real_index_after).hexdigest()
    )
    repository_canonical_assets_absent = repository_canonical_assets_absent and not real_canonical_record_path.exists() and not real_canonical_content_path.exists()

    checks = (
        canary.genai_hold_preserved,
        owner_delegation_clear,
        source_freshness_clear,
        candidate_unindexed_before,
        canonical_record_contract_clear,
        canonical_content_ref_rewritten,
        ev_retrieval_isolated,
        canonical_retrieval_regression_clear,
        negative_domain_isolation_clear,
        context_budget_clear,
        rollback_verified,
        repository_index_unchanged,
        repository_canonical_assets_absent,
        migration_contract_clear,
    )
    decision = governance["pass_decision"] if all(checks) else governance["fail_decision"]

    return EvCanonicalPromotionShadowReport(
        implementation_id=str(contract["implementation_id"]),
        decision=str(decision),
        canary_decision=canary.decision,
        owner_delegation_clear=owner_delegation_clear,
        source_freshness_clear=source_freshness_clear,
        candidate_unindexed_before=candidate_unindexed_before,
        canonical_index_count_before=len(canonical_refs),
        shadow_index_count=shadow_index_count,
        canonical_record_contract_clear=canonical_record_contract_clear,
        canonical_content_ref_rewritten=canonical_content_ref_rewritten,
        ev_retrieval_isolated=ev_retrieval_isolated,
        canonical_retrieval_regression_clear=canonical_retrieval_regression_clear,
        negative_domain_isolation_clear=negative_domain_isolation_clear,
        context_budget_clear=context_budget_clear,
        rollback_verified=rollback_verified,
        repository_index_unchanged=repository_index_unchanged,
        repository_canonical_assets_absent=repository_canonical_assets_absent,
        migration_contract_clear=migration_contract_clear,
        genai_hold_preserved=canary.genai_hold_preserved,
        repository_index_mutation_allowed=False,
        repository_canonical_assets_commit_allowed=False,
        auto_promotion_in_this_phase=False,
        vector_search_change_allowed=False,
        product_evidence=False,
    )
