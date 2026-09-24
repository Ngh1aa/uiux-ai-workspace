from pathlib import Path

from core.orchestration.intelligent_flow import (
    ANTHROPIC_FRONTEND_DESIGN,
    ANTHROPIC_SKILL_CREATOR,
    ANTHROPIC_WEBAPP_TESTING,
    ANTHROPIC_WEB_ARTIFACTS,
    ProfessionalWebsiteFlow,
)
from core.skills.loader import SkillLoader


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


def test_pinned_anthropic_resources_are_present() -> None:
    required = [
        SKILLS / ANTHROPIC_FRONTEND_DESIGN / "SKILL.md",
        SKILLS / ANTHROPIC_FRONTEND_DESIGN / "LICENSE.txt",
        SKILLS / ANTHROPIC_WEBAPP_TESTING / "SKILL.md",
        SKILLS / ANTHROPIC_WEBAPP_TESTING / "LICENSE.txt",
        SKILLS / ANTHROPIC_WEBAPP_TESTING / "scripts" / "with_server.py",
        SKILLS / ANTHROPIC_WEBAPP_TESTING / "examples" / "console_logging.py",
        SKILLS / ANTHROPIC_WEBAPP_TESTING / "examples" / "element_discovery.py",
        SKILLS / ANTHROPIC_WEBAPP_TESTING / "examples" / "static_html_automation.py",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "SKILL.md",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "LICENSE.txt",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "agents" / "analyzer.md",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "agents" / "comparator.md",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "agents" / "grader.md",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "assets" / "eval_review.html",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "references" / "schemas.md",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "scripts" / "run_eval.py",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "scripts" / "run_loop.py",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "scripts" / "aggregate_benchmark.py",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "scripts" / "generate_report.py",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "scripts" / "improve_description.py",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "scripts" / "package_skill.py",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "scripts" / "quick_validate.py",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "scripts" / "utils.py",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "eval-viewer" / "generate_review.py",
        SKILLS / ANTHROPIC_SKILL_CREATOR / "eval-viewer" / "viewer.html",
        SKILLS / ANTHROPIC_WEB_ARTIFACTS / "SKILL.md",
        SKILLS / ANTHROPIC_WEB_ARTIFACTS / "LICENSE.txt",
        SKILLS / ANTHROPIC_WEB_ARTIFACTS / "scripts" / "init-artifact.sh",
        SKILLS / ANTHROPIC_WEB_ARTIFACTS / "scripts" / "bundle-artifact.sh",
        SKILLS / ANTHROPIC_WEB_ARTIFACTS / "scripts" / "shadcn-components.tar.gz",
    ]
    assert all(path.is_file() for path in required)


def test_frontend_design_routes_through_visual_ownership_stages() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    goal = "Redesign a luxury perfume ecommerce marketplace"
    for stage in ("art_direction", "visual_composition", "implementation", "visual_qa", "repair"):
        _profile, selected, _mandatory = flow.resolve_skill_names(stage, goal)
        assert ANTHROPIC_FRONTEND_DESIGN in selected


def test_webapp_testing_routes_to_browser_and_visual_qa() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    goal = "Build a luxury perfume ecommerce marketplace"
    for stage in ("browser_qa", "visual_qa"):
        _profile, selected, _mandatory = flow.resolve_skill_names(stage, goal)
        assert ANTHROPIC_WEBAPP_TESTING in selected


def test_web_artifacts_builder_is_bounded_to_complex_interactive_prototypes() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    _profile, complex_skills, _mandatory = flow.resolve_skill_names(
        "implementation",
        "Build a SaaS dashboard with login, search, forms and analytics",
    )
    assert ANTHROPIC_WEB_ARTIFACTS in complex_skills

    _profile, simple_skills, _mandatory = flow.resolve_skill_names(
        "implementation",
        "Build a simple portfolio landing page",
    )
    assert ANTHROPIC_WEB_ARTIFACTS not in simple_skills


def test_skill_creator_is_discoverable_but_not_forced_into_website_runs() -> None:
    loader = SkillLoader(SKILLS)
    relative = {item.relative_to(SKILLS).as_posix() for item in loader.discover()}
    assert f"{ANTHROPIC_SKILL_CREATOR}/SKILL.md" in relative

    flow = ProfessionalWebsiteFlow(SKILLS)
    _profile, selected, _mandatory = flow.resolve_skill_names(
        "art_direction",
        "Redesign a luxury perfume ecommerce marketplace",
    )
    assert ANTHROPIC_SKILL_CREATOR not in selected
