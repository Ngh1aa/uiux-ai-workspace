from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from core.benchmarks.regression_corpus import (
    BenchmarkCase,
    BenchmarkCorpus,
    BenchmarkCorpusError,
    build_benchmark_report,
    compare_benchmark_reports,
    evaluate_case_result,
)


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "benchmarks" / "corpus" / "uiux-product-v1.json"


def _passing_result(case: BenchmarkCase) -> dict[str, object]:
    return {
        "case_id": case.id,
        "routes": list(case.representative_routes),
        "page_roles": list(case.required_page_roles),
        "evidence_types": list(case.required_evidence),
        "screenshot_viewports": list(case.screenshot_pack["required_viewports"]),
        "hard_rule_failures": [],
        "human_review_status": "pending",
        "human_verdict": None,
    }


def test_a12_corpus_has_eight_materially_distinct_domains_and_pending_truthful_review() -> None:
    corpus = BenchmarkCorpus.load(CORPUS_PATH)

    assert len(corpus.cases) == 8
    assert len({case.domain for case in corpus.cases}) == 8
    assert len({case.product_archetype for case in corpus.cases}) == 8
    assert len(corpus.content_hash) == 64
    for case in corpus.cases:
        assert case.human_review["status"] == "pending"
        assert case.human_review.get("verdict") is None
        assert case.screenshot_pack["status"] == "pending"
        assert set(case.screenshot_pack["required_viewports"]) == {"desktop", "tablet", "mobile"}


def test_a12_manifest_is_deterministic_and_case_content_is_hashed() -> None:
    first = BenchmarkCorpus.load(CORPUS_PATH)
    second = BenchmarkCorpus.load(CORPUS_PATH)

    assert first.content_hash == second.content_hash
    assert first.manifest() == second.manifest()
    assert len({case.content_hash for case in first.cases}) == len(first.cases)


def test_a12_objective_evaluation_cannot_manufacture_human_verdict() -> None:
    corpus = BenchmarkCorpus.load(CORPUS_PATH)
    case = corpus.cases[0]
    result = _passing_result(case)

    evaluated = evaluate_case_result(case, result)
    assert evaluated["objective_pass"] is True
    assert evaluated["overall_status"] == "objective_pass_pending_human"
    assert evaluated["human_verdict"] is None

    forged = dict(result)
    forged["human_verdict"] = "KEEP"
    with pytest.raises(BenchmarkCorpusError, match="pending human review cannot include a verdict"):
        evaluate_case_result(case, forged)


def test_a12_missing_hard_evidence_causes_objective_failure() -> None:
    corpus = BenchmarkCorpus.load(CORPUS_PATH)
    case = corpus.cases[0]
    result = _passing_result(case)
    result["evidence_types"] = ["browser_render"]
    result["hard_rule_failures"] = ["missing accessibility evidence"]

    evaluated = evaluate_case_result(case, result)
    assert evaluated["objective_pass"] is False
    assert evaluated["checks"]["evidence"] is False
    assert evaluated["checks"]["hard_rules"] is False
    assert evaluated["overall_status"] == "objective_fail"


def test_a12_complete_report_requires_every_case() -> None:
    corpus = BenchmarkCorpus.load(CORPUS_PATH)
    partial = [_passing_result(case) for case in corpus.cases[:-1]]
    report = build_benchmark_report(corpus, partial, run_label="candidate")

    assert report["complete"] is False
    assert report["objective_pass"] is False
    assert report["missing_cases"] == [corpus.cases[-1].id]

    complete = build_benchmark_report(
        corpus,
        [_passing_result(case) for case in corpus.cases],
        run_label="candidate",
    )
    assert complete["complete"] is True
    assert complete["objective_pass"] is True
    assert complete["objective_pass_count"] == 8


def test_a12_comparator_reports_regression_without_provider_ranking() -> None:
    corpus = BenchmarkCorpus.load(CORPUS_PATH)
    baseline_results = [_passing_result(case) for case in corpus.cases]
    candidate_results = copy.deepcopy(baseline_results)
    candidate_results[2]["hard_rule_failures"] = ["console error"]

    baseline = build_benchmark_report(corpus, baseline_results, run_label="baseline")
    candidate = build_benchmark_report(corpus, candidate_results, run_label="candidate")
    comparison = compare_benchmark_reports(baseline, candidate)

    assert comparison["objective_regressions"] == [corpus.cases[2].id]
    assert comparison["objective_recoveries"] == []
    assert "winner" not in comparison
    assert "score" not in comparison


def test_a12_comparison_rejects_different_corpus_hashes() -> None:
    corpus = BenchmarkCorpus.load(CORPUS_PATH)
    report = build_benchmark_report(corpus, [_passing_result(case) for case in corpus.cases], run_label="baseline")
    other = copy.deepcopy(report)
    other["corpus_hash"] = "0" * 64

    with pytest.raises(BenchmarkCorpusError, match="different corpus hashes"):
        compare_benchmark_reports(report, other)


def test_a12_pending_human_review_in_corpus_cannot_contain_verdict(tmp_path: Path) -> None:
    payload = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    payload["cases"][0]["human_review"]["verdict"] = "KEEP"
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(BenchmarkCorpusError, match="cannot fabricate a verdict"):
        BenchmarkCorpus.load(path)
