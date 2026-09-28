from __future__ import annotations

import sys
from pathlib import Path

from core.orchestration.intelligent_flow import GoalInterpreter as FactoryGoalInterpreter


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"
if str(SKILLS) not in sys.path:
    sys.path.insert(0, str(SKILLS))

from runtime.flow import FlowResolver
from runtime.task_context import GoalInterpreter as ManagedGoalInterpreter


def test_a3_change_surface_is_consistent_across_factory_and_managed_runtime() -> None:
    cases = {
        "Fix button padding": "MICRO",
        "Sửa icon trong header": "MICRO",
        "Redesign the hero section, keep the current animation": "FOCUSED",
        "Polish the pricing cards": "FOCUSED",
        "Redesign the homepage": "PAGE",
        "Cải thiện hero, pricing và footer của landing page": "PAGE",
        "Redesign the whole website": "REDESIGN",
        "Thiết kế lại toàn bộ website": "REDESIGN",
        "Build a SaaS software platform with dashboard": "PRODUCT",
        "Create a landing page for a fintech platform": "PAGE",
    }

    factory = FactoryGoalInterpreter()
    managed = ManagedGoalInterpreter()
    for goal, expected in cases.items():
        assert factory.interpret(goal).change_surface == expected, goal
        assert managed.interpret(goal).change_surface == expected, goal


def test_a3_scope_specificity_beats_broad_redesign_verb() -> None:
    factory = FactoryGoalInterpreter()
    managed = ManagedGoalInterpreter()

    for interpreter in (factory, managed):
        assert interpreter.interpret("Redesign hero section only").change_surface == "FOCUSED"
        assert interpreter.interpret("Redesign homepage only").change_surface == "PAGE"
        assert interpreter.interpret("Redesign the whole website").change_surface == "REDESIGN"


def test_a3_adaptive_flows_choose_smallest_credible_lane() -> None:
    resolver = FlowResolver(SKILLS / "flows")
    interpreter = ManagedGoalInterpreter()
    cases = {
        "Fix button padding": ("micro-ui-change", ["implementation", "qa"]),
        "Improve the existing hero": ("existing-ui-improvement", ["research", "implementation", "qa"]),
        "Redesign the homepage": ("page-ui-work", ["research", "design", "implementation", "qa"]),
        "Create a landing page for a fintech platform": ("page-ui-work", ["research", "design", "implementation", "qa"]),
        "Redesign the whole website": ("professional-website-redesign", ["research", "design", "implementation", "qa"]),
        "Build a SaaS software platform with dashboard": ("professional-website-redesign", ["research", "design", "implementation", "qa"]),
    }

    for goal, (expected_flow, expected_stages) in cases.items():
        context = interpreter.interpret(goal).to_context()
        _path, document, _score = resolver.resolve(context)
        assert document["id"] == expected_flow, goal
        assert [stage["id"] for stage in document["stages"]] == expected_stages, goal


def test_a3_flow_resolver_keeps_legacy_contexts_working() -> None:
    resolver = FlowResolver(SKILLS / "flows")

    legacy_cases = (
        ({"intent": "fix", "mode": "interactive-prototype"}, "existing-ui-improvement"),
        ({"intent": "redesign", "mode": "interactive-prototype"}, "professional-website-redesign"),
        ({"intent": "build", "mode": "interactive-prototype"}, "professional-website-redesign"),
    )
    for context, expected in legacy_cases:
        _path, document, _score = resolver.resolve(context)
        assert document["id"] == expected


def test_a3_reference_and_preserve_constraints_do_not_inflate_surface() -> None:
    goal = (
        "Fix button padding only, keep current animation, "
        "reference https://example.com for motion style"
    )
    factory = FactoryGoalInterpreter().interpret(goal)
    managed = ManagedGoalInterpreter().interpret(goal)

    assert factory.change_surface == "MICRO"
    assert managed.change_surface == "MICRO"
    assert list(factory.references) == ["https://example.com"]
    assert managed.references == ["https://example.com"]
