from __future__ import annotations

import json
from pathlib import Path

from core.actions.evaluate_visual_quality_semantic import EvaluateVisualQualitySemantic
from core.contracts.browser_qa_schema import BrowserQAResult
from core.contracts.visual_critic_schema import VisualCriticResult
from core.domain_visual_profiles import resolve_visual_profile
from core.semantic_visual_policy import (
    semantic_blocking_generic,
    semantic_coverage_issues,
)


class EvaluateVisualQualityV4(EvaluateVisualQualitySemantic):
    """Semantic VisualCritic with domain policy and screenshot-coverage hard gates.

    v3 established real multimodal screenshot review. v4 makes that review auditable:
    every supplied representative route must be covered exactly once, every route score
    must cite visible evidence, and the active website-type/vertical policy controls the
    generic-design thresholds. A partial or ungrounded model response cannot PASS.
    """

    name: str = "EvaluateVisualQualityV4"
    desc: str = (
        "Inspect rendered screenshots with domain/page-role policy, require complete "
        "evidence-grounded route coverage, and block materially generic design before PASS."
    )

    @classmethod
    def _vision_prompt(cls, context: dict, skill_excerpt: str) -> tuple[str, str]:
        system, prompt = super()._vision_prompt(context, skill_excerpt)
        profile = resolve_visual_profile(context["website_type"], context["vertical"])
        system += (
            " Apply the supplied domain visual acceptance policy as a task-specific rubric, "
            "not as a template. Domain conventions may legitimately differ: for example, "
            "government task clarity does not need luxury media density, while fragrance "
            "discovery does. Cite concrete visible screenshot evidence for every route score."
        )
        prompt += (
            "\n\nDOMAIN VISUAL ACCEPTANCE POLICY:\n"
            + json.dumps(profile, ensure_ascii=False)
            + "\n\nCoverage rules: review every supplied screenshot route exactly once; use the exact route "
            "string and page_role from each screenshot label; provide at least one concrete "
            "visible evidence statement per route. Do not invent routes or infer unseen states."
        )
        return system, prompt

    @staticmethod
    def _expected_routes(screenshots: list[tuple[str, Path]]) -> list[str]:
        routes: list[str] = []
        for label, _path in screenshots:
            prefix = "route="
            if not label.startswith(prefix):
                continue
            route = label[len(prefix) :].split(";", 1)[0].strip()
            if route and route not in routes:
                routes.append(route)
        return routes

    async def run(self, instruction: str) -> str:
        result = VisualCriticResult.model_validate_json(await super().run(instruction))
        payload = json.loads(instruction)
        report_path = Path(payload.get("browser_report_path", "")).resolve()
        if not report_path.is_file():
            return result.model_dump_json(indent=2)

        qa = BrowserQAResult.model_validate_json(report_path.read_text(encoding="utf-8"))
        context = self._run_context(report_path)
        profile = resolve_visual_profile(context["website_type"], context["vertical"])
        result.domain_policy_id = profile["id"]
        result.gates.domain_policy_applied = True

        if result.review_mode != "vision" or result.semantic_review is None:
            result.gates.semantic_route_coverage_complete = False
            result.gates.semantic_evidence_grounded = False
            result.notes.append(
                f"Domain visual policy {profile['id']} resolved, but semantic screenshot coverage "
                "could not be established without a completed vision review."
            )
            return result.model_dump_json(indent=2)

        review = result.semantic_review
        # Context artifacts are canonical. Do not let a model rename the website type,
        # vertical or known page roles in its response.
        review.website_type = context["website_type"]
        review.vertical = context["vertical"]
        for route_review in review.routes:
            if route_review.route in context["page_roles"]:
                route_review.page_role = context["page_roles"][route_review.route]

        screenshots = self._representative_screenshots(qa, context["page_roles"])
        expected_routes = self._expected_routes(screenshots)
        coverage_issues = semantic_coverage_issues(review, expected_routes)
        coverage_issues = self.dedupe_issues(coverage_issues)

        coverage_complete = not any(
            issue.category == "semantic-coverage" for issue in coverage_issues
        )
        evidence_grounded = not any(
            issue.category == "semantic-evidence" for issue in coverage_issues
        )
        blocking_generic = semantic_blocking_generic(review)

        issues = self.dedupe_issues(result.issues + coverage_issues)
        directives = self.directives_from_issues(issues)
        has_blocking_issue = any(issue.severity in {"P0", "P1"} for issue in issues)

        result.semantic_review = review
        result.issues = issues
        result.repair_directives = directives
        result.gates.semantic_route_coverage_complete = coverage_complete
        result.gates.semantic_evidence_grounded = evidence_grounded
        result.gates.semantic_visual_review_passed = (
            result.gates.semantic_visual_review_passed
            and coverage_complete
            and evidence_grounded
        )
        result.gates.domain_page_roles_reviewed = (
            result.gates.domain_page_roles_reviewed
            and coverage_complete
            and evidence_grounded
        )
        result.gates.no_blocking_generic_pattern = not blocking_generic
        result.gates.repair_directives_generated = bool(directives)
        result.gates.ready_for_repair_agent = has_blocking_issue and bool(directives)

        # Aggregate score can summarize quality, but it cannot overrule missing evidence.
        if not coverage_complete or not evidence_grounded:
            result.score.overall = min(result.score.overall, 89)

        if blocking_generic:
            result.status = "blocked"
        elif has_blocking_issue or result.score.overall < 90:
            result.status = "repair_required"
        else:
            result.status = "passed"

        result.notes.append(
            f"VisualCritic v4 applied domain policy {profile['id']} with "
            f"{len(expected_routes)} expected representative route(s); semantic PASS requires "
            "complete route coverage and visible evidence for every scored route."
        )
        if blocking_generic:
            result.notes.append(
                "The active domain policy classified the visible grammar as materially generic; "
                "this is a hard blocker regardless of aggregate polish score."
            )
        return result.model_dump_json(indent=2)
