from __future__ import annotations

from pathlib import Path

from core.benchmarks.regression_corpus import BenchmarkCorpus


REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS = REPO_ROOT / "uiux-factory" / "benchmarks" / "corpus" / "uiux-product-v2.json"


def test_a18_v2_corpus_has_twelve_distinct_domains_and_archetypes() -> None:
    corpus = BenchmarkCorpus.load(CORPUS)
    domains = {case.domain for case in corpus.cases}
    archetypes = {case.product_archetype for case in corpus.cases}

    assert corpus.version == "2.0.0"
    assert len(corpus.cases) >= 12
    assert len(domains) >= 12
    assert len(archetypes) >= 12


def test_a18_corpus_covers_domains_beyond_original_dogfood_trio() -> None:
    corpus = BenchmarkCorpus.load(CORPUS)
    domains = {case.domain for case in corpus.cases}

    assert {
        "consumer-fintech",
        "cultural-museum",
        "industrial-b2b-service",
        "healthcare-patient-portal",
        "luxury-commerce",
        "public-service",
        "editorial-media",
        "dashboard-application",
    }.issubset(domains)


def test_a18_machine_objective_contract_never_fabricates_human_verdicts() -> None:
    corpus = BenchmarkCorpus.load(CORPUS)
    assert all(case.human_review["status"] == "pending" for case in corpus.cases)
    assert all(case.human_review.get("verdict") is None for case in corpus.cases)
    assert all(case.screenshot_pack["status"] == "pending" for case in corpus.cases)
