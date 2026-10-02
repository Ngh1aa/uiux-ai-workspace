from __future__ import annotations

from pathlib import Path

from core.benchmarks.post_interop_executable_debt_audit import (
    discover_runtime_shim_consumers,
    evaluate_post_interop_executable_debt_audit,
    validate_compatibility_shim,
)


FACTORY = Path(__file__).resolve().parents[1]
REPO = FACTORY.parent
AUDIT = FACTORY / "benchmarks" / "post-interop-executable-debt-audit-v1.json"


def test_a52_3_current_audit_selects_compat_shim_retirement_readiness() -> None:
    report = evaluate_post_interop_executable_debt_audit(AUDIT)

    assert report.decision == "SELECT_COMPAT_SHIM_RETIREMENT_READINESS"
    assert report.next_package == "A53.1 — Runtime Compatibility Shim Retirement Readiness"
    assert report.scope == "architecture_debt_selection_only_no_runtime_mutation"
    assert report.source_truth_clear is True

    assert report.provider_default_migration_blocked is True
    assert report.provider_live_receipt_count == 0
    assert report.lifecycle_mutation_blocked is True
    assert len(report.lifecycle_blockers) == 6
    assert report.lifecycle_interop_observation_only is True
    assert report.genai_nist_expansion_blocked is True
    assert report.vector_semantic_retrieval_deferred is True

    assert report.shim_count == 8
    assert report.shim_contract_clear is True
    assert all(item.clear for item in report.shim_checks)
    assert report.known_consumer_contract_clear is True

    consumers = {item.path: set(item.modules) for item in report.internal_consumers}
    assert "skills_UIUX/scripts/validate-runtime-foundation.py" in consumers
    assert {"runtime.agent", "runtime.manager"}.issubset(
        consumers["skills_UIUX/scripts/validate-runtime-foundation.py"]
    )


def test_a52_3_shim_contract_rejects_independent_logic(tmp_path: Path) -> None:
    shim = tmp_path / "agent.py"
    shim.write_text(
        '"""Deprecated compatibility import."""\n'
        "from core.runtime.flow_os.agent import *\n\n"
        "def choose_flow():\n"
        "    return 'shadow-runtime'\n",
        encoding="utf-8",
    )

    clear, reasons = validate_compatibility_shim(shim, "core.runtime.flow_os.agent")

    assert clear is False
    assert "contains_independent_control_or_definition_logic" in reasons


def test_a52_3_consumer_census_detects_declared_runtime_imports(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    scripts = root / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "consumer.py").write_text(
        "from runtime.agent import ProviderNeutralAgentHarness\n"
        "from skills_UIUX.runtime.manager import DevelopmentManagerAgent\n",
        encoding="utf-8",
    )

    consumers = discover_runtime_shim_consumers(
        root,
        ["scripts"],
        ["runtime.agent", "runtime.manager"],
    )

    assert len(consumers) == 1
    assert consumers[0].path == "scripts/consumer.py"
    assert consumers[0].modules == ("runtime.agent", "runtime.manager")


def test_a52_3_audit_cannot_authorize_runtime_or_release_effects() -> None:
    report = evaluate_post_interop_executable_debt_audit(AUDIT)

    assert report.governance_boundary_clear is True
    assert report.runtime_mutation_allowed is False
    assert report.shim_deletion_allowed is False
    assert report.provider_default_change_allowed is False
    assert report.lifecycle_state_owner_change_allowed is False
    assert report.genai_promotion_allowed is False
    assert report.vector_search_change_allowed is False
    assert report.product_evidence is False
    assert report.execution_effect == "none"
    assert report.authority_effect == "none"
    assert report.gate_effect == "none"
    assert report.evidence_effect == "none"
    assert report.release_effect == "none"
