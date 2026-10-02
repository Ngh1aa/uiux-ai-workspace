from __future__ import annotations

import hashlib
import json
from pathlib import Path

from core.benchmarks.scorecard_regression import evaluate_scorecard_benchmark


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "benchmarks" / "scorecard-v1.json"
SCORECARD_SOURCE = ROOT / "core" / "brain_os" / "scorecard.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_a47_scorecard_benchmark_all_cases_pass() -> None:
    results = evaluate_scorecard_benchmark(CORPUS)
    assert results
    assert all(item.passed for item in results), [item.detail for item in results if not item.passed]


def test_a47_scorecard_benchmark_is_read_only_against_production_scorecard() -> None:
    before = _sha(SCORECARD_SOURCE)
    evaluate_scorecard_benchmark(CORPUS)
    after = _sha(SCORECARD_SOURCE)
    assert after == before


def test_a47_scorecard_benchmark_covers_runtime_outcomes_and_provenance_rejection() -> None:
    payload = json.loads(CORPUS.read_text(encoding="utf-8"))
    cases = payload["cases"]
    outcomes = {case["runtime_outcome"] for case in cases}
    assert {"passed", "failed", "blocked", "insufficient_evidence"}.issubset(outcomes)
    assert any(case.get("integrity_state") == "error" for case in cases)
    assert any(case.get("integrity_state") == "warning" for case in cases)
    assert any(case.get("duplicate_source_ref") and case.get("expected_rejected") for case in cases)
    assert any(
        case["runtime_outcome"] == "passed"
        and case.get("integrity_state") == "error"
        and case["expected_runtime_outcome"] == "passed"
        for case in cases
    )


def test_a47_scorecard_benchmark_does_not_own_runtime_gate_or_release_actions() -> None:
    source = (ROOT / "core" / "benchmarks" / "scorecard_regression.py").read_text(encoding="utf-8")
    forbidden = (
        "RunEvaluator(",
        "effective_evidence(",
        "gate_evidence_errors",
        "ProviderManagedRunner",
        "ManagedFlowController",
        "ProductionReleaseController",
        "run_target_command",
        "release_action",
        "merge_pull_request",
    )
    for token in forbidden:
        assert token not in source
