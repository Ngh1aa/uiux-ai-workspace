from __future__ import annotations

import json
from pathlib import Path

from core.runtime.flow_os.execution_driver import (
    ArtifactRegistry,
    ExecutionDriver,
    JsonCheckpointStore,
    SegmentRunner,
)
from core.runtime.flow_os.flow import FlowPlanner, ResolvedFlow, ResolvedStage
from core.runtime.flow_os.github_transaction import GitHubProductionRunner, GitHubTransactionConfig
from core.runtime.flow_os.sequence_flow import (
    MultiSurfaceRoutingError,
    ResolvedWorkPlan,
    SequenceFlowPlanner,
)
from core.runtime.flow_os.sequence_router import WorkSequenceContract, WorkSequenceInterpreter
from core.runtime.flow_os.task_context import (
    DEFAULT_DELIVERY_POLICY_ID,
    DEFAULT_FACTORY_DELIVERY_LANE,
    TASK_CONTRACT_VERSION,
    GoalInterpretation,
    GoalInterpreter,
    GoalProfile,
    TaskContract,
)
from core.runtime.flow_os.work_execution import WorkExecutionPlan


ANTHROPIC_SKILL_ROOT = "upstream/anthropic-skills/skills"
ANTHROPIC_FRONTEND_DESIGN = f"{ANTHROPIC_SKILL_ROOT}/frontend-design"
ANTHROPIC_WEBAPP_TESTING = f"{ANTHROPIC_SKILL_ROOT}/webapp-testing"
ANTHROPIC_SKILL_CREATOR = f"{ANTHROPIC_SKILL_ROOT}/skill-creator"
ANTHROPIC_WEB_ARTIFACTS = f"{ANTHROPIC_SKILL_ROOT}/web-artifacts-builder"
MOTION_COMPONENT_INTELLIGENCE = "motion-component-intelligence"


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


class ProfessionalWebsiteFlow:
    """Factory adapter over canonical Task, Sequence, Flow, Execution and Runner planning.

    GoalInterpreter remains the single-task contract owner. P1.4 adds a non-breaking
    WorkSequenceContract, P1.5 turns the sequence into stateful execution, P1.6 binds
    eligible segments to a concrete runner, and P1.7 adds a GitHub transaction boundary
    without moving routing or state ownership out of canonical Flow OS.
    """

    FACTORY_TO_FLOW_STAGE = {
        "reference_analysis": "research",
        "research": "research",
        "ux_ia": "research",
        "art_direction": "design",
        "design_contract": "design",
        "design_system": "design",
        "implementation_plan": "implementation",
        "visual_composition": "design",
        "specification_compile": "implementation",
        "implementation": "implementation",
        "browser_qa": "qa",
        "visual_qa": "qa",
        "repair": "qa",
    }

    EXTRA_BY_FACTORY_STAGE = {
        "reference_analysis": ("reference-extraction-and-design-audit",),
        "ux_ia": ("ux-research-and-journey", "journey-driven-content-and-layout"),
        "art_direction": (
            "visual-taste-calibration",
            "brand-guidelines",
            "motion-and-microinteractions",
            MOTION_COMPONENT_INTELLIGENCE,
            ANTHROPIC_FRONTEND_DESIGN,
        ),
        "design_system": ("responsive-and-device-strategy", "accessibility"),
        "implementation_plan": ("frontend-architecture-and-refactoring",),
        "visual_composition": (
            "visual-taste-calibration",
            "responsive-and-device-strategy",
            "motion-and-microinteractions",
            MOTION_COMPONENT_INTELLIGENCE,
            ANTHROPIC_FRONTEND_DESIGN,
        ),
        "specification_compile": ("prompt-compiler", "accessibility", "testing-strategy"),
        "implementation": (
            "accessibility",
            "motion-and-microinteractions",
            MOTION_COMPONENT_INTELLIGENCE,
            ANTHROPIC_FRONTEND_DESIGN,
        ),
        "browser_qa": ("visual-regression-and-design-drift", ANTHROPIC_WEBAPP_TESTING),
        "visual_qa": (
            "visual-taste-calibration",
            "visual-regression-and-design-drift",
            ANTHROPIC_FRONTEND_DESIGN,
            ANTHROPIC_WEBAPP_TESTING,
        ),
        "repair": (
            "ui-improvement",
            "visual-taste-calibration",
            "responsive-and-device-strategy",
            "motion-and-microinteractions",
            MOTION_COMPONENT_INTELLIGENCE,
            ANTHROPIC_FRONTEND_DESIGN,
        ),
    }

    COMPLEX_PROTOTYPE_FEATURES = frozenset({"auth", "dashboard", "forms", "search"})
    HIGH_LEVEL_ORDER = ("research", "design", "implementation", "qa")

    def __init__(self, skills_root: Path) -> None:
        self.skills_root = Path(skills_root).resolve()
        policy_path = self.skills_root / "runtime" / "runtime-policy.json"
        if not policy_path.is_file():
            raise FileNotFoundError(f"Runtime policy missing: {policy_path}")
        self.runtime_policy = json.loads(policy_path.read_text(encoding="utf-8"))
        self.planner = FlowPlanner(self.skills_root, self.runtime_policy)
        self.interpreter = GoalInterpreter()
        self.sequence_interpreter = WorkSequenceInterpreter(self.interpreter)
        self.sequence_planner = SequenceFlowPlanner(self.planner)

        self.flow_path = self.skills_root / "flows" / "professional-website-redesign.json"
        if not self.flow_path.is_file():
            raise FileNotFoundError(f"Professional website flow missing: {self.flow_path}")
        self.document = json.loads(self.flow_path.read_text(encoding="utf-8"))

        self.delivery_policy_path = self.skills_root / "policies" / f"{DEFAULT_DELIVERY_POLICY_ID}.json"
        if not self.delivery_policy_path.is_file():
            raise FileNotFoundError(f"Default website delivery policy missing: {self.delivery_policy_path}")
        self.delivery_policy = json.loads(self.delivery_policy_path.read_text(encoding="utf-8"))
        if self.delivery_policy.get("id") != DEFAULT_DELIVERY_POLICY_ID:
            raise ValueError(
                f"Unexpected default delivery policy id: {self.delivery_policy.get('id')!r}; "
                f"expected {DEFAULT_DELIVERY_POLICY_ID!r}"
            )
        phase_ids = [phase.get("id") for phase in self.delivery_policy.get("full_prompt_os", {}).get("phases", [])]
        if phase_ids != [0, 1, 2, 3, 4]:
            raise ValueError(f"Default delivery policy must define Prompt OS phases 0→4, got {phase_ids!r}")

    def resolve_contract(
        self,
        goal: str,
        target_truth: dict[str, str] | None = None,
    ) -> WorkSequenceContract:
        return self.sequence_interpreter.interpret(goal, target_truth=target_truth)

    def resolve(
        self,
        goal: str,
        target_truth: dict[str, str] | None = None,
    ) -> tuple[GoalInterpretation, ResolvedFlow]:
        contract = self.resolve_contract(goal, target_truth=target_truth)
        if contract.routing_mode == "sequence":
            raise MultiSurfaceRoutingError(contract.segments)
        return contract.profile, self.sequence_planner.plan_single(contract)

    def resolve_work_plan(
        self,
        goal: str,
        target_truth: dict[str, str] | None = None,
    ) -> tuple[GoalInterpretation, ResolvedWorkPlan]:
        contract = self.resolve_contract(goal, target_truth=target_truth)
        if contract.routing_mode != "sequence":
            raise ValueError("goal resolves to a single work owner; use resolve() instead")
        return contract.profile, self.sequence_planner.plan_sequence(contract)

    def resolve_execution_plan(
        self,
        goal: str,
        target_truth: dict[str, str] | None = None,
    ) -> tuple[GoalInterpretation, WorkExecutionPlan]:
        """Resolve a multi-work prompt into a resumable dependency-aware execution plan."""
        profile, work_plan = self.resolve_work_plan(goal, target_truth=target_truth)
        return profile, WorkExecutionPlan.from_resolved_work_plan(work_plan)

    def resolve_execution_driver(
        self,
        goal: str,
        runner: SegmentRunner,
        *,
        workspace_root: Path | str,
        checkpoint_path: Path | str | None = None,
        target_truth: dict[str, str] | None = None,
        max_repair_attempts: int = 2,
    ) -> tuple[GoalInterpretation, ExecutionDriver]:
        """Resolve canonical work then bind it to the P1.6 runner/registry/checkpoint driver."""
        profile, work_plan = self.resolve_work_plan(goal, target_truth=target_truth)
        execution_plan = WorkExecutionPlan.from_resolved_work_plan(work_plan)
        checkpoint = JsonCheckpointStore(checkpoint_path) if checkpoint_path else None
        driver = ExecutionDriver(
            work_plan,
            execution_plan,
            runner,
            ArtifactRegistry(workspace_root),
            checkpoint_store=checkpoint,
            max_repair_attempts=max_repair_attempts,
        )
        return profile, driver

    def resolve_github_execution_driver(
        self,
        goal: str,
        config: GitHubTransactionConfig,
        *,
        checkpoint_path: Path | str | None = None,
        target_truth: dict[str, str] | None = None,
        max_repair_attempts: int = 2,
    ) -> tuple[GoalInterpretation, ExecutionDriver, GitHubProductionRunner]:
        """Bind canonical P1.5/P1.6 execution to the governed P1.7 GitHub transaction runner."""
        runner = GitHubProductionRunner(config)
        checkpoint = checkpoint_path or (runner.transaction_root / "execution-checkpoint.json")
        profile, driver = self.resolve_execution_driver(
            goal,
            runner,
            workspace_root=runner.artifact_root,
            checkpoint_path=checkpoint,
            target_truth=target_truth,
            max_repair_attempts=max_repair_attempts,
        )
        return profile, driver, runner

    @classmethod
    def _nearest_active_stage(cls, resolved: ResolvedFlow, requested: str) -> ResolvedStage:
        stages = {stage.id: stage for stage in resolved.stages}
        if requested in stages:
            return stages[requested]
        requested_index = cls.HIGH_LEVEL_ORDER.index(requested)
        candidates = [
            (abs(cls.HIGH_LEVEL_ORDER.index(stage.id) - requested_index), cls.HIGH_LEVEL_ORDER.index(stage.id), stage)
            for stage in resolved.stages
            if stage.id in cls.HIGH_LEVEL_ORDER
        ]
        if not candidates:
            raise ValueError(f"Resolved flow {resolved.id} exposes no Factory-compatible stages")
        candidates.sort(key=lambda item: (item[0], item[1]))
        return candidates[0][2]

    def resolve_skill_names(
        self,
        factory_stage: str,
        goal: str,
        target_truth: dict[str, str] | None = None,
    ) -> tuple[GoalInterpretation, list[str], list[str]]:
        flow_stage_id = self.FACTORY_TO_FLOW_STAGE.get(factory_stage)
        if not flow_stage_id:
            raise ValueError(f"No declarative flow mapping for Factory stage: {factory_stage}")

        contract = self.resolve_contract(goal, target_truth=target_truth)
        profile = contract.profile
        selected: list[str] = []
        mandatory: list[str] = []

        if contract.routing_mode == "sequence":
            work_plan = self.sequence_planner.plan_sequence(contract)
            for work_segment in work_plan.segments:
                if flow_stage_id not in work_segment.active_stage_ids:
                    continue
                stage = self._nearest_active_stage(work_segment.flow, flow_stage_id)
                mandatory.extend(stage.mandatory_skills)
                selected.extend(stage.skills)
            if not selected:
                return profile, [], []
        else:
            resolved = self.sequence_planner.plan_single(contract)
            stage = self._nearest_active_stage(resolved, flow_stage_id)
            mandatory.extend(stage.mandatory_skills)
            selected.extend(stage.skills)

        selected.extend(self.EXTRA_BY_FACTORY_STAGE.get(factory_stage, ()))

        if (
            factory_stage == "implementation"
            and profile.mode == "interactive-prototype"
            and self.COMPLEX_PROTOTYPE_FEATURES.intersection(profile.features)
        ):
            selected.append(ANTHROPIC_WEB_ARTIFACTS)
        if factory_stage == "repair":
            selected.extend(("web-ui-code-review", "state-feedback-and-error-recovery"))
        return profile, _unique(selected), _unique(mandatory)

    def resolve_paths(
        self,
        factory_stage: str,
        goal: str,
        target_truth: dict[str, str] | None = None,
    ) -> tuple[GoalInterpretation, list[str], list[str]]:
        profile, selected, mandatory = self.resolve_skill_names(
            factory_stage,
            goal,
            target_truth=target_truth,
        )
        missing = [name for name in selected if not (self.skills_root / name / "SKILL.md").is_file()]
        if missing:
            submodule_hint = ""
            if any(name.startswith("upstream/anthropic-skills/") for name in missing):
                submodule_hint = " Run: git submodule update --init --recursive."
            raise FileNotFoundError(
                "Declarative flow references missing skills: " + ", ".join(missing) + submodule_hint
            )
        return (
            profile,
            [f"{name}/SKILL.md" for name in selected],
            [f"{name}/SKILL.md" for name in mandatory],
        )

    def resolved_factory_stages(
        self,
        goal: str,
        target_truth: dict[str, str] | None = None,
    ) -> tuple[GoalInterpretation, ResolvedFlow | ResolvedWorkPlan, list[str]]:
        """Expose canonical routing plus the compatible detailed Factory stage view."""
        contract = self.resolve_contract(goal, target_truth=target_truth)
        if contract.routing_mode == "sequence":
            work_plan = self.sequence_planner.plan_sequence(contract)
            active = {
                stage_id
                for segment in work_plan.segments
                for stage_id in segment.active_stage_ids
            }
            detailed = [stage for stage, owner in self.FACTORY_TO_FLOW_STAGE.items() if owner in active]
            return contract.profile, work_plan, detailed

        resolved = self.sequence_planner.plan_single(contract)
        active = {stage.id for stage in resolved.stages}
        detailed = [stage for stage, owner in self.FACTORY_TO_FLOW_STAGE.items() if owner in active]
        return contract.profile, resolved, detailed
