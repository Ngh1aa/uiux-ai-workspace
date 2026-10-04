from __future__ import annotations

from pathlib import Path

from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.runtime.flow_os.main_execution import advance_execution_phase, fail_execution_phase
from core.runtime.flow_os.work_execution import WorkExecutionPlan


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"
GOAL = "Audit the landing page, redesign checkout, implement it, and QA it."


def _plan() -> WorkExecutionPlan:
    factory = ProfessionalWebsiteFlow(SKILLS)
    _profile, work_plan = factory.resolve_work_plan(GOAL)
    return WorkExecutionPlan.from_resolved_work_plan(work_plan)


def _sources(tmp_path: Path) -> dict[str, tuple[str, Path]]:
    payloads = {
        "audit-findings": ("research", "# audit findings\n"),
        "design-spec": ("visual_composition", '{"status":"ready"}\n'),
        "implementation-artifact": ("implementation", '{"status":"implemented"}\n'),
        "qa-evidence": ("quality_loop", '{"status":"passed"}\n'),
        "constraint-evidence": ("quality_loop", '{"status":"passed"}\n'),
    }
    sources: dict[str, tuple[str, Path]] = {}
    for kind, (key, text) in payloads.items():
        path = tmp_path / f"{key}.artifact"
        path.write_text(text, encoding="utf-8")
        sources[kind] = (key, path)
    return sources


def test_b07_main_execution_adapter_drives_sequence_to_completion(tmp_path: Path) -> None:
    plan = _plan()
    sources = _sources(tmp_path)

    assert advance_execution_phase(plan, "audit", sources) == ["work-1"]
    assert advance_execution_phase(plan, "design", sources) == ["work-2"]
    assert advance_execution_phase(plan, "implementation", sources) == ["work-3"]
    assert advance_execution_phase(plan, "qa", sources) == ["work-4"]

    assert plan.completion_status == "completed"
    assert [node.status for node in plan.nodes] == ["passed"] * 4
    assert [node.attempts for node in plan.nodes] == [1, 1, 1, 1]
    assert {artifact.kind for artifact in plan.artifacts.values()} == {
        "audit-findings",
        "design-spec",
        "implementation-artifact",
        "qa-evidence",
    }
    assert all(
        artifact.digest and artifact.digest.startswith("sha256:")
        for artifact in plan.artifacts.values()
    )
    assert all(
        artifact.metadata["source"] == "factory-main-entrypoint"
        for artifact in plan.artifacts.values()
    )


def test_b07_main_execution_failure_blocks_downstream_nodes(tmp_path: Path) -> None:
    plan = _plan()
    sources = _sources(tmp_path)

    advance_execution_phase(plan, "audit", sources)
    advance_execution_phase(plan, "design", sources)
    failed = fail_execution_phase(
        plan,
        "implementation",
        "RuntimeError: B07 implementation fixture failure",
    )

    assert failed == "work-3"
    assert [node.status for node in plan.nodes] == ["passed", "passed", "failed", "blocked"]
    assert plan.nodes[2].blocking_reason == "RuntimeError: B07 implementation fixture failure"
    assert plan.nodes[3].blocking_reason == "upstream_failed:work-3"
    assert plan.completion_status == "failed"


def test_b07_main_entrypoints_are_wired_to_stateful_sequence_execution() -> None:
    development = (ROOT / "core" / "manager" / "development_manager.py").read_text(encoding="utf-8")
    provider = (ROOT / "core" / "manager" / "provider_intelligent_manager.py").read_text(encoding="utf-8")

    assert "advance_execution_phase" in development
    assert "fail_execution_phase" in development
    assert "stateful_execution: bool = False" in development
    assert '"schema_version": 1' in development

    assert 'self._save_flow_plan(context, engine, stateful_execution=True)' in development
    assert 'self._save_flow_plan(context, engine, stateful_execution=True)' in provider

    for phase in ("audit", "design", "implementation", "qa"):
        marker = f'self._complete_execution_phase(context, "{phase}")'
        assert marker in development
        assert marker in provider

    assert "self._assert_execution_completion(context)" in development
    assert "self._assert_execution_completion(context)" in provider
    assert "self._fail_active_execution_segment(context, error)" in development
    assert "self._fail_active_execution_segment(context, error)" in provider


def test_b07_single_task_contract_stays_on_legacy_single_path() -> None:
    contract = ProfessionalWebsiteFlow(SKILLS).resolve_contract(
        "Fix button padding on the current page."
    )
    assert contract.routing_mode == "single"
    assert contract.segments == []
