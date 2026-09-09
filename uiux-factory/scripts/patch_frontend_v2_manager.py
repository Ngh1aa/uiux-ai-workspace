from pathlib import Path
import re


path = Path(
    "core/manager/development_manager.py"
)

text = path.read_text(
    encoding="utf-8"
)


def insert_after_import(
    source: str,
    anchor_pattern: str,
    new_import: str,
) -> str:
    if new_import in source:
        return source

    match = re.search(
        anchor_pattern,
        source,
        flags=re.MULTILINE,
    )

    if not match:
        raise RuntimeError(
            "Could not find import anchor: "
            f"{anchor_pattern}"
        )

    end = match.end()

    return (
        source[:end]
        + "\n"
        + new_import
        + source[end:]
    )


text = insert_after_import(
    text,
    (
        r"from core\.agents\."
        r"implementation_planner "
        r"import ImplementationPlanner"
    ),
    (
        "from core.agents.visual_composer "
        "import VisualComposer"
    ),
)

text = insert_after_import(
    text,
    (
        r"from core\.contracts\."
        r"implementation_plan_schema "
        r"import ImplementationPlan"
    ),
    (
        "from core.contracts."
        "visual_composition_schema "
        "import VisualComposition"
    ),
)

if '"visual_composition",' not in text:
    text = text.replace(
        '        "implementation_plan",\n',
        (
            '        "implementation_plan",\n'
            '        "visual_composition",\n'
        ),
        1,
    )

visual_call = (
    "            await "
    "self._run_visual_composition(context)\n"
)

if visual_call not in text:
    anchor = (
        "            await "
        "self._run_implementation_plan(context)\n"
    )

    if anchor not in text:
        raise RuntimeError(
            "Implementation plan call anchor missing."
        )

    text = text.replace(
        anchor,
        anchor + visual_call,
        1,
    )

visual_method_marker = (
    "    async def _run_visual_composition(\n"
)

if visual_method_marker not in text:
    visual_method = '''
    async def _run_visual_composition(
        self,
        context: RunContext,
    ) -> None:
        stage = "visual_composition"

        print(
            "\\n[Stage] Visual Composition STARTED"
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
'''

    text = (
        text.rstrip()
        + "\n"
        + visual_method
        + "\n"
    )

implementation_start = text.find(
    "    async def _run_implementation(\n"
)

if implementation_start == -1:
    raise RuntimeError(
        "_run_implementation method not found. "
        "Run the previous FrontendEngineer patch first."
    )

next_method = text.find(
    "\n    async def ",
    implementation_start + 10,
)

if next_method == -1:
    implementation_end = len(text)
else:
    implementation_end = next_method

implementation = text[
    implementation_start:
    implementation_end
]

if "visual_composition_content" not in implementation:
    plan_assignment = '''        plan_path = Path(
            context.artifacts.get(
                "implementation_plan",
                "",
            )
        )
'''

    visual_assignment = '''
        visual_path = Path(
            context.artifacts.get(
                "visual_composition",
                "",
            )
        )
'''

    if plan_assignment not in implementation:
        raise RuntimeError(
            "Could not patch implementation plan path block."
        )

    implementation = implementation.replace(
        plan_assignment,
        plan_assignment + visual_assignment,
        1,
    )

    old_loop = '''        for input_path in (
            contract_path,
            system_path,
            plan_path,
        ):
'''

    new_loop = '''        for input_path in (
            contract_path,
            system_path,
            plan_path,
            visual_path,
        ):
'''

    if old_loop not in implementation:
        raise RuntimeError(
            "Could not patch implementation input loop."
        )

    implementation = implementation.replace(
        old_loop,
        new_loop,
        1,
    )

    payload_anchor = '''            "implementation_plan_content": (
                plan_path.read_text(
                    encoding="utf-8"
                )
            ),
'''

    visual_payload = '''            "visual_composition_content": (
                visual_path.read_text(
                    encoding="utf-8"
                )
            ),
'''

    if payload_anchor not in implementation:
        raise RuntimeError(
            "Could not patch implementation payload."
        )

    implementation = implementation.replace(
        payload_anchor,
        payload_anchor + visual_payload,
        1,
    )

    text = (
        text[:implementation_start]
        + implementation
        + text[implementation_end:]
    )

path.write_text(
    text,
    encoding="utf-8",
)

print(
    "DevelopmentManager patched for "
    "VisualComposer + FrontendEngineerV2."
)
