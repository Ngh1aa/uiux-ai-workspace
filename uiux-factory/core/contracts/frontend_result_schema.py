from typing import Literal

from pydantic import BaseModel, Field


class GeneratedFile(BaseModel):
    path: str
    kind: str


class SkillEvidence(BaseModel):
    name: str
    relative_path: str
    sha256: str
    rule_count: int = 0


class FrontendBuildGate(BaseModel):
    workspace_guardrail_passed: bool = False
    root_index_created: bool = False
    github_pages_static_tree_created: bool = False
    next_source_created: bool = False

    visual_composition_consumed: bool = False
    required_skills_loaded: bool = False
    semantic_html_passed: bool = False
    responsive_contract_passed: bool = False
    focus_contract_passed: bool = False
    technical_copy_gate_passed: bool = False

    ready_for_dependency_install: bool = False
    build_verified: bool = False


class FrontendResult(BaseModel):
    schema_version: str = "0.2.0"

    status: Literal[
        "generated",
        "blocked",
    ] = "generated"

    project_slug: str
    project_dir: str

    github_pages_entry: str
    next_app_dir: str

    files: list[GeneratedFile] = Field(
        default_factory=list
    )

    skills_used: list[SkillEvidence] = Field(
        default_factory=list
    )

    policy_checks: dict[str, bool] = Field(
        default_factory=dict
    )

    commands: list[str] = Field(
        default_factory=list
    )

    unresolved_items: list[str] = Field(
        default_factory=list
    )

    gates: FrontendBuildGate

    generated_by: str = "FrontendEngineerV2"
