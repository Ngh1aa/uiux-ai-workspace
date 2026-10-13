from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel, Field, field_validator

from core.contracts.spec_profile import SpecProfile


SPEC_UPSTREAM_ARTIFACTS = {
    "reference_analysis": "reference_analysis",
    "research": "research",
    "ux_ia": "ux_ia",
    "art_direction": "art_direction",
    "design_contract_content": "design_contract",
    "design_system_content": "design_system",
    "implementation_plan_content": "implementation_plan",
    "visual_composition_content": "visual_composition",
}


def specification_input_sha256(payload: dict) -> str:
    """Bind exact text of goal + eight owners; unrelated skill metadata is excluded."""
    inputs = {key: payload.get(key) for key in ("goal", *SPEC_UPSTREAM_ARTIFACTS)}
    if not all(isinstance(value, str) and value.strip() for value in inputs.values()):
        return ""
    # An explicit profile hint is also a compiler input when supplied.
    inputs["spec_profile"] = payload.get("spec_profile", "")
    return hashlib.sha256(json.dumps(inputs, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


class PromptPackGate(BaseModel):
    """Structural checks and upstream binding; never semantic or human validation."""

    upstream_binding_valid: bool = False
    goal_scope_consistent: bool = Field(default=False, description="Structural scope/domain and upstream binding; not semantic validation")
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
                self.upstream_binding_valid,
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
    schema_version: int = 2
    upstream_sha256: str = ""
    compiled_content_sha256: str = ""
    spec_profile: SpecProfile = "original_design"
    blocking_unknowns: list[str] = Field(default_factory=list)
    project_context: str = Field(min_length=80)
    research_prompt: str = Field(min_length=40)
    full_build_spec: str = Field(min_length=400)
    implementation_prompt: str = Field(min_length=120)
    qa_remediation_prompt: str = Field(min_length=120)
    gates: PromptPackGate

    def content_sha256(self) -> str:
        content = self.model_dump(include={"spec_profile", "project_context", "research_prompt",
                                          "full_build_spec", "implementation_prompt", "qa_remediation_prompt"})
        return hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

    def bind_compilation(self, payload: dict) -> None:
        """Called only by deterministic compiler owners, never on provider refinement."""
        self.upstream_sha256 = specification_input_sha256(payload)
        self.compiled_content_sha256 = self.content_sha256()

    def binding_matches(self, payload: dict) -> bool:
        expected = specification_input_sha256(payload)
        return bool(self.schema_version == 2 and expected and self.upstream_sha256 == expected
                    and self.compiled_content_sha256 == self.content_sha256())

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
