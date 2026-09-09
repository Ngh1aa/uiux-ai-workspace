from pathlib import Path

path = Path(
    "core/manager/development_manager.py"
)

text = path.read_text(
    encoding="utf-8"
)

import_agent = (
    "from core.agents.frontend_engineer import FrontendEngineer\n"
)

import_schema = (
    "from core.contracts.frontend_result_schema import FrontendResult\n"
)

if import_agent not in text:
    anchor = (
        "from core.agents.implementation_planner "
        "import ImplementationPlanner\n"
    )
    text = text.replace(
        anchor,
        anchor + import_agent,
    )

if import_schema not in text:
    anchor = (
        "from core.contracts.implementation_plan_schema "
        "import ImplementationPlan\n"
    )
    text = text.replace(
        anchor,
        anchor + import_schema,
    )

call = (
    "            await self._run_implementation(context)\n"
)

if call not in text:
    anchor = (
        "            await self._run_implementation_plan(context)\n"
    )
    text = text.replace(
        anchor,
        anchor + call,
    )

method_marker = (
    "    async def _run_implementation(\n"
)

if method_marker not in text:
    method = r'''
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

        for input_path in (
            contract_path,
            system_path,
            plan_path,
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
'''

    text = text.rstrip() + "\n" + method + "\n"

path.write_text(
    text,
    encoding="utf-8"
)

print(
    "DevelopmentManager patched for FrontendEngineer."
)
