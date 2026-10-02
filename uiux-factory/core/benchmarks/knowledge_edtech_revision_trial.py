from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from urllib.parse import urlparse

from core.benchmarks.knowledge_candidate_acceptance_trial import evaluate_knowledge_candidate_acceptance_trial
from core.brain_os.knowledge_contracts import KnowledgeRecord
from core.brain_os.knowledge_retrieval import KnowledgeIndex, KnowledgeQuery, KnowledgeRetriever


DIMENSIONS = (
    "correctness",
    "specificity_actionability",
    "relevance_noise",
    "unsupported_claim_risk",
    "decision_usefulness",
)
ALLOWED_PREFERENCES = {"A", "B", "TIE", "INSUFFICIENT"}
ALLOWED_VERDICTS = {"ACCEPT_FOR_INDEX_TRIAL", "REVISE_DRAFT", "HOLD", "REJECT"}


class KnowledgeEdtechRevisionError(ValueError):
    pass


@dataclass(frozen=True)
class EdtechRevisionTrialReport:
    trial_id: str
    prior_verdict: str
    revised_record_id: str
    revised_record_unindexed: bool
    shadow_retrieval_isolated: bool
    required_state_guidance_present: bool
    human_review_complete: bool
    preferred_output: str | None
    knowledge_condition: str
    baseline_condition: str
    material_regression: bool | None
    verdict: str
    joint_usefulness_win: bool
    correctness_guard_clear: bool
    unsupported_claim_risk_guard_clear: bool
    canonical_index_count: int
    index_mutation_allowed: bool
    canonical_acceptance_allowed: bool
    auto_promotion_allowed: bool
    vector_search_change_allowed: bool
    product_evidence: bool


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeEdtechRevisionError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeEdtechRevisionError(f"expected object: {path}")
    return payload


def _score_block(value: Any, *, label: str) -> dict[str, int]:
    if not isinstance(value, dict) or set(value) != set(DIMENSIONS):
        raise KnowledgeEdtechRevisionError(f"{label} scores must match rubric")
    if any(value[key] not in {0, 1, 2} for key in DIMENSIONS):
        raise KnowledgeEdtechRevisionError(f"{label} score outside 0..2")
    return {key: int(value[key]) for key in DIMENSIONS}


def _derive_verdict(
    *,
    review: dict[str, Any],
    knowledge_label: str,
    baseline_label: str,
) -> tuple[str, bool, bool, bool]:
    if review["status"] != "REVIEWED":
        return "HOLD", False, False, False
    if review["material_regression"] is True:
        return "REJECT", False, False, False
    preferred = review["preferred_output"]
    if preferred in {"TIE", "INSUFFICIENT"}:
        return "HOLD", False, False, False
    if preferred == baseline_label:
        return "REVISE_DRAFT", False, False, False
    if preferred != knowledge_label:
        raise KnowledgeEdtechRevisionError("review preference does not match A/B mapping")

    scores = review["scores"]
    knowledge = _score_block(scores[knowledge_label], label="knowledge")
    baseline = _score_block(scores[baseline_label], label="baseline")
    correctness_clear = knowledge["correctness"] >= baseline["correctness"]
    risk_clear = knowledge["unsupported_claim_risk"] >= baseline["unsupported_claim_risk"]
    joint_usefulness = (
        knowledge["specificity_actionability"] > baseline["specificity_actionability"]
        and knowledge["decision_usefulness"] > baseline["decision_usefulness"]
    )
    if correctness_clear and risk_clear and joint_usefulness:
        return "ACCEPT_FOR_INDEX_TRIAL", True, True, True
    return "REVISE_DRAFT", joint_usefulness, correctness_clear, risk_clear


def evaluate_knowledge_edtech_revision_trial(
    *,
    trial_path: Path,
    mapping_path: Path,
    reviews_path: Path,
    prior_trial_path: Path,
    prior_mapping_path: Path,
    prior_reviews_path: Path,
    draft_corpus_path: Path,
    proposal_path: Path,
    workspace_root: Path,
    knowledge_root: Path,
    benchmarks_root: Path,
) -> EdtechRevisionTrialReport:
    prior = evaluate_knowledge_candidate_acceptance_trial(
        trial_path=prior_trial_path,
        mapping_path=prior_mapping_path,
        reviews_path=prior_reviews_path,
        draft_corpus_path=draft_corpus_path,
        proposal_path=proposal_path,
        workspace_root=workspace_root,
        knowledge_root=knowledge_root,
        benchmarks_root=benchmarks_root,
    )
    prior_by_id = {case.case_id: case for case in prior.cases}
    prior_edtech = prior_by_id.get("edtech-lti-integration-boundaries")
    if prior_edtech is None or prior_edtech.verdict != "REVISE_DRAFT":
        raise KnowledgeEdtechRevisionError("A50.9A requires the merged A50.8 EdTech REVISE_DRAFT verdict")

    trial = _load_json(trial_path)
    expected_trial_keys = {"schema_version", "trial_id", "version", "scope", "generation", "rubric", "case"}
    if set(trial) != expected_trial_keys or trial.get("schema_version") != 1:
        raise KnowledgeEdtechRevisionError("A50.9A trial contract drifted")
    if trial["scope"] != "single_candidate_blind_revision_trial_not_product_evidence":
        raise KnowledgeEdtechRevisionError("A50.9A trial scope drifted")
    if trial["rubric"] != list(DIMENSIONS):
        raise KnowledgeEdtechRevisionError("A50.9A rubric drifted")
    generation = trial["generation"]
    if not isinstance(generation, dict) or generation.get("runtime_provider_invoked") is not False:
        raise KnowledgeEdtechRevisionError("A50.9A must not claim runtime provider execution")

    case = trial["case"]
    expected_case_keys = {
        "id", "candidate_id", "prior_record_id", "revised_record_id", "domain", "flow_id", "stage", "task", "output_a", "output_b"
    }
    if not isinstance(case, dict) or set(case) != expected_case_keys:
        raise KnowledgeEdtechRevisionError("A50.9A case contract drifted")
    if case["id"] != "edtech-lti-integration-boundaries-revision-v2":
        raise KnowledgeEdtechRevisionError("unexpected A50.9A case id")

    prior_trial = _load_json(prior_trial_path)
    prior_case = next((item for item in prior_trial.get("cases", []) if item.get("id") == "edtech-lti-integration-boundaries"), None)
    if prior_case is None or case["output_a"] != prior_case["output_b"]:
        raise KnowledgeEdtechRevisionError("A50.9A baseline must remain the exact A50.8 baseline output")

    mapping = _load_json(mapping_path)
    if mapping.get("trial_id") != trial["trial_id"] or mapping.get("scope") != "blind_mapping_not_for_reviewer_until_scoring_complete":
        raise KnowledgeEdtechRevisionError("A50.9A mapping contract drifted")
    knowledge_label = mapping.get("knowledge_condition")
    baseline_label = mapping.get("baseline_condition")
    if {knowledge_label, baseline_label} != {"A", "B"}:
        raise KnowledgeEdtechRevisionError("A50.9A mapping must use A/B exactly once")

    review_payload = _load_json(reviews_path)
    if review_payload.get("trial_id") != trial["trial_id"] or review_payload.get("review_status") not in {"PENDING", "COMPLETE"}:
        raise KnowledgeEdtechRevisionError("A50.9A review ledger contract drifted")
    policy = review_payload.get("review_policy")
    if not isinstance(policy, dict) or policy.get("reviewer_type") != "independent_human" or policy.get("blind_first") is not True:
        raise KnowledgeEdtechRevisionError("A50.9A requires blind-first independent human review")
    if policy.get("dimensions") != list(DIMENSIONS) or set(policy.get("allowed_preferences", [])) != ALLOWED_PREFERENCES:
        raise KnowledgeEdtechRevisionError("A50.9A review policy drifted")
    review = review_payload.get("case")
    if not isinstance(review, dict) or review.get("id") != case["id"]:
        raise KnowledgeEdtechRevisionError("A50.9A review case drifted")
    if review.get("status") == "PENDING":
        for field in ("preferred_output", "scores", "rationale", "material_regression", "reviewer", "reviewed_at"):
            if review.get(field) is not None:
                raise KnowledgeEdtechRevisionError(f"pending review cannot fabricate {field}")
        if review_payload["review_status"] != "PENDING":
            raise KnowledgeEdtechRevisionError("pending case requires PENDING review_status")
    elif review.get("status") == "REVIEWED":
        if review_payload["review_status"] != "COMPLETE":
            raise KnowledgeEdtechRevisionError("reviewed case requires COMPLETE review_status")
        if review.get("preferred_output") not in ALLOWED_PREFERENCES:
            raise KnowledgeEdtechRevisionError("invalid A50.9A preference")
        scores = review.get("scores")
        if not isinstance(scores, dict) or set(scores) != {"A", "B"}:
            raise KnowledgeEdtechRevisionError("reviewed A50.9A scores must contain A/B")
        _score_block(scores["A"], label="A")
        _score_block(scores["B"], label="B")
        if not isinstance(review.get("material_regression"), bool):
            raise KnowledgeEdtechRevisionError("material_regression must be boolean")
        if not str(review.get("rationale") or "").strip() or not str(review.get("reviewer") or "").strip() or not str(review.get("reviewed_at") or "").strip():
            raise KnowledgeEdtechRevisionError("reviewed A50.9A rationale/reviewer/date are required")
    else:
        raise KnowledgeEdtechRevisionError("A50.9A case status must be PENDING or REVIEWED")

    index_payload = _load_json(knowledge_root / "index.json")
    canonical_refs = index_payload.get("records")
    if index_payload.get("schema_version") != "knowledge-index.v1" or not isinstance(canonical_refs, list) or len(canonical_refs) != 3:
        raise KnowledgeEdtechRevisionError("canonical Knowledge OS index must remain exactly three records")
    if any(str(ref).startswith("drafts/") for ref in canonical_refs):
        raise KnowledgeEdtechRevisionError("canonical index must not reference drafts")

    record_path = knowledge_root / "drafts/records/edtech-lti-context-roles-services-v2.json"
    content_path = knowledge_root / "drafts/content/edtech-lti-context-roles-services-v2.md"
    record = KnowledgeRecord.model_validate(_load_json(record_path))
    if record.id != case["revised_record_id"] or record.id != "knowledge.domain.edtech-lti-context-roles-services.v2":
        raise KnowledgeEdtechRevisionError("revised EdTech record id drifted")
    if record.content_ref != "skills_UIUX/knowledge/drafts/content/edtech-lti-context-roles-services-v2.md":
        raise KnowledgeEdtechRevisionError("revised EdTech content_ref drifted")
    if record.applicable_domains != ["education-edtech"] or "design" not in record.applicable_stages:
        raise KnowledgeEdtechRevisionError("revised EdTech domain/stage drifted")
    parsed = urlparse(record.source_ref)
    if parsed.scheme != "https" or parsed.hostname != "www.1edtech.org" or record.freshness.value != "versioned":
        raise KnowledgeEdtechRevisionError("revised EdTech provenance/freshness drifted")
    revised_record_unindexed = record.id not in {
        KnowledgeRecord.model_validate(_load_json(knowledge_root / ref)).id for ref in canonical_refs
    }
    if not revised_record_unindexed:
        raise KnowledgeEdtechRevisionError("A50.9A revised draft leaked into canonical index")

    content = content_path.read_text(encoding="utf-8")
    required_concepts = (
        "launch_unavailable",
        "roster_permission_or_role_limited",
        "content_selection_failed",
        "grade_send_failed",
        "configured admin/support path",
        "retry/resubmit only when",
        "unknown/unconfirmed state",
    )
    content_lower = content.lower()
    required_state_guidance_present = all(value.lower() in content_lower for value in required_concepts)
    if not required_state_guidance_present:
        raise KnowledgeEdtechRevisionError("A50.9A revised draft is missing required concrete state/recovery guidance")

    with TemporaryDirectory(prefix="a50-9a-shadow-") as temp_dir:
        shadow_root = Path(temp_dir) / "skills_UIUX/knowledge"
        shutil.copytree(knowledge_root, shadow_root)
        shadow_refs = [*canonical_refs, "drafts/records/edtech-lti-context-roles-services-v2.json"]
        (shadow_root / "shadow-index.json").write_text(
            json.dumps({"schema_version": "knowledge-index.v1", "records": shadow_refs}, indent=2) + "\n",
            encoding="utf-8",
        )
        retriever = KnowledgeRetriever(KnowledgeIndex(shadow_root, manifest_name="shadow-index.json"))
        retrieval = retriever.retrieve(
            KnowledgeQuery(
                as_of="2026-10-02",
                domains=["education-edtech"],
                stages=["design"],
                terms=["lti", "nrps", "ags", "deep linking", "recovery"],
                limit=5,
                max_item_chars=5_500,
                max_total_chars=7_000,
            )
        )
        ids = [hit.record.id for hit in retrieval.hits]
        shadow_retrieval_isolated = ids == [record.id] and sum(item.reason == "domain_mismatch" for item in retrieval.exclusions) == 3 and retrieval.vector_search_used is False
        if not shadow_retrieval_isolated:
            raise KnowledgeEdtechRevisionError("A50.9A revised draft failed shadow retrieval isolation")

    verdict, joint, correctness_clear, risk_clear = _derive_verdict(
        review=review,
        knowledge_label=str(knowledge_label),
        baseline_label=str(baseline_label),
    )
    if verdict not in ALLOWED_VERDICTS:
        raise KnowledgeEdtechRevisionError("invalid A50.9A derived verdict")

    return EdtechRevisionTrialReport(
        trial_id=str(trial["trial_id"]),
        prior_verdict=prior_edtech.verdict,
        revised_record_id=record.id,
        revised_record_unindexed=revised_record_unindexed,
        shadow_retrieval_isolated=shadow_retrieval_isolated,
        required_state_guidance_present=required_state_guidance_present,
        human_review_complete=review["status"] == "REVIEWED",
        preferred_output=review.get("preferred_output"),
        knowledge_condition=str(knowledge_label),
        baseline_condition=str(baseline_label),
        material_regression=review.get("material_regression"),
        verdict=verdict,
        joint_usefulness_win=joint,
        correctness_guard_clear=correctness_clear,
        unsupported_claim_risk_guard_clear=risk_clear,
        canonical_index_count=len(canonical_refs),
        index_mutation_allowed=False,
        canonical_acceptance_allowed=False,
        auto_promotion_allowed=False,
        vector_search_change_allowed=False,
        product_evidence=False,
    )
