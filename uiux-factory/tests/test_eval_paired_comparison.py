"""Exercise unequal/mislabelled trials so a comparison cannot hide regressions."""
from copy import deepcopy
import json
from pathlib import Path
import runpy

import pytest

MODULE = runpy.run_path(str(Path(__file__).resolve().parents[2] / "skills_UIUX/scripts/eval-harness.py"))
compare_trials = MODULE["compare_trials"]


def trial(condition, pair, score=80):
    return {"task_id": "example", "trial_id": condition + pair, "pair_id": pair,
            "condition": condition, "score": score, "passed": score >= 80,
            "environment": {"brief_sha256": "a" * 64, "response_contract_sha256": "b" * 64,
                            "rubric_sha256": "c" * 64, "model": "test-runner",
                            "settings": {"output_limit": 450}, "tools": ["read_files", "write_output"]},
            "graders": {"agent_rubric": {"artifact": "synthetic-test-only"}}}


def test_report_retains_regression_tie_and_per_pair_results():
    before = [trial("baseline", "1", 60), trial("baseline", "2", 90), trial("baseline", "3", 80)]
    after = [trial("candidate", "3", 80), trial("candidate", "1", 80), trial("candidate", "2", 70)]
    report = compare_trials(before, after)
    assert report["overall"] == {"pairs": 3, "mean_score_delta": 0.0, "improved": 1, "tied": 1,
                                 "regressed": 1, "baseline_passes": 2, "candidate_passes": 2}
    assert len(report["pairs"]) == 3
    assert report["human_preference"] == "UNKNOWN"
    assert report["causal_improvement"] == "NOT_ESTABLISHED"


@pytest.mark.parametrize("field", ["brief_sha256", "response_contract_sha256", "rubric_sha256", "model", "settings", "tools"])
def test_changed_environment_cannot_be_averaged_into_a_comparable_pair(field):
    before, after = trial("baseline", "1"), trial("candidate", "1")
    after["environment"][field] = "d" * 64 if field.endswith("sha256") else {"changed": True} if field == "settings" else ["changed"] if field == "tools" else "changed-model"
    with pytest.raises(ValueError, match="unmatched comparison"):
        compare_trials([before], [after])


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "wrong_condition", "no_grader", "invalid_digest"])
def test_missing_invalid_or_duplicate_trials_fail_closed(mutation):
    before, after = [trial("baseline", "1")], [trial("candidate", "1")]
    if mutation == "missing": after = []
    if mutation == "duplicate": after.append(deepcopy(after[0]))
    if mutation == "wrong_condition": after[0]["condition"] = "baseline"
    if mutation == "no_grader": after[0]["graders"] = {}
    if mutation == "invalid_digest": after[0]["environment"]["brief_sha256"] = "unknown"
    with pytest.raises(ValueError): compare_trials(before, after)


def test_non_object_result_is_a_validation_error(tmp_path):
    results = tmp_path / "invalid.jsonl"
    results.write_text(json.dumps(["not", "a", "trial"]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="object"):
        MODULE["load_results"](results, {"example"})


@pytest.mark.parametrize("value", ["not-an-object", [], None])
def test_malformed_comparison_environment_is_a_validation_error(value):
    after = trial("candidate", "1")
    after["environment"] = value
    with pytest.raises(ValueError, match="environment"):
        compare_trials([trial("baseline", "1")], [after])
