from __future__ import annotations

import json
from pathlib import Path

from core.runtime.flow_os.flow import FlowPlanner, ResolvedFlow, ResolvedStage
from core.runtime.flow_os.task_context import (
    DEFAULT_DELIVERY_POLICY_ID,
    DEFAULT_FACTORY_DELIVERY_LANE,
    TASK_CONTRACT_VERSION,
    GoalInterpretation,
    GoalInterpreter,
    GoalProfile,
    TaskContract,
)


ANTHROPIC_SKILL_ROOT = "upstream/anthropic-skills/skills"
ANTHROPIC_FRONTEND_DESIGN = f"{ANTHROPIC_SKILL_ROOT}/frontend-design"
ANTHROPIC_WEBAPP_TESTING = f"{ANTHROPIC_SKILL_ROOT}/webapp-testing"
ANTHROPIC_SKILL_CREATOR = f"{ANTHROPIC_SKILL_ROOT}/skill-creator"
ANTHROPIC_WEB_ARTIFACTS = f"{ANTHROPIC_SKILL_ROOT}/web-artifacts-builder"
MOTION_COMPONENT_INTELLIGENCE = "motion-component-intelligence"


def _unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


class ProfessionalWebsiteFlow:
    """Factory specialist-stage adapter over the canonical Flow OS planner.

    Canonical GoalInterpreter owns Task Contract inference and canonical
    FlowPlanner owns flow selection, skill resolution and specialist composition.
    This adapter only maps the Factory's detailed stage vocabulary onto that
    resolved canonical flow and adds Factory-stage compatibility extras.
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

        # Compatibility view for Factory-local root-cause repair code. It is not
        # used for task/flow selection; the canonical FlowPlanner owns that.
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

    def resolve(
        self,
        goal: str,
        target_truth: dict[str, str] | None = None,
    ) -> tuple[GoalInterpretation, ResolvedFlow]:
        profile = self.interpreter.interpret(goal, target_truth=target_truth)
        return profile, self.planner.plan(profile.to_context())

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

        profile, resolved = self.resolve(goal, target_truth=target_truth)
        stage = self._nearest_active_stage(resolved, flow_stage_id)
        mandatory = list(stage.mandatory_skills)
        selected = list(stage.skills)
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
    ) -> tuple[GoalInterpretation, ResolvedFlow, list[str]]:
        """Expose canonical high-level routing plus the compatible detailed stage view."""
        profile, resolved = self.resolve(goal, target_truth=target_truth)
        active = {stage.id for stage in resolved.stages}
        detailed = [stage for stage, owner in self.FACTORY_TO_FLOW_STAGE.items() if owner in active]
        return profile, resolved, detailed
