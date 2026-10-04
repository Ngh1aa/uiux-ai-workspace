"""Canonical executable Flow OS runtime for UIUX Factory.

Declarative skills, flows, policies and schemas remain owned by skills_UIUX.
Python modules under skills_UIUX/runtime are compatibility adapters only.
"""

CANONICAL_RUNTIME_OWNER = "uiux-factory/core/runtime/flow_os"

from core.runtime.flow_os.browser_evidence import BrowserEvidenceError, PlaywrightBrowserEvidenceAdapter
from core.runtime.flow_os.browser_observation import BrowserObservationError, PlaywrightBrowserObservationAdapter
from core.runtime.flow_os.continuous_provider_truth import (
    ContinuousProviderTruthAssessment,
    assess_continuous_provider_truth,
    assess_continuous_provider_truth_payload,
)
from core.runtime.flow_os.evidence import EvidenceRecord
from core.runtime.flow_os.execution_advisor import ExecutionAdvice, build_execution_advice
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
from core.runtime.flow_os.provider_attestation import (
    CanonicalIntegrationTruthResult,
    CloudflarePagesProviderAttestor,
    KNOWN_EXTERNAL_INTEGRATION_PROVIDERS,
    NetlifyProviderAttestor,
    PROVIDER_ATTESTATION_CAPABILITIES,
    ProviderAttestationCapability,
    ProviderAttestationCoverageResult,
    ProviderAttestationResult,
    ProviderIntegrationTruth,
    RenderProviderAttestor,
    RailwayProviderAttestor,
    SUPPORTED_PROVIDER_ATTESTORS,
    VercelProviderAttestor,
    assess_provider_attestation_coverage,
    resolve_canonical_integration_truth,
)
from core.runtime.flow_os.provider_truth_history import (
    ProviderTruthBaselineSelection,
    select_previous_fleet_artifact,
)
from core.runtime.flow_os.provider_truth_transition import (
    ProviderTruthRepositoryTransition,
    ProviderTruthTransitionReport,
    build_provider_truth_transition_report,
    write_provider_truth_transition_report,
)
from core.runtime.flow_os.provider_truth_fleet import (
    ProviderTruthFleetRepository,
    ProviderTruthFleetSummary,
    build_provider_truth_fleet_summary,
    load_provider_truth_fleet_reports,
    write_provider_truth_fleet_summary,
)
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
    "CanonicalIntegrationTruthResult",
    "CloudflarePagesProviderAttestor",
    "ContinuousProviderTruthAssessment",
    "KNOWN_EXTERNAL_INTEGRATION_PROVIDERS",
    "ContainerSandbox",
    "DeploymentResult",
    "EvidenceRecord",
    "ExecutionAdvice",
    "ExternalSideEffectAssessment",
    "ExternalSideEffectBlocked",
    "ExternalSideEffectEvidence",
    "FlowPlanner",
    "GitHubExternalSideEffectObserver",
    "GoalInterpretation",
    "GoalInterpreter",
    "ManagedFlowController",
    "ManagedWebsiteRun",
    "NetlifyProviderAttestor",
    "PROVIDER_ATTESTATION_CAPABILITIES",
    "PlaywrightBrowserEvidenceAdapter",
    "PlaywrightBrowserObservationAdapter",
    "PreviewPolicy",
    "ProductionReleaseController",
    "ProductionReleaseError",
    "ProviderAttestationResult",
    "ProviderAttestationCapability",
    "ProviderAttestationCoverageResult",
    "ProviderIntegrationTruth",
    "ProviderTruthFleetRepository",
    "ProviderTruthFleetSummary",
    "ProviderTruthBaselineSelection",
    "ProviderTruthRepositoryTransition",
    "ProviderTruthTransitionReport",
    "RenderProviderAttestor",
    "RailwayProviderAttestor",
    "ResolvedFlow",
    "ResolvedStage",
    "SafeReadError",
    "SafeReadResult",
    "SafeReader",
    "SUPPORTED_PROVIDER_ATTESTORS",
    "SandboxSpec",
    "SandboxUnavailableError",
    "TargetCommandResult",
    "TargetRunner",
    "TargetRunnerError",
    "TaskContract",
    "VercelProviderAttestor",
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
    "assess_continuous_provider_truth",
    "assess_continuous_provider_truth_payload",
    "assess_provider_attestation_coverage",
    "build_execution_advice",
    "build_provider_truth_fleet_summary",
    "build_provider_truth_transition_report",
    "configured_vision_creative_analyzer",
    "detect_static_integrations",
    "load_provider_truth_fleet_reports",
    "resolve_canonical_integration_truth",
    "sanitize_creative_output",
    "sanitize_vision_output",
    "select_previous_fleet_artifact",
    "write_provider_truth_fleet_summary",
    "write_provider_truth_transition_report",
]