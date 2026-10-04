from __future__ import annotations

from pathlib import Path

from core.orchestration.intelligent_flow import GoalInterpreter as FactoryGoalInterpreter
from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.flow import FlowResolver
from core.runtime.flow_os.managed import ManagedFlowController as DevelopmentManagerAgent
from core.runtime.flow_os.task_context import GoalInterpreter as ManagedGoalInterpreter


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


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
