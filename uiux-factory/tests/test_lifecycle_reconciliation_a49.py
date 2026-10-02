from __future__ import annotations

from pathlib import Path

from core.runtime.lifecycle_reconciliation import current_lifecycle_reconciliation


ROOT = Path(__file__).resolve().parents[1]


def test_a49_reconciliation_covers_same_ten_canonical_comparison_phases() -> None:
    report = current_lifecycle_reconciliation()
    expected = [
        "INTAKE",
        "INTERPRET",
        "PLAN",
        "RESEARCH",
        "DESIGN",
        "IMPLEMENT",
        "QA",
        "REPLAN",
        "FINALIZE",
        "RELEASE",
    ]

    assert [item.phase for item in report.factory.phases] == expected
    assert [item.phase for item in report.managed.phases] == expected
    assert report.adapter_required is True
    assert report.execution_effect == "none"
    assert report.authority_effect == "none"
    assert report.gate_effect == "none"
    assert report.evidence_effect == "none"
    assert report.release_effect == "none"


def test_a49_reconciliation_preserves_real_non_parity_instead_of_claiming_equivalence() -> None:
    report = current_lifecycle_reconciliation()

    assert report.factory.top_level_entrypoint == "uiux-factory/run.py::main"
    assert report.managed.top_level_entrypoint == "skills_UIUX/scripts/uiux-agent.py --managed"
    assert report.factory.state_model == "core.runtime.run_context.RunContext"
    assert report.managed.state_model == "core.runtime.flow_os.managed.ManagedWebsiteRun"
    assert report.factory.phase("RELEASE").support == "not_exposed"
    assert report.managed.phase("RELEASE").support == "external_controller"
    assert report.managed.phase("REPLAN").support == "native"
    assert report.factory.phase("DESIGN").support == "native"
    assert len(report.non_parity) >= 5


def test_a49_shared_invariants_keep_truth_and_authority_separate_from_lifecycle_shape() -> None:
    report = current_lifecycle_reconciliation()
    joined = "\n".join(report.shared_invariants).lower()

    assert "provider/model prose is not trusted evidence" in joined
    assert "memory is advisory" in joined
    assert "authority cannot be escalated" in joined
    assert "release authority is separate" in joined


def test_a49_factory_source_still_exposes_audited_product_lifecycle_entrypoints() -> None:
    run_source = (ROOT / "run.py").read_text(encoding="utf-8")
    manager_source = (
        ROOT / "core/manager/provider_intelligent_manager.py"
    ).read_text(encoding="utf-8")
    creative_source = (
        ROOT / "core/manager/creative_director_manager.py"
    ).read_text(encoding="utf-8")

    assert "async def main(" in run_source
    assert "CreativeDirectorDevelopmentManager(root=ROOT)" in run_source
    for name in (
        "_run_reference_analysis",
        "_run_research",
        "_run_ux_ia",
        "_run_art_direction",
        "_run_design_contract",
        "_run_design_system",
        "_run_implementation_plan",
        "_run_visual_composition",
        "_run_ai_implementation",
        "_run_quality_loop",
    ):
        assert name in manager_source
    assert "async def run_revision(" in creative_source


def test_a49_managed_source_still_exposes_audited_checkpoint_lifecycle_entrypoints() -> None:
    managed_source = (
        ROOT / "core/runtime/flow_os/managed.py"
    ).read_text(encoding="utf-8")
    cli_source = (
        ROOT.parent / "skills_UIUX/scripts/uiux-agent.py"
    ).read_text(encoding="utf-8")

    for name in (
        "def interpret_goal(",
        "def resolve_flow(",
        "def start_from_goal(",
        "def start_stage(",
        "def complete_stage(",
        "def replan(",
        "def record_evaluation(",
    ):
        assert name in managed_source

    assert "ManagedFlowController(harness)" in cli_source
    assert "ProductionReleaseController(harness)" in cli_source
    assert "release.finalize_workspace(" in cli_source
    assert "release.deploy_production(" in cli_source


def test_a49_reconciliation_module_is_descriptive_only() -> None:
    source = (
        ROOT / "core/runtime/lifecycle_reconciliation.py"
    ).read_text(encoding="utf-8")

    forbidden = (
        "subprocess.",
        "urllib.",
        "requests.",
        "aiohttp.",
        "os.system",
        "execute_plan(",
        "run_stage(",
        "deploy_production(",
        "finalize_workspace(",
    )
    for token in forbidden:
        assert token not in source
