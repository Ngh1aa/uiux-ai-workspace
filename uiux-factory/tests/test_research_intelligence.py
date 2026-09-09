from pathlib import Path

from core.orchestration.intelligent_flow import GoalInterpreter, ProfessionalWebsiteFlow
from core.orchestration.reference_intelligence import ReferenceIntelligencePlanner
from core.research.domain_intelligence import DomainInterpreter
from core.research.live_web_research import LiveWebResearch


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


def test_domain_interpreter_detects_vertical_below_website_type() -> None:
    goal_interpreter = GoalInterpreter()
    domain_interpreter = DomainInterpreter()
    cases = {
        "Luxury perfume ecommerce marketplace": ("ecommerce", "luxury-fragrance"),
        "Fashion ecommerce store for streetwear": ("ecommerce", "fashion"),
        "Electronics shop for laptops and smartphones": ("ecommerce", "electronics"),
        "University admissions website": ("education", "higher-education"),
        "Luxury resort booking website": ("hospitality", "hotel-resort"),
    }
    for goal, expected in cases.items():
        goal_profile = goal_interpreter.interpret(goal)
        domain = domain_interpreter.interpret(goal, goal_profile.website_type)
        assert (domain.website_type, domain.vertical) == expected


def test_reference_planner_prefers_vertical_finalists_and_caps_at_four() -> None:
    plan = ReferenceIntelligencePlanner().plan(
        goal="Redesign a luxury perfume ecommerce marketplace",
        user_urls=[],
        target_reference_count=99,
    )
    assert plan.website_type == "ecommerce"
    assert plan.vertical == "luxury-fragrance"
    assert plan.target_reference_count == 4
    assert len(plan.selected) == 4
    assert all(item.domain == "luxury-fragrance" for item in plan.selected)
    assert any("diptyque" in item.url.lower() for item in plan.selected)


def test_live_research_builds_three_query_families_from_vertical() -> None:
    queries = LiveWebResearch.build_query_families(
        website_type="ecommerce",
        vertical="luxury-fragrance",
    )
    assert set(queries) == {
        "industry-reality",
        "page-role-task",
        "visual-art-direction",
    }
    assert all(queries.values())
    flattened = " ".join(
        query
        for family in queries.values()
        for query in family
    ).lower()
    assert "luxury fragrance" in flattened
    assert "product listing" in flattened
    assert "product detail" in flattened


def test_live_research_is_truthfully_disabled_without_api_key() -> None:
    researcher = LiveWebResearch(api_key="")
    assert researcher.enabled is False
    assert researcher.search("luxury fragrance ecommerce") == []


def test_prototype_modes_route_visual_experience_skill() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    for stage in (
        "research",
        "art_direction",
        "visual_composition",
        "implementation",
        "visual_qa",
    ):
        profile, skills, _mandatory = flow.resolve_skill_names(
            stage,
            "Create a visual prototype for a luxury perfume ecommerce marketplace",
        )
        assert profile.mode == "visual-prototype"
        assert "prototype-visual-experience-qa" in skills
