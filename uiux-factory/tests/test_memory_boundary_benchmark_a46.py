from __future__ import annotations

import hashlib
from pathlib import Path

from core.benchmarks.memory_boundary_regression import (
    MemoryBoundaryCorpus,
    run_memory_boundary_benchmark,
)


FACTORY = Path(__file__).resolve().parents[1]
CORPUS = FACTORY / "benchmarks" / "memory-boundary-v1.json"
STORE = FACTORY / "core" / "memory" / "brain_memory.py"
ADAPTER = FACTORY / "core" / "brain_os" / "adapters" / "memory_context.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_a46_memory_boundary_benchmark_all_cases_pass() -> None:
    report = run_memory_boundary_benchmark(MemoryBoundaryCorpus.load(CORPUS))

    assert report["passed"] is True
    assert report["pass_count"] == report["case_count"] == 6


def test_a46_memory_boundary_benchmark_covers_project_and_run_isolation() -> None:
    corpus = MemoryBoundaryCorpus.load(CORPUS)
    ids = {case.id for case in corpus.cases}

    assert "current-run-excluded" in ids
    assert "cross-project-write-rejected" in ids
    assert "historical-hypothesis-recall" in ids
    assert "recall-limit-newest-first" in ids


def test_a46_every_recall_case_locks_post_routing_and_no_authority_effects() -> None:
    report = run_memory_boundary_benchmark(MemoryBoundaryCorpus.load(CORPUS))

    for row in report["cases"]:
        if row["operation"] != "recall":
            continue
        assert row["flow_id"] == "page-ui-work"
        assert row["checks"]["post_routing"] is True
        assert row["checks"]["flow_unchanged"] is True
        assert row["checks"]["flow_effect_none"] is True
        assert row["checks"]["authority_effect_none"] is True
        assert row["checks"]["gate_effect_none"] is True
        assert row["checks"]["evidence_effect_none"] is True
        assert row["checks"]["not_current_evidence"] is True
        assert row["checks"]["current_run_excluded"] is True


def test_a46_memory_benchmark_is_read_only_against_production_memory_sources() -> None:
    before = {path: _sha(path) for path in (STORE, ADAPTER)}
    run_memory_boundary_benchmark(MemoryBoundaryCorpus.load(CORPUS))
    after = {path: _sha(path) for path in (STORE, ADAPTER)}

    assert before == after


def test_a46_memory_benchmark_evaluator_has_no_flow_gate_execution_or_release_owner() -> None:
    source = (
        FACTORY / "core" / "benchmarks" / "memory_boundary_regression.py"
    ).read_text(encoding="utf-8")
    forbidden = (
        "FlowPlanner(",
        "select_canonical_flow(",
        "ManagedFlowController",
        "ProviderManagedRunner",
        "gate_evidence_errors",
        "run_target_command",
        "release_action",
        "ProductionReleaseController",
        "merge_pull_request",
    )
    for token in forbidden:
        assert token not in source
