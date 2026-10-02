from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


EXPECTED_SCOPE = "model_assisted_blind_pair_trial_not_human_or_product_evidence"
EXPECTED_CASES = {
    "nova-amount-display": "knowledge.domain.financial-currency-locale-formatting.v1",
    "lumen-object-metadata": "knowledge.domain.cultural-object-metadata-rights-iiif.v1",
    "cennext-motor-claims": "knowledge.domain.industrial-motor-system-claims-doe.v1",
}
DIMENSIONS = (
    "correctness",
    "specificity_actionability",
    "relevance_noise",
    "unsupported_claim_risk",
    "decision_usefulness",
)
CONDITIONS = {"with_retrieved_knowledge", "without_retrieved_knowledge"}
PREFERENCES = {"A", "B", "TIE", "INSUFFICIENT"}


@dataclass(frozen=True)
class TrialGovernanceResult:
    trial_id: str
    case_count: int
    human_review_complete: bool
    reviewed_case_count: int
    knowledge_preferred_count: int
    baseline_preferred_count: int
    tie_count: int
    insufficient_count: int
    material_regression_count: int
    expansion_recommendation: Literal[
        "HOLD_PENDING_HUMAN",
        "REVISE_BEFORE_EXPANSION",
        "CONSIDER_EXPANSION",
    ]
    expand_allowed: Literal[False] = False
    auto_mutation_allowed: Literal[False] = False
    current_run_evidence: Literal[False] = False
    product_evidence: Literal[False] = False


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalized_output(lines: list[str]) -> tuple[str, ...]:
    return tuple(" ".join(str(line).split()) for line in lines)


def _validate_trial_packet(trial: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if trial.get("trial_id") != "knowledge-value-trial-v1":
        raise ValueError("unexpected knowledge value trial id")
    if trial.get("scope") != EXPECTED_SCOPE:
        raise ValueError("knowledge value trial scope must remain advisory-only")

    generation = trial.get("generation") or {}
    if generation.get("runtime_provider_invoked") is not False:
        raise ValueError("A50.5 captured samples must not claim a runtime provider invocation")
    if not str(generation.get("surface", "")).strip():
        raise ValueError("generation surface provenance is required")
    if not str(generation.get("model", "")).strip():
        raise ValueError("generation model provenance is required")
    if not str(generation.get("generated_on", "")).strip():
        raise ValueError("generation date is required")

    rubric = tuple(trial.get("rubric") or ())
    if rubric != DIMENSIONS:
        raise ValueError("trial rubric drifted from the canonical five dimensions")

    cases = trial.get("cases") or []
    by_id = {case.get("id"): case for case in cases}
    if set(by_id) != set(EXPECTED_CASES):
        raise ValueError("trial must contain exactly the three A50.5 project cases")

    for case_id, case in by_id.items():
        if not str(case.get("repository", "")).startswith("https://github.com/Ngh1aa/"):
            raise ValueError(f"{case_id}: repository provenance is required")
        if not str(case.get("task", "")).strip():
            raise ValueError(f"{case_id}: task is required")
        for label in ("output_a", "output_b"):
            lines = case.get(label)
            if not isinstance(lines, list) or len(lines) < 3:
                raise ValueError(f"{case_id}: {label} must contain at least three reviewable statements")
            if any(not str(line).strip() for line in lines):
                raise ValueError(f"{case_id}: {label} contains an empty statement")
        if _normalized_output(case["output_a"]) == _normalized_output(case["output_b"]):
            raise ValueError(f"{case_id}: paired outputs must differ")

    return by_id


def _validate_mapping(mapping: dict[str, Any], trial_cases: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if mapping.get("trial_id") != "knowledge-value-trial-v1":
        raise ValueError("trial mapping id mismatch")
    blind = mapping.get("blinding") or {}
    if blind.get("mode") != "procedural_repository_blind":
        raise ValueError("A50.5 must declare its procedural repository blinding mode")
    if blind.get("cryptographically_blind") is not False:
        raise ValueError("repository trial must not overclaim cryptographic blinding")

    mappings = mapping.get("cases") or []
    by_id = {case.get("id"): case for case in mappings}
    if set(by_id) != set(trial_cases):
        raise ValueError("mapping must cover exactly the trial cases")

    knowledge_labels: list[str] = []
    for case_id, case in by_id.items():
        conditions = {case.get("output_a_condition"), case.get("output_b_condition")}
        if conditions != CONDITIONS:
            raise ValueError(f"{case_id}: A/B mapping must contain each condition exactly once")
        if case.get("knowledge_record_id") != EXPECTED_CASES[case_id]:
            raise ValueError(f"{case_id}: knowledge record mapping drifted")
        knowledge_labels.append("A" if case["output_a_condition"] == "with_retrieved_knowledge" else "B")

    if len(set(knowledge_labels)) < 2:
        raise ValueError("knowledge condition must not use the same A/B label for every case")

    governance = mapping.get("governance") or {}
    if governance.get("expand_allowed") is not False:
        raise ValueError("A50.5 mapping may not directly allow corpus expansion")
    if governance.get("current_expansion_state") != "HOLD":
        raise ValueError("checked-in A50.5 mapping must remain HOLD until independent human review")
    return by_id


def _validate_scores(case_id: str, scores: Any) -> dict[str, dict[str, int]]:
    if not isinstance(scores, dict) or set(scores) != {"A", "B"}:
        raise ValueError(f"{case_id}: reviewed case requires A and B score maps")
    normalized: dict[str, dict[str, int]] = {}
    for label in ("A", "B"):
        channel = scores[label]
        if not isinstance(channel, dict) or set(channel) != set(DIMENSIONS):
            raise ValueError(f"{case_id}: {label} scores must cover the canonical dimensions")
        normalized[label] = {}
        for dimension in DIMENSIONS:
            value = channel[dimension]
            if not isinstance(value, int) or isinstance(value, bool) or value not in {0, 1, 2}:
                raise ValueError(f"{case_id}: {label}.{dimension} must be 0, 1 or 2")
            normalized[label][dimension] = value
    return normalized


def _validate_reviews(
    reviews: dict[str, Any],
    trial_cases: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    if reviews.get("trial_id") != "knowledge-value-trial-v1":
        raise ValueError("human review ledger trial id mismatch")
    policy = reviews.get("review_policy") or {}
    if policy.get("reviewer_type") != "independent_human" or policy.get("blind_first") is not True:
        raise ValueError("A50.5 requires an independent human blind-first review policy")
    if tuple(policy.get("dimensions") or ()) != DIMENSIONS:
        raise ValueError("human review dimensions drifted from the trial rubric")

    review_cases = reviews.get("cases") or []
    by_id = {case.get("id"): case for case in review_cases}
    if set(by_id) != set(trial_cases):
        raise ValueError("human review ledger must cover exactly the trial cases")

    complete_count = 0
    for case_id, case in by_id.items():
        status = case.get("status")
        if status == "PENDING":
            for field in ("preferred_output", "scores", "rationale", "material_regression", "reviewer", "reviewed_at"):
                if case.get(field) is not None:
                    raise ValueError(f"{case_id}: pending review must not contain a fabricated {field}")
            continue
        if status != "REVIEWED":
            raise ValueError(f"{case_id}: unsupported review status")
        preference = case.get("preferred_output")
        if preference not in PREFERENCES:
            raise ValueError(f"{case_id}: invalid reviewer preference")
        _validate_scores(case_id, case.get("scores"))
        if not str(case.get("rationale", "")).strip():
            raise ValueError(f"{case_id}: reviewed case requires rationale")
        if not isinstance(case.get("material_regression"), bool):
            raise ValueError(f"{case_id}: reviewed case requires material_regression boolean")
        if not str(case.get("reviewer", "")).strip() or not str(case.get("reviewed_at", "")).strip():
            raise ValueError(f"{case_id}: reviewed case requires reviewer provenance and timestamp")
        complete_count += 1

    expected_status = "COMPLETE" if complete_count == len(by_id) else "PENDING"
    if reviews.get("review_status") != expected_status:
        raise ValueError("review_status must reflect whether all case reviews are complete")
    return by_id


def evaluate_knowledge_value_trial(
    *,
    trial_path: Path,
    mapping_path: Path,
    reviews_path: Path,
) -> TrialGovernanceResult:
    trial = _load(trial_path)
    mapping = _load(mapping_path)
    reviews = _load(reviews_path)

    trial_cases = _validate_trial_packet(trial)
    mapping_cases = _validate_mapping(mapping, trial_cases)
    review_cases = _validate_reviews(reviews, trial_cases)

    knowledge_preferred = 0
    baseline_preferred = 0
    ties = 0
    insufficient = 0
    regressions = 0
    reviewed = 0
    usefulness_wins = 0

    for case_id, review in review_cases.items():
        if review.get("status") != "REVIEWED":
            continue
        reviewed += 1
        if review["material_regression"]:
            regressions += 1

        preference = review["preferred_output"]
        mapping_case = mapping_cases[case_id]
        knowledge_label = "A" if mapping_case["output_a_condition"] == "with_retrieved_knowledge" else "B"
        baseline_label = "B" if knowledge_label == "A" else "A"
        if preference == knowledge_label:
            knowledge_preferred += 1
        elif preference == baseline_label:
            baseline_preferred += 1
        elif preference == "TIE":
            ties += 1
        else:
            insufficient += 1

        scores = _validate_scores(case_id, review["scores"])
        k = scores[knowledge_label]
        b = scores[baseline_label]
        if (
            k["specificity_actionability"] > b["specificity_actionability"]
            and k["decision_usefulness"] > b["decision_usefulness"]
        ):
            usefulness_wins += 1

    complete = reviewed == len(trial_cases)
    if not complete:
        recommendation: Literal[
            "HOLD_PENDING_HUMAN", "REVISE_BEFORE_EXPANSION", "CONSIDER_EXPANSION"
        ] = "HOLD_PENDING_HUMAN"
    elif (
        regressions == 0
        and baseline_preferred == 0
        and knowledge_preferred >= 2
        and usefulness_wins >= 2
    ):
        recommendation = "CONSIDER_EXPANSION"
    else:
        recommendation = "REVISE_BEFORE_EXPANSION"

    return TrialGovernanceResult(
        trial_id=trial["trial_id"],
        case_count=len(trial_cases),
        human_review_complete=complete,
        reviewed_case_count=reviewed,
        knowledge_preferred_count=knowledge_preferred,
        baseline_preferred_count=baseline_preferred,
        tie_count=ties,
        insufficient_count=insufficient,
        material_regression_count=regressions,
        expansion_recommendation=recommendation,
    )
