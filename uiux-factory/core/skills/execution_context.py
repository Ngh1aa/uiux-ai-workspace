from __future__ import annotations

from hashlib import sha256
from typing import Any

from pydantic import BaseModel, Field


class SkillSource(BaseModel):
    name: str
    relative_path: str
    absolute_path: str
    sha256: str
    content_chars: int
    selected_sections: list[str] = Field(default_factory=list)
    rule_lines: list[str] = Field(default_factory=list)
    compiled_excerpt: str = ""


class SkillSelection(BaseModel):
    stage: str
    domain: str
    goal: str
    reasons: dict[str, str] = Field(default_factory=dict)
    relative_paths: list[str] = Field(default_factory=list)


class SkillExecutionContext(BaseModel):
    schema_version: str = "1.0.0"
    stage: str
    domain: str
    goal: str
    goal_sha256: str
    skills_root: str
    selection: SkillSelection
    sources: list[SkillSource] = Field(default_factory=list)
    upstream_artifacts: dict[str, str] = Field(default_factory=dict)
    compiled_instruction: str = ""
    evidence_dir: str = ""

    @classmethod
    def goal_hash(cls, goal: str) -> str:
        return sha256(goal.encode("utf-8")).hexdigest()

    def metadata(self) -> dict[str, Any]:
        return {
            "skill_runtime": self.schema_version,
            "skill_stage": self.stage,
            "skill_domain": self.domain,
            "skill_goal_sha256": self.goal_sha256,
            "skill_paths": [s.relative_path for s in self.sources],
            "skill_sha256": {s.relative_path: s.sha256 for s in self.sources},
            "skill_evidence_dir": self.evidence_dir,
        }
