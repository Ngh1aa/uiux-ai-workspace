"""Canonical executable Flow OS runtime for UIUX Factory.

Declarative skills, flows, policies and schemas remain owned by skills_UIUX.
Python modules under skills_UIUX/runtime are compatibility adapters only.
"""

CANONICAL_RUNTIME_OWNER = "uiux-factory/core/runtime/flow_os"

from core.runtime.flow_os.browser_evidence import BrowserEvidenceError, PlaywrightBrowserEvidenceAdapter
from core.runtime.flow_os.browser_observation import BrowserObservationError, PlaywrightBrowserObservationAdapter
from core.runtime.flow_os.evidence import EvidenceRecord
from core.runtime.flow_os.external_side_effects import (
    ExternalSideEffectAssessment,
    ExternalSideEffectBlocked,
    ExternalSideEffectEvidence,
    GitHubExternalSideEffectObserver,
    PreviewPolicy,
    assess_external_side_effects,
    detect_static_integrations,
)
from core.runtime.flow_os.file_tools import WorkspaceFileError, WorkspaceFileTools
from core.runtime.flow_os.flow import FlowPlanner, ResolvedFlow, ResolvedStage
from core.runtime.flow_os.managed import ManagedFlowController, ManagedWebsiteRun
from core.runtime.flow_os.release import (
    CommandDeployAdapter,
    DeploymentResult,
    ProductionReleaseController,
    ProductionReleaseError,
)
from core.runtime.flow_os.safe_read import SafeReadError, SafeReadResult, SafeReader
from core.runtime.flow_os.sandbox import ContainerSandbox, SandboxSpec, SandboxUnavailableError
from core.runtime.flow_os.target_runner import TargetCommandResult, TargetRunner, TargetRunnerError
from core.runtime.flow_os.task_context import GoalInterpretation, GoalInterpreter, TaskContract
from core.runtime.flow_os.vision_director import (
    CommandVisionCreativeAnalyzer,
    VisionCreativeAnalyzer,
    VisionCreativeDirectorAdapter,
    VisionCreativeDirectorError,
    configured_vision_creative_analyzer,
    sanitize_creative_output,
)
from core.runtime.flow_os.vision_evidence import (
    VisionAnalyzer,
    VisionEvidenceAdapter,
    VisionEvidenceError,
    sanitize_vision_output,
)
from core.runtime.flow_os.workspace import (
    WorkspaceFinalizeResult,
    WorkspaceIsolationError,
    WorkspaceMetadata,
    WorktreeManager,
)

__all__ = [
    "BrowserEvidenceError",
    "BrowserObservationError",
    "CANONICAL_RUNTIME_OWNER",
    "CommandDeployAdapter",
    "CommandVisionCreativeAnalyzer",
    "ContainerSandbox",
    "DeploymentResult",
    "EvidenceRecord",
    "ExternalSideEffectAssessment",
    "ExternalSideEffectBlocked",
    "ExternalSideEffectEvidence",
    "FlowPlanner",
    "GitHubExternalSideEffectObserver",
    "GoalInterpretation",
    "GoalInterpreter",
    "ManagedFlowController",
    "ManagedWebsiteRun",
    "PlaywrightBrowserEvidenceAdapter",
    "PlaywrightBrowserObservationAdapter",
    "PreviewPolicy",
    "ProductionReleaseController",
    "ProductionReleaseError",
    "ResolvedFlow",
    "ResolvedStage",
    "SafeReadError",
    "SafeReadResult",
    "SafeReader",
    "SandboxSpec",
    "SandboxUnavailableError",
    "TargetCommandResult",
    "TargetRunner",
    "TargetRunnerError",
    "TaskContract",
    "VisionAnalyzer",
    "VisionCreativeAnalyzer",
    "VisionCreativeDirectorAdapter",
    "VisionCreativeDirectorError",
    "VisionEvidenceAdapter",
    "VisionEvidenceError",
    "WorkspaceFileError",
    "WorkspaceFileTools",
    "WorkspaceFinalizeResult",
    "WorkspaceIsolationError",
    "WorkspaceMetadata",
    "WorktreeManager",
    "assess_external_side_effects",
    "configured_vision_creative_analyzer",
    "detect_static_integrations",
    "sanitize_creative_output",
    "sanitize_vision_output",
]