from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

from core.contracts.frontend_result_schema import FrontendResult
from core.manager.development_manager import DevelopmentManager
from core.orchestration.reference_intelligence import ReferenceIntelligencePlanner
from core.orchestration.skill_governance import FlowReplanner, ReplanDecision, SkillGovernanceSnapshot
from core.orchestration.stage_replan_v1 import (
    REPLAN_STAGE_ORDER as V1_REPLAN_STAGE_ORDER,
    STAGE_ARTIFACT_KEYS as V1_STAGE_ARTIFACT_KEYS,
    canonical_replan_stage,
    evidence_replan_target,
    stages_from,
)
from core.runtime.run_context import RunContext


class IntelligentDevelopmentManager(DevelopmentManager):
    """Skills-driven manager layered on top of the proven Factory pipeline.

    The base DevelopmentManager remains the execution safety net. This class
    activates cross-phase policies that already exist in skills_UIUX:
    curated reference intelligence, immutable governance provenance and bounded
    evidence-driven replanning after final QA fails.
    """

    REPLAN_STAGE_ORDER = V1_REPLAN_STAGE_ORDER
    STAGE_ARTIFACT_KEYS = V1_STAGE_ARTIFACT_KEYS

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

    @classmethod
    def _canonical_replan_stage(cls, owner_stage: str | None) -> str | None:
        return canonical_replan_stage(owner_stage)

    @classmethod
    def _stages_from(cls, target_stage: str) -> tuple[str, ...]:
        return stages_from(target_stage)

    @classmethod
    def _evidence_replan_target(cls, quality_result, quality_output_dir: Path) -> str | None:
        return evidence_replan_target(quality_result, quality_output_dir)

    def _quality_replan_decision(
        self,
        context: RunContext,
        *,
        evidence_target_stage: str | None = None,
    ) -> ReplanDecision:
        task_context = self.flow.interpreter.interpret(context.goal).to_dict()
        design_owned = {
            "research",
            "ux_ia",
            "art_direction",
            "design_contract",
            "design_system",
            "visual_composition",
        }
        policy_stage = "design" if evidence_target_stage in design_owned else "qa"
        policy = self.replanner.decide(
            signal="GATE_FAIL",
            current_stage=policy_stage,
            task_context=task_context,
            replan_count=self._root_replan_count,
        )
        if not policy.accepted or not evidence_target_stage:
            return policy
        return ReplanDecision(
            accepted=True,
            signal=policy.signal,
            reason=(
                f"{policy.reason} Evidence ownership requires invalidation from "
                f"{evidence_target_stage!r} rather than patching a downstream symptom."
            ),
            target_stage=evidence_target_stage,
            add_skills=policy.add_skills,
            drop_skills=policy.drop_skills,
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

    def _invalidate_from_stage(self, context: RunContext, target_stage: str) -> tuple[str, ...]:
        stages = self._stages_from(target_stage)
        invalidated_keys: list[str] = []
        for stage in stages:
            for key in self.STAGE_ARTIFACT_KEYS.get(stage, ()):
                if key in context.artifacts:
                    context.artifacts.pop(key, None)
                    invalidated_keys.append(key)

        for key in ("prototype_acceptance", "evidence_remediation_plan", "quality_loop"):
            if key in context.artifacts:
                context.artifacts.pop(key, None)
                invalidated_keys.append(key)
        for key in tuple(context.artifacts):
            if key.startswith("verification_"):
                context.artifacts.pop(key, None)
                invalidated_keys.append(key)

        affected_stages = set(stages) | {"browser_qa", "visual_qa", "repair", "quality_loop"}
        context.completed_stages = [
            stage for stage in context.completed_stages if stage not in affected_stages
        ]
        context.save()
        self.team_runner.event_bus(context).emit(
            "flow.stages_invalidated",
            stage="quality_loop",
            data={
                "target_stage": stages[0],
                "rerun_stages": list(stages),
                "artifact_keys": invalidated_keys,
            },
        )
        return stages

    async def _run_replan_stage(
        self,
        context: RunContext,
        stage: str,
        frontend: FrontendResult,
    ) -> None:
        if stage == "research":
            await self._run_research(context)
        elif stage == "ux_ia":
            await self._run_ux_ia(context)
        elif stage == "art_direction":
            await self._run_art_direction(context)
        elif stage == "design_contract":
            await self._run_design_contract(context)
        elif stage == "design_system":
            await self._run_design_system(context)
        elif stage == "implementation_plan":
            await self._run_implementation_plan(context)
        elif stage == "visual_composition":
            await self._run_visual_composition(context)
        elif stage == "implementation":
            if frontend.generated_by == "AIFrontendBuilder":
                provider = self.team_runner.provider
                if provider is None:
                    raise RuntimeError("AI root-cause regeneration requires the active provider.")
                await self._run_ai_implementation(context, provider)
            else:
                await self._run_template_implementation(context)
        else:
            raise ValueError(f"Unsupported root-cause replan stage: {stage!r}")

    async def _regenerate_after_replan(
        self,
        context: RunContext,
        frontend: FrontendResult,
        decision: ReplanDecision,
    ) -> FrontendResult:
        target_stage = self._canonical_replan_stage(decision.target_stage)
        if target_stage is None:
            raise RuntimeError(
                f"Replanning policy requested unsupported stage {decision.target_stage!r}."
            )

        rerun_stages = self._invalidate_from_stage(context, target_stage)
        for index, stage in enumerate(rerun_stages):
            if index == 0:
                with self._temporary_stage_skills(stage, decision):
                    await self._run_replan_stage(context, stage, frontend)
            else:
                await self._run_replan_stage(context, stage, frontend)

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
        quality_output_dir = context.run_dir
        current = await self._execute_quality(context, frontend, quality_output_dir)
        if current.status != "passed":
            self._write(
                context,
                "quality_loop_before_replan",
                "quality-loop-before-replan.json",
                current.model_dump_json(indent=2),
            )

        while current.status != "passed":
            evidence_target = self._evidence_replan_target(current, quality_output_dir)
            remediation_path = quality_output_dir / "evidence-remediation-plan.json"
            if remediation_path.is_file():
                context.add_artifact("evidence_remediation_plan", remediation_path)

            decision = self._quality_replan_decision(
                context,
                evidence_target_stage=evidence_target,
            )
            replan_payload = {
                "schema_version": 1,
                "replan_index": self._root_replan_count + 1,
                "source": "skills_UIUX/flows/professional-website-redesign.json",
                "trigger": {
                    "signal": "GATE_FAIL",
                    "current_stage": "qa",
                    "quality_status": current.status,
                    "stop_reason": current.stop_reason,
                    "score": current.final_score,
                    "evidence_owner_stage": evidence_target,
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
                break

            self._root_replan_count += 1
            frontend = await self._regenerate_after_replan(context, frontend, decision)
            quality_output_dir = context.run_dir / f"root-replan-{self._root_replan_count:02d}"
            context.start_stage(stage)
            current = await self._execute_quality(context, frontend, quality_output_dir)
            self._write(
                context,
                f"quality_loop_replan_{self._root_replan_count}",
                f"quality-loop-replan-{self._root_replan_count:02d}.json",
                current.model_dump_json(indent=2),
            )

        final = current
        acceptance_path = quality_output_dir / "prototype-acceptance.json"
        if acceptance_path.is_file():
            context.add_artifact("prototype_acceptance", acceptance_path)

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
