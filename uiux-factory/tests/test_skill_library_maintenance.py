"""Exercise Factory against its own maintenance requests, not a UI fixture."""
import json
from pathlib import Path

import pytest

from core.runtime.flow_os.external_task import build_external_task_manifest
from core.runtime.flow_os.target_truth import TargetTruthProbe

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime/runtime-policy.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("goal", [
    "Implement five skill-library upgrades and fix workflow routing defects.",
    "Nâng cấp thư viện skill UX, bổ sung kiến thức ngành và bài tập thực hành.",
    "Update SKILL.md guidance and add regression evals.",
    "Update SKILL.md guidance for iOS app permission recovery.",
])
def test_maintenance_uses_existing_governance_without_frontend_work(goal):
    packet = build_external_task_manifest(
        SKILLS, POLICY, goal, "Ngh1aa/uiux-ai-workspace",
        authority="branch_write", target_root=ROOT,
    ).to_dict()
    assert packet["resolved_flow"]["id"] == "skill-library-maintenance"
    assert packet["authority"] == "branch_write"
    skills = {s for stage in packet["stages"] for s in stage["skills"]}
    assert "skill-authoring-and-governance" in skills
    assert "frontend-implementation" not in skills
    assert not any(stage["design_workflow"]["decision_contract_required"] for stage in packet["stages"])


def test_read_only_maintenance_does_not_acquire_implementation_authority():
    packet = build_external_task_manifest(
        SKILLS, POLICY, "Review only the skill library; do not change code.",
        "Ngh1aa/uiux-ai-workspace", authority="branch_write", target_root=ROOT,
    ).to_dict()
    assert packet["resolved_flow"]["id"] == "skill-library-audit"
    assert packet["authority"] == "read_only"
    assert all(stage["agent"] != "implementation" for stage in packet["stages"])


@pytest.mark.parametrize("goal", [
    "Build a website for teaching career skills with a course catalog.",
    "Fix the dashboard using SKILL.md as a reference.",
    "Improve the Home page with https://example.com/design/SKILL.md as reference.",
    "Use SKILL.md to fix the checkout form.",
    "Sửa giao diện theo SKILL.md, giữ brand.",
    "Fix the header; do not update SKILL.md.",
])
def test_designing_a_skills_website_is_not_library_maintenance(goal):
    packet = build_external_task_manifest(
        SKILLS, POLICY, goal,
        "example/learning", authority="branch_write",
    ).to_dict()
    assert not packet["resolved_flow"]["id"].startswith("skill-library")


@pytest.mark.parametrize("readme,expected", [
    ("# Build toolkit\n\nA developer tool.\n\n## CI\nRun the foundation job.\n", "generic"),
    ("# Heritage\n\n## Overview\nA museum and artwork discovery experience.\n\n## CI\nRun foundation checks.\n", "art-culture"),
    ("# Helping Hands\n\nA nonprofit charity supporting local families.\n", "nonprofit"),
])
def test_readme_fallback_uses_identity_not_operating_instructions(tmp_path, readme, expected):
    (tmp_path / "README.md").write_text(readme, encoding="utf-8")
    fields = TargetTruthProbe(tmp_path).probe().fields
    actual = fields.get("domain") if expected == "art-culture" else fields.get("website_type", "generic")
    assert actual == expected
