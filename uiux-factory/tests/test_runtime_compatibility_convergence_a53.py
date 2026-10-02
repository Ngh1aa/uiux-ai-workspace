from __future__ import annotations

from pathlib import Path

from core.benchmarks.runtime_compatibility_convergence import (
    evaluate_runtime_compatibility_convergence,
)


FACTORY = Path(__file__).resolve().parents[1]
REPO = FACTORY.parent
CONTRACT = FACTORY / "benchmarks" / "runtime-compatibility-convergence-v1.json"


def test_flow1_current_state_has_zero_first_party_shim_consumers() -> None:
    report = evaluate_runtime_compatibility_convergence(CONTRACT)

    assert report.decision == "FIRST_PARTY_RUNTIME_COMPAT_CONVERGENCE_PASS"
    assert report.historical_baseline_clear is True
    assert report.historical_consumer_files == 8
    assert report.historical_consumer_imports == 19
    assert report.internal_consumer_file_count == 0
    assert report.internal_consumer_import_count == 0
    assert report.zero_internal_consumers is True


def test_flow1_compatibility_shims_remain_thin_and_identity_equivalent() -> None:
    report = evaluate_runtime_compatibility_convergence(CONTRACT)

    assert report.shim_count == 8
    assert report.shim_contract_clear is True
    assert report.identity_checks_clear is True
    assert report.identity_checks
    assert all(check.identical for check in report.identity_checks)


def test_flow1_migrated_scripts_use_canonical_factory_bootstrap() -> None:
    report = evaluate_runtime_compatibility_convergence(CONTRACT)

    assert report.migrated_consumer_contract_clear is True
    assert report.script_bootstrap_clear is True

    for relative in (
        "skills_UIUX/scripts/context-manifest.py",
        "skills_UIUX/scripts/validate-flows.py",
        "skills_UIUX/scripts/validate-provider-runtime.py",
        "skills_UIUX/scripts/validate-runtime-foundation.py",
    ):
        source = (REPO / relative).read_text(encoding="utf-8")
        assert 'FACTORY_ROOT = ROOT.parent / "uiux-factory"' in source
        assert "from core.runtime.flow_os." in source
        assert "from runtime." not in source


def test_flow1_does_not_authorize_shim_removal_or_runtime_authority_changes() -> None:
    report = evaluate_runtime_compatibility_convergence(CONTRACT)

    assert report.governance_boundary_clear is True
    assert report.shim_deletion_allowed is False
    assert report.external_removal_safety_inferred is False
    assert report.runtime_behavior_change_allowed is False
    assert report.provider_default_change_allowed is False
    assert report.lifecycle_state_owner_change_allowed is False
    assert report.routing_change_allowed is False
    assert report.evidence_authority_change_allowed is False
    assert report.gate_authority_change_allowed is False
    assert report.release_authority_change_allowed is False
    assert report.product_evidence is False
    assert report.execution_effect == "none"
    assert report.authority_effect == "none"
    assert report.gate_effect == "none"
    assert report.evidence_effect == "none"
    assert report.release_effect == "none"
