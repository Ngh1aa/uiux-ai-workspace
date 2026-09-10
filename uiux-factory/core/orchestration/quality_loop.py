from __future__ import annotations

import json
from pathlib import Path

from core.agents.browser_qa_agent import BrowserQAAgent
from core.agents.repair_agent import RepairAgent
from core.agents.visual_critic import VisualCritic
from core.contracts.browser_qa_schema import BrowserQAResult
from core.contracts.quality_loop_schema import QualityIteration, QualityLoopResult
from core.contracts.repair_result_schema import RepairResult
from core.contracts.visual_critic_schema import VisualCriticResult
from core.team.team_runner import UIUXTeamRunner
from core.verification.evidence_contract import EvidenceContractEvaluator
from core.verification.post_render_evaluators import PostRenderEvaluatorSuite


class QualityLoopRunner:
    """BrowserQA -> VisualCritic -> post-render evidence -> 56-rule contract -> repair."""

    def __init__(
        self,
        *,
        team_runner: UIUXTeamRunner,
        run_context,
        max_iterations: int = 3,
        min_score_improvement: int = 1,
    ) -> None:
        if max_iterations < 1:
            raise ValueError("max_iterations must be >= 1")
        self.team_runner = team_runner
        self.run_context = run_context
        self.max_iterations = max_iterations
        self.min_score_improvement = min_score_improvement
        self.evidence_contract = EvidenceContractEvaluator()

    @staticmethod
    def fingerprint(critic: VisualCriticResult) -> str:
        rows = sorted((issue.severity, issue.category, issue.route) for issue in critic.issues)
        return json.dumps(rows, ensure_ascii=False, separators=(",", ":"))

    def _evaluate_acceptance(
        self,
        *,
        project_dir: Path,
        output_dir: Path,
        browser_path: Path,
        critic_path: Path,
    ):
        report = self.evidence_contract.evaluate(
            run_id=self.run_context.run_id,
            run_dir=self.run_context.run_dir,
            project_dir=project_dir,
            browser_report_path=browser_path,
            visual_critic_path=critic_path,
        )
        acceptance_path = output_dir / "prototype-acceptance.json"
        acceptance_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        if output_dir.resolve() == self.run_context.run_dir.resolve():
            self.run_context.add_artifact("prototype_acceptance", acceptance_path)
        self.team_runner.event_bus(self.run_context).emit(
            "verification.prototype_acceptance_evaluated",
            stage="visual_qa",
            data={
                "artifact": str(acceptance_path.resolve()),
                "registry_version": report.registry_version,
                "machine_status": report.machine_status,
                "final_status": report.final_status,
                "summary": report.summary.model_dump(),
                "project_digest": report.project_digest,
                "stale_evidence_count": report.stale_evidence_count,
            },
        )
        return report, acceptance_path

    async def _run_post_render_evidence(
        self,
        *,
        project_dir: Path,
        browser_path: Path,
        iteration_dir: Path,
    ) -> dict[str, str]:
        suite = PostRenderEvaluatorSuite(
            run_dir=self.run_context.run_dir,
            project_dir=project_dir,
            browser_report_path=browser_path,
            evidence_dir=iteration_dir / "verification-evidence",
        )
        try:
            outputs = await suite.run()
        except Exception as exc:
            self.team_runner.event_bus(self.run_context).emit(
                "verification.post_render_evaluators_failed",
                stage="visual_qa",
                data={"error": f"{type(exc).__name__}: {exc}"},
            )
            return {}

        for name, raw_path in outputs.items():
            path = Path(raw_path)
            if path.is_file():
                self.run_context.add_artifact(f"verification_{name}", path)
        self.team_runner.event_bus(self.run_context).emit(
            "verification.post_render_evaluators_completed",
            stage="visual_qa",
            data={"artifacts": outputs},
        )
        return outputs

    async def run(
        self,
        *,
        project_dir: Path,
        project_slug: str,
        output_dir: Path,
    ) -> QualityLoopResult:
        project_dir = Path(project_dir).resolve()
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        iterations: list[QualityIteration] = []
        previous_score = None
        previous_fingerprint = None
        latest_browser = None
        latest_critic = None
        latest_repair = None

        for iteration in range(1, self.max_iterations + 1):
            iteration_dir = output_dir / "quality-loop" / f"iteration-{iteration:02d}"
            iteration_dir.mkdir(parents=True, exist_ok=True)

            browser_message = await self.team_runner.run_role(
                role_class=BrowserQAAgent,
                stage="browser_qa",
                instruction=json.dumps(
                    {
                        "project_dir": str(project_dir),
                        "project_slug": project_slug,
                        "output_dir": str(iteration_dir),
                    },
                    ensure_ascii=False,
                ),
                context=self.run_context,
            )
            browser = BrowserQAResult.model_validate_json(browser_message.content)
            browser_path = iteration_dir / "browser-report.json"
            browser_path.write_text(browser.model_dump_json(indent=2), encoding="utf-8")
            latest_browser = browser_path

            current = QualityIteration(
                iteration=iteration,
                browser_status=browser.status,
                browser_ready=browser.gates.ready_for_visual_critic,
                iteration_dir=str(iteration_dir),
            )

            if not browser.gates.ready_for_visual_critic:
                iterations.append(current)
                return QualityLoopResult(
                    status="blocked",
                    project_slug=project_slug,
                    project_dir=str(project_dir),
                    max_iterations=self.max_iterations,
                    iterations=iterations,
                    final_score=None,
                    stop_reason="browser_qa_not_ready",
                    browser_report_path=str(browser_path),
                )

            critic_message = await self.team_runner.run_role(
                role_class=VisualCritic,
                stage="visual_qa",
                instruction=json.dumps({"browser_report_path": str(browser_path)}, ensure_ascii=False),
                context=self.run_context,
            )
            critic = VisualCriticResult.model_validate_json(critic_message.content)
            critic_path = iteration_dir / "visual-critic.json"
            critic_path.write_text(critic.model_dump_json(indent=2), encoding="utf-8")
            latest_critic = critic_path

            current.critic_status = critic.status
            current.critic_score = critic.score.overall
            current.issue_fingerprint = self.fingerprint(critic)

            if critic.status == "passed":
                iterations.append(current)
                await self._run_post_render_evidence(
                    project_dir=project_dir,
                    browser_path=browser_path,
                    iteration_dir=iteration_dir,
                )
                acceptance, _acceptance_path = self._evaluate_acceptance(
                    project_dir=project_dir,
                    output_dir=output_dir,
                    browser_path=browser_path,
                    critic_path=critic_path,
                )
                if acceptance.machine_status != "passed":
                    return QualityLoopResult(
                        status="blocked",
                        project_slug=project_slug,
                        project_dir=str(project_dir),
                        max_iterations=self.max_iterations,
                        iterations=iterations,
                        final_score=critic.score.overall,
                        stop_reason="prototype_evidence_contract_blocked",
                        browser_report_path=str(browser_path),
                        visual_critic_path=str(critic_path),
                    )
                return QualityLoopResult(
                    status="passed",
                    project_slug=project_slug,
                    project_dir=str(project_dir),
                    max_iterations=self.max_iterations,
                    iterations=iterations,
                    final_score=critic.score.overall,
                    stop_reason=(
                        "prototype_machine_pass_human_review_required"
                        if acceptance.final_status == "human_review_required"
                        else "prototype_final_approved"
                    ),
                    browser_report_path=str(browser_path),
                    visual_critic_path=str(critic_path),
                )

            if not critic.gates.ready_for_repair_agent:
                iterations.append(current)
                return QualityLoopResult(
                    status="blocked",
                    project_slug=project_slug,
                    project_dir=str(project_dir),
                    max_iterations=self.max_iterations,
                    iterations=iterations,
                    final_score=critic.score.overall,
                    stop_reason="critic_has_no_actionable_repair",
                    browser_report_path=str(browser_path),
                    visual_critic_path=str(critic_path),
                )

            if (
                previous_score is not None
                and previous_fingerprint == current.issue_fingerprint
                and critic.score.overall - previous_score < self.min_score_improvement
            ):
                iterations.append(current)
                return QualityLoopResult(
                    status="stagnated",
                    project_slug=project_slug,
                    project_dir=str(project_dir),
                    max_iterations=self.max_iterations,
                    iterations=iterations,
                    final_score=critic.score.overall,
                    stop_reason="same_issue_fingerprint_without_minimum_score_improvement",
                    browser_report_path=str(browser_path),
                    visual_critic_path=str(critic_path),
                )

            if iteration >= self.max_iterations:
                iterations.append(current)
                return QualityLoopResult(
                    status="max_iterations",
                    project_slug=project_slug,
                    project_dir=str(project_dir),
                    max_iterations=self.max_iterations,
                    iterations=iterations,
                    final_score=critic.score.overall,
                    stop_reason="max_iterations_reached",
                    browser_report_path=str(browser_path),
                    visual_critic_path=str(critic_path),
                )

            repair_message = await self.team_runner.run_role(
                role_class=RepairAgent,
                stage="repair",
                instruction=json.dumps(
                    {
                        "visual_critic_path": str(critic_path),
                        "browser_report_path": str(browser_path),
                        "output_dir": str(iteration_dir),
                    },
                    ensure_ascii=False,
                ),
                context=self.run_context,
            )
            repair = RepairResult.model_validate_json(repair_message.content)
            repair_path = iteration_dir / "repair-result.json"
            repair_path.write_text(repair.model_dump_json(indent=2), encoding="utf-8")
            latest_repair = repair_path

            current.repair_status = repair.status
            current.applied_directives = repair.applied_directives
            current.deferred_directives = repair.deferred_directives
            iterations.append(current)

            if repair.status in ("blocked", "noop") or repair.applied_directives == 0:
                return QualityLoopResult(
                    status="blocked",
                    project_slug=project_slug,
                    project_dir=str(project_dir),
                    max_iterations=self.max_iterations,
                    iterations=iterations,
                    final_score=critic.score.overall,
                    stop_reason="repair_agent_made_no_change",
                    browser_report_path=str(browser_path),
                    visual_critic_path=str(critic_path),
                    repair_result_path=str(repair_path),
                )

            previous_score = critic.score.overall
            previous_fingerprint = current.issue_fingerprint

        return QualityLoopResult(
            status="max_iterations",
            project_slug=project_slug,
            project_dir=str(project_dir),
            max_iterations=self.max_iterations,
            iterations=iterations,
            final_score=previous_score,
            stop_reason="loop_exhausted",
            browser_report_path=str(latest_browser) if latest_browser else None,
            visual_critic_path=str(latest_critic) if latest_critic else None,
            repair_result_path=str(latest_repair) if latest_repair else None,
        )
