from __future__ import annotations

import sys
from pathlib import Path

from core.orchestration.intelligent_flow import GoalInterpreter as FactoryGoalInterpreter


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
sys.path.insert(0, str(WORKSPACE / "skills_UIUX"))

from runtime.task_context import GoalInterpreter as RuntimeGoalInterpreter  # noqa: E402


def test_factory_and_managed_runtime_goal_interpreters_stay_in_parity() -> None:
    goals = [
        "Design a B2B fintech multi-rail settlement platform for PSP operations",
        "Validate a SaaS concept with real users using moderated usability testing",
        "Prepare a dashboard as a production candidate with analytics instrumentation and stakeholders",
        "Build a visual prototype portfolio landing page",
    ]

    factory = FactoryGoalInterpreter()
    runtime = RuntimeGoalInterpreter()

    for goal in goals:
        a = factory.interpret(goal)
        b = runtime.interpret(goal)
        assert a.website_type == b.website_type
        assert a.domain == b.domain
        assert a.product_archetype == b.product_archetype
        assert a.validation_lane == b.validation_lane
        assert set(a.features) == set(b.features)
        assert a.mode == b.mode
        assert a.risk == b.risk
