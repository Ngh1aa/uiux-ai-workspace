from pathlib import Path
import json

import pytest

from core.runtime.flow_os.adaptive_surface import classify_change_surface
from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.runtime.flow_os.task_context import GoalInterpreter
from core.runtime.flow_os.external_task import build_external_task_manifest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


@pytest.mark.parametrize("term", ["HTML to Figma", "HTML-to-Figma", "HTML→Figma", "html.to.design", "Figma export", "dmaya.ai/html-to-figma"])
def test_export_feature_is_inferred(term):
    profile = GoalInterpreter().interpret(f"Implement {term} for Nova with 70 screens")
    assert "html-to-figma-export" in profile.features
    assert profile.change_surface == "PRODUCT"


@pytest.mark.parametrize("goal", ["Implement 70 screens", "Triển khai 70 màn Nova", "Build multi-screen capture routes", "Audit all screens for export"])
def test_screen_inventory_does_not_shrink_to_one_page(goal):
    assert classify_change_surface(goal, "build", []) == "PRODUCT"


@pytest.mark.parametrize("goal", ["Build one screen for HTML to Figma", "Build 1 screen for Figma export", "Build one page with 70 states"])
def test_single_screen_stays_page_sized(goal):
    assert classify_change_surface(goal, "build", []) == "PAGE"


def test_export_specialist_composes_into_resolved_product_stages():
    profile, flow = ProfessionalWebsiteFlow(SKILLS).resolve("Build Nova HTML to Figma export for 70 screens using canonical renderer")
    assert profile.change_surface == "PRODUCT"
    for stage in flow.stages:
        assert "html-to-figma-export" in stage.skills
    assert (SKILLS / "html-to-figma-export" / "SKILL.md").is_file()


def test_ordinary_fintech_work_does_not_load_export_skill():
    _profile, flow = ProfessionalWebsiteFlow(SKILLS).resolve("Improve the fintech transfer amount screen")
    assert all("html-to-figma-export" not in stage.skills for stage in flow.stages)


def test_read_only_export_audit_keeps_research_and_qa_only():
    policy = json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))
    manifest = build_external_task_manifest(SKILLS, policy, "Audit existing Nova HTML to Figma export", "Ngh1aa/Nova", authority="read_only").to_dict()
    stages = manifest["resolved_flow"]["stages"]
    assert [stage["id"] for stage in stages] == ["research", "qa"]
    assert all("html-to-figma-export" in stage["skills"] for stage in stages)
