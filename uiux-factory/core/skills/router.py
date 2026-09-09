from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.orchestration.intelligent_flow import GoalInterpreter, ProfessionalWebsiteFlow
from core.skills.execution_context import SkillSelection


@dataclass(frozen=True)
class RoutedSkill:
    path: str
    reason: str


class AdaptiveSkillRouter:
    """Route real skills_UIUX paths using its declarative professional website flow."""

    _interpreter = GoalInterpreter()

    @classmethod
    def infer_domain(cls, goal: str) -> str:
        return cls._interpreter.interpret(goal).website_type

    @classmethod
    def route(
        cls,
        stage: str,
        goal: str,
        domain: str | None = None,
        skills_root: Path | None = None,
    ) -> SkillSelection:
        if skills_root is None:
            workspace_root = Path(__file__).resolve().parents[3]
            skills_root = workspace_root / "skills_UIUX"

        flow = ProfessionalWebsiteFlow(skills_root)
        profile, paths, mandatory_paths = flow.resolve_paths(stage, goal)
        resolved_domain = domain or profile.website_type

        reasons: dict[str, str] = {}
        mandatory = set(mandatory_paths)
        for path in paths:
            skill_name = path.removesuffix("/SKILL.md")
            if path in mandatory:
                reasons[path] = (
                    f"Mandatory capability from skills_UIUX professional website flow "
                    f"for {flow.FACTORY_TO_FLOW_STAGE[stage]} stage: {skill_name}."
                )
            else:
                reasons[path] = (
                    f"Domain/factory-stage capability selected for website_type="
                    f"{profile.website_type}: {skill_name}."
                )

        return SkillSelection(
            stage=stage,
            domain=resolved_domain,
            goal=goal,
            relative_paths=paths,
            mandatory_paths=mandatory_paths,
            reasons=reasons,
        )

    @classmethod
    def all_declared_paths(cls, skills_root: Path | None = None) -> set[str]:
        if skills_root is None:
            workspace_root = Path(__file__).resolve().parents[3]
            skills_root = workspace_root / "skills_UIUX"
        paths: set[str] = set()
        flow = ProfessionalWebsiteFlow(skills_root)
        document = flow.document
        for stage in document.get("stages", []):
            for skill in stage.get("required_skills", []):
                paths.add(f"{skill}/SKILL.md")
            for rule in stage.get("conditional_skills", []):
                for skill in rule.get("skills", []):
                    paths.add(f"{skill}/SKILL.md")
        for extras in flow.EXTRA_BY_FACTORY_STAGE.values():
            paths.update(f"{skill}/SKILL.md" for skill in extras)
        paths.update(
            {
                "web-ui-code-review/SKILL.md",
                "state-feedback-and-error-recovery/SKILL.md",
            }
        )
        return paths

    @classmethod
    def validate_declared_paths(cls, skills_root: Path) -> list[str]:
        return [
            relative_path
            for relative_path in sorted(cls.all_declared_paths(skills_root))
            if not (Path(skills_root) / relative_path).is_file()
        ]
