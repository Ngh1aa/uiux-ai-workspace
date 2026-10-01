from __future__ import annotations

import hashlib
from pathlib import Path

from core.benchmarks.repair_proposal_regression import (
    RepairProposalCorpus,
    run_repair_proposal_benchmark,
)


FACTORY = Path(__file__).resolve().parents[1]
CORPUS = FACTORY / "benchmarks" / "repair-proposals-v1.json"
ORCHESTRATOR = FACTORY / "core" / "brain_os" / "repair_orchestrator.py"
LINEAGE = FACTORY / "core" / "brain_os" / "adapters" / "repair_lineage.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_a45_repair_proposal_benchmark_all_cases_pass() -> None:
    corpus = RepairProposalCorpus.load(CORPUS)
    report = run_repair_proposal_benchmark(corpus)

    assert report["passed"] is True
    assert report["pass_count"] == report["case_count"] == 9


def test_a45_repair_proposal_benchmark_covers_all_core_critics_and_fallback() -> None:
    corpus = RepairProposalCorpus.load(CORPUS)
    critics = {case.critic for case in corpus.cases}

    assert {
        "visual",
        "ux_ia",
        "design_system",
        "accessibility",
        "product",
        "runtime",
        "evidence_truth",
        "custom_critic",
    }.issubset(critics)
    assert {case.severity.value for case in corpus.cases} == {"P0", "P1", "P2"}


def test_a45_benchmark_is_read_only_against_production_proposal_sources() -> None:
    before = {_path: _sha(_path) for _path in (ORCHESTRATOR, LINEAGE)}
    corpus = RepairProposalCorpus.load(CORPUS)
    run_repair_proposal_benchmark(corpus)
    after = {_path: _sha(_path) for _path in (ORCHESTRATOR, LINEAGE)}

    assert before == after


def test_a45_every_benchmark_case_guards_false_verification_and_auto_execution() -> None:
    report = run_repair_proposal_benchmark(RepairProposalCorpus.load(CORPUS))

    for row in report["cases"]:
        assert row["checks"]["root_proposed"] is True
        assert row["checks"]["directive_proposed"] is True
        assert row["checks"]["retest_pending"] is True
        assert row["checks"]["no_retest_evidence"] is True
        assert row["checks"]["no_verified_by"] is True
        assert row["checks"]["no_retested_by"] is True
        assert row["checks"]["no_trusted_flag"] is True
        assert row["checks"]["no_execution_claim"] is True
        assert row["checks"]["no_verification_claim"] is True
        assert row["checks"]["no_authority_effect"] is True


def test_a45_benchmark_evaluator_does_not_own_execution_or_release() -> None:
    source = (FACTORY / "core" / "benchmarks" / "repair_proposal_regression.py").read_text(
        encoding="utf-8"
    )
    forbidden = (
        "ProviderManagedRunner",
        "ManagedFlowController",
        "ProductionReleaseController",
        "gate_evidence_errors",
        "run_target_command",
        "release_action",
        "merge_pull_request",
        "EvidenceRecord(",
    )
    for token in forbidden:
        assert token not in source
