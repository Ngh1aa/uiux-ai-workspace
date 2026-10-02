from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


LifecyclePhase = Literal[
    "INTAKE",
    "INTERPRET",
    "PLAN",
    "RESEARCH",
    "DESIGN",
    "IMPLEMENT",
    "QA",
    "REPLAN",
    "FINALIZE",
    "RELEASE",
]
SupportKind = Literal["native", "flow_stage", "external_controller", "not_exposed"]


@dataclass(frozen=True)
class LifecycleSurfacePhase:
    phase: LifecyclePhase
    support: SupportKind
    owner: str
    entrypoints: tuple[str, ...]
    input_contract: str
    output_contract: str
    evidence_contract: str
    authority_contract: str
    side_effects: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class LifecycleSurfaceProfile:
    surface_id: Literal["factory_product", "managed_flow"]
    top_level_entrypoint: str
    state_model: str
    phases: tuple[LifecycleSurfacePhase, ...]

    def phase(self, phase: LifecyclePhase) -> LifecycleSurfacePhase:
        for item in self.phases:
            if item.phase == phase:
                return item
        raise KeyError(phase)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class LifecycleReconciliation:
    schema_version: Literal["lifecycle-reconciliation.v1"]
    factory: LifecycleSurfaceProfile
    managed: LifecycleSurfaceProfile
    shared_invariants: tuple[str, ...]
    non_parity: tuple[str, ...]
    adapter_required: Literal[True] = True
    execution_effect: Literal["none"] = "none"
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"
    release_effect: Literal["none"] = "none"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def factory_lifecycle_profile() -> LifecycleSurfaceProfile:
    return LifecycleSurfaceProfile(
        surface_id="factory_product",
        top_level_entrypoint="uiux-factory/run.py::main",
        state_model="core.runtime.run_context.RunContext",
        phases=(
            LifecycleSurfacePhase(
                "INTAKE",
                "native",
                "uiux-factory/run.py",
                ("_resolve_goal", "main"),
                "natural-language goal + optional DesignContext/run/revision inputs",
                "exclusive Factory run slot + initialized manager invocation",
                "input/run provenance artifacts only; no QA evidence implied",
                "caller selects engine/runtime inputs; release authority is not granted here",
                ("acquire RunLock",),
            ),
            LifecycleSurfacePhase(
                "INTERPRET",
                "native",
                "core/manager/ + core/orchestration/intelligent_flow.py",
                ("CreativeDirectorDevelopmentManager.run", "ProfessionalWebsiteFlow"),
                "goal + DesignContext",
                "Factory flow/task interpretation used by downstream stage routing",
                "interpretation/plan artifacts are context, not gate evidence",
                "canonical runtime/flow policy bounds execution",
            ),
            LifecycleSurfacePhase(
                "PLAN",
                "native",
                "core/manager/provider_intelligent_manager.py",
                ("_save_flow_plan", "_run_reference_analysis"),
                "interpreted goal/context + routed skills/runtime preset",
                "flow-plan/reference/governance planning artifacts",
                "planning artifacts do not satisfy rendered/runtime gates",
                "manager owns product-stage sequencing; providers do not",
                ("write run artifacts",),
            ),
            LifecycleSurfacePhase(
                "RESEARCH",
                "native",
                "core/manager/",
                ("_run_research",),
                "goal/context/reference analysis",
                "research artifact",
                "research provenance may support decisions but does not prove runtime UI quality",
                "bounded by manager/runtime/tool policy",
                ("write research artifact",),
            ),
            LifecycleSurfacePhase(
                "DESIGN",
                "native",
                "core/manager/",
                (
                    "_run_ux_ia",
                    "_run_art_direction",
                    "_run_design_contract",
                    "_run_design_system",
                    "_run_implementation_plan",
                    "_run_visual_composition",
                ),
                "research + project/design context",
                "UX/IA, art direction, design contract/system, implementation plan, visual composition",
                "design artifacts express decisions/contracts; rendered QA remains separate",
                "manager + human creative governance retain design/revision authority",
                ("write design artifacts",),
            ),
            LifecycleSurfacePhase(
                "IMPLEMENT",
                "native",
                "core/manager/provider_intelligent_manager.py",
                ("_run_ai_implementation", "_run_template_implementation", "_run_external_handoff"),
                "implementation/visual contracts + selected engine",
                "implemented project or bounded external handoff",
                "implementation output is not automatically trusted QA evidence",
                "engine/provider cannot self-authorize gates/release",
                ("project/file mutation for authorized internal path", "external handoff artifact"),
            ),
            LifecycleSurfacePhase(
                "QA",
                "native",
                "core/manager/ + uiux-factory/qa/",
                ("_run_quality_loop",),
                "implemented target + runtime/browser/visual QA tooling",
                "quality-loop result + canonical QA artifacts",
                "trusted runtime/browser/validator evidence remains owned by existing evidence/QA layers",
                "gate truth remains canonical evidence-driven runtime policy",
                ("browser/render/validator observation", "bounded repair loop"),
            ),
            LifecycleSurfacePhase(
                "REPLAN",
                "native",
                "core/orchestration/skill_governance.py + manager quality/revision loops",
                ("FlowReplanner", "CreativeDirectorDevelopmentManager.run_revision"),
                "root cause / review directive / failed quality condition",
                "bounded revised downstream execution path",
                "prior evidence is preserved or invalidated according to stage ownership; no synthetic PASS",
                "human/manager/runtime policy bounds replanning",
                ("invalidate/rerun downstream work",),
            ),
            LifecycleSurfacePhase(
                "FINALIZE",
                "native",
                "core/runtime/run_context.py + manager",
                ("RunContext.complete",),
                "completed canonical Factory stages",
                "terminal Factory run state/artifact set",
                "completion status is distinct from production release evidence",
                "manager may complete a run but does not gain production release authority",
                ("persist terminal run state",),
            ),
            LifecycleSurfacePhase(
                "RELEASE",
                "not_exposed",
                "separate release/deployment workflows",
                (),
                "n/a in default run.py product lifecycle",
                "no production deployment performed by default run.py",
                "release truth requires separate governed evidence/workflow",
                "no implicit release authority",
            ),
        ),
    )


def managed_lifecycle_profile() -> LifecycleSurfaceProfile:
    return LifecycleSurfaceProfile(
        surface_id="managed_flow",
        top_level_entrypoint="skills_UIUX/scripts/uiux-agent.py --managed",
        state_model="core.runtime.flow_os.managed.ManagedWebsiteRun",
        phases=(
            LifecycleSurfacePhase(
                "INTAKE",
                "native",
                "skills_UIUX/scripts/uiux-agent.py",
                ("main", "_managed_overrides"),
                "--task/--project + authority + optional declarative overrides",
                "ProviderNeutralAgentHarness + managed run invocation",
                "CLI/task metadata is context, not gate evidence",
                "caller authority is bounded by runtime policy",
            ),
            LifecycleSurfacePhase(
                "INTERPRET",
                "native",
                "core/runtime/flow_os/managed.py",
                ("ManagedFlowController.interpret_goal", "ManagedFlowController.start_from_goal"),
                "natural-language task + bounded overrides",
                "canonical GoalInterpreter task context",
                "interpreted task context is not runtime evidence",
                "requested authority can reduce but never increase caller authority",
            ),
            LifecycleSurfacePhase(
                "PLAN",
                "native",
                "core/runtime/flow_os/managed.py",
                ("ManagedFlowController.resolve_flow", "ManagedFlowController.start"),
                "task context + optional additional/excluded skills",
                "canonical ResolvedFlow + first active stage + checkpoint",
                "planning/memory context cannot satisfy gates",
                "FlowPlanner is canonical routing owner",
                ("create managed checkpoint",),
            ),
            LifecycleSurfacePhase(
                "RESEARCH",
                "flow_stage",
                "core/runtime/flow_os/managed.py + resolved flow",
                ("ManagedFlowController.start_stage",),
                "active resolved research stage when present",
                "specialist RunState/checkpoint",
                "stage evidence only becomes gate-relevant through canonical evidence handling",
                "stage agent/authority capped by flow/runtime policy",
                ("isolated specialist execution",),
            ),
            LifecycleSurfacePhase(
                "DESIGN",
                "flow_stage",
                "core/runtime/flow_os/managed.py + resolved flow",
                ("ManagedFlowController.start_stage",),
                "active resolved design stage(s) when present",
                "specialist RunState/checkpoint",
                "model/provider claims remain non-evidence until observed/validated",
                "flow owns stage order and agent routing",
                ("isolated specialist execution",),
            ),
            LifecycleSurfacePhase(
                "IMPLEMENT",
                "flow_stage",
                "core/runtime/flow_os/provider_runner.py + managed.py",
                ("ProviderManagedRunner.run_active_stage", "ManagedFlowController.start_stage"),
                "active implementation stage + provider/tool policy",
                "specialist state/actions/artifacts",
                "provider output cannot self-satisfy trusted gates",
                "bounded tools/authority; flow owns routing",
                ("authorized isolated worktree/tool actions",),
            ),
            LifecycleSurfacePhase(
                "QA",
                "flow_stage",
                "core/runtime/flow_os/ + browser evidence adapters",
                ("ManagedFlowController.start_stage", "ManagedFlowController.complete_stage"),
                "active QA stage + observations/browser/validator evidence",
                "completed QA specialist stage or blocked/failed state",
                "latest-effective trusted evidence drives terminal evaluation",
                "human-marked gates may require explicit approval",
                ("capture/attach evidence", "checkpoint stage outcome"),
            ),
            LifecycleSurfacePhase(
                "REPLAN",
                "native",
                "core/runtime/flow_os/managed.py",
                ("ManagedFlowController.replan",),
                "active stage + declarative replan signal/current context",
                "ReplanDecision and optionally revised ResolvedFlow/checkpoint",
                "advisory memory is stripped from canonical replanning policy",
                "FlowPlanner decides bounded replan; caller/provider cannot bypass it",
                ("invalidate downstream completed stages on accepted applied replan",),
            ),
            LifecycleSurfacePhase(
                "FINALIZE",
                "external_controller",
                "core/runtime/flow_os/release.py",
                ("ProductionReleaseController.finalize_workspace",),
                "completed/eligible managed run + external_write authority",
                "committed/merged isolated worktree result",
                "finalization does not manufacture QA/release evidence",
                "requires explicit authority and release-controller checks",
                ("commit/fast-forward merge/optional worktree cleanup",),
            ),
            LifecycleSurfacePhase(
                "RELEASE",
                "external_controller",
                "core/runtime/flow_os/release.py",
                ("ProductionReleaseController.deploy_production",),
                "eligible managed run + release authority + explicit PRODUCTION confirmation",
                "production deploy result",
                "release eligibility remains evidence/policy-driven",
                "requires explicit release authority and confirmation",
                ("production deployment via configured adapter",),
            ),
        ),
    )


def current_lifecycle_reconciliation() -> LifecycleReconciliation:
    return LifecycleReconciliation(
        schema_version="lifecycle-reconciliation.v1",
        factory=factory_lifecycle_profile(),
        managed=managed_lifecycle_profile(),
        shared_invariants=(
            "canonical GoalInterpreter/FlowPlanner remain routing owners",
            "provider/model prose is not trusted evidence",
            "memory is advisory and cannot satisfy current-run gates",
            "human/runtime authority cannot be escalated by natural language or provider output",
            "release authority is separate from run/stage completion",
        ),
        non_parity=(
            "Factory exposes one async product pipeline while managed execution exposes explicit checkpoint/stage operations",
            "Factory design lifecycle has named domain stages; managed research/design/implementation/QA are resolved declarative flow stages",
            "Factory default run finalizes RunContext but does not expose production deployment; managed CLI has separate finalize/release controller actions",
            "Factory creative revision is source-run/downstream-stage aware; managed replanning is declarative signal/flow-revision based",
            "Factory product artifacts and ManagedWebsiteRun checkpoints use different top-level state schemas",
        ),
    )
