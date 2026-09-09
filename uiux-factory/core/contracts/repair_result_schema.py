from typing import Literal

from pydantic import BaseModel, Field


class RepairActionLog(BaseModel):
    directive_priority: int
    route: str
    target: str
    action: str
    status: Literal["applied", "deferred"]
    evidence: str


class RepairGate(BaseModel):
    critic_consumed: bool = False
    browser_report_consumed: bool = False
    required_skills_loaded: bool = False
    backups_created: bool = False
    repair_overlay_created: bool = False
    html_links_injected: bool = False
    regression_required: bool = True


class RepairResult(BaseModel):
    schema_version: str = "0.1.0"

    status: Literal[
        "applied",
        "partial",
        "noop",
        "blocked",
    ]

    project_slug: str
    project_dir: str
    repair_css: str | None = None

    modified_files: list[str] = Field(default_factory=list)
    backup_files: list[str] = Field(default_factory=list)

    actions: list[RepairActionLog] = Field(default_factory=list)

    applied_directives: int = 0
    deferred_directives: int = 0

    skills_used: list[str] = Field(default_factory=list)

    gates: RepairGate

    notes: list[str] = Field(default_factory=list)

    generated_by: str = "RepairAgent"
