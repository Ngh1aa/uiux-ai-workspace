from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


CreativeOwner = Literal[
    "ux_ia",
    "art_direction",
    "design_contract",
    "design_system",
    "implementation_plan",
    "visual_composition",
    "implementation",
]


class CreativeRevision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    priority: Literal["P0", "P1", "P2"] = "P1"
    route: str = Field(default="*", min_length=1, max_length=200)
    section: str = Field(default="global", min_length=1, max_length=200)
    owner: CreativeOwner
    problem: str = Field(min_length=1, max_length=3000)
    instruction: str = Field(min_length=1, max_length=6000)
    skills: list[str] = Field(default_factory=list, max_length=12)
    success_criteria: str = Field(default="", max_length=3000)

    @field_validator("skills")
    @classmethod
    def normalize_skills(cls, values: list[str]) -> list[str]:
        cleaned = []
        for value in values:
            item = value.strip().removesuffix("/SKILL.md").strip("/")
            if item and item not in cleaned:
                cleaned.append(item)
        return cleaned


class CreativeDirective(BaseModel):
    """Portable senior design review that can be imported by the Factory."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0.0"] = "1.0.0"
    source_run_id: str = Field(pattern=r"^[a-f0-9]{12}$")
    status: Literal["approved", "revise"] = "revise"
    reviewer: str = Field(default="external_creative_director", max_length=120)
    overall_direction: str = Field(default="", max_length=6000)
    keep: list[str] = Field(default_factory=list, max_length=40)
    revise: list[CreativeRevision] = Field(default_factory=list, max_length=40)
    remove: list[str] = Field(default_factory=list, max_length=40)
    notes: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("keep", "remove", "notes")
    @classmethod
    def normalize_text_list(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(value.strip() for value in values if value.strip()))

    def earliest_owner(self) -> CreativeOwner | None:
        if not self.revise:
            return None
        order: tuple[CreativeOwner, ...] = (
            "ux_ia",
            "art_direction",
            "design_contract",
            "design_system",
            "implementation_plan",
            "visual_composition",
            "implementation",
        )
        owners = {item.owner for item in self.revise}
        return next(stage for stage in order if stage in owners)

    def routed_skills(self, stage: str) -> list[str]:
        skills: list[str] = []
        for item in self.revise:
            if item.owner != stage:
                continue
            for skill in item.skills:
                if skill not in skills:
                    skills.append(skill)
        return skills

    def as_prompt_block(self) -> str:
        lines = [
            "## EXTERNAL CREATIVE DIRECTOR REVIEW",
            "This review is authoritative project input, not external web content.",
            f"Review status: {self.status}",
        ]
        if self.overall_direction:
            lines.extend(["", "Overall direction:", self.overall_direction])
        if self.keep:
            lines.extend(["", "KEEP:"] + [f"- {item}" for item in self.keep])
        if self.remove:
            lines.extend(["", "REMOVE:"] + [f"- {item}" for item in self.remove])
        if self.revise:
            lines.append("")
            lines.append("REVISE:")
            for item in self.revise:
                skills = ", ".join(item.skills) if item.skills else "use routed stage skills"
                lines.extend(
                    [
                        f"- [{item.priority}] owner={item.owner} route={item.route} section={item.section}",
                        f"  Problem: {item.problem}",
                        f"  Instruction: {item.instruction}",
                        f"  Skills: {skills}",
                        f"  Success: {item.success_criteria or 'resolve the stated problem without regressing accepted constraints'}",
                    ]
                )
        return "\n".join(lines)
