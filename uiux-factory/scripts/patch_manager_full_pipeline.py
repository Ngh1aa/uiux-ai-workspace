from __future__ import annotations

import re
import shutil
from pathlib import Path


MANAGER = Path(
    "core/manager/development_manager.py"
)


def block_end(
    lines: list[str],
    start_index: int,
) -> int:
    depth = 0

    for index in range(
        start_index,
        len(lines),
    ):
        line = lines[index]
        depth += line.count("(")
        depth -= line.count(")")

        if depth == 0:
            return index

    raise RuntimeError(
        "Could not locate call block end."
    )


def replace_direct_role_call(
    lines: list[str],
    role_name: str,
) -> tuple[list[str], bool]:
    marker = (
        f"result = await "
        f"{role_name}().run("
    )

    for index, line in enumerate(
        lines
    ):
        if marker not in line:
            continue

        indent = (
            line[
                :len(line)
                - len(
                    line.lstrip()
                )
            ]
        )

        end = block_end(
            lines,
            index,
        )

        replacement = [
            (
                f"{indent}result = await "
                "self.team_runner.run_role(\n"
            ),
            (
                f"{indent}    "
                f"role_class={role_name},\n"
            ),
            (
                f"{indent}    "
                "stage=stage,\n"
            ),
            (
                f"{indent}    "
                "instruction=json.dumps(\n"
            ),
            (
                f"{indent}        "
                "payload,\n"
            ),
            (
                f"{indent}        "
                "ensure_ascii=False,\n"
            ),
            (
                f"{indent}    "
                "),\n"
            ),
            (
                f"{indent}    "
                "context=context,\n"
            ),
            (
                f"{indent}"
                ")\n"
            ),
        ]

        return (
            lines[:index]
            + replacement
            + lines[
                end + 1:
            ],
            True,
        )

    return (
        lines,
        False,
    )


def insert_quality_call(
    text: str,
) -> tuple[str, bool]:
    call = (
        "            await "
        "self._run_quality_loop(context)"
    )

    if call in text:
        return (
            text,
            False,
        )

    pattern = re.compile(
        r"^(?P<indent>\s{12})"
        r"await self\._run_implementation"
        r"\(context\)\s*$",
        flags=re.MULTILINE,
    )

    match = pattern.search(
        text
    )

    if not match:
        raise RuntimeError(
            "Could not find main run() call to "
            "_run_implementation(context)."
        )

    insertion = (
        match.group(0)
        + "\n"
        + call
    )

    return (
        text[:match.start()]
        + insertion
        + text[match.end():],
        True,
    )


QUALITY_METHOD = r'''
    async def _run_quality_loop(
        self,
        context: RunContext,
    ) -> None:
        from pathlib import Path

        from core.contracts.frontend_result_schema import (
            FrontendResult,
        )
        from core.orchestration.quality_loop import (
            QualityLoopRunner,
        )

        stage = "quality_loop"

        print(
            "\n[Stage] Quality Loop STARTED"
        )

        frontend_result_path = Path(
            context.artifacts.get(
                "implementation",
                "",
            )
        )

        if not frontend_result_path.exists():
            raise RuntimeError(
                "Quality loop cannot start: "
                "frontend-result artifact missing."
            )

        frontend = (
            FrontendResult
            .model_validate_json(
                frontend_result_path
                .read_text(
                    encoding="utf-8"
                )
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

        context.start_stage(
            stage
        )

        runner = QualityLoopRunner(
            team_runner=(
                self.team_runner
            ),
            run_context=context,
            max_iterations=3,
            min_score_improvement=1,
        )

        result = await runner.run(
            project_dir=project_dir,
            project_slug=(
                frontend.project_slug
            ),
            output_dir=(
                context.run_dir
            ),
        )

        artifact_path = (
            context.run_dir
            / "quality-loop.json"
        )

        artifact_path.write_text(
            result.model_dump_json(
                indent=2
            ),
            encoding="utf-8",
        )

        context.add_artifact(
            "quality_loop",
            artifact_path,
        )

        if result.status == "passed":
            context.complete_stage(
                stage
            )

            print(
                "[Stage] Quality Loop COMPLETED"
            )
            print(
                f"[Quality Status] "
                f"{result.status}"
            )
            print(
                f"[Final Score] "
                f"{result.final_score}"
            )
            print(
                f"[Iterations] "
                f"{len(result.iterations)}"
            )
            print(
                f"[Artifact] "
                f"{artifact_path}"
            )

            return

        raise RuntimeError(
            "Quality loop stopped without PASS: "
            f"status={result.status}; "
            f"reason={result.stop_reason}; "
            f"score={result.final_score}; "
            f"artifact={artifact_path}"
        )
'''


def main() -> None:
    if not MANAGER.exists():
        raise FileNotFoundError(
            "DevelopmentManager not found: "
            f"{MANAGER.resolve()}"
        )

    backup = MANAGER.with_suffix(
        ".py.before-full-pipeline-v1"
    )

    if not backup.exists():
        shutil.copy2(
            MANAGER,
            backup,
        )

    lines = MANAGER.read_text(
        encoding="utf-8",
    ).splitlines(
        keepends=True
    )

    patched_roles = []

    for role_name in (
        "VisualComposer",
        "FrontendEngineer",
    ):
        lines, changed = (
            replace_direct_role_call(
                lines,
                role_name,
            )
        )

        if changed:
            patched_roles.append(
                role_name
            )
            print(
                f"[PATCHED] {role_name}"
            )
        else:
            print(
                f"[SKIP] {role_name} "
                "(already integrated or block absent)"
            )

    text = "".join(
        lines
    )

    text, inserted_call = (
        insert_quality_call(
            text
        )
    )

    print(
        "[Quality Call] "
        + (
            "INSERTED"
            if inserted_call
            else "ALREADY PRESENT"
        )
    )

    if (
        "    async def _run_quality_loop("
        not in text
    ):
        text = (
            text.rstrip()
            + "\n"
            + QUALITY_METHOD
            + "\n"
        )

        print(
            "[Quality Method] INSERTED"
        )
    else:
        print(
            "[Quality Method] ALREADY PRESENT"
        )

    MANAGER.write_text(
        text,
        encoding="utf-8",
    )

    direct_remaining = []

    for role_name in (
        "VisualComposer",
        "FrontendEngineer",
    ):
        if (
            f"{role_name}().run("
            in text
        ):
            direct_remaining.append(
                role_name
            )

    has_quality_call = (
        "await self._run_quality_loop(context)"
        in text
    )

    has_quality_method = (
        "async def _run_quality_loop("
        in text
    )

    print()
    print(
        f"[Backup] {backup}"
    )
    print(
        "[Remaining Direct Visual/Frontend] "
        f"{len(direct_remaining)}"
    )
    print(
        "[Quality Loop Call Present] "
        f"{has_quality_call}"
    )
    print(
        "[Quality Loop Method Present] "
        f"{has_quality_method}"
    )

    for role_name in (
        direct_remaining
    ):
        print(
            f"  - {role_name}"
        )

    if (
        direct_remaining
        or not has_quality_call
        or not has_quality_method
    ):
        raise SystemExit(2)

    print()
    print(
        "PASS: visual composition, implementation and "
        "quality loop are connected to the integrated runtime."
    )


if __name__ == "__main__":
    main()
