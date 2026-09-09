from pathlib import Path

from core.orchestration.intelligent_flow import GoalInterpreter, ProfessionalWebsiteFlow
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
        assert interpreter.interpret(goal).website_type == expected


def test_flow_routes_domain_skills_from_skills_uiux_manifest() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    profile, skills, mandatory = flow.resolve_skill_names(
        "research",
        "Tạo website bán hàng ecommerce có checkout và tìm kiếm",
    )
    assert profile.website_type == "ecommerce"
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
        goal="Create an experimental interactive microsite for an art event",
        skills_root=SKILLS,
    )
    assert selection.domain == "generic"
    assert "project-context/SKILL.md" in selection.mandatory_paths
