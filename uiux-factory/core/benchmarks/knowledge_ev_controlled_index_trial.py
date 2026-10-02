from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from core.benchmarks.knowledge_candidate_acceptance_trial import evaluate_knowledge_candidate_acceptance_trial
from core.benchmarks.knowledge_ready_candidate_drafts import evaluate_knowledge_ready_candidate_drafts
from core.brain_os.knowledge_contracts import KnowledgeRecord
from core.brain_os.knowledge_retrieval import KnowledgeIndex, KnowledgeQuery, KnowledgeRetriever


class KnowledgeEvControlledIndexError(ValueError):
    pass


@dataclass(frozen=True)
class EvControlledIndexTrialReport:
    trial_id: str
    decision: str
    prior_acceptance_verdict: str
    draft_decision: str
    usefulness_evidence_clear: bool
    canonical_index_count: int
    canary_index_count: int
    ev_retrieval_isolated: bool
    canonical_retrieval_regression_clear: bool
    negative_domain_isolation_clear: bool
    context_budget_clear: bool
    rollback_verified: bool
    canonical_index_hash_before: str
    canonical_index_hash_after: str
    genai_hold_preserved: bool
    promotion_proposal_allowed: bool
    index_mutation_allowed: bool
    canonical_promotion_allowed: bool
    auto_promotion_allowed: bool
    vector_search_change_allowed: bool
    product_evidence: bool


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeEvControlledIndexError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeEvControlledIndexError(f"expected object: {path}")
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


def evaluate_knowledge_ev_controlled_index_trial(
    trial_path: Path,
    *,
    acceptance_trial_path: Path,
    acceptance_mapping_path: Path,
    acceptance_reviews_path: Path,
    draft_corpus_path: Path,
    proposal_path: Path,
    workspace_root: Path,
    knowledge_root: Path,
    benchmarks_root: Path,
) -> EvControlledIndexTrialReport:
    trial = _load_json(trial_path)
    expected_top = {
        "schema_version",
        "trial_id",
        "version",
        "checked_on",
        "scope",
        "candidate",
        "canonical_regression_cases",
        "negative_isolation_domains",
        "governance",
    }
    if set(trial) != expected_top or trial.get("schema_version") != 1:
        raise KnowledgeEvControlledIndexError("A50.9B trial contract drifted")
    if trial["scope"] != "temporary_canary_index_not_canonical_promotion":
        raise KnowledgeEvControlledIndexError("A50.9B trial scope drifted")

    governance = trial["governance"]
    expected_governance = {
        "canonical_index_expected_count",
        "canary_index_expected_count",
        "required_prior_ev_verdict",
        "required_draft_decision",
        "index_mutation_allowed",
        "canonical_promotion_allowed",
        "auto_promotion_allowed",
        "vector_search_change_allowed",
        "product_evidence",
        "genai_candidate_status",
        "pass_decision",
        "fail_decision",
    }
    if not isinstance(governance, dict) or set(governance) != expected_governance:
        raise KnowledgeEvControlledIndexError("A50.9B governance contract drifted")
    if governance["canonical_index_expected_count"] != 3 or governance["canary_index_expected_count"] != 4:
        raise KnowledgeEvControlledIndexError("A50.9B must remain a 3→4 temporary canary")
    for field in (
        "index_mutation_allowed",
        "canonical_promotion_allowed",
        "auto_promotion_allowed",
        "vector_search_change_allowed",
        "product_evidence",
    ):
        if governance[field] is not False:
            raise KnowledgeEvControlledIndexError(f"A50.9B must keep {field}=false")
    if governance["genai_candidate_status"] != "HOLD_FRESHNESS_REVIEW":
        raise KnowledgeEvControlledIndexError("GenAI/NIST HOLD boundary drifted")
    if governance["pass_decision"] != "CANARY_PASS" or governance["fail_decision"] != "CANARY_FAIL":
        raise KnowledgeEvControlledIndexError("A50.9B decision vocabulary drifted")

    acceptance = evaluate_knowledge_candidate_acceptance_trial(
        trial_path=acceptance_trial_path,
        mapping_path=acceptance_mapping_path,
        reviews_path=acceptance_reviews_path,
        draft_corpus_path=draft_corpus_path,
        proposal_path=proposal_path,
        workspace_root=workspace_root,
        knowledge_root=knowledge_root,
        benchmarks_root=benchmarks_root,
    )
    acceptance_by_id = {case.case_id: case for case in acceptance.cases}
    ev_acceptance = acceptance_by_id.get("ev-ocpp-charging-session-truth")
    if ev_acceptance is None or ev_acceptance.verdict != governance["required_prior_ev_verdict"]:
        raise KnowledgeEvControlledIndexError("A50.9B requires the merged EV ACCEPT_FOR_INDEX_TRIAL verdict")
    usefulness_evidence_clear = bool(
        ev_acceptance.human_review_complete
        and ev_acceptance.material_regression is False
        and ev_acceptance.joint_usefulness_win
        and ev_acceptance.correctness_guard_clear
        and ev_acceptance.unsupported_claim_risk_guard_clear
    )
    if not usefulness_evidence_clear:
        raise KnowledgeEvControlledIndexError("EV human usefulness/safety precondition is not clear")

    draft_report = evaluate_knowledge_ready_candidate_drafts(
        draft_corpus_path,
        proposal_path=proposal_path,
        workspace_root=workspace_root,
        knowledge_root=knowledge_root,
        benchmarks_root=benchmarks_root,
    )
    ev_draft = next((case for case in draft_report.cases if case.candidate_id == "a50-6-ev-ocpp"), None)
    if ev_draft is None or ev_draft.decision != governance["required_draft_decision"]:
        raise KnowledgeEvControlledIndexError("A50.9B requires the verified EV KEEP_DRAFT baseline")
    if not draft_report.genai_hold_preserved or governance["genai_candidate_status"] != "HOLD_FRESHNESS_REVIEW":
        raise KnowledgeEvControlledIndexError("GenAI/NIST must remain on freshness HOLD")

    candidate = trial["candidate"]
    expected_candidate_keys = {
        "case_id",
        "candidate_id",
        "record_id",
        "record_path",
        "domain",
        "stage",
        "terms",
        "max_item_chars",
        "max_total_chars",
    }
    if not isinstance(candidate, dict) or set(candidate) != expected_candidate_keys:
        raise KnowledgeEvControlledIndexError("A50.9B candidate contract drifted")
    if candidate["candidate_id"] != "a50-6-ev-ocpp" or candidate["record_id"] != ev_draft.record_id:
        raise KnowledgeEvControlledIndexError("A50.9B candidate does not match accepted EV draft")
    if candidate["domain"] != "mobility-ev" or candidate["stage"] != "design":
        raise KnowledgeEvControlledIndexError("A50.9B EV domain/stage drifted")
    if not isinstance(candidate["terms"], list) or not candidate["terms"]:
        raise KnowledgeEvControlledIndexError("A50.9B EV terms are required")

    canonical_index_path = knowledge_root / "index.json"
    canonical_bytes_before = canonical_index_path.read_bytes()
    canonical_hash_before = hashlib.sha256(canonical_bytes_before).hexdigest()
    canonical_payload = json.loads(canonical_bytes_before.decode("utf-8"))
    canonical_refs = canonical_payload.get("records")
    if canonical_payload.get("schema_version") != "knowledge-index.v1" or not isinstance(canonical_refs, list) or len(canonical_refs) != 3:
        raise KnowledgeEvControlledIndexError("canonical index must remain exactly three records before canary")
    if any(str(ref).startswith(("drafts/", "revisions/")) for ref in canonical_refs):
        raise KnowledgeEvControlledIndexError("canonical index must not reference draft/revision records")

    canonical_index = KnowledgeIndex(knowledge_root)
    canonical_records, _canonical_digest = canonical_index.load()
    canonical_ids = [item.record.id for item in canonical_records]
    if len(canonical_ids) != 3 or len(set(canonical_ids)) != 3:
        raise KnowledgeEvControlledIndexError("canonical index ids drifted")
    canonical_retriever = KnowledgeRetriever(canonical_index)

    record_rel_workspace = str(candidate["record_path"])
    record_path = (workspace_root / record_rel_workspace).resolve()
    if not record_path.is_relative_to(knowledge_root.resolve()) or not record_path.is_file():
        raise KnowledgeEvControlledIndexError("EV draft record path is invalid")
    ev_record = KnowledgeRecord.model_validate(_load_json(record_path))
    if ev_record.id != candidate["record_id"] or ev_record.applicable_domains != ["mobility-ev"]:
        raise KnowledgeEvControlledIndexError("EV draft metadata drifted")
    ev_ref = str(record_path.relative_to(knowledge_root.resolve())).replace("\\", "/")
    if ev_ref in canonical_refs or ev_record.id in set(canonical_ids):
        raise KnowledgeEvControlledIndexError("EV draft is already canonical before A50.9B")

    regression_cases = trial["canonical_regression_cases"]
    if not isinstance(regression_cases, list) or len(regression_cases) != 3:
        raise KnowledgeEvControlledIndexError("A50.9B must cover exactly three canonical regression cases")
    negative_domains = trial["negative_isolation_domains"]
    if negative_domains != ["education-edtech", "ai-software"]:
        raise KnowledgeEvControlledIndexError("A50.9B negative isolation domains drifted")

    ev_retrieval_isolated = False
    canonical_retrieval_regression_clear = True
    negative_domain_isolation_clear = True
    context_budget_clear = False
    rollback_verified = False
    canary_count = 0

    with TemporaryDirectory(prefix="a50-9b-canary-") as temp_dir:
        shadow_root = Path(temp_dir) / "skills_UIUX/knowledge"
        shutil.copytree(knowledge_root, shadow_root)
        canary_refs = [*canonical_refs, ev_ref]
        (shadow_root / "canary-index.json").write_text(
            json.dumps({"schema_version": "knowledge-index.v1", "records": canary_refs}, indent=2) + "\n",
            encoding="utf-8",
        )
        canary_index = KnowledgeIndex(shadow_root, manifest_name="canary-index.json")
        canary_records, _canary_digest = canary_index.load()
        canary_count = len(canary_records)
        if canary_count != governance["canary_index_expected_count"]:
            raise KnowledgeEvControlledIndexError("A50.9B canary index must contain exactly four records")
        if len({item.record.id for item in canary_records}) != canary_count:
            raise KnowledgeEvControlledIndexError("A50.9B canary index contains duplicate ids")
        canary_retriever = KnowledgeRetriever(canary_index)

        ev_result = canary_retriever.retrieve(
            _query(
                as_of=trial["checked_on"],
                domain=candidate["domain"],
                stage=candidate["stage"],
                terms=[str(term) for term in candidate["terms"]],
                max_item_chars=int(candidate["max_item_chars"]),
                max_total_chars=int(candidate["max_total_chars"]),
            )
        )
        ev_ids = [hit.record.id for hit in ev_result.hits]
        ev_hit = next((hit for hit in ev_result.hits if hit.record.id == ev_record.id), None)
        ev_retrieval_isolated = (
            ev_ids == [ev_record.id]
            and sum(item.reason == "domain_mismatch" for item in ev_result.exclusions) == 3
            and ev_result.vector_search_used is False
        )
        context_chars = ev_hit.delivered_content_chars if ev_hit else 0
        context_budget_clear = 250 <= context_chars <= int(candidate["max_item_chars"])

        for raw in regression_cases:
            expected_keys = {"id", "domain", "stage", "terms", "expected_record_id"}
            if not isinstance(raw, dict) or set(raw) != expected_keys:
                raise KnowledgeEvControlledIndexError("canonical regression case contract drifted")
            query = _query(
                as_of=trial["checked_on"],
                domain=str(raw["domain"]),
                stage=str(raw["stage"]),
                terms=[str(term) for term in raw["terms"]],
            )
            canonical_result = canonical_retriever.retrieve(query)
            canary_result = canary_retriever.retrieve(query)
            expected_id = str(raw["expected_record_id"])
            canonical_hit_ids = [hit.record.id for hit in canonical_result.hits]
            canary_hit_ids = [hit.record.id for hit in canary_result.hits]
            if canonical_hit_ids != [expected_id] or canary_hit_ids != canonical_hit_ids:
                canonical_retrieval_regression_clear = False
            if not any(item.record_ref == ev_ref and item.reason == "domain_mismatch" for item in canary_result.exclusions):
                canonical_retrieval_regression_clear = False
            if canonical_result.vector_search_used or canary_result.vector_search_used:
                canonical_retrieval_regression_clear = False

        for domain in negative_domains:
            result = canary_retriever.retrieve(
                _query(
                    as_of=trial["checked_on"],
                    domain=str(domain),
                    stage="design",
                    terms=["knowledge", "integration", "state"],
                )
            )
            if result.hits or sum(item.reason == "domain_mismatch" for item in result.exclusions) != 4 or result.vector_search_used:
                negative_domain_isolation_clear = False

        (shadow_root / "rollback-index.json").write_text(
            json.dumps({"schema_version": "knowledge-index.v1", "records": canonical_refs}, indent=2) + "\n",
            encoding="utf-8",
        )
        rollback_records, _rollback_digest = KnowledgeIndex(shadow_root, manifest_name="rollback-index.json").load()
        rollback_ids = [item.record.id for item in rollback_records]
        rollback_verified = rollback_ids == canonical_ids

    canonical_bytes_after = canonical_index_path.read_bytes()
    canonical_hash_after = hashlib.sha256(canonical_bytes_after).hexdigest()
    rollback_verified = rollback_verified and canonical_hash_before == canonical_hash_after and canonical_bytes_before == canonical_bytes_after

    checks = (
        usefulness_evidence_clear,
        ev_retrieval_isolated,
        canonical_retrieval_regression_clear,
        negative_domain_isolation_clear,
        context_budget_clear,
        rollback_verified,
        draft_report.genai_hold_preserved,
        canary_count == governance["canary_index_expected_count"],
    )
    decision = governance["pass_decision"] if all(checks) else governance["fail_decision"]

    return EvControlledIndexTrialReport(
        trial_id=str(trial["trial_id"]),
        decision=str(decision),
        prior_acceptance_verdict=ev_acceptance.verdict,
        draft_decision=ev_draft.decision,
        usefulness_evidence_clear=usefulness_evidence_clear,
        canonical_index_count=len(canonical_refs),
        canary_index_count=canary_count,
        ev_retrieval_isolated=ev_retrieval_isolated,
        canonical_retrieval_regression_clear=canonical_retrieval_regression_clear,
        negative_domain_isolation_clear=negative_domain_isolation_clear,
        context_budget_clear=context_budget_clear,
        rollback_verified=rollback_verified,
        canonical_index_hash_before=canonical_hash_before,
        canonical_index_hash_after=canonical_hash_after,
        genai_hold_preserved=draft_report.genai_hold_preserved,
        promotion_proposal_allowed=decision == governance["pass_decision"],
        index_mutation_allowed=False,
        canonical_promotion_allowed=False,
        auto_promotion_allowed=False,
        vector_search_change_allowed=False,
        product_evidence=False,
    )
