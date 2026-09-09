from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from shutil import copy2

from core.contracts.creative_review_schema import CreativeDirective
from core.contracts.design_context_schema import DesignContext
from core.contracts.implementation_plan_schema import ImplementationPlan
from core.contracts.visual_composition_schema import VisualComposition
from core.manager.visual_brain_manager import VisualBrainDevelopmentManager
from core.orchestration.creative_revision_policy import (
    context_with_review,
    inject_review_constraints,
    retarget_slug,
)
from core.runtime.run_context import RunContext


class CreativeDirectorDevelopmentManager(VisualBrainDevelopmentManager):
    """Visual Brain manager with bounded external creative-review revisions.

    A revision never mutates the source run. It creates a new run, rehydrates
    accepted upstream artifacts, invalidates from the earliest review owner and
    executes the canonical downstream pipeline and quality loop again.
    """

    REVISION_STAGES = (
        "ux_ia",
        "art_direction",
        "design_contract",
        "design_system",
        "implementation_plan",
        "visual_composition",
        "implementation",
    )

    COPY_ARTIFACTS = {
        "reference_analysis": (("reference_analysis", "reference-dna.json"),),
        "research": (("research", "research.md"),),
        "ux_ia": (("ux_ia", "ux-ia.md"),),
        "art_direction": (("art_direction", "art-direction.md"),),
        "design_contract": (("design_contract", "design-contract.json"),),
        "design_system": (
            ("design_system", "design-system.json"),
            ("design_document", "DESIGN.md"),
            ("design_tokens", "tokens.css"),
        ),
        "implementation_plan": (("implementation_plan", "implementation-plan.json"),),
        "visual_composition": (
            ("visual_composition", "visual-composition.json"),
            ("visual_brain", "visual-brain.json"),
        ),
    }

    def __init__(self, root: Path):
        super().__init__(root)
        self.creative_directive: CreativeDirective | None = None

    @staticmethod
    def _read_json(path: Path) -> dict:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"Expected JSON object: {path}")
        return payload

    def _source_run(self, source_run_id: str) -> tuple[Path, dict]:
        source_dir = (self.root / "runs" / source_run_id).resolve()
        runs_root = (self.root / "runs").resolve()
        if not source_dir.is_relative_to(runs_root):
            raise ValueError("Invalid source run path.")
        state = source_dir / "run.json"
        if not state.is_file():
            raise FileNotFoundError(f"Source run not found: {source_run_id}")
        summary = self._read_json(state)
        if summary.get("status") != "completed":
            raise RuntimeError("Creative review revisions require a completed source run.")
        return source_dir, summary

    def _copy_stage(self, source_dir: Path, context: RunContext, stage: str) -> None:
        specs = self.COPY_ARTIFACTS.get(stage, ())
        for key, filename in specs:
            source = source_dir / filename
            if not source.is_file():
                raise RuntimeError(
                    f"Cannot resume after {stage}: source artifact is missing: {filename}"
                )
            target = context.run_dir / filename
            copy2(source, target)
            context.add_artifact(key, target)
        context.complete_stage(stage)

    def _retarget_copied_project(self, context: RunContext, source_run_id: str) -> None:
        raw_plan = context.artifacts.get("implementation_plan")
        if raw_plan:
            path = Path(raw_plan)
            plan = ImplementationPlan.model_validate_json(path.read_text(encoding="utf-8"))
            plan.project_slug = retarget_slug(
                plan.project_slug,
                source_run_id,
                context.run_id,
            )
            path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
            context.add_artifact("implementation_plan", path)

        raw_visual = context.artifacts.get("visual_composition")
        if raw_visual:
            path = Path(raw_visual)
            visual = VisualComposition.model_validate_json(path.read_text(encoding="utf-8"))
            visual.project_slug = retarget_slug(
                visual.project_slug,
                source_run_id,
                context.run_id,
            )
            path.write_text(visual.model_dump_json(indent=2), encoding="utf-8")
            context.add_artifact("visual_composition", path)

    @contextmanager
    def _creative_stage_skills(self, stage: str):
        directive = self.creative_directive
        extras = tuple(directive.routed_skills(stage)) if directive else ()
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
                "Creative directive references missing skills: " + ", ".join(missing)
            )

        mapping = self.flow.EXTRA_BY_FACTORY_STAGE
        previous = tuple(mapping.get(stage, ()))
        mapping[stage] = tuple(dict.fromkeys(previous + extras))
        try:
            yield
        finally:
            mapping[stage] = previous

    async def _run_revision_stage(
        self,
        context: RunContext,
        stage: str,
        engine: str,
        provider,
    ) -> None:
        with self._creative_stage_skills(stage):
            if stage == "ux_ia":
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
                if engine == "ai":
                    await self._run_ai_implementation(context, provider)
                else:
                    await self._run_template_implementation(context)
            else:
                raise ValueError(f"Unsupported creative revision stage: {stage}")

    async def run_revision(
        self,
        *,
        source_run_id: str,
        directive: CreativeDirective,
        run_id: str,
        engine: str,
    ) -> RunContext:
        if directive.source_run_id != source_run_id:
            raise ValueError(
                "Creative directive source_run_id does not match the requested source run."
            )
        target = directive.earliest_owner()
        if directive.status == "approved" or target is None:
            raise ValueError("Approved creative reviews do not require a revision run.")
        if target not in self.REVISION_STAGES:
            raise ValueError(f"Unsupported creative revision owner: {target}")

        source_dir, summary = self._source_run(source_run_id)
        source_goal = str(summary.get("goal", "")).strip()
        if not source_goal:
            raise RuntimeError("Source run is missing its product goal.")

        source_context_path = source_dir / "design-context.json"
        source_context = (
            DesignContext.model_validate_json(
                source_context_path.read_text(encoding="utf-8")
            )
            if source_context_path.is_file()
            else DesignContext()
        )
        design_context = context_with_review(source_context, directive)
        review_goal = source_goal + "\n\n" + directive.as_prompt_block()

        context = RunContext(
            root=self.root,
            goal=review_goal,
            design_context=design_context,
        )
        context.run_id = run_id
        context.initialize()
        self.creative_directive = directive

        provider = None
        if engine == "ai":
            from core.runtime.free_provider import FreeProvider

            provider = FreeProvider.from_env(self.root)
            self.team_runner.set_provider(provider)

        try:
            context_path = context.run_dir / "design-context.json"
            context_path.write_text(
                design_context.model_dump_json(indent=2),
                encoding="utf-8",
            )
            context.add_artifact("design_context", context_path)
            self._save_flow_plan(context, engine)
            self._save_governance_snapshot(context)

            directive_path = context.run_dir / "creative-directive.json"
            directive_path.write_text(
                directive.model_dump_json(indent=2),
                encoding="utf-8",
            )
            context.add_artifact("creative_directive", directive_path)

            provenance = {
                "schema_version": "1.0.0",
                "source_run_id": source_run_id,
                "revision_run_id": context.run_id,
                "earliest_invalidated_stage": target,
                "engine": engine,
                "policy": (
                    "Preserve accepted upstream evidence; invalidate from the earliest "
                    "creative-review owner; never mutate the source run; always rerun "
                    "rendered quality gates."
                ),
            }
            provenance_path = context.run_dir / "creative-revision.json"
            provenance_path.write_text(
                json.dumps(provenance, indent=2),
                encoding="utf-8",
            )
            context.add_artifact("creative_revision", provenance_path)

            canonical_before_target = (
                "reference_analysis",
                "research",
                "ux_ia",
                "art_direction",
                "design_contract",
                "design_system",
                "implementation_plan",
                "visual_composition",
            )
            target_index = (
                canonical_before_target.index(target)
                if target in canonical_before_target
                else len(canonical_before_target)
            )
            for stage in canonical_before_target[:target_index]:
                self._copy_stage(source_dir, context, stage)

            self._retarget_copied_project(context, source_run_id)
            inject_review_constraints(context, directive, target)

            start = self.REVISION_STAGES.index(target)
            for stage in self.REVISION_STAGES[start:]:
                await self._run_revision_stage(context, stage, engine, provider)

            await self._run_quality_loop(context)
            context.complete()
            return context
        except Exception as error:
            context.add_error(error)
            raise
        finally:
            self.creative_directive = None
