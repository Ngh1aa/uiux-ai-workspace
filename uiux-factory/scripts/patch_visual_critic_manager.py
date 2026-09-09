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
        r"browser_qa_agent "
        r"import BrowserQAAgent"
    ),
    (
        "from core.agents.visual_critic "
        "import VisualCritic"
    ),
)

text = insert_import(
    text,
    (
        r"from core\.contracts\."
        r"browser_qa_schema "
        r"import BrowserQAResult"
    ),
    (
        "from core.contracts.visual_critic_schema "
        "import VisualCriticResult"
    ),
)

visual_call = (
    "            await "
    "self._run_visual_qa(context)\n"
)

if visual_call not in text:
    browser_call = (
        "            await "
        "self._run_browser_qa(context)\n"
    )

    if browser_call not in text:
        raise RuntimeError(
            "Browser QA call not found."
        )

    text = text.replace(
        browser_call,
        browser_call + visual_call,
        1,
    )

marker = (
    "    async def _run_visual_qa(\n"
)

if marker not in text:
    method = """
    async def _run_visual_qa(
        self,
        context: RunContext,
    ) -> None:
        stage = "visual_qa"

        print(
            "\\n[Stage] Visual Critic STARTED"
        )

        browser_report_path = Path(
            context.artifacts.get(
                "browser_qa",
                "",
            )
        )

        if not browser_report_path.exists():
            raise RuntimeError(
                "VisualCritic cannot start: "
                "browser-report artifact missing."
            )

        context.start_stage(stage)

        result = await VisualCritic().run(
            json.dumps(
                {
                    "browser_report_path": str(
                        browser_report_path
                    )
                },
                ensure_ascii=False,
            )
        )

        if not result:
            raise RuntimeError(
                "VisualCritic returned no result."
            )

        critic = VisualCriticResult.model_validate_json(
            result.content
        )

        artifact_path = (
            context.run_dir
            / "visual-critic.json"
        )

        artifact_path.write_text(
            critic.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        context.add_artifact(
            "visual_qa",
            artifact_path,
        )

        context.complete_stage(stage)

        print(
            "[Stage] Visual Critic COMPLETED"
        )

        print(
            f"[Overall Score] {critic.score.overall}"
        )

        print(
            f"[Issues] {len(critic.issues)}"
        )

        print(
            "[Ready for RepairAgent] "
            f"{critic.gates.ready_for_repair_agent}"
        )

        print(
            f"[Artifact] {artifact_path}"
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
    "DevelopmentManager patched for VisualCritic."
)
