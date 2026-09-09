from __future__ import annotations

from pathlib import Path
from typing import Type

from metagpt.roles.role import Role

from core.events.run_event_bus import RunEventBus
from core.messages.artifact_message import make_stage_message
from core.skills.compiler import SkillInstructionCompiler
from core.skills.router import AdaptiveSkillRouter
from core.team.uiux_team import UIUXMetaTeam


class UIUXTeamRunner:
    """
    MetaGPT Team + real skills_UIUX execution bridge.

    It preserves the existing deterministic Actions while making the exact
    selected skill source part of each MetaGPT stage Message and durable run
    evidence.
    """

    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.workspace_root = self.root.parent
        self.skills_root = self.workspace_root / "skills_UIUX"

        if not self.skills_root.exists():
            raise FileNotFoundError(
                f"skills_UIUX sibling repository not found: {self.skills_root}"
            )

        self.meta_team = UIUXMetaTeam(root=self.root)
        self.compiler = SkillInstructionCompiler(skills_root=self.skills_root)
        self._event_buses: dict[str, RunEventBus] = {}

    def event_bus(self, context) -> RunEventBus:
        run_id = context.run_id

        if run_id in self._event_buses:
            return self._event_buses[run_id]

        bus = RunEventBus(
            event_path=Path(context.run_dir) / "events.jsonl",
            run_id=run_id,
        )
        self._event_buses[run_id] = bus

        if hasattr(context, "add_artifact"):
            if "events" not in getattr(context, "artifacts", {}):
                context.add_artifact("events", bus.event_path)

        bus.emit(
            "team.initialized",
            data={
                "engine": "MetaGPT.Team",
                "use_mgx": False,
                "skills_root": str(self.skills_root),
            },
        )
        return bus

    @staticmethod
    def upstream_artifacts(context) -> dict[str, str]:
        return {
            key: str(value)
            for key, value in getattr(context, "artifacts", {}).items()
            if value
        }

    async def run_role(
        self,
        *,
        role_class: Type[Role],
        stage: str,
        instruction: str,
        context,
    ):
        bus = self.event_bus(context)
        domain = AdaptiveSkillRouter.infer_domain(context.goal)
        selection = AdaptiveSkillRouter.route(
            stage=stage,
            goal=context.goal,
            domain=domain,
        )

        missing = AdaptiveSkillRouter.validate_declared_paths(self.skills_root)
        if missing:
            raise FileNotFoundError(
                "UIUX Factory refuses to start with missing/invented router skills:\n- "
                + "\n- ".join(missing)
            )

        bus.emit(
            "skills.resolving",
            stage=stage,
            data={
                "domain": domain,
                "requested_paths": selection.relative_paths,
            },
        )

        skill_context = self.compiler.build(
            selection=selection,
            run_dir=Path(context.run_dir),
            upstream_artifacts=self.upstream_artifacts(context),
        )

        skill_artifact = (
            Path(skill_context.evidence_dir)
            / "skill-context.json"
        )

        if hasattr(context, "add_artifact"):
            context.add_artifact(
                f"skill_context_{stage}",
                skill_artifact,
            )

        bus.emit(
            "skills.resolved",
            stage=stage,
            data={
                "domain": domain,
                "skills": [
                    {
                        "name": source.name,
                        "path": source.relative_path,
                        "sha256": source.sha256,
                        "sections": source.selected_sections,
                    }
                    for source in skill_context.sources
                ],
                "evidence": str(skill_artifact),
            },
        )

        role = self.meta_team.get_or_hire(role_class)
        enriched = self.compiler.enrich_instruction(
            instruction,
            skill_context,
        )
        if stage in {"art_direction", "visual_composition"}:
            from core.skills.frontend_design_policy import FRONTEND_DESIGN_POLICY
            # Keep the existing structured message envelope intact.
            if enriched.lstrip().startswith("{"):
                import json
                payload = json.loads(enriched)
                payload["frontend_design_policy"] = FRONTEND_DESIGN_POLICY
                enriched = json.dumps(payload, ensure_ascii=False)
            else:
                enriched += "\n\n## FRONTEND DESIGN POLICY\n" + FRONTEND_DESIGN_POLICY

        message = make_stage_message(
            content=enriched,
            role_name=role.name,
            stage=stage,
            run_id=context.run_id,
            skill_context=skill_context,
            extra_metadata={
                "agent_class": f"{role_class.__module__}.{role_class.__name__}",
            },
        )

        bus.emit(
            "agent.started",
            stage=stage,
            agent=role.name,
            data={
                "profile": role.profile,
                "role_class": role_class.__name__,
                "skill_count": len(skill_context.sources),
                "team_roles": self.meta_team.role_names(),
            },
        )

        try:
            result = await role.run(message)

            if not result:
                raise RuntimeError(
                    f"{role_class.__name__} returned no result."
                )

            bus.emit(
                "agent.completed",
                stage=stage,
                agent=role.name,
                data={
                    "profile": role.profile,
                    "result_chars": len(result.content or ""),
                },
            )

            return result

        except Exception as error:
            bus.emit(
                "agent.failed",
                stage=stage,
                agent=role.name,
                data={
                    "error_type": type(error).__name__,
                    "error": str(error),
                },
            )
            raise

        finally:
            self.meta_team.clear_message_buffers()
