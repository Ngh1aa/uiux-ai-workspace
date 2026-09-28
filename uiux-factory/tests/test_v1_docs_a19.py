from __future__ import annotations

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
