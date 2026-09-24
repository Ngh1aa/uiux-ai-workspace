from typing import Literal

from pydantic import BaseModel, Field


class QualityIteration(BaseModel):
    iteration: int
    browser_status: str
    browser_ready: bool
    critic_status: str | None = None
    critic_score: int | None = None
    issue_fingerprint: str | None = None
    repair_status: str | None = None
    applied_directives: int = 0
    deferred_directives: int = 0
    iteration_dir: str


class QualityLoopResult(BaseModel):
    schema_version: str = "0.2.0"

    status: Literal[
        "passed",
        "blocked",
        "stagnated",
        "max_iterations",
    ]

    project_slug: str
    project_dir: str

    max_iterations: int
    iterations: list[QualityIteration] = Field(
        default_factory=list
    )

    final_score: int | None = None
    stop_reason: str

    browser_report_path: str | None = None
    visual_critic_path: str | None = None
    repair_result_path: str | None = None

    generated_by: str = "QualityLoopRunnerV2"
