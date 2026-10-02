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
from core.runtime.provider_lane import (
    LEGACY_PROVIDER_LANE,
    MANAGED_COMPAT_PROVIDER_LANE,
    provider_lane_provenance,
    resolve_factory_provider_lane,
)
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
        lane_raw = context.artifacts.get("provider_lane")
        if lane_raw:
            lane_path = Path(lane_raw)
            if lane_path.is_file():
                payload["provider_lane"] = json.loads(lane_path.read_text(encoding="utf-8"))
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        context.add_artifact("flow_plan", path)

    @staticmethod
    def _validate_engine_context(engine: str, design_context: DesignContext) -> None:
        if engine not in {"template", "ai", "external"}:
            raise ValueError("Unknown generation engine.")
        if engine == "external" and design_context.brain != "external":
            raise ValueError(
                "External engine requires DesignContext.brain='external' and a target project."
            )
        if design_context.brain == "external" and engine != "external":
            raise ValueError(
                "DesignContext.brain='external' must use engine='external'; internal providers "
                "must not silently replace the declared external brain."
            )

    def _run_external_handoff(self, context: RunContext) -> Path:
        target = context.design_context.target
        if target is None:
            raise RuntimeError("External brain handoff requires a target project contract.")

        context.start_stage("external_handoff")
        payload = {
            "schema_version": "1.0.0",
            "status": "awaiting_external_implementation_and_qa",
            "brain": "external",
            "target": target.model_dump(),
            "factory_artifacts": {
                key: value
                for key, value in context.artifacts.items()
                if key
                in {
                    "research",
                    "ux_ia",
                    "art_direction",
                    "design_contract",
                    "design_system",
                    "design_tokens",
                    "implementation_plan",
                    "visual_composition",
                    "visual_brain",
                    "skill_governance",
                }
            },
            "policy": (
                "The external brain owns implementation and creative judgment in the target "
                "repository. Factory must not invoke an internal provider, generate the fixture "
                "template, or claim BrowserQA/VisualCritic PASS in this handoff run. After the "
                "external implementation is committed, run Cloud QA against the declared target "
                "repository, ref, project root, commands and routes."
            ),
        }
        path = self._write(
            context,
            "external_handoff",
            "external-handoff.json",
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        )
        context.complete_stage("external_handoff")
        context.event_bus().emit(
            "run.handoff_ready",
            data={"artifact": str(path), "target": target.repository},
        )
        context.status = "handoff_ready"
        context.active_stage = None
        context.save()
        return path

    async def run(
        self,
        goal: str,
        design_context: DesignContext | None = None,
        run_id: str | None = None,
        intelligence_only: bool = False,
        engine: str = "ai",
        runtime_preset: str = "standard",
    ) -> RunContext:
        resolved_context = design_context or DesignContext()
        self._validate_engine_context(engine, resolved_context)

        context = RunContext(
            root=self.root,
            goal=goal,
            design_context=resolved_context,
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
            lane_decision = None
            if engine == "ai":
                lane_decision = resolve_factory_provider_lane()
                if lane_decision.lane == LEGACY_PROVIDER_LANE:
                    from core.runtime.free_provider import FreeProvider

                    provider = FreeProvider.from_env(self.root)
                elif lane_decision.lane == MANAGED_COMPAT_PROVIDER_LANE:
                    from core.runtime.flow_os.factory_provider_adapter import (
                        ManagedArtifactCompletionAdapter,
                    )

                    provider = ManagedArtifactCompletionAdapter.from_env(self.root)
                else:  # defensive; resolver already fails closed on unknown values
                    raise RuntimeError(f"Unsupported provider lane: {lane_decision.lane}")

                self.team_runner.set_provider(provider)
                lane_payload = provider_lane_provenance(lane_decision)
                lane_path = self._write(
                    context,
                    "provider_lane",
                    "provider-lane.json",
                    json.dumps(lane_payload, indent=2, ensure_ascii=False) + "\n",
                )
                context.event_bus().emit(
                    "provider.lane_selected",
                    data={
                        "lane": lane_decision.lane,
                        "explicit_opt_in": lane_decision.explicit_opt_in,
                        "artifact": str(lane_path),
                    },
                )

            print(f"\n[DevelopmentManager] Run ID: {context.run_id}")
            print(f"[DevelopmentManager] Goal received: {goal}")
            print(f"[DevelopmentManager] Engine: {engine}")
            if lane_decision is not None:
                print(f"[DevelopmentManager] Provider lane: {lane_decision.lane}")
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

            if engine == "external":
                self._run_external_handoff(context)
                return context
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