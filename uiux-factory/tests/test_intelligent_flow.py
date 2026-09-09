import json
from pathlib import Path

from core.orchestration.intelligent_flow import (
    DEFAULT_DELIVERY_POLICY_ID,
    DEFAULT_FACTORY_DELIVERY_LANE,
    GoalInterpreter,
    ProfessionalWebsiteFlow,
)
from core.skills.router import AdaptiveSkillRouter


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


def test_goal_interpreter_supports_professional_website_domains() -> None:
    interpreter = GoalInterpreter()
    cases = {
        "Tạo website bán hàng có giỏ hàng và checkout": "ecommerce",
        "Build a SaaS software platform with dashboard": "saas",
        "Thiết kế website khách sạn có đặt phòng": "hospitality",
        "Redesign website bất động sản căn hộ": "real-estate",
        "Tạo portfolio creative studio": "portfolio",
        "Website tin tức và tạp chí": "news",
    }
    for goal, expected in cases.items():
        profile = interpreter.interpret(goal)
        assert profile.website_type == expected
        assert profile.delivery_policy == DEFAULT_DELIVERY_POLICY_ID
        assert profile.delivery_lane == DEFAULT_FACTORY_DELIVERY_LANE
        assert profile.to_dict()["delivery"] == {
            "policy": "adaptive-prompt-os-v4",
            "lane": "full_prompt_os",
        }


def test_factory_default_delivery_policy_is_pinned_to_upstream_source() -> None:
    config = json.loads((ROOT / "config" / "default-website-delivery.json").read_text(encoding="utf-8"))
    assert config["policy_id"] == "adaptive-prompt-os-v4"
    assert config["factory_lane"] == "full_prompt_os"
    assert config["skills_source"] == {
        "repository": "Ngh1aa/skills_UIUX",
        "commit": "e8ed8c9212d20edb2cf4c8c0881fff34add7076e",
    }
    assert config["behavior"]["representative_first"] is True
    assert config["behavior"]["human_visual_veto"] is True
    assert config["behavior"]["production_smoke_when_deployed"] is True


def test_flow_loads_default_prompt_os_v4_policy() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    assert flow.delivery_policy_path.is_file()
    assert flow.delivery_policy["id"] == "adaptive-prompt-os-v4"
    assert [phase["id"] for phase in flow.delivery_policy["full_prompt_os"]["phases"]] == [0, 1, 2, 3, 4]
    assert flow.delivery_policy["full_prompt_os"]["representative_gate"]["requires_opened_rendered_evidence"] is True
    assert flow.delivery_policy["full_prompt_os"]["human_visual_veto"]["required_for_substantial_visual_work"] is True
    assert flow.delivery_policy["release"]["production_smoke_required_when_deployed"] is True


def test_flow_routes_domain_skills_from_skills_uiux_manifest() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    profile, skills, mandatory = flow.resolve_skill_names(
        "research",
        "Tạo website bán hàng ecommerce có checkout và tìm kiếm",
    )
    assert profile.website_type == "ecommerce"
    assert profile.delivery_policy == "adaptive-prompt-os-v4"
    assert "ecommerce-website" in skills
    assert "conversion-and-content" in skills
    assert "site-search-and-findability" in skills
    assert "project-context" in mandatory


def test_all_factory_stages_have_declarative_skill_paths() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    for stage in flow.FACTORY_TO_FLOW_STAGE:
        _profile, paths, mandatory = flow.resolve_paths(stage, "Tạo website SaaS hiện đại có dashboard")
        assert paths
        assert mandatory
        assert all((SKILLS / path).is_file() for path in paths)


def test_router_no_longer_defaults_every_unknown_goal_to_corporate() -> None:
    selection = AdaptiveSkillRouter.route(
        stage="research",
        goal="Create a distinctive interactive web experience for a new concept",
        skills_root=SKILLS,
    )
    assert selection.domain == "generic"
    assert "project-context/SKILL.md" in selection.mandatory_paths
