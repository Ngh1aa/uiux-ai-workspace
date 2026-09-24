from __future__ import annotations

import json
import os
from pathlib import Path
import re

from core.actions.evaluate_visual_quality import EvaluateVisualQuality
from core.contracts.browser_qa_schema import BrowserQAResult
from core.contracts.visual_critic_schema import (
    SemanticVisualReview,
    VisualCriticResult,
    VisualIssue,
    VisualScore,
)
from core.runtime.free_provider import ProviderError
from core.runtime.free_vision_provider import FreeVisionProvider
from core.skills.policy_resolver import SkillPolicyResolver


class EvaluateVisualQualityV3(EvaluateVisualQuality):
    """VisualCritic v3: deterministic browser truth + semantic screenshot review.

    Pixel metrics remain useful for runtime/layout evidence, but they are not allowed to
    establish aesthetic/domain quality by themselves unless the owner explicitly opts
    into proxy-only acceptance with UIUX_ALLOW_PROXY_VISUAL_PASS=1.
    """

    name: str = "EvaluateVisualQualityV3"
    desc: str = (
        "Inspect representative rendered screenshots against website domain, vertical, "
        "page role and anti-generic design policies before allowing visual PASS."
    )

    ANTHROPIC_FRONTEND = "upstream/anthropic-skills/skills/frontend-design/SKILL.md"
    ANTHROPIC_WEBAPP = "upstream/anthropic-skills/skills/webapp-testing/SKILL.md"

    @staticmethod
    def _clean_json_text(text: str) -> str:
        value = text.strip()
        if value.startswith("```"):
            value = re.sub(r"^```(?:json)?\s*", "", value, flags=re.IGNORECASE)
            value = re.sub(r"\s*```$", "", value)
        start = value.find("{")
        end = value.rfind("}")
        if start >= 0 and end > start:
            value = value[start : end + 1]
        return value

    @staticmethod
    def _read_optional(path: Path, limit: int = 12000) -> str:
        if not path.is_file():
            return ""
        try:
            return path.read_text(encoding="utf-8", errors="ignore")[:limit]
        except OSError:
            return ""

    @classmethod
    def _run_context(cls, report_path: Path) -> dict:
        # browser-report.json lives at run_dir/quality-loop/iteration-NN/.
        run_dir = report_path.parents[2]
        research = cls._read_optional(run_dir / "research.md")
        art_direction = cls._read_optional(run_dir / "art-direction.md")
        contract = cls._read_optional(run_dir / "design-contract.json")
        composition_text = cls._read_optional(run_dir / "visual-composition.json", 18000)

        website_type = "generic"
        vertical = "generic"
        match = re.search(r"Website archetype:\s*`([^`]+)`", research)
        if match:
            website_type = match.group(1).strip()
        match = re.search(r"Vertical/sub-industry:\s*`([^`]+)`", research)
        if match:
            vertical = match.group(1).strip()

        page_roles: dict[str, str] = {}
        composition_summary: dict = {}
        if composition_text:
            try:
                composition = json.loads(composition_text)
                page_roles = {
                    str(page.get("path", "/")): str(page.get("page_role", "unknown"))
                    for page in composition.get("pages", [])
                }
                composition_summary = {
                    "visual_signature": composition.get("visual_signature", ""),
                    "composition_principles": composition.get("composition_principles", []),
                    "pages": [
                        {
                            "path": page.get("path"),
                            "page_role": page.get("page_role"),
                            "composition_family": page.get("composition_family"),
                            "first_visual_anchor": page.get("first_visual_anchor"),
                            "anti_monotony_rules": page.get("anti_monotony_rules", []),
                        }
                        for page in composition.get("pages", [])
                    ],
                }
            except json.JSONDecodeError:
                pass

        return {
            "run_dir": run_dir,
            "website_type": website_type,
            "vertical": vertical,
            "page_roles": page_roles,
            "research": research,
            "art_direction": art_direction,
            "design_contract": contract,
            "visual_composition": composition_summary,
        }

    @staticmethod
    def _representative_screenshots(
        qa: BrowserQAResult,
        page_roles: dict[str, str],
        limit: int = 8,
    ) -> list[tuple[str, Path]]:
        best: dict[str, tuple[int, object]] = {}
        for item in qa.evidence:
            screenshot = Path(item.screenshot).resolve()
            if not screenshot.is_file():
                continue
            area = int(item.viewport.width) * int(item.viewport.height)
            previous = best.get(item.route)
            if previous is None or area > previous[0]:
                best[item.route] = (area, item)

        selected: list[tuple[str, Path]] = []
        route_order = list(qa.routes) if qa.routes else sorted(best)
        for route in route_order:
            if route not in best:
                continue
            item = best[route][1]
            role = page_roles.get(route, "unknown")
            label = f"route={route}; page_role={role}; viewport={item.viewport.name}"
            selected.append((label, Path(item.screenshot).resolve()))
            if len(selected) >= limit:
                break
        return selected

    @staticmethod
    def _semantic_issues(review: SemanticVisualReview) -> list[VisualIssue]:
        issues: list[VisualIssue] = []

        if review.blocking_generic:
            issues.append(
                VisualIssue(
                    severity="P1",
                    category="generic-ai",
                    route="*",
                    viewport="representative",
                    evidence=(
                        "Semantic screenshot review found a site-level interchangeable/generic "
                        f"visual grammar. {review.site_summary}"
                    ),
                    recommendation=(
                        "Invalidate the owning art-direction/composition decision. Re-establish a "
                        "domain-specific visual signature instead of adding another cosmetic layer."
                    ),
                )
            )

        if len(review.routes) >= 3 and review.cross_route_variety < 60:
            issues.append(
                VisualIssue(
                    severity="P1",
                    category="composition-variety",
                    route="*",
                    viewport="representative",
                    evidence=(
                        f"Cross-route visual variety scored {review.cross_route_variety}/100; "
                        "materially different page roles are reading as the same template family."
                    ),
                    recommendation=(
                        "Recompose representative page roles around their different user decisions; "
                        "do not reuse the same hero + identical cards + CTA grammar everywhere."
                    ),
                )
            )

        for route in review.routes:
            evidence = "; ".join(route.evidence[:3]) or "Semantic screenshot inspection."
            tells = "; ".join(route.generic_tells[:3])
            rec = route.recommendations[0] if route.recommendations else (
                "Revisit the owning art-direction and page-role composition from rendered evidence."
            )

            if route.blocking_generic or route.generic_ai_feel >= 45:
                issues.append(
                    VisualIssue(
                        severity="P1",
                        category="generic-ai",
                        route=route.route,
                        viewport="representative",
                        evidence=(
                            f"Generic-AI feel {route.generic_ai_feel}/100. {tells or evidence}"
                        ),
                        recommendation=rec,
                    )
                )
            if route.domain_fit < 65:
                issues.append(
                    VisualIssue(
                        severity="P1",
                        category="domain-fit",
                        route=route.route,
                        viewport="representative",
                        evidence=f"Domain fit {route.domain_fit}/100. {evidence}",
                        recommendation=rec,
                    )
                )
            if route.page_role_fit < 65:
                issues.append(
                    VisualIssue(
                        severity="P1",
                        category="page-role",
                        route=route.route,
                        viewport="representative",
                        evidence=f"Page-role fit {route.page_role_fit}/100. {evidence}",
                        recommendation=rec,
                    )
                )
            if route.decision_object_dominance < 55:
                issues.append(
                    VisualIssue(
                        severity="P1",
                        category="decision-object",
                        route=route.route,
                        viewport="representative",
                        evidence=(
                            "Primary decision object dominance scored "
                            f"{route.decision_object_dominance}/100. {evidence}"
                        ),
                        recommendation=rec,
                    )
                )
            if route.media_relevance < 55:
                issues.append(
                    VisualIssue(
                        severity="P1",
                        category="media",
                        route=route.route,
                        viewport="representative",
                        evidence=f"Domain/media relevance {route.media_relevance}/100. {evidence}",
                        recommendation=rec,
                    )
                )

        return issues

    @classmethod
    def _merge_semantic_score(
        cls,
        base: VisualScore,
        review: SemanticVisualReview,
        issues: list[VisualIssue],
    ) -> VisualScore:
        if not review.routes:
            return base

        def avg(name: str) -> float:
            return sum(float(getattr(route, name)) for route in review.routes) / len(review.routes)

        semantic_visual = (
            avg("domain_fit")
            + avg("page_role_fit")
            + avg("media_relevance")
            + avg("distinctiveness")
        ) / 4
        semantic_hierarchy = (avg("hierarchy") + avg("decision_object_dominance")) / 2
        visual = cls.clamp(base.visual * 0.4 + semantic_visual * 0.6)
        hierarchy = cls.clamp(base.hierarchy * 0.4 + semantic_hierarchy * 0.6)
        brand = cls.clamp(base.brand_fidelity * 0.35 + review.brand_distinctiveness * 0.65)
        generic = cls.clamp(
            max(
                base.generic_ai_feel,
                avg("generic_ai_feel"),
                100 - review.cross_route_variety if len(review.routes) >= 3 else 0,
            )
        )
        p0 = sum(issue.severity == "P0" for issue in issues)
        p1 = sum(issue.severity == "P1" for issue in issues)
        overall = cls.clamp(
            (
                visual
                + hierarchy
                + base.typography
                + base.spacing
                + base.responsive
                + brand
                + base.accessibility
                + (100 - generic)
            )
            / 8
            - p0 * 2
            - p1 * 0.5
        )
        return VisualScore(
            visual=visual,
            hierarchy=hierarchy,
            typography=base.typography,
            spacing=base.spacing,
            responsive=base.responsive,
            brand_fidelity=brand,
            accessibility=base.accessibility,
            generic_ai_feel=generic,
            overall=overall,
        )

    @classmethod
    def _vision_prompt(cls, context: dict, skill_excerpt: str) -> tuple[str, str]:
        system = (
            "You are a senior visual design critic. Inspect the supplied rendered screenshots, "
            "not the implementation intent. Judge each route against its domain, vertical and "
            "page role. Be evidence-specific. Do not reward generic polish. Legitimate cards are "
            "fine when they serve the task; block interchangeable card-soup, generic SaaS grammar "
            "in unrelated domains, repeated template chrome, weak decision-object dominance, "
            "irrelevant stock media, or identical compositions across materially different roles. "
            "Return JSON only and use integer scores from 0 to 100."
        )
        project = {
            "website_type": context["website_type"],
            "vertical": context["vertical"],
            "page_roles": context["page_roles"],
            "visual_composition": context["visual_composition"],
            "research_excerpt": context["research"][:5000],
            "art_direction_excerpt": context["art_direction"][:5000],
            "design_contract_excerpt": context["design_contract"][:5000],
            "frontend_design_policy_excerpt": skill_excerpt[:5000],
        }
        schema = {
            "reviewed": True,
            "site_summary": "specific visible summary",
            "website_type": context["website_type"],
            "vertical": context["vertical"],
            "blocking_generic": False,
            "cross_route_variety": 0,
            "brand_distinctiveness": 0,
            "routes": [
                {
                    "route": "/",
                    "page_role": "home",
                    "domain_fit": 0,
                    "page_role_fit": 0,
                    "decision_object_dominance": 0,
                    "media_relevance": 0,
                    "hierarchy": 0,
                    "distinctiveness": 0,
                    "generic_ai_feel": 0,
                    "blocking_generic": False,
                    "generic_tells": [],
                    "evidence": [],
                    "recommendations": [],
                }
            ],
        }
        prompt = (
            "PROJECT EVIDENCE:\n"
            + json.dumps(project, ensure_ascii=False)
            + "\n\nReturn exactly this JSON shape, with one route object per supplied screenshot:\n"
            + json.dumps(schema, ensure_ascii=False)
            + "\n\nFor luxury fragrance/perfume, visible fragrance/product/media identity must be "
            "credible for the specific page role; do not accept a generic SaaS/card dashboard "
            "merely because spacing and typography are clean."
        )
        return system, prompt

    async def run(self, instruction: str) -> str:
        base = VisualCriticResult.model_validate_json(await super().run(instruction))
        payload = json.loads(instruction)
        report_path = Path(payload.get("browser_report_path", "")).resolve()
        qa = BrowserQAResult.model_validate_json(report_path.read_text(encoding="utf-8"))
        context = self._run_context(report_path)

        resolver = SkillPolicyResolver()
        try:
            frontend_skill = resolver.load(self.ANTHROPIC_FRONTEND)
            webapp_skill = resolver.load(self.ANTHROPIC_WEBAPP)
            for name in (frontend_skill.name, webapp_skill.name):
                if name not in base.skills_used:
                    base.skills_used.append(name)
        except FileNotFoundError as exc:
            issue = VisualIssue(
                severity="P1",
                category="semantic-vision",
                route="*",
                viewport="*",
                evidence=f"Pinned Anthropic visual QA skill is unavailable: {exc}",
                recommendation="Run: git submodule update --init --recursive, then rerun QA.",
            )
            base.issues = self.dedupe_issues(base.issues + [issue])
            base.repair_directives = self.directives_from_issues(base.issues)
            base.status = "blocked"
            base.gates.proxy_only_mode = True
            base.gates.no_blocking_generic_pattern = False
            base.gates.ready_for_repair_agent = False
            base.notes.append("Semantic visual PASS is blocked because the pinned upstream skill is missing.")
            return base.model_dump_json(indent=2)

        screenshots = self._representative_screenshots(qa, context["page_roles"])
        base.gates.semantic_visual_review_attempted = True
        allow_proxy_pass = os.getenv("UIUX_ALLOW_PROXY_VISUAL_PASS", "").strip() == "1"

        try:
            provider = FreeVisionProvider.from_env(Path(__file__).resolve().parents[2])
            system, prompt = self._vision_prompt(context, frontend_skill.excerpt)
            response = await provider.complete_vision(
                stage="visual_qa",
                system=system,
                prompt=prompt,
                images=screenshots,
            )
            review = SemanticVisualReview.model_validate_json(self._clean_json_text(response))
        except (ProviderError, ValueError, json.JSONDecodeError) as exc:
            base.review_mode = "proxy"
            base.gates.proxy_only_mode = True
            base.gates.semantic_visual_review_passed = False
            base.gates.domain_page_roles_reviewed = False
            base.gates.no_blocking_generic_pattern = False
            base.notes.append(f"Semantic screenshot review unavailable: {type(exc).__name__}.")
            if not allow_proxy_pass:
                issue = VisualIssue(
                    severity="P1",
                    category="semantic-vision",
                    route="*",
                    viewport="representative",
                    evidence=(
                        "VisualCritic only has pixel/DOM proxies. That evidence cannot establish "
                        "domain fit, page-role fit or absence of generic card-soup."
                    ),
                    recommendation=(
                        "Configure a free-tier multimodal model through the existing FreeProvider "
                        "settings, or explicitly set UIUX_ALLOW_PROXY_VISUAL_PASS=1 to accept the "
                        "weaker proxy-only gate."
                    ),
                )
                base.issues = self.dedupe_issues(base.issues + [issue])
                base.repair_directives = self.directives_from_issues(base.issues)
                base.status = "blocked"
                base.gates.repair_directives_generated = bool(base.repair_directives)
                base.gates.ready_for_repair_agent = False
            return base.model_dump_json(indent=2)

        semantic_issues = self._semantic_issues(review)
        issues = self.dedupe_issues(base.issues + semantic_issues)
        score = self._merge_semantic_score(base.score, review, issues)
        directives = self.directives_from_issues(issues)
        blocking_generic = review.blocking_generic or any(
            route.blocking_generic or route.generic_ai_feel >= 45 for route in review.routes
        )
        has_blocking_issue = any(issue.severity in {"P0", "P1"} for issue in issues)

        base.semantic_review = review
        base.review_mode = "vision"
        base.issues = issues
        base.score = score
        base.repair_directives = directives
        base.gates.semantic_visual_review_passed = review.reviewed and bool(review.routes)
        base.gates.domain_page_roles_reviewed = bool(review.routes)
        base.gates.no_blocking_generic_pattern = not blocking_generic
        base.gates.proxy_only_mode = False
        base.gates.repair_directives_generated = bool(directives)
        base.gates.ready_for_repair_agent = has_blocking_issue and bool(directives)

        if blocking_generic:
            base.status = "blocked"
        elif has_blocking_issue or score.overall < 90:
            base.status = "repair_required"
        else:
            base.status = "passed"

        base.notes = [
            note
            for note in base.notes
            if "human/vision review remains the richer option" not in note
        ]
        base.notes.append(
            "VisualCritic v3 consumed representative rendered screenshots with semantic "
            "domain/page-role review; deterministic pixel/browser evidence remains a separate gate."
        )
        if blocking_generic:
            base.notes.append(
                "Generic/interchangeable visual grammar is a hard PASS blocker; repair should "
                "invalidate the owning art-direction/composition decision, not add cosmetic CSS."
            )
        return base.model_dump_json(indent=2)
