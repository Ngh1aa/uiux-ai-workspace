from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


SpecProfile = Literal[
    "pixel_faithful",
    "preserve_and_extend",
    "redesign",
    "original_design",
]


class PromptPackGate(BaseModel):
    goal_scope_consistent: bool = False
    preserve_change_consistent: bool = False
    responsive_scope_consistent: bool = False
    qa_maps_to_spec: bool = False
    implementation_reads_full_spec: bool = False
    no_hidden_chat_dependency: bool = False
    no_example_project_leakage: bool = False

    @property
    def passed(self) -> bool:
        return all(
            (
                self.goal_scope_consistent,
                self.preserve_change_consistent,
                self.responsive_scope_consistent,
                self.qa_maps_to_spec,
                self.implementation_reads_full_spec,
                self.no_hidden_chat_dependency,
                self.no_example_project_leakage,
            )
        )


class PromptPack(BaseModel):
    schema_version: int = 1
    spec_profile: SpecProfile = "original_design"
    blocking_unknowns: list[str] = Field(default_factory=list)
    project_context: str = Field(min_length=80)
    research_prompt: str = Field(min_length=40)
    full_build_spec: str = Field(min_length=400)
    implementation_prompt: str = Field(min_length=120)
    qa_remediation_prompt: str = Field(min_length=120)
    gates: PromptPackGate

    @field_validator("full_build_spec")
    @classmethod
    def validate_full_build_spec(cls, value: str) -> str:
        required = (
            "## 0. Mission",
            "## 1. Source of truth",
            "## 14. QA checklist",
            "## 15. Deliverables",
            "## 16. Definition of Done",
        )
        missing = [heading for heading in required if heading not in value]
        if missing:
            raise ValueError("Full build spec missing required headings: " + ", ".join(missing))
        return value

    @field_validator("implementation_prompt")
    @classmethod
    def validate_implementation_reads_spec(cls, value: str) -> str:
        if "02-FULL-BUILD-SPEC.md" not in value:
            raise ValueError("Implementation prompt must explicitly read 02-FULL-BUILD-SPEC.md")
        return value

    @field_validator("qa_remediation_prompt")
    @classmethod
    def validate_qa_reads_spec(cls, value: str) -> str:
        if "02-FULL-BUILD-SPEC.md" not in value:
            raise ValueError("QA/remediation prompt must evaluate against 02-FULL-BUILD-SPEC.md")
        return value
