import json
from pathlib import Path

from core.agents.art_director import ArtDirector
from core.agents.design_contract_agent import DesignContractAgent
from core.agents.design_system_agent import DesignSystemAgent
from core.agents.implementation_planner import ImplementationPlanner
from core.agents.visual_composer import VisualComposer
from core.agents.frontend_engineer import FrontendEngineer
from core.agents.research_agent import ResearchAgent
from core.agents.ux_strategist import UXStrategist
from core.contracts.design_system_schema import DesignSystemContract
from core.contracts.implementation_plan_schema import ImplementationPlan
from core.contracts.visual_composition_schema import VisualComposition
from core.contracts.frontend_result_schema import FrontendResult
from core.contracts.schema import DesignContract
from core.runtime.run_context import RunContext


class DevelopmentManager:
    FLOW = [
        "research",
        "ux_ia",
        "art_direction",
        "design_contract",
        "design_system",
        "implementation_plan",
        "visual_composition",
        "implementation",
        "browser_qa",
        "visual_qa",
        "repair",
    ]

    def __init__(self, root: Path):
        self.root = root.resolve()

    def print_flow(self) -> None:
        print("\n[FlowResolver]")

        for index, stage in enumerate(
            self.FLOW,
            start=1,
        ):
            print(f"  {index}. {stage}")

    async def run(
        self,
        goal: str,
    ) -> RunContext:
        context = RunContext(
            root=self.root,
            goal=goal,
        )

        context.initialize()

        print(
            f"\n[DevelopmentManager] "
            f"Run ID: {context.run_id}"
        )

        print(
            f"[DevelopmentManager] "
            f"Goal received: {goal}"
        )

        self.print_flow()

        try:
            await self._run_research(context)
            await self._run_ux_ia(context)
            await self._run_art_direction(context)
            await self._run_design_contract(context)
            await self._run_design_system(context)
            await self._run_implementation_plan(context)
            await self._run_visual_composition(context)
            await self._run_implementation(context)

            context.complete()

            return context

        except Exception as error:
            context.add_error(error)
            raise

    async def _run_research(
        self,
        context: RunContext,
    ) -> None:
        stage = "research"

        print("\n[Stage] Research STARTED")

        context.start_stage(stage)

        agent = ResearchAgent()

        result = await agent.run(
            context.goal
        )

        if not result:
            raise RuntimeError(
                "ResearchAgent returned no result."
            )

        artifact_path = (
            context.run_dir
            / "research.md"
        )

        artifact_path.write_text(
            result.content,
            encoding="utf-8",
        )

        context.add_artifact(
            "research",
            artifact_path,
        )

        context.complete_stage(stage)

        print("[Stage] Research COMPLETED")
        print(f"[Artifact] {artifact_path}")

    async def _run_ux_ia(
        self,
        context: RunContext,
    ) -> None:
        stage = "ux_ia"

        print("\n[Stage] UX / IA STARTED")

        research_raw = context.artifacts.get(
            "research"
        )

        if not research_raw:
            raise RuntimeError(
                "UX/IA cannot start: "
                "research artifact missing."
            )

        research_path = Path(
            research_raw
        )

        if not research_path.exists():
            raise RuntimeError(
                f"Research artifact not found: "
                f"{research_path}"
            )

        research_content = (
            research_path.read_text(
                encoding="utf-8"
            )
        )

        context.start_stage(stage)

        instruction = (
            "## GOAL\n\n"
            + context.goal
            + "\n\n"
            + "## RESEARCH\n\n"
            + research_content
        )

        agent = UXStrategist()

        result = await agent.run(
            instruction
        )

        if not result:
            raise RuntimeError(
                "UXStrategist returned no result."
            )

        artifact_path = (
            context.run_dir
            / "ux-ia.md"
        )

        artifact_path.write_text(
            result.content,
            encoding="utf-8",
        )

        context.add_artifact(
            "ux_ia",
            artifact_path,
        )

        context.complete_stage(stage)

        print("[Stage] UX / IA COMPLETED")
        print(f"[Artifact] {artifact_path}")

    async def _run_art_direction(
        self,
        context: RunContext,
    ) -> None:
        stage = "art_direction"

        print(
            "\n[Stage] Art Direction STARTED"
        )

        research_raw = context.artifacts.get(
            "research"
        )

        ux_ia_raw = context.artifacts.get(
            "ux_ia"
        )

        if not research_raw:
            raise RuntimeError(
                "Art Direction cannot start: "
                "research artifact missing."
            )

        if not ux_ia_raw:
            raise RuntimeError(
                "Art Direction cannot start: "
                "UX / IA artifact missing."
            )

        research_path = Path(
            research_raw
        )

        ux_ia_path = Path(
            ux_ia_raw
        )

        if not research_path.exists():
            raise RuntimeError(
                f"Research artifact not found: "
                f"{research_path}"
            )

        if not ux_ia_path.exists():
            raise RuntimeError(
                f"UX / IA artifact not found: "
                f"{ux_ia_path}"
            )

        research_content = (
            research_path.read_text(
                encoding="utf-8"
            )
        )

        ux_ia_content = (
            ux_ia_path.read_text(
                encoding="utf-8"
            )
        )

        context.start_stage(stage)

        instruction = (
            "## GOAL\n\n"
            + context.goal
            + "\n\n"
            + "## RESEARCH\n\n"
            + research_content
            + "\n\n"
            + "## UX_IA\n\n"
            + ux_ia_content
        )

        agent = ArtDirector()

        result = await agent.run(
            instruction
        )

        if not result:
            raise RuntimeError(
                "ArtDirector returned no result."
            )

        artifact_path = (
            context.run_dir
            / "art-direction.md"
        )

        artifact_path.write_text(
            result.content,
            encoding="utf-8",
        )

        context.add_artifact(
            "art_direction",
            artifact_path,
        )

        context.complete_stage(stage)

        print(
            "[Stage] Art Direction COMPLETED"
        )

        print(
            f"[Artifact] {artifact_path}"
        )

    async def _run_design_contract(
        self,
        context: RunContext,
    ) -> None:
        stage = "design_contract"

        print(
            "\n[Stage] Design Contract STARTED"
        )

        required = {
            "research": context.artifacts.get(
                "research"
            ),
            "ux_ia": context.artifacts.get(
                "ux_ia"
            ),
            "art_direction": context.artifacts.get(
                "art_direction"
            ),
        }

        for name, raw_path in required.items():
            if not raw_path:
                raise RuntimeError(
                    "Design Contract cannot start: "
                    f"{name} artifact missing."
                )

        artifacts = {}

        for name, raw_path in required.items():
            path = Path(raw_path)

            if not path.exists():
                raise RuntimeError(
                    f"Artifact not found: {path}"
                )

            artifacts[name] = {
                "path": str(
                    path.resolve()
                ),
                "content": path.read_text(
                    encoding="utf-8"
                ),
            }

        context.start_stage(stage)

        payload = {
            "goal": context.goal,
            "artifacts": artifacts,
        }

        agent = DesignContractAgent()

        result = await agent.run(
            json.dumps(
                payload,
                ensure_ascii=False,
            )
        )

        if not result:
            raise RuntimeError(
                "DesignContractAgent returned no result."
            )

        contract = (
            DesignContract.model_validate_json(
                result.content
            )
        )

        artifact_path = (
            context.run_dir
            / "design-contract.json"
        )

        artifact_path.write_text(
            contract.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        context.add_artifact(
            "design_contract",
            artifact_path,
        )

        context.complete_stage(stage)

        print(
            "[Stage] Design Contract COMPLETED"
        )

        print(
            f"[Artifact] {artifact_path}"
        )

    async def _run_design_system(
        self,
        context: RunContext,
    ) -> None:
        stage = "design_system"

        print(
            "\n[Stage] Design System STARTED"
        )

        design_contract_raw = (
            context.artifacts.get(
                "design_contract"
            )
        )

        if not design_contract_raw:
            raise RuntimeError(
                "Design System cannot start: "
                "design_contract artifact missing."
            )

        design_contract_path = Path(
            design_contract_raw
        )

        if not design_contract_path.exists():
            raise RuntimeError(
                "Design Contract artifact not found: "
                f"{design_contract_path}"
            )

        design_contract_content = (
            design_contract_path.read_text(
                encoding="utf-8"
            )
        )

        context.start_stage(stage)

        payload = {
            "design_contract_path": str(
                design_contract_path.resolve()
            ),
            "design_contract_content": (
                design_contract_content
            ),
        }

        agent = DesignSystemAgent()

        result = await agent.run(
            json.dumps(
                payload,
                ensure_ascii=False,
            )
        )

        if not result:
            raise RuntimeError(
                "DesignSystemAgent returned no result."
            )

        design_system = (
            DesignSystemContract.model_validate_json(
                result.content
            )
        )

        artifact_path = (
            context.run_dir
            / "design-system.json"
        )

        artifact_path.write_text(
            design_system.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        context.add_artifact(
            "design_system",
            artifact_path,
        )

        context.complete_stage(stage)

        print(
            "[Stage] Design System COMPLETED"
        )

        print(
            f"[Artifact] {artifact_path}"
        )

    async def _run_implementation_plan(
        self,
        context: RunContext,
    ) -> None:
        stage = "implementation_plan"

        print(
            "\n[Stage] Implementation Plan STARTED"
        )

        design_contract_raw = context.artifacts.get(
            "design_contract"
        )

        design_system_raw = context.artifacts.get(
            "design_system"
        )

        if not design_contract_raw:
            raise RuntimeError(
                "Implementation Plan cannot start: "
                "design_contract artifact missing."
            )

        if not design_system_raw:
            raise RuntimeError(
                "Implementation Plan cannot start: "
                "design_system artifact missing."
            )

        design_contract_path = Path(
            design_contract_raw
        )

        design_system_path = Path(
            design_system_raw
        )

        if not design_contract_path.exists():
            raise RuntimeError(
                "Design Contract artifact not found: "
                f"{design_contract_path}"
            )

        if not design_system_path.exists():
            raise RuntimeError(
                "Design System artifact not found: "
                f"{design_system_path}"
            )

        design_contract_content = (
            design_contract_path.read_text(
                encoding="utf-8"
            )
        )

        design_system_content = (
            design_system_path.read_text(
                encoding="utf-8"
            )
        )

        context.start_stage(stage)

        payload = {
            "design_contract_path": str(
                design_contract_path.resolve()
            ),
            "design_contract_content": (
                design_contract_content
            ),
            "design_system_path": str(
                design_system_path.resolve()
            ),
            "design_system_content": (
                design_system_content
            ),
        }

        agent = ImplementationPlanner()

        result = await agent.run(
            json.dumps(
                payload,
                ensure_ascii=False,
            )
        )

        if not result:
            raise RuntimeError(
                "ImplementationPlanner returned no result."
            )

        implementation_plan = (
            ImplementationPlan.model_validate_json(
                result.content
            )
        )

        if not (
            implementation_plan.gates
            .ready_for_frontend_engineer
        ):
            raise RuntimeError(
                "Implementation Plan is not ready "
                "for FrontendEngineer."
            )

        artifact_path = (
            context.run_dir
            / "implementation-plan.json"
        )

        artifact_path.write_text(
            implementation_plan.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        context.add_artifact(
            "implementation_plan",
            artifact_path,
        )

        context.complete_stage(stage)

        print(
            "[Stage] Implementation Plan COMPLETED"
        )

        print(
            f"[Artifact] {artifact_path}"
        )

    async def _run_implementation(
        self,
        context: RunContext,
    ) -> None:
        stage = "implementation"

        print(
            "\n[Stage] Frontend Implementation STARTED"
        )

        contract_path = Path(
            context.artifacts.get(
                "design_contract",
                "",
            )
        )

        system_path = Path(
            context.artifacts.get(
                "design_system",
                "",
            )
        )

        plan_path = Path(
            context.artifacts.get(
                "implementation_plan",
                "",
            )
        )

        visual_path = Path(
            context.artifacts.get(
                "visual_composition",
                "",
            )
        )

        for input_path in (
            contract_path,
            system_path,
            plan_path,
            visual_path,
        ):
            if not input_path.exists():
                raise RuntimeError(
                    "Implementation input missing: "
                    f"{input_path}"
                )

        context.start_stage(stage)

        payload = {
            "factory_root": str(self.root),
            "design_contract_content": (
                contract_path.read_text(
                    encoding="utf-8"
                )
            ),
            "design_system_content": (
                system_path.read_text(
                    encoding="utf-8"
                )
            ),
            "implementation_plan_content": (
                plan_path.read_text(
                    encoding="utf-8"
                )
            ),
            "visual_composition_content": (
                visual_path.read_text(
                    encoding="utf-8"
                )
            ),
        }

        result = await FrontendEngineer().run(
            json.dumps(
                payload,
                ensure_ascii=False,
            )
        )

        if not result:
            raise RuntimeError(
                "FrontendEngineer returned no result."
            )

        frontend = (
            FrontendResult.model_validate_json(
                result.content
            )
        )

        if not (
            frontend.gates.workspace_guardrail_passed
            and frontend.gates.root_index_created
            and frontend.gates.next_source_created
        ):
            raise RuntimeError(
                "Frontend implementation gate failed."
            )

        artifact_path = (
            context.run_dir
            / "frontend-result.json"
        )

        artifact_path.write_text(
            frontend.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        context.add_artifact(
            "implementation",
            artifact_path,
        )

        context.complete_stage(stage)

        print(
            "[Stage] Frontend Implementation COMPLETED"
        )

        print(
            f"[Artifact] {artifact_path}"
        )

        print(
            "[Generated Project] "
            f"{frontend.project_dir}"
        )

        print(
            "[GitHub Pages Entry] "
            f"{frontend.github_pages_entry}"
        )

    async def _run_visual_composition(
        self,
        context: RunContext,
    ) -> None:
        stage = "visual_composition"

        print(
            "\n[Stage] Visual Composition STARTED"
        )

        contract_path = Path(
            context.artifacts.get(
                "design_contract",
                "",
            )
        )

        system_path = Path(
            context.artifacts.get(
                "design_system",
                "",
            )
        )

        plan_path = Path(
            context.artifacts.get(
                "implementation_plan",
                "",
            )
        )

        for input_path in (
            contract_path,
            system_path,
            plan_path,
        ):
            if not input_path.exists():
                raise RuntimeError(
                    "Visual Composition input missing: "
                    f"{input_path}"
                )

        context.start_stage(
            stage
        )

        payload = {
            "design_contract_content": (
                contract_path.read_text(
                    encoding="utf-8"
                )
            ),
            "design_system_content": (
                system_path.read_text(
                    encoding="utf-8"
                )
            ),
            "implementation_plan_content": (
                plan_path.read_text(
                    encoding="utf-8"
                )
            ),
        }

        result = await VisualComposer().run(
            json.dumps(
                payload,
                ensure_ascii=False,
            )
        )

        if not result:
            raise RuntimeError(
                "VisualComposer returned no result."
            )

        composition = (
            VisualComposition
            .model_validate_json(
                result.content
            )
        )

        if not (
            composition.gates
            .ready_for_frontend_engineer
        ):
            raise RuntimeError(
                "Visual Composition is not ready."
            )

        artifact_path = (
            context.run_dir
            / "visual-composition.json"
        )

        artifact_path.write_text(
            composition.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        context.add_artifact(
            "visual_composition",
            artifact_path,
        )

        context.complete_stage(
            stage
        )

        print(
            "[Stage] Visual Composition COMPLETED"
        )

        print(
            f"[Artifact] {artifact_path}"
        )

