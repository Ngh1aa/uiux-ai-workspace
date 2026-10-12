from __future__ import annotations

import ast
import re

import pytest

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FACTORY_ROOT = REPO_ROOT / "uiux-factory"


def test_a19_v1_quickstart_exposes_short_goal_run_resume_and_recovery() -> None:
    text = (FACTORY_ROOT / "docs" / "V1-QUICKSTART.md").read_text(encoding="utf-8")
    assert "python scripts/run_autonomous_flow.py" in text
    assert "--goal" in text
    assert "--resume-run-id" in text
    assert "--recover-snapshot" in text
    assert "prompt → audit → plan → execute → QA" in text
    assert "Do not copy a full Factory workflow into the prompt" in text


def test_a19_factory_readme_points_to_one_canonical_quickstart() -> None:
    text = (FACTORY_ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/V1-QUICKSTART.md" in text
    assert "run_autonomous_flow.py" in text


@pytest.mark.parametrize("relative", ["README.md", "uiux-factory/README.md",
    "uiux-factory/docs/V1-QUICKSTART.md", "uiux-factory/docs/FREE_BRAIN.md",
    "uiux-factory/docs/DEEPSEEK_HARNESS_RUNTIME.md"])
def test_round2_build_examples_explicitly_opt_into_write(relative):
    text = (REPO_ROOT / relative).read_text(encoding="utf-8")
    examples = [(number, line) for number, line in enumerate(text.splitlines(), 1)
                if re.search(r"\brun\.py\s+[\"']", line) and "--intelligence-only" not in line]
    assert examples, f"No native build example inspected: {relative}"
    for number, line in examples:
        assert "--authority branch_write" in line, f"Missing explicit write opt-in: {relative}:{number}: {line}"
    assert "read_only" in text and "opt-in" in text.lower(), f"Missing authority explanation: {relative}"


def test_round2_native_cli_retains_read_only_default():
    tree = ast.parse((FACTORY_ROOT / "run.py").read_text(encoding="utf-8"))
    authority_args = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                      and isinstance(node.func, ast.Attribute) and node.func.attr == "add_argument"
                      and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == "--authority"]
    assert len(authority_args) == 1
    defaults = [kw.value for kw in authority_args[0].keywords if kw.arg == "default"]
    assert len(defaults) == 1 and isinstance(defaults[0], ast.Constant) and defaults[0].value == "read_only"
