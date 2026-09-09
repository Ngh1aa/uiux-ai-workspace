from __future__ import annotations

import re
import shutil
from pathlib import Path


path = Path("core/manager/development_manager.py")

if not path.exists():
    raise FileNotFoundError(
        f"DevelopmentManager not found: {path.resolve()}"
    )

backup = path.with_suffix(".py.before-core-integration-v1")

if not backup.exists():
    shutil.copy2(path, backup)

text = path.read_text(encoding="utf-8")

import_line = "from core.team.team_runner import UIUXTeamRunner"

if import_line not in text:
    imports = list(
        re.finditer(
            r"^(?:from|import)\s+.+$",
            text,
            flags=re.MULTILINE,
        )
    )

    if not imports:
        raise RuntimeError("Could not locate manager imports.")

    last = imports[-1]
    text = (
        text[: last.end()]
        + "\n"
        + import_line
        + text[last.end() :]
    )

init_anchor = "        self.root = root.resolve()"
runner_line = "        self.team_runner = UIUXTeamRunner(root=self.root)"

if runner_line not in text:
    if init_anchor not in text:
        raise RuntimeError(
            "Could not find DevelopmentManager __init__ root assignment."
        )

    text = text.replace(
        init_anchor,
        init_anchor + "\n" + runner_line,
        1,
    )

pattern = re.compile(
    r"(?P<indent>        )"
    r"agent = (?P<role>[A-Za-z_][A-Za-z0-9_]*)\(\)"
    r"\s*\n\s*"
    r"result = await agent\.run\("
    r"\s*(?P<instruction>[A-Za-z_][A-Za-z0-9_.]*)\s*"
    r"\)",
    flags=re.MULTILINE,
)

replacements = 0


def replace_agent_call(match: re.Match) -> str:
    global replacements
    replacements += 1

    role = match.group("role")
    instruction = match.group("instruction")

    return (
        "        result = await self.team_runner.run_role(\n"
        f"            role_class={role},\n"
        "            stage=stage,\n"
        f"            instruction={instruction},\n"
        "            context=context,\n"
        "        )"
    )


text = pattern.sub(replace_agent_call, text)

if replacements == 0 and "self.team_runner.run_role(" not in text:
    raise RuntimeError(
        "No direct agent.run blocks matched. "
        "The current DevelopmentManager shape differs from this patch."
    )

path.write_text(text, encoding="utf-8")

print("DevelopmentManager core integration patch complete.")
print(f"[Direct Agent Calls Replaced] {replacements}")
print(f"[Backup] {backup}")
print("[Runtime] MetaGPT Team + real skills_UIUX execution context")
