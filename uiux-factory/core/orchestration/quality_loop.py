from __future__ import annotations

import json
from pathlib import Path

from core.agents.browser_qa_agent import BrowserQAAgent
from core.agents.repair_agent import RepairAgent
from core.agents.visual_critic import VisualCritic
from core.contracts.browser_qa_schema import BrowserQAResult
from core.contracts.quality_loop_schema import (
    QualityIteration,
    QualityLoopResult,
)
from core.contracts.repair_result_schema import RepairResult
from core.contracts.visual_critic_schema import VisualCriticResult
from core.team.team_runner import UIUXTeamRunner


class QualityLoopRunner:
    """
    BrowserQA -> VisualCritic -> Repair -> regression.

    V2 difference:
    every BrowserQA / VisualCritic / Repair role runs through UIUXTeamRunner,
    so MetaGPT Team + real skills_UIUX execution policy remains active during
    the quality loop too.
    """

    def __init__(
        self,
        *,
        team_runner: UIUXTeamRunner,
        run_context,
        max_iterations: int = 3,
        min_score_improvement: int = 1,
    ) -> None:
        if max_iterations < 1:
            raise ValueError(
                "max_iterations must be >= 1"
            )

        self.team_runner = team_runner
        self.run_context = run_context
        self.max_iterations = max_iterations
        self.min_score_improvement = min_score_improvement

    @staticmethod
    def fingerprint(
        critic: VisualCriticResult,
    ) -> str:
        rows = sorted(
            (
                issue.severity,
                issue.category,
                issue.route,
            )
            for issue in critic.issues
        )

        return json.dumps(
            rows,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    async def run(
        self,
        *,
        project_dir: Path,
        project_slug: str,
        output_dir: Path,
    ) -> QualityLoopResult:
        project_dir = Path(
            project_dir
        ).resolve()

        output_dir = Path(
            output_dir
        ).resolve()

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        iterations: list[
            QualityIteration
        ] = []

        previous_score = None
        previous_fingerprint = None

        latest_browser = None
        latest_critic = None
        latest_repair = None

        for iteration in range(
            1,
            self.max_iterations + 1,
        ):
            iteration_dir = (
                output_dir
                / "quality-loop"
                / f"iteration-{iteration:02d}"
            )

            iteration_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            browser_message = (
                await self.team_runner.run_role(
                    role_class=BrowserQAAgent,
                    stage="browser_qa",
                    instruction=json.dumps(
                        {
                            "project_dir": str(
                                project_dir
                            ),
                            "project_slug": (
                                project_slug
                            ),
                            "output_dir": str(
                                iteration_dir
                            ),
                        },
                        ensure_ascii=False,
                    ),
                    context=(
                        self.run_context
                    ),
                )
            )

            browser = (
                BrowserQAResult
                .model_validate_json(
                    browser_message.content
                )
            )

            browser_path = (
                iteration_dir
                / "browser-report.json"
            )

            browser_path.write_text(
                browser.model_dump_json(
                    indent=2
                ),
                encoding="utf-8",
            )

            latest_browser = (
                browser_path
            )

            current = QualityIteration(
                iteration=iteration,
                browser_status=(
                    browser.status
                ),
                browser_ready=(
                    browser.gates
                    .ready_for_visual_critic
                ),
                iteration_dir=str(
                    iteration_dir
                ),
            )

            if not (
                browser.gates
                .ready_for_visual_critic
            ):
                iterations.append(
                    current
                )

                return QualityLoopResult(
                    status="blocked",
                    project_slug=(
                        project_slug
                    ),
                    project_dir=str(
                        project_dir
                    ),
                    max_iterations=(
                        self.max_iterations
                    ),
                    iterations=iterations,
                    final_score=None,
                    stop_reason=(
                        "browser_qa_not_ready"
                    ),
                    browser_report_path=str(
                        browser_path
                    ),
                )

            critic_message = (
                await self.team_runner.run_role(
                    role_class=VisualCritic,
                    stage="visual_qa",
                    instruction=json.dumps(
                        {
                            "browser_report_path": str(
                                browser_path
                            )
                        },
                        ensure_ascii=False,
                    ),
                    context=(
                        self.run_context
                    ),
                )
            )

            critic = (
                VisualCriticResult
                .model_validate_json(
                    critic_message.content
                )
            )

            critic_path = (
                iteration_dir
                / "visual-critic.json"
            )

            critic_path.write_text(
                critic.model_dump_json(
                    indent=2
                ),
                encoding="utf-8",
            )

            latest_critic = (
                critic_path
            )

            current.critic_status = (
                critic.status
            )
            current.critic_score = (
                critic.score.overall
            )
            current.issue_fingerprint = (
                self.fingerprint(
                    critic
                )
            )

            if critic.status == "passed":
                iterations.append(
                    current
                )

                return QualityLoopResult(
                    status="passed",
                    project_slug=(
                        project_slug
                    ),
                    project_dir=str(
                        project_dir
                    ),
                    max_iterations=(
                        self.max_iterations
                    ),
                    iterations=iterations,
                    final_score=(
                        critic.score.overall
                    ),
                    stop_reason=(
                        "visual_critic_passed"
                    ),
                    browser_report_path=str(
                        browser_path
                    ),
                    visual_critic_path=str(
                        critic_path
                    ),
                )

            if not (
                critic.gates
                .ready_for_repair_agent
            ):
                iterations.append(
                    current
                )

                return QualityLoopResult(
                    status="blocked",
                    project_slug=(
                        project_slug
                    ),
                    project_dir=str(
                        project_dir
                    ),
                    max_iterations=(
                        self.max_iterations
                    ),
                    iterations=iterations,
                    final_score=(
                        critic.score.overall
                    ),
                    stop_reason=(
                        "critic_has_no_actionable_repair"
                    ),
                    browser_report_path=str(
                        browser_path
                    ),
                    visual_critic_path=str(
                        critic_path
                    ),
                )

            if (
                previous_score is not None
                and previous_fingerprint
                == current.issue_fingerprint
                and (
                    critic.score.overall
                    - previous_score
                    < self.min_score_improvement
                )
            ):
                iterations.append(
                    current
                )

                return QualityLoopResult(
                    status="stagnated",
                    project_slug=(
                        project_slug
                    ),
                    project_dir=str(
                        project_dir
                    ),
                    max_iterations=(
                        self.max_iterations
                    ),
                    iterations=iterations,
                    final_score=(
                        critic.score.overall
                    ),
                    stop_reason=(
                        "same_issue_fingerprint_without_"
                        "minimum_score_improvement"
                    ),
                    browser_report_path=str(
                        browser_path
                    ),
                    visual_critic_path=str(
                        critic_path
                    ),
                )

            if iteration >= self.max_iterations:
                iterations.append(
                    current
                )

                return QualityLoopResult(
                    status="max_iterations",
                    project_slug=(
                        project_slug
                    ),
                    project_dir=str(
                        project_dir
                    ),
                    max_iterations=(
                        self.max_iterations
                    ),
                    iterations=iterations,
                    final_score=(
                        critic.score.overall
                    ),
                    stop_reason=(
                        "max_iterations_reached"
                    ),
                    browser_report_path=str(
                        browser_path
                    ),
                    visual_critic_path=str(
                        critic_path
                    ),
                )

            repair_message = (
                await self.team_runner.run_role(
                    role_class=RepairAgent,
                    stage="repair",
                    instruction=json.dumps(
                        {
                            "visual_critic_path": str(
                                critic_path
                            ),
                            "browser_report_path": str(
                                browser_path
                            ),
                            "output_dir": str(
                                iteration_dir
                            ),
                        },
                        ensure_ascii=False,
                    ),
                    context=(
                        self.run_context
                    ),
                )
            )

            repair = (
                RepairResult
                .model_validate_json(
                    repair_message.content
                )
            )

            repair_path = (
                iteration_dir
                / "repair-result.json"
            )

            repair_path.write_text(
                repair.model_dump_json(
                    indent=2
                ),
                encoding="utf-8",
            )

            latest_repair = (
                repair_path
            )

            current.repair_status = (
                repair.status
            )
            current.applied_directives = (
                repair.applied_directives
            )
            current.deferred_directives = (
                repair.deferred_directives
            )

            iterations.append(
                current
            )

            if (
                repair.status
                in (
                    "blocked",
                    "noop",
                )
                or repair.applied_directives
                == 0
            ):
                return QualityLoopResult(
                    status="blocked",
                    project_slug=(
                        project_slug
                    ),
                    project_dir=str(
                        project_dir
                    ),
                    max_iterations=(
                        self.max_iterations
                    ),
                    iterations=iterations,
                    final_score=(
                        critic.score.overall
                    ),
                    stop_reason=(
                        "repair_agent_made_no_change"
                    ),
                    browser_report_path=str(
                        browser_path
                    ),
                    visual_critic_path=str(
                        critic_path
                    ),
                    repair_result_path=str(
                        repair_path
                    ),
                )

            previous_score = (
                critic.score.overall
            )
            previous_fingerprint = (
                current.issue_fingerprint
            )

        return QualityLoopResult(
            status="max_iterations",
            project_slug=project_slug,
            project_dir=str(
                project_dir
            ),
            max_iterations=(
                self.max_iterations
            ),
            iterations=iterations,
            final_score=(
                previous_score
            ),
            stop_reason=(
                "loop_exhausted"
            ),
            browser_report_path=(
                str(latest_browser)
                if latest_browser
                else None
            ),
            visual_critic_path=(
                str(latest_critic)
                if latest_critic
                else None
            ),
            repair_result_path=(
                str(latest_repair)
                if latest_repair
                else None
            ),
        )
