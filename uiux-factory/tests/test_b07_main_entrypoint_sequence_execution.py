from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from core.manager.development_manager import DevelopmentManager
from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.runtime.flow_os.work_execution import WorkExecutionPlan


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"
GOAL = "Audit the landing page, redesign checkout, implement it, and QA it."


class _MainEntryPointHarness(DevelopmentManager):
    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.flow = ProfessionalWebsiteFlow(SKILLS)
        self.team_runner = object()

    async def _stage(
        self,
        context,
        stage: str,
        key: str,
        filename: str,
        payload: str,
    ) -> None:
        context.start_stage(stage)
        self._write(context, key, filename, payload)
        context.complete_stage(stage)

    async def _run_reference_analysis(self, context) -> None:
        await self._stage(context, "reference_analysis", "reference_analysis", "reference-dna.json", "{}")

    async def _run_research(self, context) -> None:
        await self._stage(context, "research", "research", "research.md", "# audit findings\n")

    async def _run_ux_ia(self, context) -> None:
        await self._stage(context, "ux_ia", "ux_ia", "ux-ia.md", "# ux\n")

    async def _run_art_direction(self, context) -> None:
        await self._stage(context, "art_direction", "art_direction", "art-direction.md", "# art\n")

    async def _run_design_contract(self, context) -> None:
        await self._stage(context, "design_contract", "design_contract", "design-contract.json", "{}")

    async def _run_design_system(self, context) -> None:
        await self._stage(context, "design_system", "design_system", "design-system.json", "{}")

    async def _run_implementation_plan(self, context) -> None:
        await self._stage(
            context,
            "implementation_plan",
            "implementation_plan",
            "implementation-plan.json",
            "{}",
        )

    async def _run_visual_composition(self, context) -> None:
        await self._stage(
            context,
            "visual_composition",
            "visual_composition",
            "visual-composition.json",
            '{"status":"ready"}',
        )

    async def _run_specification_compile(self, context) -> None:
        await self._stage(
            context,
            "specification_compile",
            "full_build_spec",
            "02-FULL-BUILD-SPEC.md",
            "# implementation spec\n",
        )

    async def _run_template_implementation(self, context) -> None:
        await self._stage(
            context,
            "implementation",
            "implementation",
            "frontend-result.json",
            '{"status":"implemented"}',
        )

    async def _run_quality_loop(self, context) -> None:
        context.start_stage("quality_loop")
        self._write(context, "quality_loop", "quality-loop.json", '{"status":"passed"}')
        context.complete_stage("browser_qa")
        context.complete_stage("visual_qa")
        context.complete_stage("quality_loop")


class _FailingImplementationHarness(_MainEntryPointHarness):
    async def _run_template_implementation(self, context) -> None:
        context.start_stage("implementation")
        raise RuntimeError("B07 implementation fixture failure")


def _execution(context) -> WorkExecutionPlan:
    path = Path(context.artifacts["execution_plan"])
    return WorkExecutionPlan.from_dict(json.loads(path.read_text(encoding="utf-8")))


def test_b07_main_entrypoint_consumes_sequence_plan_to_completion(tmp_path: Path) -> None:
    manager = _MainEntryPointHarness(tmp_path)
    context = asyncio.run(
        manager.run(
            GOAL,
            run_id="b07-main-sequence",
            engine="template",
        )
    )

    assert context.status == "completed"
    assert {"flow_plan", "work_plan", "execution_plan"}.issubset(context.artifacts)

    flow_plan = json.loads(Path(context.artifacts["flow_plan"]).read_text(encoding="utf-8"))
    assert flow_plan["routing_mode"] == "sequence"
    assert flow_plan["execution"]["stateful"] is True
    assert flow_plan["execution"]["initial_status"] == "in_progress"
    assert [segment["phase"] for segment in flow_plan["work_segments"]] == [
        "audit",
        "design",
        "implementation",
        "qa",
    ]

    plan = _execution(context)
    assert plan.completion_status == "completed"
    assert [node.status for node in plan.nodes] == ["passed"] * 4
    assert [node.attempts for node in plan.nodes] == [1, 1, 1, 1]
    assert {artifact.kind for artifact in plan.artifacts.values()} == {
        "audit-findings",
        "design-spec",
        "implementation-artifact",
        "qa-evidence",
    }
    assert all(artifact.digest and artifact.digest.startswith("sha256:") for artifact in plan.artifacts.values())
    assert all(artifact.metadata["source"] == "factory-main-entrypoint" for artifact in plan.artifacts.values())

    events = (context.run_dir / "events.jsonl").read_text(encoding="utf-8")
    assert events.count('"event": "flow.execution_phase_completed"') == 4


def test_b07_main_entrypoint_failure_blocks_downstream_execution(tmp_path: Path) -> None:
    manager = _FailingImplementationHarness(tmp_path)

    with pytest.raises(RuntimeError, match="B07 implementation fixture failure"):
        asyncio.run(
            manager.run(
                GOAL,
                run_id="b07-main-failure",
                engine="template",
            )
        )

    state = json.loads((tmp_path / "runs" / "b07-main-failure" / "run.json").read_text(encoding="utf-8"))
    assert state["status"] == "failed"
    plan_path = Path(state["artifacts"]["execution_plan"])
    plan = WorkExecutionPlan.from_dict(json.loads(plan_path.read_text(encoding="utf-8")))

    assert [node.status for node in plan.nodes] == ["passed", "passed", "failed", "blocked"]
    assert plan.nodes[2].blocking_reason == "RuntimeError: B07 implementation fixture failure"
    assert plan.nodes[3].blocking_reason == "upstream_failed:work-3"
    assert plan.completion_status == "failed"


def test_b07_single_task_keeps_legacy_main_path_without_execution_plan(tmp_path: Path) -> None:
    manager = _MainEntryPointHarness(tmp_path)
    context = asyncio.run(
        manager.run(
            "Fix button padding on the current page.",
            run_id="b07-single-task",
            engine="template",
        )
    )

    assert context.status == "completed"
    assert "work_plan" not in context.artifacts
    assert "execution_plan" not in context.artifacts
    flow_plan = json.loads(Path(context.artifacts["flow_plan"]).read_text(encoding="utf-8"))
    assert flow_plan["routing_mode"] == "single"
    assert flow_plan["execution"]["stateful"] is False
