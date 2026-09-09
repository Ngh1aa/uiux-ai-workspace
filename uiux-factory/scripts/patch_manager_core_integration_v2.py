from __future__ import annotations

import re
import shutil
from pathlib import Path


path = Path("core/manager/development_manager.py")

if not path.exists():
    raise FileNotFoundError(
        f"DevelopmentManager not found: {path.resolve()}"
    )

backup = path.with_suffix(
    ".py.before-core-integration-v2"
)

if not backup.exists():
    shutil.copy2(path, backup)

text = path.read_text(
    encoding="utf-8",
)

targets = {
    "DesignContractAgent",
    "DesignSystemAgent",
    "ImplementationPlanner",
}

replacements = 0

for role in sorted(targets):
    pattern_text = (
        r"(?P<indent>^[ \t]*)"
        + r"agent[ \t]*=[ \t]*"
        + re.escape(role)
        + r"\(\)[ \t]*\n"
        + r"(?P=indent)"
        + r"result[ \t]*=[ \t]*await[ \t]+agent\.run\("
        + r"[ \t]*\n"
        + r"(?P=indent)[ \t]+json\.dumps\("
        + r"[ \t]*\n"
        + r"(?P=indent)[ \t]+payload,[ \t]*\n"
        + r"(?P=indent)[ \t]+ensure_ascii=False,[ \t]*\n"
        + r"(?P=indent)[ \t]*\)[ \t]*\n"
        + r"(?P=indent)\)"
    )

    pattern = re.compile(
        pattern_text,
        flags=re.MULTILINE,
    )

    def repl(match: re.Match) -> str:
        global replacements

        indent = match.group("indent")
        replacements += 1

        return (
            f"{indent}result = await self.team_runner.run_role(\n"
            f"{indent}    role_class={role},\n"
            f"{indent}    stage=stage,\n"
            f"{indent}    instruction=json.dumps(\n"
            f"{indent}        payload,\n"
            f"{indent}        ensure_ascii=False,\n"
            f"{indent}    ),\n"
            f"{indent}    context=context,\n"
            f"{indent})"
        )

    text, count = pattern.subn(
        repl,
        text,
        count=1,
    )

    if count == 0:
        print(
            f"[WARN] No exact block matched for {role}"
        )
    else:
        print(
            f"[PATCHED] {role}"
        )

path.write_text(
    text,
    encoding="utf-8",
)

print()
print(
    f"[Total Replacements] {replacements}"
)
print(
    f"[Backup] {backup}"
)

remaining = []

for role in sorted(targets):
    if re.search(
        rf"agent\s*=\s*{role}\(\)",
        text,
    ):
        remaining.append(
            role
        )

print(
    f"[Remaining Direct Targets] {len(remaining)}"
)

for role in remaining:
    print(
        f"  - {role}"
    )

if remaining:
    raise SystemExit(2)

print(
    "PASS: targeted direct agent.run blocks "
    "now use UIUXTeamRunner."
)
