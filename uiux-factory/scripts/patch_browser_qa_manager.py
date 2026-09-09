from pathlib import Path
import re


path = Path(
    "core/manager/development_manager.py"
)

text = path.read_text(
    encoding="utf-8",
)


def insert_import(
    source: str,
    anchor_regex: str,
    new_import: str,
) -> str:
    if new_import in source:
        return source

    match = re.search(
        anchor_regex,
        source,
        flags=re.MULTILINE,
    )

    if not match:
        raise RuntimeError(
            "Could not find import anchor: "
            f"{anchor_regex}"
        )

    end = match.end()

    return (
        source[:end]
        + "\n"
        + new_import
        + source[end:]
    )


text = insert_import(
    text,
    (
        r"from core\.agents\."
        r"frontend_engineer "
        r"import FrontendEngineer"
    ),
    (
        "from core.agents.browser_qa_agent "
        "import BrowserQAAgent"
    ),
)

text = insert_import(
    text,
    (
        r"from core\.contracts\."
        r"frontend_result_schema "
        r"import FrontendResult"
    ),
    (
        "from core.contracts.browser_qa_schema "
        "import BrowserQAResult"
    ),
)

browser_call = (
    "            await "
    "self._run_browser_qa(context)\n"
)

if browser_call not in text:
    implementation_call = (
        "            await "
        "self._run_implementation(context)\n"
    )

    if implementation_call not in text:
        raise RuntimeError(
            "Could not find implementation call."
        )

    text = text.replace(
        implementation_call,
        implementation_call + browser_call,
        1,
    )

method_marker = (
    "    async def _run_browser_qa(\n"
)

if method_marker not in text:
    method = """
    async def _run_browser_qa(
        self,
        context: RunContext,
    ) -> None:
        stage = "browser_qa"

        print(
            "\\n[Stage] Browser QA STARTED"
        )

        frontend_result_path = Path(
            context.artifacts.get(
                "implementation",
                "",
            )
        )

        if not frontend_result_path.exists():
            raise RuntimeError(
                "Browser QA cannot start: "
                "frontend-result artifact missing."
            )

        frontend = FrontendResult.model_validate_json(
            frontend_result_path.read_text(
                encoding="utf-8"
            )
        )

        project_dir = Path(
            frontend.project_dir
        )

        if not project_dir.exists():
            raise RuntimeError(
                "Generated project missing: "
                f"{project_dir}"
            )

        context.start_stage(stage)

        payload = {
            "project_dir": str(project_dir),
            "project_slug": frontend.project_slug,
            "output_dir": str(context.run_dir),
        }

        result = await BrowserQAAgent().run(
            json.dumps(
                payload,
                ensure_ascii=False,
            )
        )

        if not result:
            raise RuntimeError(
                "BrowserQAAgent returned no result."
            )

        qa = BrowserQAResult.model_validate_json(
            result.content
        )

        artifact_path = (
            context.run_dir
            / "browser-report.json"
        )

        artifact_path.write_text(
            qa.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        context.add_artifact(
            "browser_qa",
            artifact_path,
        )

        if not qa.gates.ready_for_visual_critic:
            print(
                "[Stage] Browser QA PARTIAL"
            )
            print(
                "[Browser QA] Evidence captured, "
                "but runtime/layout issues remain."
            )
        else:
            print(
                "[Stage] Browser QA COMPLETED"
            )

        context.complete_stage(stage)

        print(
            f"[Artifact] {artifact_path}"
        )

        print(
            "[Screenshots] "
            f"{qa.summary.get('screenshots', 0)}"
        )

        print(
            "[Ready for VisualCritic] "
            f"{qa.gates.ready_for_visual_critic}"
        )
"""

    text = (
        text.rstrip()
        + "\n"
        + method
        + "\n"
    )

path.write_text(
    text,
    encoding="utf-8",
)

print(
    "DevelopmentManager patched for BrowserQAAgent."
)
