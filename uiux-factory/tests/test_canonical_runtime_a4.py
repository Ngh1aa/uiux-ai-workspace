from __future__ import annotations

import json
import sys
from pathlib import Path

from core.orchestration.intelligent_flow import GoalInterpreter as FactoryAdapterGoalInterpreter
from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.runtime.flow_os import CANONICAL_RUNTIME_OWNER
from core.runtime.flow_os.flow import FlowPlanner
from core.runtime.flow_os.managed import ManagedFlowController
from core.runtime.flow_os.task_context import GoalInterpreter as CanonicalGoalInterpreter


FACTORY = Path(__file__).resolve().parents[1]
WORKSPACE = FACTORY.parent
SKILLS = WORKSPACE / "skills_UIUX"
if str(SKILLS) not in sys.path:
    sys.path.insert(0, str(SKILLS))

from runtime.flow import DevelopmentManager as LegacyFlowManager
from runtime.manager import DevelopmentManagerAgent as LegacyManagedController
from runtime.task_context import GoalInterpreter as LegacyGoalInterpreter


def test_a4_canonical_runtime_owner_is_factory() -> None:
    assert CANONICAL_RUNTIME_OWNER == "uiux-factory/core/runtime/flow_os"
    assert FactoryAdapterGoalInterpreter is CanonicalGoalInterpreter
    assert LegacyGoalInterpreter is CanonicalGoalInterpreter
    assert LegacyFlowManager is FlowPlanner
    assert LegacyManagedController is ManagedFlowController


def test_a4_canonical_planner_is_shared_by_factory_adapter() -> None:
    flow = ProfessionalWebsiteFlow(SKILLS)
    cases = {
        "Fix button padding": "micro-ui-change",
        "Redesign the homepage": "page-ui-work",
        "Redesign the whole website": "professional-website-redesign",
        "Build a SaaS software platform with dashboard": "professional-website-redesign",
    }
    for goal, expected_flow in cases.items():
        profile, resolved = flow.resolve(goal)
        assert resolved.id == expected_flow
        direct = flow.planner.plan(profile.to_context())
        assert direct.id == resolved.id
        assert [stage.id for stage in direct.stages] == [stage.id for stage in resolved.stages]


def test_a4_legacy_runtime_python_files_are_only_compatibility_shims() -> None:
    wrappers = {
        "adaptive_surface.py": "core.runtime.flow_os.adaptive_surface",
        "agent.py": "core.runtime.flow_os.agent",
        "flow.py": "core.runtime.flow_os.flow",
        "manager.py": "core.runtime.flow_os.managed",
        "mcp_server.py": "core.runtime.flow_os.mcp_server",
        "provider.py": "core.runtime.flow_os.provider",
        "provider_runner.py": "core.runtime.flow_os.provider_runner",
        "task_context.py": "core.runtime.flow_os.task_context",
    }
    forbidden_definitions = (
        "class GoalInterpreter",
        "class FlowResolver",
        "class FlowPlanner",
        "class DevelopmentManagerAgent",
        "class ManagedFlowController",
        "class ProviderNeutralAgentHarness",
    )
    for filename, target in wrappers.items():
        source = (SKILLS / "runtime" / filename).read_text(encoding="utf-8")
        assert target in source, filename
        for definition in forbidden_definitions:
            assert definition not in source, (filename, definition)


def test_a4_official_managed_cli_imports_factory_runtime_directly() -> None:
    source = (SKILLS / "scripts" / "uiux-agent.py").read_text(encoding="utf-8")
    assert "from core.runtime.flow_os.agent import ProviderNeutralAgentHarness" in source
    assert "from core.runtime.flow_os.managed import ManagedFlowController" in source
    assert "from core.runtime.flow_os.provider import create_provider" in source
    assert "from core.runtime.flow_os.provider_runner import ProviderManagedRunner" in source
    assert "from runtime." not in source


def test_a4_skills_runtime_remains_declarative_input_owner() -> None:
    policy = json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))
    planner = FlowPlanner(SKILLS, policy)
    loaded = {doc["id"] for _path, doc in planner.flow_resolver.load()}
    assert {
        "micro-ui-change",
        "existing-ui-improvement",
        "page-ui-work",
        "professional-website-redesign",
    }.issubset(loaded)
