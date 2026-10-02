from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from core.benchmarks.knowledge_edtech_canonical_promotion_proposal import evaluate_knowledge_edtech_canonical_promotion_proposal
from core.brain_os.knowledge_contracts import KnowledgeRecord
from core.brain_os.knowledge_retrieval import KnowledgeIndex, KnowledgeQuery, KnowledgeRetriever


class KnowledgeEdtechPromotionShadowError(ValueError):
    pass


@dataclass(frozen=True)
class EdtechCanonicalPromotionShadowReport:
    trial_id: str
    decision: str
    proposal_decision: str
    pre_shadow_count: int
    shadow_count: int
    record_contract_clear: bool
    content_exact_copy: bool
    semantic_copy_clear: bool
    retrieval_regression_clear: bool
    edtech_retrieval_isolated: bool
    ai_negative_isolation_clear: bool
    context_budget_clear: bool
    vector_search_disabled: bool
    rollback_verified: bool
    repository_index_unchanged: bool
    repository_canonical_assets_absent: bool
    genai_hold_preserved: bool
    canonical_apply_allowed: bool
    product_evidence: bool


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeEdtechPromotionShadowError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeEdtechPromotionShadowError(f"expected object: {path}")
    return payload


def _query(*, as_of: str, domain: str, stage: str, terms: list[str]) -> KnowledgeQuery:
    return KnowledgeQuery(
        as_of=as_of,
        domains=[domain],
        stages=[stage],
        terms=terms,
        limit=5,
        max_item_chars=5500,
        max_total_chars=7000,
    )


def evaluate_knowledge_edtech_canonical_promotion_shadow(
    *,
    shadow_trial_path: Path,
    proposal_path: Path,
    review_path: Path,
    canonical_state_path: Path,
    expansion_proposal_path: Path,
    owner_delegation_path: Path,
    workspace_root: Path,
    knowledge_root: Path,
) -> EdtechCanonicalPromotionShadowReport:
    trial = _load_json(shadow_trial_path)
    if trial.get("schema_version") != 1 or trial.get("phase") != "A50.12":
        raise KnowledgeEdtechPromotionShadowError("A50.12 shadow contract drifted")
    if trial.get("scope") != "shadow_canonical_apply_no_repository_mutation":
        raise KnowledgeEdtechPromotionShadowError("A50.12 shadow scope drifted")

    governance = trial.get("governance")
    if not isinstance(governance, dict):
        raise KnowledgeEdtechPromotionShadowError("A50.12 governance is required")
    if governance.get("pre_shadow_canonical_count") != 4 or governance.get("shadow_canonical_count") != 5:
        raise KnowledgeEdtechPromotionShadowError("A50.12 must model a 4→5 shadow promotion")
    for field in (
        "repository_index_mutation_allowed",
        "repository_canonical_asset_creation_allowed",
        "vector_search_change_allowed",
        "product_evidence",
    ):
        if governance.get(field) is not False:
            raise KnowledgeEdtechPromotionShadowError(f"A50.12 must keep {field}=false")
    if governance.get("genai_candidate_status") != "HOLD_FRESHNESS_REVIEW":
        raise KnowledgeEdtechPromotionShadowError("A50.12 must preserve GenAI/NIST HOLD")

    proposal = evaluate_knowledge_edtech_canonical_promotion_proposal(
        proposal_path=proposal_path,
        review_path=review_path,
        canonical_state_path=canonical_state_path,
        expansion_proposal_path=expansion_proposal_path,
        owner_delegation_path=owner_delegation_path,
        workspace_root=workspace_root,
        knowledge_root=knowledge_root,
    )
    if proposal.decision != governance.get("required_proposal_decision"):
        raise KnowledgeEdtechPromotionShadowError("A50.12 requires approved A50.11 proposal")

    state = _load_json(canonical_state_path)
    expected_records = state.get("expected_records")
    if not isinstance(expected_records, list) or len(expected_records) != 4:
        raise KnowledgeEdtechPromotionShadowError("A50.12 requires four-record canonical state v2")
    pre_refs = [str(item["ref"]) for item in expected_records]
    pre_ids = [str(item["id"]) for item in expected_records]

    index_path = knowledge_root / "index.json"
    repository_index_before = index_path.read_bytes()
    repository_index_payload = _load_json(index_path)
    if repository_index_payload.get("records") != pre_refs:
        raise KnowledgeEdtechPromotionShadowError("A50.12 repository index is not the exact four-record baseline")

    candidate = trial.get("candidate")
    if not isinstance(candidate, dict):
        raise KnowledgeEdtechPromotionShadowError("A50.12 candidate is required")
    revision_record_path = workspace_root / str(candidate["revision_record_path"])
    revision_content_path = workspace_root / str(candidate["revision_content_path"])
    canonical_record_repo_path = knowledge_root / str(candidate["canonical_record_relpath"])
    canonical_content_repo_path = knowledge_root / str(candidate["canonical_content_relpath"])
    repository_canonical_assets_absent = not canonical_record_repo_path.exists() and not canonical_content_repo_path.exists()
    if not repository_canonical_assets_absent:
        raise KnowledgeEdtechPromotionShadowError("A50.12 repository canonical EdTech assets must remain absent")

    revision_payload = _load_json(revision_record_path)
    revision_record = KnowledgeRecord.model_validate(revision_payload)
    if revision_record.id != candidate.get("record_id") or revision_record.applicable_domains != ["education-edtech"]:
        raise KnowledgeEdtechPromotionShadowError("A50.12 EdTech revision identity drifted")
    if revision_record.id in pre_ids:
        raise KnowledgeEdtechPromotionShadowError("A50.12 EdTech candidate is already indexed")

    record_contract_clear = False
    content_exact_copy = False
    semantic_copy_clear = False
    retrieval_regression_clear = True
    edtech_retrieval_isolated = False
    ai_negative_isolation_clear = False
    context_budget_clear = True
    vector_search_disabled = True
    rollback_verified = False
    shadow_count = 0

    with TemporaryDirectory(prefix="a50-12-edtech-shadow-") as temp_dir:
        shadow_root = Path(temp_dir) / "skills_UIUX/knowledge"
        shutil.copytree(knowledge_root, shadow_root)

        shadow_content = shadow_root / str(candidate["canonical_content_relpath"])
        shadow_record = shadow_root / str(candidate["canonical_record_relpath"])
        shadow_content.parent.mkdir(parents=True, exist_ok=True)
        shadow_record.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(revision_content_path, shadow_content)

        canonical_payload = dict(revision_payload)
        canonical_payload["content_ref"] = str(candidate["canonical_content_ref"])
        shadow_record.write_text(json.dumps(canonical_payload, indent=2) + "\n", encoding="utf-8")
        canonical_record = KnowledgeRecord.model_validate(_load_json(shadow_record))

        record_contract_clear = bool(
            canonical_record.id == revision_record.id
            and canonical_record.content_ref == candidate["canonical_content_ref"]
            and canonical_record.applicable_domains == ["education-edtech"]
            and canonical_record.advisory_only is True
            and canonical_record.current_run_evidence is False
            and canonical_record.authority_effect == "none"
            and canonical_record.gate_effect == "none"
            and canonical_record.evidence_effect == "none"
            and canonical_record.release_effect == "none"
        )
        content_exact_copy = shadow_content.read_bytes() == revision_content_path.read_bytes()
        canonical_semantic = dict(canonical_payload)
        revision_semantic = dict(revision_payload)
        canonical_semantic.pop("content_ref", None)
        revision_semantic.pop("content_ref", None)
        semantic_copy_clear = canonical_semantic == revision_semantic

        shadow_refs = [*pre_refs, str(candidate["canonical_record_relpath"])]
        (shadow_root / "index.json").write_text(
            json.dumps({"schema_version": "knowledge-index.v1", "records": shadow_refs}, indent=2) + "\n",
            encoding="utf-8",
        )
        shadow_index = KnowledgeIndex(shadow_root)
        shadow_records, _shadow_digest = shadow_index.load()
        shadow_count = len(shadow_records)
        if shadow_count != 5 or len({item.record.id for item in shadow_records}) != 5:
            raise KnowledgeEdtechPromotionShadowError("A50.12 shadow index must contain five unique records")
        retriever = KnowledgeRetriever(shadow_index)

        for case in state.get("active_regression_cases", []):
            result = retriever.retrieve(_query(
                as_of=trial["checked_on"],
                domain=str(case["domain"]),
                stage=str(case["stage"]),
                terms=[str(term) for term in case["terms"]],
            ))
            if [hit.record.id for hit in result.hits] != [str(case["expected_record_id"])]:
                retrieval_regression_clear = False
            if sum(item.reason == "domain_mismatch" for item in result.exclusions) != 4:
                retrieval_regression_clear = False
            if result.indexed_record_count != 5:
                retrieval_regression_clear = False
            if result.vector_search_used:
                vector_search_disabled = False
            hit = result.hits[0] if result.hits else None
            if hit is None or not (250 <= hit.delivered_content_chars <= 5500):
                context_budget_clear = False

        edtech_result = retriever.retrieve(_query(
            as_of=trial["checked_on"],
            domain="education-edtech",
            stage="design",
            terms=["lti", "nrps", "ags", "deep linking", "recovery"],
        ))
        edtech_retrieval_isolated = bool(
            [hit.record.id for hit in edtech_result.hits] == [revision_record.id]
            and sum(item.reason == "domain_mismatch" for item in edtech_result.exclusions) == 4
            and edtech_result.indexed_record_count == 5
            and edtech_result.vector_search_used is False
        )
        edtech_hit = edtech_result.hits[0] if edtech_result.hits else None
        if edtech_hit is None or not (250 <= edtech_hit.delivered_content_chars <= 5500):
            context_budget_clear = False
        if edtech_result.vector_search_used:
            vector_search_disabled = False

        ai_result = retriever.retrieve(_query(
            as_of=trial["checked_on"],
            domain="ai-software",
            stage="design",
            terms=["risk", "ai", "integration"],
        ))
        ai_negative_isolation_clear = bool(
            not ai_result.hits
            and sum(item.reason == "domain_mismatch" for item in ai_result.exclusions) == 5
            and ai_result.indexed_record_count == 5
            and ai_result.vector_search_used is False
        )
        if ai_result.vector_search_used:
            vector_search_disabled = False

        # Exact rollback inside the shadow copy: restore four refs, remove only new EdTech assets.
        (shadow_root / "index.json").write_bytes(repository_index_before)
        shadow_record.unlink()
        shadow_content.unlink()
        rolled_records, _rolled_digest = KnowledgeIndex(shadow_root).load()
        rollback_verified = bool(
            [item.record.id for item in rolled_records] == pre_ids
            and (shadow_root / "index.json").read_bytes() == repository_index_before
            and not shadow_record.exists()
            and not shadow_content.exists()
        )

    repository_index_unchanged = index_path.read_bytes() == repository_index_before
    repository_canonical_assets_absent = bool(
        repository_canonical_assets_absent
        and not canonical_record_repo_path.exists()
        and not canonical_content_repo_path.exists()
    )

    expansion = _load_json(expansion_proposal_path)
    genai = next((item for item in expansion.get("candidates", []) if item.get("candidate_id") == "a50-6-genai-nist"), None)
    genai_hold_preserved = bool(isinstance(genai, dict) and genai.get("proposal_status") == governance["genai_candidate_status"])

    checks = (
        record_contract_clear,
        content_exact_copy,
        semantic_copy_clear,
        retrieval_regression_clear,
        edtech_retrieval_isolated,
        ai_negative_isolation_clear,
        context_budget_clear,
        vector_search_disabled,
        rollback_verified,
        repository_index_unchanged,
        repository_canonical_assets_absent,
        genai_hold_preserved,
        shadow_count == governance["shadow_canonical_count"],
    )
    decision = governance["pass_decision"] if all(checks) else governance["fail_decision"]

    return EdtechCanonicalPromotionShadowReport(
        trial_id=str(trial["trial_id"]),
        decision=str(decision),
        proposal_decision=proposal.decision,
        pre_shadow_count=len(pre_refs),
        shadow_count=shadow_count,
        record_contract_clear=record_contract_clear,
        content_exact_copy=content_exact_copy,
        semantic_copy_clear=semantic_copy_clear,
        retrieval_regression_clear=retrieval_regression_clear,
        edtech_retrieval_isolated=edtech_retrieval_isolated,
        ai_negative_isolation_clear=ai_negative_isolation_clear,
        context_budget_clear=context_budget_clear,
        vector_search_disabled=vector_search_disabled,
        rollback_verified=rollback_verified,
        repository_index_unchanged=repository_index_unchanged,
        repository_canonical_assets_absent=repository_canonical_assets_absent,
        genai_hold_preserved=genai_hold_preserved,
        canonical_apply_allowed=decision == governance["pass_decision"],
        product_evidence=False,
    )
