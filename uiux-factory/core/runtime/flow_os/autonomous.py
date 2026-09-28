from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.managed import ManagedFlowController, ManagedWebsiteRun
from core.runtime.flow_os.provider import ModelProvider
from core.runtime.flow_os.provider_runner import ProviderManagedRunner, ProviderRunResult
from core.runtime.flow_os.resilience import CheckpointRecoveryManager


_SOURCE_TRUTH_CANDIDATES = (
    "PROJECT-CONTEXT.md",
    "PROJECT_CONTEXT.md",
    "AGENTS.md",
    "README.md",
    ".uiux-profile.json",
    "package.json",
)

_PHASE_ORDER = ("audit", "plan", "execute", "qa")


@dataclass(frozen=True)
class ProjectAudit:
    project_root: str
    source_truth: tuple[str, ...]
    git_repository: bool
    package_project: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_root": self.project_root,
            "source_truth": list(self.source_truth),
            "git_repository": self.git_repository,
            "package_project": self.package_project,
        }


@dataclass(frozen=True)
class AutonomousRunResult:
    manager_run_id: str
    flow_id: str
    flow_revision: int
    state: str
    active_stage: str
    completed_stages: tuple[str, ...]
    lifecycle: tuple[str, ...]
    audit: ProjectAudit
    provider: str
    model: str
    cycles: int
    message: str
    recovery_snapshot: str | None
    workspace: dict[str, Any] | None
    truth_boundary: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["completed_stages"] = list(self.completed_stages)
        payload["lifecycle"] = list(self.lifecycle)
        payload["audit"] = self.audit.to_dict()
        return payload


def audit_project_truth(
    project_root: Path,
    explicit_sources: Iterable[str] | None = None,
) -> ProjectAudit:
    root = Path(project_root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"project root does not exist: {root}")

    if explicit_sources is None:
        sources = tuple(name for name in _SOURCE_TRUTH_CANDIDATES if (root / name).is_file())
    else:
        normalized: list[str] = []
        for raw in explicit_sources:
            value = str(raw).strip().replace("\\", "/")
            while value.startswith("./"):
                value = value[2:]
            if not value or value.startswith("/") or ".." in Path(value).parts:
                raise ValueError(f"unsafe explicit source path: {raw!r}")
            candidate = (root / value).resolve()
            if not candidate.is_relative_to(root) or not candidate.is_file():
                raise FileNotFoundError(f"explicit source does not exist: {value}")
            if value not in normalized:
                normalized.append(value)
        sources = tuple(normalized)

    return ProjectAudit(
        project_root=str(root),
        source_truth=sources,
        git_repository=(root / ".git").exists(),
        package_project=(root / "package.json").is_file(),
    )


class AutonomousFlowRunner:
    """Release-grade entrypoint over the canonical Flow Agent OS.

    This class deliberately does not invent a second planner, tool registry, or gate
    system. It composes the existing GoalInterpreter/FlowPlanner through
    ManagedFlowController and the existing model→tool→evidence loop through
    ProviderManagedRunner.

    Completion means the canonical managed run reached COMPLETED. It never implies
    merge, deployment, production release, human aesthetic approval, or user-outcome
    validation.
    """

    def __init__(
        self,
        *,
        skills_root: Path,
        project_root: Path,
        provider: ModelProvider,
    ) -> None:
        self.skills_root = Path(skills_root).resolve()
        self.project_root = Path(project_root).resolve()
        self.provider = provider
        self.harness = ProviderNeutralAgentHarness(self.skills_root, self.project_root)
        self.manager = ManagedFlowController(self.harness)
        self.provider_runner = ProviderManagedRunner(self.manager, provider)
        self.recovery = CheckpointRecoveryManager(self.project_root)

    @staticmethod
    def _plan_lifecycle(managed: ManagedWebsiteRun) -> tuple[str, ...]:
        return _PHASE_ORDER

    def _snapshot_label(self, managed: ManagedWebsiteRun) -> str:
        return (
            f"pre-drive-r{managed.flow.revision}-"
            f"p{managed.replan_count}-{managed.active_stage}"
        )

    def _result(
        self,
        managed: ManagedWebsiteRun,
        audit: ProjectAudit,
        provider_result: ProviderRunResult,
        snapshot_label: str | None,
    ) -> AutonomousRunResult:
        manager_state = self.harness.resume(managed.manager_run_id)
        raw_workspace = manager_state.context.get("workspace")
        workspace = dict(raw_workspace) if isinstance(raw_workspace, dict) else None
        return AutonomousRunResult(
            manager_run_id=managed.manager_run_id,
            flow_id=managed.flow.id,
            flow_revision=managed.flow.revision,
            state=managed.state if managed.state == "COMPLETED" else provider_result.state,
            active_stage=managed.active_stage,
            completed_stages=tuple(managed.completed_stages),
            lifecycle=self._plan_lifecycle(managed),
            audit=audit,
            provider=provider_result.provider,
            model=provider_result.model,
            cycles=provider_result.cycles,
            message=provider_result.message,
            recovery_snapshot=snapshot_label,
            workspace=workspace,
            truth_boundary=(
                "Autonomous completion is a canonical Flow/gate verdict inside an isolated "
                "workspace. It does not authorize merge/deploy/release and does not fabricate "
                "human, aesthetic, accessibility, or user-outcome claims beyond recorded evidence."
            ),
        )

    def _drive(
        self,
        managed: ManagedWebsiteRun,
        audit: ProjectAudit,
        *,
        max_cycles: int,
        max_turns_per_stage: int,
        auto_replan: bool,
        dry_run: bool,
    ) -> AutonomousRunResult:
        if managed.state in {"READY", "REPLANNED", "RUNNING"} and audit.source_truth:
            self.manager.start_stage(managed, explicit_sources=list(audit.source_truth))

        snapshot_label: str | None = None
        if managed.state not in {"COMPLETED", "FAILED", "BLOCKED"}:
            snapshot_label = self._snapshot_label(managed)
            self.recovery.snapshot(managed.manager_run_id, snapshot_label)

        provider_result = self.provider_runner.run_to_boundary(
            managed,
            max_cycles=max_cycles,
            max_turns_per_stage=max_turns_per_stage,
            auto_replan=auto_replan,
            dry_run=dry_run,
        )
        return self._result(managed, audit, provider_result, snapshot_label)

    def start(
        self,
        goal: str,
        *,
        authority: str = "branch_write",
        overrides: dict[str, Any] | None = None,
        explicit_sources: Iterable[str] | None = None,
        max_cycles: int = 16,
        max_turns_per_stage: int = 12,
        auto_replan: bool = True,
        dry_run: bool = False,
    ) -> AutonomousRunResult:
        text = str(goal).strip()
        if not text:
            raise ValueError("autonomous run requires a non-empty goal")
        audit = audit_project_truth(self.project_root, explicit_sources)
        managed = self.manager.start_from_goal(
            text,
            authority=authority,
            overrides=overrides,
        )
        return self._drive(
            managed,
            audit,
            max_cycles=max_cycles,
            max_turns_per_stage=max_turns_per_stage,
            auto_replan=auto_replan,
            dry_run=dry_run,
        )

    def resume(
        self,
        manager_run_id: str,
        *,
        explicit_sources: Iterable[str] | None = None,
        max_cycles: int = 16,
        max_turns_per_stage: int = 12,
        auto_replan: bool = True,
        dry_run: bool = False,
    ) -> AutonomousRunResult:
        audit = audit_project_truth(self.project_root, explicit_sources)
        managed = self.manager.resume(str(manager_run_id))
        return self._drive(
            managed,
            audit,
            max_cycles=max_cycles,
            max_turns_per_stage=max_turns_per_stage,
            auto_replan=auto_replan,
            dry_run=dry_run,
        )
