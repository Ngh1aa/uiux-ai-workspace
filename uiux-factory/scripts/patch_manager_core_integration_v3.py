from __future__ import annotations

import re
import shutil
from pathlib import Path


MANAGER = Path("core/manager/development_manager.py")

TARGETS = (
    "DesignContractAgent",
    "DesignSystemAgent",
    "ImplementationPlanner",
)


def find_block_end(
    lines: list[str],
    start_index: int,
) -> int:
    """
    Find the closing line of:
        result = await agent.run(
            ...
        )

    Uses parenthesis depth instead of exact whitespace/formatting.
    """
    depth = 0
    started = False

    for index in range(
        start_index,
        len(lines),
    ):
        line = lines[index]

        if not started:
            marker = (
                "result = await agent.run("
            )

            if marker not in line:
                continue

            started = True

        # Current manager payloads are normal Python expressions.
        # Counting delimiters is intentionally simple and robust
        # against whitespace/line wrapping changes.
        depth += line.count("(")
        depth -= line.count(")")

        if (
            started
            and depth == 0
        ):
            return index

    raise RuntimeError(
        "Could not find the closing parenthesis "
        "for `result = await agent.run(...)`."
    )


def patch_target(
    lines: list[str],
    role_name: str,
) -> tuple[
    list[str],
    bool,
]:
    agent_pattern = re.compile(
        rf"^(?P<indent>\s*)agent\s*=\s*"
        rf"{re.escape(role_name)}\(\)\s*$"
    )

    for agent_index, line in enumerate(
        lines
    ):
        match = agent_pattern.match(
            line.rstrip("\r\n")
        )

        if not match:
            continue

        indent = match.group(
            "indent"
        )

        # Locate the actual direct run call after the agent declaration.
        run_index = None

        for candidate in range(
            agent_index + 1,
            min(
                len(lines),
                agent_index + 12,
            ),
        ):
            stripped = (
                lines[candidate]
                .strip()
            )

            if not stripped:
                continue

            if stripped.startswith(
                "result = await agent.run("
            ):
                run_index = candidate
                break

            # If another statement appears first, don't patch the wrong block.
            if (
                stripped.startswith(
                    (
                        "agent = ",
                        "result = ",
                        "return ",
                    )
                )
            ):
                break

        if run_index is None:
            raise RuntimeError(
                f"Found `{role_name}()` but could not find "
                "`result = await agent.run(...)` immediately after it."
            )

        end_index = find_block_end(
            lines,
            run_index,
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

        # Remove:
        #   agent = Role()
        #   blank lines in between
        #   result = await agent.run(...)
        #
        # and replace with one TeamRunner call.
        new_lines = (
            lines[:agent_index]
            + replacement
            + lines[
                end_index + 1:
            ]
        )

        return (
            new_lines,
            True,
        )

    return (
        lines,
        False,
    )


def direct_targets(
    text: str,
) -> list[str]:
    remaining = []

    for role_name in TARGETS:
        if re.search(
            rf"agent\s*=\s*"
            rf"{re.escape(role_name)}\(\)",
            text,
        ):
            remaining.append(
                role_name
            )

    return remaining


def main() -> None:
    if not MANAGER.exists():
        raise FileNotFoundError(
            "DevelopmentManager not found: "
            f"{MANAGER.resolve()}"
        )

    backup = MANAGER.with_suffix(
        ".py.before-core-integration-v3"
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

    patched = []

    for role_name in TARGETS:
        lines, changed = patch_target(
            lines,
            role_name,
        )

        if changed:
            patched.append(
                role_name
            )
            print(
                f"[PATCHED] {role_name}"
            )
        else:
            print(
                f"[SKIP] {role_name} "
                "(direct block not present)"
            )

    text = "".join(
        lines
    )

    remaining = direct_targets(
        text
    )

    MANAGER.write_text(
        text,
        encoding="utf-8",
    )

    print()
    print(
        f"[Patched This Run] {len(patched)}"
    )
    print(
        f"[Backup] {backup}"
    )
    print(
        "[Remaining Direct Targets] "
        f"{len(remaining)}"
    )

    for role_name in remaining:
        print(
            f"  - {role_name}"
        )

    # Also show any generic direct agent.run calls still present,
    # so the user can verify the Manager is fully integrated.
    direct_run_lines = []

    for line_number, line in enumerate(
        text.splitlines(),
        start=1,
    ):
        if (
            "result = await agent.run("
            in line
        ):
            direct_run_lines.append(
                line_number
            )

    print(
        "[Remaining `result = await agent.run(`] "
        f"{len(direct_run_lines)}"
    )

    for line_number in (
        direct_run_lines
    ):
        print(
            f"  - line {line_number}"
        )

    if remaining:
        raise SystemExit(2)

    print()
    print(
        "PASS: DesignContractAgent, DesignSystemAgent "
        "and ImplementationPlanner no longer bypass UIUXTeamRunner."
    )


if __name__ == "__main__":
    main()
