from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from core.benchmarks.knowledge_edtech_revision_trial import evaluate_knowledge_edtech_revision_trial
from core.benchmarks.knowledge_ready_candidate_drafts import evaluate_knowledge_ready_candidate_drafts
from core.brain_os.knowledge_contracts import KnowledgeRecord
from core.brain_os.knowledge_retrieval import KnowledgeIndex, KnowledgeQuery, KnowledgeRetriever


class KnowledgeEdtechControlledIndexError(ValueError):
    pass


@dataclass(frozen=True)
class EdtechControlledIndexTrialReport:
    trial_id: str
    decision: str
    prior_revision_verdict: str
    usefulness_evidence_clear: bool
    revision_record_unindexed: bool
    canonical_index_count: int
    canary_index_count: int
    edtech_retrieval_isolated: bool
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
        raise KnowledgeEdtechControlledIndexError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeEdtechControlledIndexError(f"expected object: {path}")
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


def evaluate_knowledge_edtech_controlled_index_trial(
    trial_path: Path,
    *,
    revision_trial_path: Path,
    revision_mapping_path: Path,
    revision_reviews_path: Path,
    prior_trial_path: Path,
    prior_mapping_path: Path,
    prior_reviews_path: Path,
    draft_corpus_path: Path,
    proposal_path: Path,
    workspace_root: Path,
    knowledge_root: Path,
    benchmarks_root: Path,
) -> EdtechControlledIndexTrialReport:
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
        raise KnowledgeEdtechControlledIndexError("A50.9C trial contract drifted")
    if trial["scope"] != "temporary_canary_index_not_canonical_promotion":
        raise KnowledgeEdtechControlledIndexError("A50.9C trial scope drifted")

    governance = trial["governance"]
    expected_governance = {
        "canonical_index_expected_count",
        "canary_index_expected_count",
        "required_prior_edtech_verdict",
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
        raise KnowledgeEdtechControlledIndexError("A50.9C governance contract drifted")
    if governance["canonical_index_expected_count"] != 3 or governance["canary_index_expected_count"] != 4:
        raise KnowledgeEdtechControlledIndexError("A50.9C must remain a 3→4 temporary canary")
    for field in (
        "index_mutation_allowed",
        "canonical_promotion_allowed",
        "auto_promotion_allowed",
        "vector_search_change_allowed",
        "product_evidence",
    ):
        if governance[field] is not False:
            raise KnowledgeEdtechControlledIndexError(f"A50.9C must keep {field}=false")
    if governance["genai_candidate_status"] != "HOLD_FRESHNESS_REVIEW":
        raise KnowledgeEdtechControlledIndexError("GenAI/NIST HOLD boundary drifted")
    if governance["pass_decision"] != "CANARY_PASS" or governance["fail_decision"] != "CANARY_FAIL":
        raise KnowledgeEdtechControlledIndexError("A50.9C decision vocabulary drifted")

    revision = evaluate_knowledge_edtech_revision_trial(
        trial_path=revision_trial_path,
        mapping_path=revision_mapping_path,
        reviews_path=revision_reviews_path,
        prior_trial_path=prior_trial_path,
        prior_mapping_path=prior_mapping_path,
        prior_reviews_path=prior_reviews_path,
        draft_corpus_path=draft_corpus_path,
        proposal_path=proposal_path,
        workspace_root=workspace_root,
        knowledge_root=knowledge_root,
        benchmarks_root=benchmarks_root,
    )
    if revision.verdict != governance["required_prior_edtech_verdict"]:
        raise KnowledgeEdtechControlledIndexError("A50.9C requires the merged EdTech ACCEPT_FOR_INDEX_TRIAL verdict")
    usefulness_evidence_clear = bool(
        revision.human_review_complete
        and revision.material_regression is False
        and revision.joint_usefulness_win
        and revision.correctness_guard_clear
        and revision.unsupported_claim_risk_guard_clear
        and revision.required_state_guidance_present
        and revision.shadow_retrieval_isolated
    )
    if not usefulness_evidence_clear:
        raise KnowledgeEdtechControlledIndexError("EdTech human usefulness/safety precondition is not clear")

    draft_report = evaluate_knowledge_ready_candidate_drafts(
        draft_corpus_path,
        proposal_path=proposal_path,
        workspace_root=workspace_root,
        knowledge_root=knowledge_root,
        benchmarks_root=benchmarks_root,
    )
    if not draft_report.genai_hold_preserved:
        raise KnowledgeEdtechControlledIndexError("GenAI/NIST must remain on freshness HOLD")

    candidate = trial["candidate"]
    expected_candidate_keys = {
        "case_id",
        "record_id",
        "record_path",
        "domain",
        "stage",
        "terms",
        "max_item_chars",
        "max_total_chars",
    }
    if not isinstance(candidate, dict) or set(candidate) != expected_candidate_keys:
        raise KnowledgeEdtechControlledIndexError("A50.9C candidate contract drifted")
    if candidate["record_id"] != revision.revised_record_id:
        raise KnowledgeEdtechControlledIndexError("A50.9C candidate does not match accepted EdTech v2 revision")
    if candidate["domain"] != "education-edtech" or candidate["stage"] != "design":
        raise KnowledgeEdtechControlledIndexError("A50.9C EdTech domain/stage drifted")
    if not isinstance(candidate["terms"], list) or not candidate["terms"]:
        raise KnowledgeEdtechControlledIndexError("A50.9C EdTech terms are required")

    canonical_index_path = knowledge_root / "index.json"
    canonical_bytes_before = canonical_index_path.read_bytes()
    canonical_hash_before = hashlib.sha256(canonical_bytes_before).hexdigest()
    canonical_payload = json.loads(canonical_bytes_before.decode("utf-8"))
    canonical_refs = canonical_payload.get("records")
    if canonical_payload.get("schema_version") != "knowledge-index.v1" or not isinstance(canonical_refs, list) or len(canonical_refs) != 3:
        raise KnowledgeEdtechControlledIndexError("canonical index must remain exactly three records before canary")
    if any(str(ref).startswith(("drafts/", "revisions/")) for ref in canonical_refs):
        raise KnowledgeEdtechControlledIndexError("canonical index must not reference draft/revision records")

    canonical_index = KnowledgeIndex(knowledge_root)
    canonical_records, _canonical_digest = canonical_index.load()
    canonical_ids = [item.record.id for item in canonical_records]
    if len(canonical_ids) != 3 or len(set(canonical_ids)) != 3:
        raise KnowledgeEdtechControlledIndexError("canonical index ids drifted")
    canonical_retriever = KnowledgeRetriever(canonical_index)

    record_path = (workspace_root / str(candidate["record_path"])).resolve()
    if not record_path.is_relative_to(knowledge_root.resolve()) or not record_path.is_file():
        raise KnowledgeEdtechControlledIndexError("EdTech revision record path is invalid")
    edtech_record = KnowledgeRecord.model_validate(_load_json(record_path))
    if edtech_record.id != candidate["record_id"] or edtech_record.applicable_domains != ["education-edtech"]:
        raise KnowledgeEdtechControlledIndexError("EdTech revision metadata drifted")
    edtech_ref = str(record_path.relative_to(knowledge_root.resolve())).replace("\\", "/")
    if edtech_ref in canonical_refs or edtech_record.id in set(canonical_ids) or not revision.revised_record_unindexed:
        raise KnowledgeEdtechControlledIndexError("EdTech v2 is already canonical before A50.9C")

    regression_cases = trial["canonical_regression_cases"]
    if not isinstance(regression_cases, list) or len(regression_cases) != 3:
        raise KnowledgeEdtechControlledIndexError("A50.9C must cover exactly three canonical regression cases")
    negative_domains = trial["negative_isolation_domains"]
    if negative_domains != ["mobility-ev", "ai-software"]:
        raise KnowledgeEdtechControlledIndexError("A50.9C negative isolation domains drifted")

    edtech_retrieval_isolated = False
    canonical_retrieval_regression_clear = True
    negative_domain_isolation_clear = True
    context_budget_clear = False
    rollback_verified = False
    canary_count = 0

    with TemporaryDirectory(prefix="a50-9c-canary-") as temp_dir:
        shadow_root = Path(temp_dir) / "skills_UIUX/knowledge"
        shutil.copytree(knowledge_root, shadow_root)
        canary_refs = [*canonical_refs, edtech_ref]
        (shadow_root / "canary-index.json").write_text(
            json.dumps({"schema_version": "knowledge-index.v1", "records": canary_refs}, indent=2) + "\n",
            encoding="utf-8",
        )
        canary_index = KnowledgeIndex(shadow_root, manifest_name="canary-index.json")
        canary_records, _canary_digest = canary_index.load()
        canary_count = len(canary_records)
        if canary_count != governance["canary_index_expected_count"]:
            raise KnowledgeEdtechControlledIndexError("A50.9C canary index must contain exactly four records")
        if len({item.record.id for item in canary_records}) != canary_count:
            raise KnowledgeEdtechControlledIndexError("A50.9C canary index contains duplicate ids")
        canary_retriever = KnowledgeRetriever(canary_index)

        edtech_result = canary_retriever.retrieve(
            _query(
                as_of=trial["checked_on"],
                domain=candidate["domain"],
                stage=candidate["stage"],
                terms=[str(term) for term in candidate["terms"]],
                max_item_chars=int(candidate["max_item_chars"]),
                max_total_chars=int(candidate["max_total_chars"]),
            )
        )
        edtech_ids = [hit.record.id for hit in edtech_result.hits]
        edtech_hit = next((hit for hit in edtech_result.hits if hit.record.id == edtech_record.id), None)
        edtech_retrieval_isolated = (
            edtech_ids == [edtech_record.id]
            and sum(item.reason == "domain_mismatch" for item in edtech_result.exclusions) == 3
            and edtech_result.vector_search_used is False
        )
        context_chars = edtech_hit.delivered_content_chars if edtech_hit else 0
        context_budget_clear = 250 <= context_chars <= int(candidate["max_item_chars"])

        for raw in regression_cases:
            expected_keys = {"id", "domain", "stage", "terms", "expected_record_id"}
            if not isinstance(raw, dict) or set(raw) != expected_keys:
                raise KnowledgeEdtechControlledIndexError("canonical regression case contract drifted")
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
            if not any(item.record_ref == edtech_ref and item.reason == "domain_mismatch" for item in canary_result.exclusions):
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
        rollback_verified = [item.record.id for item in rollback_records] == canonical_ids

    canonical_bytes_after = canonical_index_path.read_bytes()
    canonical_hash_after = hashlib.sha256(canonical_bytes_after).hexdigest()
    rollback_verified = rollback_verified and canonical_hash_before == canonical_hash_after and canonical_bytes_before == canonical_bytes_after

    checks = (
        usefulness_evidence_clear,
        edtech_retrieval_isolated,
        canonical_retrieval_regression_clear,
        negative_domain_isolation_clear,
        context_budget_clear,
        rollback_verified,
        draft_report.genai_hold_preserved,
        canary_count == governance["canary_index_expected_count"],
    )
    decision = governance["pass_decision"] if all(checks) else governance["fail_decision"]

    return EdtechControlledIndexTrialReport(
        trial_id=str(trial["trial_id"]),
        decision=str(decision),
        prior_revision_verdict=revision.verdict,
        usefulness_evidence_clear=usefulness_evidence_clear,
        revision_record_unindexed=revision.revised_record_unindexed,
        canonical_index_count=len(canonical_refs),
        canary_index_count=canary_count,
        edtech_retrieval_isolated=edtech_retrieval_isolated,
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
