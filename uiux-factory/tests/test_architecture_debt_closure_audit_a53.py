from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.benchmarks.architecture_debt_closure_audit import (
    ArchitectureDebtClosureAuditError,
    evaluate_architecture_debt_closure_audit,
)


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "uiux-factory/benchmarks/architecture-debt-closure-audit-v1.json"


def test_flow3_current_repo_closes_architecture_debt_ledger_for_upgrade() -> None:
    report = evaluate_architecture_debt_closure_audit(AUDIT)

    assert report.decision == "ARCHITECTURE_DEBT_LEDGER_CLOSED_FOR_UPGRADE"
    assert report.source_contract_clear is True
    assert report.area_contract_clear is True
    assert report.governance_boundary_clear is True
    assert report.closed_count == 4
    assert report.intentional_hold_count == 5
    assert report.actionable_debt_count == 0
    assert report.flow4_allowed is True
    assert all(item.evidence_clear for item in report.areas)


def test_flow3_intentional_holds_are_explicit_non_blocking_and_triggered() -> None:
    report = evaluate_architecture_debt_closure_audit(AUDIT)
    holds = [item for item in report.areas if item.classification == "INTENTIONAL_HOLD"]

    assert {item.id for item in holds} == {
        "provider_default_migration",
        "lifecycle_mutation_convergence",
        "genai_nist_expansion",
        "vector_semantic_retrieval",
        "compatibility_surface_removal",
    }
    assert all(item.upgrade_blocker is False for item in holds)
    assert all(item.trigger.strip() for item in holds)


def test_flow3_zero_internal_consumers_never_implies_compatibility_removal() -> None:
    report = evaluate_architecture_debt_closure_audit(AUDIT)
    areas = {item.id: item for item in report.areas}

    assert areas["runtime_flow_os_single_owner"].classification == "CLOSED"
    assert areas["compatibility_surface_removal"].classification == "INTENTIONAL_HOLD"
    assert report.compatibility_shim_deletion_allowed is False


def test_flow3_has_no_authority_or_runtime_mutation_effects() -> None:
    report = evaluate_architecture_debt_closure_audit(AUDIT)

    assert report.runtime_mutation_allowed is False
    assert report.provider_default_change_allowed is False
    assert report.lifecycle_state_owner_change_allowed is False
    assert report.routing_change_allowed is False
    assert report.knowledge_index_mutation_allowed is False
    assert report.vector_search_change_allowed is False
    assert report.compatibility_shim_deletion_allowed is False
    assert report.evidence_authority_change_allowed is False
    assert report.gate_authority_change_allowed is False
    assert report.release_authority_change_allowed is False
    assert report.product_evidence is False
    assert (
        report.execution_effect,
        report.authority_effect,
        report.gate_effect,
        report.evidence_effect,
        report.release_effect,
    ) == ("none",) * 5


def test_flow3_rejects_relabeling_provider_hold_as_closed(tmp_path: Path) -> None:
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    for area in payload["areas"]:
        if area["id"] == "provider_default_migration":
            area["classification"] = "CLOSED"
            area["closure_basis"] = "zero receipts are fine"
            area.pop("hold_trigger", None)
            area.pop("upgrade_blocker", None)
            break
    target = tmp_path / "audit.json"
    target.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ArchitectureDebtClosureAuditError, match="classification drifted"):
        evaluate_architecture_debt_closure_audit(target)


def test_flow3_rejects_promoting_vector_hold_without_separate_evidence(tmp_path: Path) -> None:
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    for area in payload["areas"]:
        if area["id"] == "vector_semantic_retrieval":
            area["classification"] = "CLOSED"
            area["closure_basis"] = "vector work no longer matters"
            area.pop("hold_trigger", None)
            area.pop("upgrade_blocker", None)
            break
    target = tmp_path / "audit.json"
    target.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ArchitectureDebtClosureAuditError, match="classification drifted"):
        evaluate_architecture_debt_closure_audit(target)


def test_flow3_governance_drift_fails_closed(tmp_path: Path) -> None:
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    payload["governance"]["runtime_mutation_allowed"] = True
    target = tmp_path / "audit.json"
    # Keep the same repository-relative location so source-contract paths still resolve.
    benchmark_dir = tmp_path / "uiux-factory" / "benchmarks"
    benchmark_dir.mkdir(parents=True)
    target = benchmark_dir / "architecture-debt-closure-audit-v1.json"
    target.write_text(json.dumps(payload), encoding="utf-8")

    # A copied contract outside the repository must fail closed before it can claim PASS.
    with pytest.raises(ArchitectureDebtClosureAuditError):
        evaluate_architecture_debt_closure_audit(target)
