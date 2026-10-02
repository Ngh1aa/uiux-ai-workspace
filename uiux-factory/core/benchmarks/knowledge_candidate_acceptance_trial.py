from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.benchmarks.knowledge_ready_candidate_drafts import evaluate_knowledge_ready_candidate_drafts


SCHEMA_VERSION = 1
EXPECTED_SCOPE = "model_assisted_blind_candidate_acceptance_trial_not_product_evidence"
ALLOWED_PREFERENCES = {"A", "B", "TIE", "INSUFFICIENT"}
ALLOWED_VERDICTS = {"ACCEPT_FOR_INDEX_TRIAL", "REVISE_DRAFT", "HOLD", "REJECT"}
DIMENSIONS = (
    "correctness",
    "specificity_actionability",
    "relevance_noise",
    "unsupported_claim_risk",
    "decision_usefulness",
)


class KnowledgeCandidateAcceptanceError(ValueError):
    pass


@dataclass(frozen=True)
class CandidateAcceptanceCaseResult:
    case_id: str
    candidate_id: str
    record_id: str
    human_review_complete: bool
    preferred_output: str | None
    knowledge_condition: str
    baseline_condition: str
    material_regression: bool | None
    verdict: str
    joint_usefulness_win: bool
    correctness_guard_clear: bool
    unsupported_claim_risk_guard_clear: bool
    rationale: str


@dataclass(frozen=True)
class KnowledgeCandidateAcceptanceReport:
    trial_id: str
    version: str
    trial_hash: str
    draft_validation_passed: bool
    human_review_complete: bool
    reviewed_case_count: int
    accepted_for_index_trial_count: int
    revise_draft_count: int
    hold_count: int
    reject_count: int
    index_mutation_allowed: bool
    canonical_acceptance_allowed: bool
    auto_promotion_allowed: bool
    vector_search_change_allowed: bool
    product_evidence: bool
    cases: tuple[CandidateAcceptanceCaseResult, ...]


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeCandidateAcceptanceError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeCandidateAcceptanceError(f"expected object: {path}")
    return payload


def _validate_trial(payload: dict[str, Any]) -> list[dict[str, Any]]:
    expected_top = {"schema_version", "trial_id", "version", "scope", "generation", "rubric", "cases"}
    if set(payload) != expected_top:
        raise KnowledgeCandidateAcceptanceError("acceptance trial top-level keys do not match v1 contract")
    if payload["schema_version"] != SCHEMA_VERSION:
        raise KnowledgeCandidateAcceptanceError("acceptance trial schema_version must be 1")
    if payload["scope"] != EXPECTED_SCOPE:
        raise KnowledgeCandidateAcceptanceError("acceptance trial scope drifted")
    if payload["rubric"] != list(DIMENSIONS):
        raise KnowledgeCandidateAcceptanceError("acceptance trial rubric drifted")
    generation = payload["generation"]
    expected_generation = {
        "surface",
        "model",
        "generated_on",
        "runtime_provider_invoked",
        "source_task",
        "note",
    }
    if not isinstance(generation, dict) or set(generation) != expected_generation:
        raise KnowledgeCandidateAcceptanceError("generation metadata keys do not match v1 contract")
    if generation["runtime_provider_invoked"] is not False:
        raise KnowledgeCandidateAcceptanceError("A50.8 must not claim a runtime provider invocation")
    if not str(generation["model"]).strip() or not str(generation["note"]).strip():
        raise KnowledgeCandidateAcceptanceError("generation model/note are required")
    cases = payload["cases"]
    if not isinstance(cases, list) or len(cases) != 2:
        raise KnowledgeCandidateAcceptanceError("A50.8 must contain exactly two candidate cases")
    seen: set[str] = set()
    expected_case_keys = {
        "id",
        "candidate_id",
        "draft_record_id",
        "domain",
        "flow_id",
        "stage",
        "task",
        "output_a",
        "output_b",
    }
    for case in cases:
        if not isinstance(case, dict) or set(case) != expected_case_keys:
            raise KnowledgeCandidateAcceptanceError("acceptance trial case keys do not match v1 contract")
        case_id = str(case["id"]).strip()
        if not case_id or case_id in seen:
            raise KnowledgeCandidateAcceptanceError("acceptance trial case ids must be unique/non-empty")
        seen.add(case_id)
        for field in ("candidate_id", "draft_record_id", "domain", "flow_id", "stage", "task"):
            if not str(case[field]).strip():
                raise KnowledgeCandidateAcceptanceError(f"{case_id}: {field} is required")
        for field in ("output_a", "output_b"):
            values = case[field]
            if not isinstance(values, list) or len(values) < 3 or any(not isinstance(v, str) or not v.strip() for v in values):
                raise KnowledgeCandidateAcceptanceError(f"{case_id}: {field} must be a non-empty string array")
    return cases


def _validate_mapping(payload: dict[str, Any], case_ids: set[str]) -> dict[str, dict[str, Any]]:
    expected_top = {"schema_version", "trial_id", "mapping_version", "scope", "cases"}
    if set(payload) != expected_top or payload["schema_version"] != SCHEMA_VERSION:
        raise KnowledgeCandidateAcceptanceError("acceptance mapping contract drifted")
    if payload["scope"] != "blind_mapping_not_for_reviewer_until_scoring_complete":
        raise KnowledgeCandidateAcceptanceError("acceptance mapping scope drifted")
    cases = payload["cases"]
    if not isinstance(cases, list) or len(cases) != len(case_ids):
        raise KnowledgeCandidateAcceptanceError("acceptance mapping case count drifted")
    output: dict[str, dict[str, Any]] = {}
    for raw in cases:
        if not isinstance(raw, dict) or set(raw) != {"id", "knowledge_condition", "baseline_condition"}:
            raise KnowledgeCandidateAcceptanceError("acceptance mapping case keys drifted")
        case_id = str(raw["id"])
        knowledge = raw["knowledge_condition"]
        baseline = raw["baseline_condition"]
        if case_id not in case_ids or case_id in output:
            raise KnowledgeCandidateAcceptanceError("acceptance mapping case ids drifted")
        if {knowledge, baseline} != {"A", "B"}:
            raise KnowledgeCandidateAcceptanceError(f"{case_id}: mapping must use A/B exactly once")
        output[case_id] = raw
    if set(output) != case_ids:
        raise KnowledgeCandidateAcceptanceError("acceptance mapping does not cover all trial cases")
    return output


def _validate_reviews(payload: dict[str, Any], case_ids: set[str]) -> tuple[str, dict[str, dict[str, Any]]]:
    expected_top = {"schema_version", "trial_id", "review_version", "review_status", "review_policy", "cases"}
    if set(payload) != expected_top or payload["schema_version"] != SCHEMA_VERSION:
        raise KnowledgeCandidateAcceptanceError("acceptance review ledger contract drifted")
    if payload["review_status"] not in {"PENDING", "COMPLETE"}:
        raise KnowledgeCandidateAcceptanceError("review_status must be PENDING or COMPLETE")
    policy = payload["review_policy"]
    expected_policy = {
        "reviewer_type",
        "blind_first",
        "allowed_preferences",
        "score_scale",
        "score_meaning",
        "dimensions",
    }
    if not isinstance(policy, dict) or set(policy) != expected_policy:
        raise KnowledgeCandidateAcceptanceError("review policy contract drifted")
    if policy["reviewer_type"] != "independent_human" or policy["blind_first"] is not True:
        raise KnowledgeCandidateAcceptanceError("A50.8 requires blind-first independent human review")
    if set(policy["allowed_preferences"]) != ALLOWED_PREFERENCES or policy["dimensions"] != list(DIMENSIONS):
        raise KnowledgeCandidateAcceptanceError("review policy preference/dimension set drifted")
    if policy["score_scale"] != [0, 1, 2]:
        raise KnowledgeCandidateAcceptanceError("review score scale drifted")

    cases = payload["cases"]
    if not isinstance(cases, list) or len(cases) != len(case_ids):
        raise KnowledgeCandidateAcceptanceError("review case count drifted")
    output: dict[str, dict[str, Any]] = {}
    for raw in cases:
        expected_case = {
            "id",
            "status",
            "preferred_output",
            "scores",
            "rationale",
            "material_regression",
            "reviewer",
            "reviewed_at",
        }
        if not isinstance(raw, dict) or set(raw) != expected_case:
            raise KnowledgeCandidateAcceptanceError("review case keys drifted")
        case_id = str(raw["id"])
        if case_id not in case_ids or case_id in output:
            raise KnowledgeCandidateAcceptanceError("review case ids drifted")
        if raw["status"] == "PENDING":
            for field in ("preferred_output", "scores", "rationale", "material_regression", "reviewer", "reviewed_at"):
                if raw[field] is not None:
                    raise KnowledgeCandidateAcceptanceError(f"{case_id}: pending review cannot fabricate {field}")
        elif raw["status"] == "REVIEWED":
            preferred = raw["preferred_output"]
            if preferred not in ALLOWED_PREFERENCES:
                raise KnowledgeCandidateAcceptanceError(f"{case_id}: invalid preferred_output")
            scores = raw["scores"]
            if not isinstance(scores, dict) or set(scores) != {"A", "B"}:
                raise KnowledgeCandidateAcceptanceError(f"{case_id}: reviewed scores must contain A/B")
            for label in ("A", "B"):
                values = scores[label]
                if not isinstance(values, dict) or set(values) != set(DIMENSIONS):
                    raise KnowledgeCandidateAcceptanceError(f"{case_id}: {label} score dimensions drifted")
                if any(values[d] not in {0, 1, 2} for d in DIMENSIONS):
                    raise KnowledgeCandidateAcceptanceError(f"{case_id}: score outside 0..2")
            if not isinstance(raw["material_regression"], bool):
                raise KnowledgeCandidateAcceptanceError(f"{case_id}: material_regression must be boolean")
            if not str(raw["rationale"] or "").strip() or not str(raw["reviewer"] or "").strip() or not str(raw["reviewed_at"] or "").strip():
                raise KnowledgeCandidateAcceptanceError(f"{case_id}: reviewed rationale/reviewer/date are required")
        else:
            raise KnowledgeCandidateAcceptanceError(f"{case_id}: review status must be PENDING or REVIEWED")
        output[case_id] = raw

    reviewed_count = sum(1 for item in output.values() if item["status"] == "REVIEWED")
    if payload["review_status"] == "PENDING" and reviewed_count == len(case_ids):
        raise KnowledgeCandidateAcceptanceError("review_status PENDING conflicts with all cases reviewed")
    if payload["review_status"] == "COMPLETE" and reviewed_count != len(case_ids):
        raise KnowledgeCandidateAcceptanceError("review_status COMPLETE requires every case reviewed")
    return str(payload["review_status"]), output


def _verdict_for_review(*, review: dict[str, Any], knowledge_label: str, baseline_label: str) -> tuple[str, bool, bool, bool, str]:
    if review["status"] != "REVIEWED":
        return "HOLD", False, False, False, "human review pending"
    preferred = review["preferred_output"]
    if review["material_regression"] is True:
        return "REJECT", False, False, False, "material regression reported by human reviewer"
    if preferred in {"TIE", "INSUFFICIENT"}:
        return "HOLD", False, False, False, "human review did not establish a useful advantage"
    if preferred == baseline_label:
        return "REVISE_DRAFT", False, False, False, "baseline preferred over knowledge-assisted condition"
    if preferred != knowledge_label:
        raise KnowledgeCandidateAcceptanceError("review preference does not match A/B mapping")

    scores = review["scores"]
    knowledge = scores[knowledge_label]
    baseline = scores[baseline_label]
    correctness_clear = knowledge["correctness"] >= baseline["correctness"]
    risk_clear = knowledge["unsupported_claim_risk"] >= baseline["unsupported_claim_risk"]
    joint_usefulness = (
        knowledge["specificity_actionability"] > baseline["specificity_actionability"]
        and knowledge["decision_usefulness"] > baseline["decision_usefulness"]
    )
    if correctness_clear and risk_clear and joint_usefulness:
        return "ACCEPT_FOR_INDEX_TRIAL", True, True, True, "knowledge-assisted condition won with joint usefulness and safety/correctness guards clear"
    return "REVISE_DRAFT", joint_usefulness, correctness_clear, risk_clear, "knowledge-assisted condition preferred but acceptance guards were not all satisfied"


def evaluate_knowledge_candidate_acceptance_trial(
    *,
    trial_path: Path,
    mapping_path: Path,
    reviews_path: Path,
    draft_corpus_path: Path,
    proposal_path: Path,
    workspace_root: Path,
    knowledge_root: Path,
    benchmarks_root: Path,
) -> KnowledgeCandidateAcceptanceReport:
    trial_bytes = trial_path.read_bytes()
    trial = json.loads(trial_bytes.decode("utf-8"))
    if not isinstance(trial, dict):
        raise KnowledgeCandidateAcceptanceError("acceptance trial must be an object")
    cases = _validate_trial(trial)
    case_ids = {str(case["id"]) for case in cases}

    mapping_payload = _load_json(mapping_path)
    reviews_payload = _load_json(reviews_path)
    if mapping_payload.get("trial_id") != trial.get("trial_id") or reviews_payload.get("trial_id") != trial.get("trial_id"):
        raise KnowledgeCandidateAcceptanceError("trial/mapping/review ids must match")
    mapping = _validate_mapping(mapping_payload, case_ids)
    review_status, reviews = _validate_reviews(reviews_payload, case_ids)

    draft_report = evaluate_knowledge_ready_candidate_drafts(
        draft_corpus_path,
        proposal_path=proposal_path,
        workspace_root=workspace_root,
        knowledge_root=knowledge_root,
        benchmarks_root=benchmarks_root,
    )
    if draft_report.passed != draft_report.total or draft_report.keep_draft_count != 2 or draft_report.revise_draft_count != 0:
        raise KnowledgeCandidateAcceptanceError("A50.8 requires the verified A50.7 KEEP_DRAFT 2/2 baseline")
    if draft_report.canonical_index_count != 3 or draft_report.canonical_acceptance_allowed is not False:
        raise KnowledgeCandidateAcceptanceError("A50.8 must preserve the three-record canonical index boundary")

    draft_by_candidate = {case.candidate_id: case for case in draft_report.cases}
    results: list[CandidateAcceptanceCaseResult] = []
    for case in cases:
        case_id = str(case["id"])
        candidate_id = str(case["candidate_id"])
        draft = draft_by_candidate.get(candidate_id)
        if draft is None or draft.record_id != case["draft_record_id"]:
            raise KnowledgeCandidateAcceptanceError(f"{case_id}: trial candidate does not match A50.7 draft")
        mapped = mapping[case_id]
        knowledge_label = str(mapped["knowledge_condition"])
        baseline_label = str(mapped["baseline_condition"])
        review = reviews[case_id]
        verdict, joint, correctness_clear, risk_clear, rationale = _verdict_for_review(
            review=review,
            knowledge_label=knowledge_label,
            baseline_label=baseline_label,
        )
        if verdict not in ALLOWED_VERDICTS:
            raise KnowledgeCandidateAcceptanceError(f"{case_id}: invalid derived verdict")
        results.append(
            CandidateAcceptanceCaseResult(
                case_id=case_id,
                candidate_id=candidate_id,
                record_id=str(case["draft_record_id"]),
                human_review_complete=review["status"] == "REVIEWED",
                preferred_output=review["preferred_output"],
                knowledge_condition=knowledge_label,
                baseline_condition=baseline_label,
                material_regression=review["material_regression"],
                verdict=verdict,
                joint_usefulness_win=joint,
                correctness_guard_clear=correctness_clear,
                unsupported_claim_risk_guard_clear=risk_clear,
                rationale=rationale,
            )
        )

    reviewed_count = sum(item.human_review_complete for item in results)
    human_complete = review_status == "COMPLETE" and reviewed_count == len(results)
    return KnowledgeCandidateAcceptanceReport(
        trial_id=str(trial["trial_id"]),
        version=str(trial["version"]),
        trial_hash=hashlib.sha256(trial_bytes).hexdigest()[:16],
        draft_validation_passed=True,
        human_review_complete=human_complete,
        reviewed_case_count=reviewed_count,
        accepted_for_index_trial_count=sum(item.verdict == "ACCEPT_FOR_INDEX_TRIAL" for item in results),
        revise_draft_count=sum(item.verdict == "REVISE_DRAFT" for item in results),
        hold_count=sum(item.verdict == "HOLD" for item in results),
        reject_count=sum(item.verdict == "REJECT" for item in results),
        index_mutation_allowed=False,
        canonical_acceptance_allowed=False,
        auto_promotion_allowed=False,
        vector_search_change_allowed=False,
        product_evidence=False,
        cases=tuple(results),
    )
