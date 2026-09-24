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
        assert profile.domain in {"generic", "financial-services"}


def test_factory_default_delivery_policy_is_pinned_to_upstream_source() -> None:
    config = json.loads((ROOT / "config" / "default-website-delivery.json").read_text(encoding="utf-8"))
    assert config["policy_id"] == "adaptive-prompt-os-v4"
    assert config["factory_lane"] == "full_prompt_os"
    assert config["policy_source"] == {
        "repository": "Ngh1aa/skills_UIUX",
        "commit": "e8ed8c9212d20edb2cf4c8c0881fff34add7076e",
        "path": "policies/adaptive-prompt-os-v4.json",
        "blob_sha": "c98521827e9bc242c3594a315739809c5574a800",
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


def test_goal_interpreter_classifies_financial_domain_and_archetypes() -> None:
    interpreter = GoalInterpreter()

    finflow = interpreter.interpret(
        "Design a B2B fintech multi-rail settlement platform for PSP and MTO payout operations"
    )
    assert finflow.domain == "financial-services"
    assert finflow.product_archetype == "payments-infrastructure"

    kyc = interpreter.interpret("Build a KYC AML onboarding review workflow")
    assert kyc.domain == "financial-services"
    assert kyc.product_archetype == "compliance-operations"

    nova = interpreter.interpret("Create a consumer banking app for spending, saving and debit cards")
    assert nova.domain == "financial-services"
    assert nova.product_archetype == "consumer-banking"

    lumen = interpreter.interpret("Create an immersive digital museum experience")
    assert lumen.domain == "generic"
    assert lumen.product_archetype == "generic"


def test_financial_projects_route_financial_product_intelligence() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    profile, skills, _mandatory = flow.resolve_skill_names(
        "research",
        "Redesign a fintech settlement and payment rails landing page for PSP operations",
    )
    assert profile.domain == "financial-services"
    assert profile.product_archetype == "payments-infrastructure"
    assert "financial-product-intelligence" in skills
    assert "trust-credibility-and-transparency" in skills


def test_agentic_workflow_routes_specialist_orchestration_only_when_signaled() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)

    profile, skills, _mandatory = flow.resolve_skill_names(
        "implementation",
        "Build a multi-agent orchestration workflow with subagent verification",
    )
    assert "agentic-workflow" in profile.features
    assert "specialist-agent-orchestration" in skills

    _plain_profile, plain_skills, _mandatory = flow.resolve_skill_names(
        "implementation",
        "Build a responsive portfolio landing page",
    )
    assert "specialist-agent-orchestration" not in plain_skills


def test_adaptive_router_prefers_business_domain_when_known() -> None:
    assert AdaptiveSkillRouter.infer_domain(
        "B2B fintech settlement infrastructure for PSPs"
    ) == "financial-services"


def test_validation_lane_scales_lifecycle_rigor_without_overloading_prototypes() -> None:
    interpreter = GoalInterpreter()

    fast = interpreter.interpret("Build a visual prototype portfolio landing page")
    assert fast.validation_lane == "prototype"

    evidence_led = interpreter.interpret(
        "Test this SaaS concept with real users using moderated usability testing"
    )
    assert evidence_led.validation_lane == "evidence-led"
    assert "user-validation" in evidence_led.features

    production = interpreter.interpret(
        "Prepare this SaaS dashboard as a production candidate with analytics instrumentation"
    )
    assert production.mode == "production-candidate"
    assert production.validation_lane == "production-learning"
    assert "outcome-measurement" in production.features


def test_evidence_led_and_production_learning_route_lifecycle_skills() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)

    profile, research_skills, _mandatory = flow.resolve_skill_names(
        "research",
        "Validate this SaaS concept with real users before implementation",
    )
    assert profile.validation_lane == "evidence-led"
    assert "real-user-validation" in research_skills
    assert "user-research-planning-and-recruitment" in research_skills

    prod_profile, implementation_skills, _mandatory = flow.resolve_skill_names(
        "implementation",
        "Prepare this SaaS dashboard as a production candidate with success metrics",
    )
    assert prod_profile.validation_lane == "production-learning"
    assert "outcome-metrics-and-instrumentation" in implementation_skills

    _prod_profile, qa_skills, _mandatory = flow.resolve_skill_names(
        "browser_qa",
        "Prepare this SaaS dashboard as a production candidate with success metrics",
    )
    assert "post-launch-learning-loop" in qa_skills
    assert "human-governance-and-playbacks" in qa_skills


def test_plain_prototype_does_not_route_enterprise_lifecycle_overhead() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    profile, skills, _mandatory = flow.resolve_skill_names(
        "research",
        "Build a distinctive interactive portfolio prototype",
    )
    assert profile.validation_lane == "prototype"
    assert "real-user-validation" not in skills
    assert "outcome-metrics-and-instrumentation" not in skills
    assert "human-governance-and-playbacks" not in skills
