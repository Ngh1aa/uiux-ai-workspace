from __future__ import annotations

from pathlib import Path
import json

import pytest

from core.orchestration.intelligent_flow import GoalInterpreter as FactoryGoalInterpreter
from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.flow import FlowResolver
from core.runtime.flow_os.managed import ManagedFlowController as DevelopmentManagerAgent
from core.runtime.flow_os.task_context import GoalInterpreter as ManagedGoalInterpreter
from core.runtime.flow_os.external_task import build_external_task_manifest
from core.runtime.flow_os.sequence_router import WorkSequenceInterpreter


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime/runtime-policy.json").read_text(encoding="utf-8"))


def _manifest(goal: str, authority: str = "branch_write") -> dict:
    return build_external_task_manifest(SKILLS, POLICY, goal, "owner/repo", authority=authority).to_dict()


def test_a2_intents_are_consistent_across_factory_and_managed_runtime() -> None:
    cases = {
        "Improve the existing hero": "improve",
        "Cải thiện hero hiện tại": "improve",
        "Fix the mobile navigation": "fix",
        "Sửa hero hiện tại": "fix",
        "Polish the pricing cards": "polish",
        "Tinh chỉnh typography": "polish",
        "Redesign the whole website": "redesign",
        "Xây lại website": "rebuild",
    }

    factory = FactoryGoalInterpreter()
    managed = ManagedGoalInterpreter()
    for goal, expected in cases.items():
        assert factory.interpret(goal).intent == expected
        assert managed.interpret(goal).intent == expected


def test_a2_task_contract_extracts_natural_language_constraints() -> None:
    goal = (
        "Sửa hero Nova đẹp hơn, giữ nguyên animation hiện tại, "
        "đừng thay đổi navigation; tham khảo https://example.com về visual direction."
    )

    factory = FactoryGoalInterpreter().interpret(goal).to_dict()
    managed = ManagedGoalInterpreter().interpret(goal).to_context()

    for contract in (factory, managed):
        assert contract["task_contract_version"] == "1.0"
        assert contract["intent"] == "fix"
        assert "hero" in contract["scope"]
        assert any("animation" in item for item in contract["preserve"])
        assert any("navigation" in item for item in contract["forbidden"])
        assert contract["references"] == ["https://example.com"]
        assert contract["authority"] == "unspecified"


def test_a2_reference_clause_does_not_expand_change_scope() -> None:
    goal = "Cải thiện hero, tham khảo https://example.com chỉ về animation"
    factory = FactoryGoalInterpreter().interpret(goal)
    managed = ManagedGoalInterpreter().interpret(goal)

    assert list(factory.scope) == ["hero"]
    assert managed.scope == ["hero"]
    assert list(factory.references) == ["https://example.com"]
    assert managed.references == ["https://example.com"]


def test_a2_existing_ui_intents_route_to_focused_flow() -> None:
    resolver = FlowResolver(SKILLS / "flows")
    interpreter = ManagedGoalInterpreter()

    for goal in (
        "Improve the existing hero",
        "Fix the current mobile navigation",
        "Polish the pricing cards",
        "Cải thiện hero hiện tại",
        "Sửa mobile nav hiện tại",
        "Tinh chỉnh typography hiện tại",
    ):
        context = interpreter.interpret(goal).to_context()
        _path, document, _score = resolver.resolve(context)
        assert document["id"] == "existing-ui-improvement"


def test_a2_read_only_language_reduces_effective_authority(tmp_path: Path) -> None:
    harness = ProviderNeutralAgentHarness(SKILLS, tmp_path)
    manager = DevelopmentManagerAgent(harness)

    managed = manager.start_from_goal(
        "Chỉ audit UI, không sửa code",
        authority="branch_write",
    )

    assert managed.task_context["authority"] == "read_only"
    assert managed.task_context["effective_authority"] == "read_only"
    assert managed.authority == "read_only"


def test_a2_language_never_escalates_above_caller_authority(tmp_path: Path) -> None:
    harness = ProviderNeutralAgentHarness(SKILLS, tmp_path)
    manager = DevelopmentManagerAgent(harness)

    managed = manager.start_from_goal(
        "Deploy production after QA",
        authority="branch_write",
    )

    assert managed.task_context["authority"] == "release"
    assert managed.task_context["effective_authority"] == "branch_write"
    assert managed.authority == "branch_write"


def test_a2_negative_fix_phrase_routes_to_explicit_audit_intent() -> None:
    goal = "Chỉ audit UI, không sửa code"
    assert FactoryGoalInterpreter().interpret(goal).intent == "audit"
    assert ManagedGoalInterpreter().interpret(goal).intent == "audit"


@pytest.mark.parametrize("goal", [
    "Chỉ đọc repo, tìm tất cả lỗi và lập danh sách task sửa lỗi",
    "đọc repo cho mình xem hệ thống còn lỗi gì hay không nếu có tìm hết tất cả các lỗi lập thành danh sách task tối ưu thời gian và không bị dư token",
    "Review the repository and list bugs to fix later",
    "Read the repo and list tasks to fix bugs",
    "List bugs to fix later",
    "Review button spacing only",
    "Chỉ đọc và kiểm tra nút, không sửa code",
])
def test_batch1_reported_repairs_do_not_authorize_implementation(goal: str) -> None:
    manifest = _manifest(goal, "release")
    assert manifest["task_contract"]["intent"] in {"audit", "review"}
    assert manifest["authority"] == "read_only"
    assert manifest["resolved_flow"]["id"] == "audit-review"
    assert [stage["agent"] for stage in manifest["stages"]] == ["research", "qa"]


@pytest.mark.parametrize("goal", [
    "Audit the existing website, then fix navbar, then run QA",
    "Trước tiên audit website, sau đó sửa navbar, cuối cùng kiểm thử",
    "Review the repo and fix the bugs now",
])
def test_batch1_immediate_repairs_keep_mutating_intent(goal: str) -> None:
    manifest = _manifest(goal)
    assert manifest["task_contract"]["intent"] == "fix"
    assert manifest["authority"] == "branch_write"
    assert any(stage["agent"] == "implementation" for stage in manifest["stages"])


@pytest.mark.parametrize("authority", ["branch_write", "release"])
@pytest.mark.parametrize("goal", [
    "Fix button spacing only; do not deploy production",
    "Sửa nút và không lên production",
    "Fix button spacing only; don't deploy to production",
    "Fix button spacing only; đừng deploy preview",
    "Fix button spacing only; no deployment",
    "Fix button spacing only; without deployment",
    "Fix button spacing only; không deploy",
])
def test_batch1_negated_deployment_keeps_small_task_bounded(goal: str, authority: str) -> None:
    manifest = _manifest(goal, authority)
    baseline = _manifest("Fix button spacing only")
    contract = manifest["task_contract"]
    assert manifest["authority"] == "branch_write"
    assert contract["mode"] == "interactive-prototype"
    assert contract["risk"] == "standard"
    assert contract["validation_lane"] == "prototype"
    assert contract["forbidden"]
    assert manifest["resolved_flow"]["id"] == "micro-ui-change"
    assert [s["skills"] for s in manifest["stages"]] == [s["skills"] for s in baseline["stages"]]
    assert manifest["execution_advice"]["overall_profile"]["recommended_capability"] == baseline["execution_advice"]["overall_profile"]["recommended_capability"]


@pytest.mark.parametrize("goal", [
    "Review a dashboard without payment integration",
    "Review a dashboard; không có payment integration",
])
def test_batch1_excluded_features_do_not_route_to_payment_specialist(goal: str) -> None:
    contract = ManagedGoalInterpreter().interpret(goal)
    assert contract.website_type == "saas"
    assert contract.domain == "generic"
    assert "payment" not in contract.features
    assert _manifest(goal)["execution_advice"]["overall_profile"]["recommended_capability"] != "advanced"


@pytest.mark.parametrize("constraint", ["không thay đổi style", "đừng thay đổi style", "do not change style"])
def test_batch1_style_constraint_is_preserved_in_contract_and_segments(constraint: str) -> None:
    goal = f"Improve homepage; {constraint}"
    assert "style" in _manifest(goal)["task_contract"]["forbidden"]
    sequence = WorkSequenceInterpreter().interpret(f"Improve homepage, then fix navbar; {constraint}")
    assert sequence.segments
    assert all("style" in segment.forbidden for segment in sequence.segments)


@pytest.mark.parametrize("goal,website_type,domain", [
    ("Review workshop schedule", "generic", "generic"),
    ("Review banknote typography", "generic", "generic"),
    ("Review shopping catalog", "generic", "commerce-retail"),
    ("Review an online store checkout", "ecommerce", "commerce-retail"),
    ("Review banking payments", "generic", "financial-services"),
    ("Review a fintech payment platform", "generic", "financial-services"),
])
def test_batch1_taxonomy_matches_tokens_not_embedded_substrings(goal: str, website_type: str, domain: str) -> None:
    contract = ManagedGoalInterpreter().interpret(goal)
    assert contract.website_type == website_type
    assert contract.domain == domain


@pytest.mark.parametrize("goal,authority,mode", [
    ("Fix button spacing then deploy production", "release", "production"),
    ("Fix button spacing then deploy preview", "external_write", "interactive-prototype"),
    ("Fix spacing; do not deploy production but deploy preview", "external_write", "interactive-prototype"),
    ("Fix the production bug; do not deploy", "branch_write", "production"),
    ("Không deploy production, sửa lỗi đăng nhập", "branch_write", "interactive-prototype"),
])
def test_batch1_positive_actions_and_project_context_survive_negation(goal: str, authority: str, mode: str) -> None:
    contract = ManagedGoalInterpreter().interpret(goal)
    assert contract.authority == authority
    assert contract.mode == mode
    assert contract.intent == "fix"


def test_batch1_absence_is_distinct_from_a_mutation_prohibition() -> None:
    absent = ManagedGoalInterpreter().interpret("Improve homepage; không có auth")
    assert absent.forbidden == []
    assert absent.features == []
    goal = "Improve homepage; không thay đổi style và animation, nhưng sửa navbar"
    contract = ManagedGoalInterpreter().interpret(goal)
    assert contract.forbidden == ["style và animation"]
    assert "navigation" in contract.scope
    assert "motion" not in contract.features


@pytest.mark.parametrize("content,archetype", [
    ("course and lesson", "learning-experience"),
    ("courses, lessons and assignments", "learning-experience"),
    ("coursework and lessonbook", "generic"),
])
def test_batch1_taxonomy_retains_explicit_plural_aliases(content: str, archetype: str) -> None:
    contract = ManagedGoalInterpreter().interpret(f"Build an EdTech learning platform with {content}")
    assert contract.domain == "education-edtech"
    assert contract.product_archetype == archetype

def test_portfolio_figma_request_routes_professional_artifact_skill() -> None:
    goal = (
        "Improve my UI UX designer portfolio and make the Figma file professional "
        "with case study and prototype proof"
    )
    contract = ManagedGoalInterpreter().interpret(goal)
    assert contract.website_type == "portfolio"
    assert "figma-artifact" in contract.features

    resolver = FlowResolver(SKILLS / "flows")
    _path, document, _score = resolver.resolve(contract.to_context())
    assert document["id"] == "portfolio-career-system"

    manifest = _manifest(goal)
    stages = {stage["id"]: stage["skills"] for stage in manifest["stages"]}
    assert "figma-professional-artifact" in stages["research"]
    assert "figma-professional-artifact" in stages["design"]
    assert "figma-professional-artifact" in stages["qa"]

