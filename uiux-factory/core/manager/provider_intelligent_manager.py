from __future__ import annotations

import json
import re
from pathlib import Path

from core.contracts.design_context_schema import DesignContext
from core.manager.intelligent_manager import IntelligentDevelopmentManager
from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.orchestration.reference_intelligence import ReferenceIntelligencePlanner
from core.orchestration.skill_governance import FlowReplanner, SkillGovernanceSnapshot
from core.runtime.harness_runtime import HarnessInspiredRuntime
from core.runtime.run_context import RunContext
from core.team.intelligent_team_runner import IntelligentTeamRunner


class ProviderIntelligentDevelopmentManager(IntelligentDevelopmentManager):
    """Intelligent manager with provider loops and a composable per-run runtime."""

    def __init__(self, root: Path):
        super().__init__(root)

        # Replace only the execution bridge; all sequencing, contracts, reference
        # intelligence and root-cause replanning continue to come from the proven
        # IntelligentDevelopmentManager implementation.
        self.team_runner = IntelligentTeamRunner(root=self.root)
        self.flow = ProfessionalWebsiteFlow(self.team_runner.skills_root)
        self.reference_planner = ReferenceIntelligencePlanner()
        self.replanner = FlowReplanner(self.flow.document)
        self.governance = SkillGovernanceSnapshot(self.team_runner.skills_root)
        self._root_replan_count = 0

        self.runtime = HarnessInspiredRuntime(self.root)
        self.team_runner.set_runtime(self.runtime)

    def _save_flow_plan(self, context: RunContext, engine: str) -> None:
        super()._save_flow_plan(context, engine)
        raw = context.artifacts.get("flow_plan")
        if not raw or not self.runtime.has_active(context):
            return
        path = Path(raw)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["runtime"] = self.runtime.snapshot(context)
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        context.add_artifact("flow_plan", path)

    async def run(
        self,
        goal: str,
        design_context: DesignContext | None = None,
        run_id: str | None = None,
        intelligence_only: bool = False,
        engine: str = "template",
        runtime_preset: str = "standard",
    ) -> RunContext:
        if engine not in {"template", "ai"}:
            raise ValueError("Unknown generation engine.")

        context = RunContext(
            root=self.root,
            goal=goal,
            design_context=design_context or DesignContext(),
            runtime_preset=runtime_preset,
        )
        if run_id:
            if not re.fullmatch(r"[a-zA-Z0-9-]{1,80}", run_id):
                raise ValueError("Invalid run ID.")
            context.run_id = run_id
        context.initialize()

        try:
            self.runtime.activate(context, runtime_preset)
            self.runtime.require(context, "skills.compose")

            provider = None
            if engine == "ai":
                from core.runtime.free_provider import FreeProvider

                provider = FreeProvider.from_env(self.root)
                self.team_runner.set_provider(provider)

            print(f"\n[DevelopmentManager] Run ID: {context.run_id}")
            print(f"[DevelopmentManager] Goal received: {goal}")
            print(f"[DevelopmentManager] Engine: {engine}")
            print(f"[DevelopmentManager] Runtime preset: {context.runtime_preset}")
            self.print_flow()

            input_path = context.run_dir / "design-context.json"
            input_path.write_text(context.design_context.model_dump_json(indent=2), encoding="utf-8")
            context.add_artifact("design_context", input_path)
            self._save_flow_plan(context, engine)

            await self._run_reference_analysis(context)
            self.runtime.require(context, "research.web")
            await self._run_research(context)
            await self._run_ux_ia(context)
            await self._run_art_direction(context)
            await self._run_design_contract(context)
            await self._run_design_system(context)

            if intelligence_only:
                context.complete()
                return context

            await self._run_implementation_plan(context)
            await self._run_visual_composition(context)

            if engine == "ai":
                await self._run_ai_implementation(context, provider)
            else:
                await self._run_template_implementation(context)

            self.runtime.require(context, "browser.qa")
            self.runtime.require(context, "visual.qa")
            await self._run_quality_loop(context)
            context.complete()
            return context
        except Exception as error:
            context.add_error(error)
            raise
        finally:
            self.runtime.deactivate(context)
