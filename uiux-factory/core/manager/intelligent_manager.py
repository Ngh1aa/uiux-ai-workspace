from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

from core.contracts.frontend_result_schema import FrontendResult
from core.manager.development_manager import DevelopmentManager
from core.orchestration.reference_intelligence import ReferenceIntelligencePlanner
from core.orchestration.skill_governance import FlowReplanner, ReplanDecision, SkillGovernanceSnapshot
from core.runtime.run_context import RunContext


class IntelligentDevelopmentManager(DevelopmentManager):
    """Skills-driven manager layered on top of the proven Factory pipeline.

    The base DevelopmentManager remains the execution safety net. This class
    activates cross-phase policies that already exist in skills_UIUX:
    curated reference intelligence, immutable governance provenance and bounded
    evidence-driven replanning after final QA fails.
    """

    def __init__(self, root: Path):
        super().__init__(root)
        self.reference_planner = ReferenceIntelligencePlanner()
        self.replanner = FlowReplanner(self.flow.document)
        self.governance = SkillGovernanceSnapshot(self.team_runner.skills_root)
        self._root_replan_count = 0

    def _save_design_context(self, context: RunContext) -> None:
        path = context.run_dir / "design-context.json"
        path.write_text(context.design_context.model_dump_json(indent=2), encoding="utf-8")
        context.add_artifact("design_context", path)

    def _save_governance_snapshot(self, context: RunContext) -> None:
        payload = self.governance.build()
        path = self._write(
            context,
            "skill_governance",
            "skill-governance.json",
            json.dumps(payload, indent=2, ensure_ascii=False),
        )
        self.team_runner.event_bus(context).emit(
            "skills.governance_locked",
            stage="reference_analysis",
            data={
                "artifact": str(path),
                "policy_files": payload["policy_files"],
            },
        )

    def _apply_reference_intelligence(self, context: RunContext) -> None:
        supplied = list(context.design_context.reference_urls)
        plan = self.reference_planner.plan(
            goal=context.goal,
            user_urls=supplied,
            auto_enabled=context.design_context.auto_inspiration,
            target_reference_count=context.design_context.inspiration_target,
        )
        self._write(
            context,
            "reference_benchmark_plan",
            "reference-benchmark-plan.json",
            plan.model_dump_json(indent=2),
        )

        if plan.final_reference_urls != supplied:
            context.design_context = context.design_context.model_copy(
                update={"reference_urls": plan.final_reference_urls}
            )
            self._save_design_context(context)

        self.team_runner.event_bus(context).emit(
            "reference.intelligence_planned",
            stage="reference_analysis",
            data={
                "website_type": plan.website_type,
                "user_reference_count": plan.user_reference_count,
                "auto_selected": [item.model_dump() for item in plan.selected],
                "final_reference_urls": plan.final_reference_urls,
            },
        )

    async def _run_reference_analysis(self, context: RunContext) -> None:
        self._save_governance_snapshot(context)
        self._apply_reference_intelligence(context)
        await super()._run_reference_analysis(context)

    @contextmanager
    def _temporary_stage_skills(self, stage: str, decision: ReplanDecision):
        """Temporarily expose policy-selected corrective skills to the existing router.

        Factory runs are already cross-process locked, so this bounded class-level
        override cannot race another local pipeline. The original routing table is
        restored even when regeneration fails.
        """

        if decision.drop_skills:
            raise RuntimeError(
                "Factory does not silently drop skills during root-cause replanning; "
                "the declarative policy must be reviewed first."
            )

        extras = tuple(decision.add_skills)
        if not extras:
            yield
            return

        missing = [
            name
            for name in extras
            if not (self.team_runner.skills_root / name / "SKILL.md").is_file()
        ]
        if missing:
            raise FileNotFoundError(
                "Replanning policy references missing skills: " + ", ".join(missing)
            )

        mapping = self.flow.EXTRA_BY_FACTORY_STAGE
        previous = tuple(mapping.get(stage, ()))
        mapping[stage] = tuple(dict.fromkeys(previous + extras))
        try:
            yield
        finally:
            mapping[stage] = previous

    def _quality_replan_decision(self, context: RunContext) -> ReplanDecision:
        task_context = self.flow.interpreter.interpret(context.goal).to_dict()
        return self.replanner.decide(
            signal="GATE_FAIL",
            current_stage="qa",
            task_context=task_context,
            replan_count=self._root_replan_count,
        )

    async def _execute_quality(self, context: RunContext, frontend: FrontendResult, output_dir: Path):
        from core.orchestration.quality_loop import QualityLoopRunner

        runner = QualityLoopRunner(
            team_runner=self.team_runner,
            run_context=context,
            max_iterations=4,
            min_score_improvement=1,
        )
        return await runner.run(
            project_dir=Path(frontend.project_dir),
            project_slug=frontend.project_slug,
            output_dir=output_dir,
        )

    async def _regenerate_after_replan(
        self,
        context: RunContext,
        frontend: FrontendResult,
        decision: ReplanDecision,
    ) -> FrontendResult:
        if decision.target_stage != "implementation":
            raise RuntimeError(
                "Current Factory root-cause replan supports QA → implementation. "
                f"Policy requested {decision.target_stage!r}; upstream design replans "
                "must be handled by a dedicated stage invalidation pass."
            )

        with self._temporary_stage_skills("implementation", decision):
            if frontend.generated_by == "AIFrontendBuilder":
                provider = self.team_runner.provider
                if provider is None:
                    raise RuntimeError("AI root-cause regeneration requires the active provider.")
                await self._run_ai_implementation(context, provider)
            else:
                await self._run_template_implementation(context)

        refreshed_path = self._require(context, "implementation")
        return FrontendResult.model_validate_json(refreshed_path.read_text(encoding="utf-8"))

    async def _run_quality_loop(self, context: RunContext) -> None:
        stage = "quality_loop"
        print("\n[Stage] Quality Loop STARTED")
        frontend_path = self._require(context, "implementation")
        frontend = FrontendResult.model_validate_json(frontend_path.read_text(encoding="utf-8"))
        if not Path(frontend.project_dir).is_dir():
            raise RuntimeError(f"Generated project missing: {frontend.project_dir}")

        context.start_stage(stage)
        first = await self._execute_quality(context, frontend, context.run_dir)
        if first.status == "passed":
            final = first
        else:
            self._write(
                context,
                "quality_loop_before_replan",
                "quality-loop-before-replan.json",
                first.model_dump_json(indent=2),
            )
            decision = self._quality_replan_decision(context)
            replan_payload = {
                "schema_version": 1,
                "replan_index": self._root_replan_count + 1,
                "source": "skills_UIUX/flows/professional-website-redesign.json",
                "trigger": {
                    "signal": "GATE_FAIL",
                    "current_stage": "qa",
                    "quality_status": first.status,
                    "stop_reason": first.stop_reason,
                    "score": first.final_score,
                },
                "decision": decision.to_dict(),
                "principle": "replan from evidence and root cause; do not blind-retry the same repair loop",
            }
            self._write(
                context,
                f"replan_{self._root_replan_count + 1}",
                f"replan-{self._root_replan_count + 1:02d}.json",
                json.dumps(replan_payload, indent=2, ensure_ascii=False),
            )
            self.team_runner.event_bus(context).emit(
                "flow.replan_decided",
                stage="quality_loop",
                data=replan_payload,
            )

            if not decision.accepted:
                final = first
            else:
                self._root_replan_count += 1
                frontend = await self._regenerate_after_replan(context, frontend, decision)
                context.start_stage(stage)
                final = await self._execute_quality(
                    context,
                    frontend,
                    context.run_dir / f"root-replan-{self._root_replan_count:02d}",
                )
                self._write(
                    context,
                    f"quality_loop_replan_{self._root_replan_count}",
                    f"quality-loop-replan-{self._root_replan_count:02d}.json",
                    final.model_dump_json(indent=2),
                )

        artifact = self._write(
            context,
            "quality_loop",
            "quality-loop.json",
            final.model_dump_json(indent=2),
        )
        if final.status != "passed":
            raise RuntimeError(
                "Quality loop stopped without PASS after skills-driven root-cause handling: "
                f"status={final.status}; reason={final.stop_reason}; "
                f"score={final.final_score}; artifact={artifact}"
            )

        context.complete_stage("browser_qa")
        context.complete_stage("visual_qa")
        context.complete_stage(stage)
        print(
            "[Stage] Quality Loop COMPLETED — "
            f"score={final.final_score}; iterations={len(final.iterations)}; "
            f"root_replans={self._root_replan_count}"
        )
