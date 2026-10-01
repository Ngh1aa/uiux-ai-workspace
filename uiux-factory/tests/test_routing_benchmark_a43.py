from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from core.benchmarks.routing_regression import (
    ALLOWED_SURFACES,
    RoutingBenchmarkCorpus,
    RoutingBenchmarkError,
    build_routing_report,
)
from core.runtime.flow_os.flow import FlowPlanner


FACTORY = Path(__file__).resolve().parents[1]
WORKSPACE = FACTORY.parent
SKILLS = WORKSPACE / "skills_UIUX"
BENCHMARK = FACTORY / "benchmarks" / "routing-v1.json"


def _policy() -> dict[str, object]:
    return json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


def _flow_hashes() -> dict[str, str]:
    output: dict[str, str] = {}
    for path in sorted((SKILLS / "flows").glob("*.json")):
        output[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return output


def test_a43_routing_corpus_is_strict_diverse_and_complete() -> None:
    corpus = RoutingBenchmarkCorpus.load(BENCHMARK)

    assert corpus.benchmark_id == "brain-routing-v1"
    assert len(corpus.cases) >= 30
    assert {case.expected_surface for case in corpus.cases} == ALLOWED_SURFACES
    assert len({case.id for case in corpus.cases}) == len(corpus.cases)
    assert any("portfolio" in case.tags for case in corpus.cases)
    assert any("fintech" in case.tags for case in corpus.cases)
    assert any("lumen" in case.tags for case in corpus.cases)
    assert any("cennext" in case.tags for case in corpus.cases)


def test_a43_full_routing_benchmark_passes_without_mutating_flow_policy() -> None:
    corpus = RoutingBenchmarkCorpus.load(BENCHMARK)
    policy = _policy()
    planner = FlowPlanner(SKILLS, policy)
    before = _flow_hashes()

    report = build_routing_report(
        corpus,
        planner=planner,
        policy_doc=policy,
        run_label="pytest",
    )

    after = _flow_hashes()
    assert before == after
    assert report["routing_mutation"] is False
    assert report["authority_effect"] == "none"
    assert report["case_count"] == len(corpus.cases)
    assert report["pass_count"] == len(corpus.cases), [
        (row["case_id"], row["checks"], row["expected"], row["actual"])
        for row in report["cases"]
        if not row["passed"]
    ]
    assert report["failure_ids"] == []
    assert report["passed"] is True


def test_a43_routing_benchmark_checks_all_three_layers() -> None:
    corpus = RoutingBenchmarkCorpus.load(BENCHMARK)
    cases = {case.id: case for case in corpus.cases}

    assert cases["micro-portfolio-card"].expected_flow == "micro-ui-change"
    assert cases["focused-portfolio-hero"].expected_flow == "existing-ui-improvement"
    assert cases["redesign-portfolio"].expected_flow == "portfolio-career-system"
    assert cases["product-portfolio"].expected_flow == "portfolio-career-system"

    fintech = cases["page-fintech-landing"]
    assert fintech.expected_domain == "financial-services"
    assert {
        "financial-product-intelligence",
        "trust-credibility-and-transparency",
        "landing-page",
        "conversion-and-content",
    }.issubset(fintech.jit_contains)

    production = cases["page-production-dashboard"]
    assert "outcome-metrics-and-instrumentation" in production.jit_contains

    evidence_led = cases["page-real-user-validation"]
    assert "real-user-validation" in evidence_led.jit_contains


def test_a43_routing_corpus_rejects_missing_surface_coverage(tmp_path: Path) -> None:
    raw = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    raw["cases"] = [case for case in raw["cases"] if case["expected_surface"] != "PRODUCT"]
    path = tmp_path / "routing.json"
    path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(RoutingBenchmarkError, match="cover all change surfaces"):
        RoutingBenchmarkCorpus.load(path)


def test_a43_routing_corpus_rejects_skill_expectations_without_stage(tmp_path: Path) -> None:
    raw = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    raw["cases"][0]["mandatory_contains"] = ["accessibility"]
    raw["cases"][0].pop("stage_id", None)
    path = tmp_path / "routing.json"
    path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(RoutingBenchmarkError, match="skill expectations require stage_id"):
        RoutingBenchmarkCorpus.load(path)
