from __future__ import annotations

from collections import Counter
from pathlib import Path

from core.contracts.browser_qa_schema import BrowserQAResult
from core.contracts.prototype_acceptance_schema import (
    AcceptanceSummary,
    PrototypeAcceptanceReport,
    RequirementResult,
)
from core.contracts.visual_critic_schema import VisualCriticResult
from core.verification.evidence_provenance import evidence_ref, project_digest
from core.verification.prototype_checklist_registry import prototype_requirements


class PrototypeAcceptanceEvaluator:
    """Evidence ledger for the 56-item prototype checklist.

    V1 is intentionally conservative. It only returns `passed` for requirements
    that current BrowserQA/VisualCritic evidence can actually establish. Planned
    evaluators stay `untested`; human-only checks stay `cantTell`. This prevents
    a clean visual score from being misrepresented as complete checklist proof.
    """

    IMPLEMENTED_IDS = {
        "P1-03",
        "P1-06",
        "P2-06",
        "P3-08",
        "P3-11",
        "P3-13",
        "P3-14",
        "P6-02",
    }

    @staticmethod
    def _issue_categories(critic: VisualCriticResult) -> set[str]:
        return {issue.category for issue in critic.issues if issue.severity in {"P0", "P1"}}

    @staticmethod
    def _vision_ready(critic: VisualCriticResult) -> bool:
        return bool(
            critic.review_mode == "vision"
            and critic.semantic_review is not None
            and critic.gates.semantic_visual_review_passed
            and critic.gates.semantic_route_coverage_complete
            and critic.gates.semantic_evidence_grounded
        )

    def _implemented_result(
        self,
        requirement_id: str,
        browser: BrowserQAResult,
        critic: VisualCriticResult,
        browser_evidence,
        critic_evidence,
    ) -> RequirementResult:
        categories = self._issue_categories(critic)
        vision_ready = self._vision_ready(critic)
        review = critic.semantic_review

        if requirement_id == "P1-03":
            if not vision_ready or review is None:
                return RequirementResult(requirement_id=requirement_id, outcome="cantTell", rationale="A complete screenshot-grounded semantic review is required to establish website type/domain fit.", evidence=[critic_evidence])
            valid = review.website_type.strip().lower() not in {"", "generic", "unknown"}
            return RequirementResult(requirement_id=requirement_id, outcome="passed" if valid else "failed", rationale=f"Semantic review resolved website_type={review.website_type!r}.", evidence=[critic_evidence])

        if requirement_id == "P1-06":
            if not vision_ready:
                return RequirementResult(requirement_id=requirement_id, outcome="cantTell", rationale="Anti-generic quality cannot be established from proxy-only evidence.", evidence=[critic_evidence])
            blocked = bool({"generic-ai", "composition-variety"} & categories) or not critic.gates.no_blocking_generic_pattern
            return RequirementResult(requirement_id=requirement_id, outcome="failed" if blocked else "passed", rationale="Semantic VisualCritic inspected the rendered routes for generic/interchangeable grammar.", evidence=[critic_evidence])

        if requirement_id == "P2-06":
            if not vision_ready or review is None or not review.routes:
                return RequirementResult(requirement_id=requirement_id, outcome="cantTell", rationale="Decision-object prominence requires screenshot-grounded route evidence.", evidence=[critic_evidence])
            failed = "decision-object" in categories
            return RequirementResult(requirement_id=requirement_id, outcome="failed" if failed else "passed", rationale="Decision-object dominance was evaluated per representative route.", evidence=[critic_evidence])

        if requirement_id == "P3-08":
            failed = bool({"spacing", "composition"} & categories) or critic.score.spacing < 90
            return RequirementResult(requirement_id=requirement_id, outcome="failed" if failed else "passed", rationale=f"VisualCritic spacing score={critic.score.spacing}; blocking spacing/composition issues={sorted({"spacing", "composition"} & categories)}.", evidence=[critic_evidence])

        if requirement_id == "P3-11":
            if not vision_ready:
                return RequirementResult(requirement_id=requirement_id, outcome="cantTell", rationale="Domain/page-role layout fit requires semantic screenshot review.", evidence=[critic_evidence])
            failed = bool({"domain-fit", "page-role"} & categories)
            return RequirementResult(requirement_id=requirement_id, outcome="failed" if failed else "passed", rationale=f"Domain policy {critic.domain_policy_id} was applied to representative page roles.", evidence=[critic_evidence])

        if requirement_id == "P3-13":
            if not vision_ready:
                return RequirementResult(requirement_id=requirement_id, outcome="cantTell", rationale="Media relevance requires semantic screenshot review.", evidence=[critic_evidence])
            return RequirementResult(requirement_id=requirement_id, outcome="failed" if "media" in categories else "passed", rationale="Rendered media relevance was judged against the active domain/vertical policy.", evidence=[critic_evidence])

        if requirement_id == "P3-14":
            if not vision_ready:
                return RequirementResult(requirement_id=requirement_id, outcome="cantTell", rationale="Distinctiveness requires semantic screenshot review.", evidence=[critic_evidence])
            failed = bool({"distinctiveness", "brand-distinctiveness", "generic-ai"} & categories)
            return RequirementResult(requirement_id=requirement_id, outcome="failed" if failed else "passed", rationale="VisualCritic checked visible distinctiveness and anti-generic evidence.", evidence=[critic_evidence])

        if requirement_id == "P6-02":
            widths = sorted({item.width for item in browser.viewports})
            has_mobile = any(350 <= width <= 430 for width in widths)
            has_tablet = any(700 <= width <= 900 for width in widths)
            has_desktop = any(width >= 1280 for width in widths)
            no_overflow = browser.gates.no_horizontal_overflow
            passed = has_mobile and has_tablet and has_desktop and no_overflow
            return RequirementResult(requirement_id=requirement_id, outcome="passed" if passed else "failed", rationale=f"BrowserQA widths={widths}; no_horizontal_overflow={no_overflow}.", evidence=[browser_evidence])

        return RequirementResult(requirement_id=requirement_id, outcome="untested", rationale="No evaluator is registered for this requirement yet.")

    def evaluate(
        self,
        *,
        run_id: str,
        browser_report_path: Path,
        visual_critic_path: Path,
    ) -> PrototypeAcceptanceReport:
        browser_path = Path(browser_report_path).resolve()
        critic_path = Path(visual_critic_path).resolve()
        browser = BrowserQAResult.model_validate_json(browser_path.read_text(encoding="utf-8"))
        critic = VisualCriticResult.model_validate_json(critic_path.read_text(encoding="utf-8"))
        project_dir = Path(browser.project_dir).resolve()
        digest = project_digest(project_dir)

        browser_evidence = evidence_ref(browser_path, kind="browser-report", evaluator=browser.generated_by, source_digest=digest)
        critic_evidence = evidence_ref(critic_path, kind="visual-critic", evaluator=critic.generated_by, source_digest=digest)

        requirements = prototype_requirements()
        results: list[RequirementResult] = []
        for requirement in requirements:
            if requirement.automation_status == "manual":
                results.append(
                    RequirementResult(
                        requirement_id=requirement.id,
                        outcome="cantTell",
                        rationale="This checklist item requires real human/participant evidence. The AI evaluator is not allowed to self-certify it.",
                    )
                )
            elif requirement.id in self.IMPLEMENTED_IDS:
                results.append(self._implemented_result(requirement.id, browser, critic, browser_evidence, critic_evidence))
            else:
                results.append(
                    RequirementResult(
                        requirement_id=requirement.id,
                        outcome="untested",
                        rationale=f"Evaluator {requirement.evaluator!r} is planned but not implemented in PrototypeAcceptanceEvaluatorV1.",
                    )
                )

        outcome_counts = Counter(item.outcome for item in results)
        automation_counts = Counter(item.automation_status for item in requirements)
        summary = AcceptanceSummary(
            total=len(requirements),
            passed=outcome_counts["passed"],
            failed=outcome_counts["failed"],
            inapplicable=outcome_counts["inapplicable"],
            cantTell=outcome_counts["cantTell"],
            untested=outcome_counts["untested"],
            implemented=automation_counts["implemented"],
            planned=automation_counts["planned"],
            manual=automation_counts["manual"],
        )

        by_id = {item.id: item for item in requirements}
        blocking = [
            item.requirement_id
            for item in results
            if by_id[item.requirement_id].machine_required
            and item.outcome not in {"passed", "inapplicable"}
        ]
        unresolved_planned = [
            item.requirement_id
            for item in results
            if by_id[item.requirement_id].automation_status == "planned"
            and item.outcome not in {"passed", "inapplicable"}
        ]
        human = [
            item.requirement_id
            for item in results
            if by_id[item.requirement_id].automation_status == "manual"
            and item.outcome not in {"passed", "inapplicable"}
        ]
        failed_any = [item.requirement_id for item in results if item.outcome == "failed"]

        machine_status = "blocked" if blocking else "passed"
        if failed_any or unresolved_planned or blocking:
            final_status = "blocked"
        elif human:
            final_status = "human_review_required"
        else:
            final_status = "approved"

        return PrototypeAcceptanceReport(
            run_id=run_id,
            project_dir=str(project_dir),
            project_digest=digest,
            browser_report_path=str(browser_path),
            visual_critic_path=str(critic_path),
            requirements=requirements,
            results=results,
            summary=summary,
            machine_status=machine_status,
            final_status=final_status,
            blocking_requirement_ids=blocking,
            human_review_requirement_ids=human,
            notes=[
                "Outcome semantics follow ACT-style passed/failed/inapplicable/cantTell/untested separation.",
                "V1 deliberately leaves planned evaluators untested rather than converting missing evidence into a pass.",
                "Evidence is bound to the generated project digest; later revisions must regenerate evidence.",
            ],
        )
