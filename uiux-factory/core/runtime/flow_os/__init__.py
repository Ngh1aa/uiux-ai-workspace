"""Canonical executable Flow OS runtime for UIUX Factory.

Declarative skills, flows, policies and schemas remain owned by skills_UIUX.
Python modules under skills_UIUX/runtime are compatibility adapters only.
"""

CANONICAL_RUNTIME_OWNER = "uiux-factory/core/runtime/flow_os"

from core.runtime.flow_os.flow import FlowPlanner, ResolvedFlow, ResolvedStage
from core.runtime.flow_os.managed import ManagedFlowController, ManagedWebsiteRun
from core.runtime.flow_os.safe_read import SafeReadError, SafeReadResult, SafeReader
from core.runtime.flow_os.task_context import GoalInterpretation, GoalInterpreter, TaskContract

__all__ = [
    "CANONICAL_RUNTIME_OWNER",
    "FlowPlanner",
    "GoalInterpretation",
    "GoalInterpreter",
    "ManagedFlowController",
    "ManagedWebsiteRun",
    "ResolvedFlow",
    "ResolvedStage",
    "SafeReadError",
    "SafeReadResult",
    "SafeReader",
    "TaskContract",
]
