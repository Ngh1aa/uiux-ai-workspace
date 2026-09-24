import json
import re
from pathlib import Path
from typing import ClassVar

from metagpt.actions import Action

from core.contracts.browser_qa_schema import BrowserQAResult
from core.contracts.visual_critic_schema import (
    RepairDirective,
    VisualCriticGate,
    VisualCriticResult,
    VisualIssue,
    VisualScore,
)
from core.skills.policy_resolver import SkillPolicyResolver


class EvaluateVisualQuality(Action):
    name: str = "EvaluateVisualQuality"

    desc: str = (
        "Evaluate rendered browser evidence with route-aware, "
        "evidence-backed heuristics and real skills_UIUX policies."
    )

    BASE_CRITIC_SKILLS: ClassVar[tuple[str, ...]] = (
        "ui-craft-and-visual-qa/SKILL.md",
        "visual-taste-calibration/SKILL.md",
        "visual-regression-and-design-drift/SKILL.md",
        "visual-design-direction/SKILL.md",
        "design-system-and-components/SKILL.md",
        "responsive-and-device-strategy/SKILL.md",
        "accessibility/SKILL.md",
    )

    ECOMMERCE_SKILL: ClassVar[str] = (
        "ecommerce-website/SKILL.md"
    )

    TRANSACTION_ROUTES: ClassVar[tuple[str, ...]] = (
        "/cart/",
        "/checkout/",
    )

    @staticmethod
    def clamp(value: float) -> int:
        return max(
            0,
            min(
                100,
                int(round(value)),
            ),
        )

    @staticmethod
    def image_metrics(
        screenshot: Path,
    ) -> dict[str, float]:
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError(
                "Pillow is required for VisualCritic. "
                "Run: python -m pip install pillow"
            ) from exc

        with Image.open(
            screenshot
        ).convert("RGB") as image:
            width, height = image.size

            sample = image.resize(
                (
                    min(width, 220),
                    min(height, 220),
                )
            )

            pixels = list(
                sample.getdata()
            )

            total = max(
                1,
                len(pixels),
            )

            light = 0
            dark = 0
            saturated = 0

            for r, g, b in pixels:
                luminance = (
                    0.2126 * r
                    + 0.7152 * g
                    + 0.0722 * b
                )

                if luminance > 245:
                    light += 1

                if luminance < 28:
                    dark += 1

                if (
                    max(r, g, b)
                    - min(r, g, b)
                    > 55
                ):
                    saturated += 1

            return {
                "width": float(width),
                "height": float(height),
                "white_ratio": light / total,
                "dark_ratio": dark / total,
                "saturated_ratio": saturated / total,
            }

    @staticmethod
    def route_to_html(
        project_dir: Path,
        route: str,
    ) -> Path:
        if route == "/":
            return (
                project_dir
                / "index.html"
            )

        return (
            project_dir
            / route.strip("/")
            / "index.html"
        )

    @classmethod
    def transaction_structure_ok(
        cls,
        project_dir: Path,
        route: str,
    ) -> bool:
        html_path = cls.route_to_html(
            project_dir,
            route,
        )

        if not html_path.exists():
            return False

        text = html_path.read_text(
            encoding="utf-8"
        ).lower()

        if (
            "transaction-layout"
            not in text
        ):
            return False

        if route == "/cart/":
            return (
                text.count(
                    'class="summary"'
                )
                >= 2
                and "checkout/" in text
            )

        if route == "/checkout/":
            return (
                "<form" in text
                and text.count(
                    "<input"
                )
                >= 2
                and 'class="summary"' in text
            )

        return True

    @staticmethod
    def browser_scores(
        qa: BrowserQAResult,
    ) -> tuple[int, int, int]:
        responsive = 100
        accessibility = 100
        typography = 96

        overflow_count = int(
            qa.summary.get(
                "overflow_count",
                0,
            )
        )

        page_errors = int(
            qa.summary.get(
                "page_error_count",
                0,
            )
        )

        broken_links = int(
            qa.summary.get(
                "broken_link_count",
                0,
            )
        )

        responsive -= (
            overflow_count * 20
        )

        if not (
            qa.gates
            .semantic_smoke_passed
        ):
            accessibility -= 25
            typography -= 8

        if page_errors:
            accessibility -= min(
                35,
                page_errors * 10,
            )

        if broken_links:
            accessibility -= min(
                24,
                broken_links * 5,
            )

        if overflow_count:
            typography -= min(
                20,
                overflow_count * 6,
            )

        return (
            max(0, responsive),
            max(0, accessibility),
            max(0, typography),
        )

    @staticmethod
    def composition_family_count(
        project_dir: Path,
    ) -> int:
        path = (
            project_dir
            / "visual-composition.json"
        )

        if not path.exists():
            return 0

        try:
            payload = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )
        except (
            json.JSONDecodeError,
            OSError,
        ):
            return 0

        families = {
            str(
                page.get(
                    "composition_family",
                    "",
                )
            ).strip()
            for page in payload.get(
                "pages",
                []
            )
            if str(
                page.get(
                    "composition_family",
                    "",
                )
            ).strip()
        }

        return len(families)

    @staticmethod
    def brand_token_score(
        project_dir: Path,
    ) -> int:
        css_path = (
            project_dir
            / "assets"
            / "site.css"
        )

        if not css_path.exists():
            return 78

        css = css_path.read_text(
            encoding="utf-8"
        )

        has_primary = bool(
            re.search(
                r"--brand\s*:",
                css,
            )
        )

        uses_primary = css.count(
            "var(--brand)"
        )

        if (
            has_primary
            and uses_primary >= 3
        ):
            return 94

        if has_primary:
            return 88

        return 80

    @classmethod
    def visual_heuristics(
        cls,
        qa: BrowserQAResult,
        project_dir: Path,
    ) -> tuple[
        dict[str, int],
        list[VisualIssue],
    ]:
        issues: list[VisualIssue] = []
        metrics = []

        transaction_ok = {
            route: cls.transaction_structure_ok(
                project_dir,
                route,
            )
            for route in cls.TRANSACTION_ROUTES
            if route in qa.routes
        }

        for item in qa.evidence:
            screenshot = Path(
                item.screenshot
            )

            if not screenshot.exists():
                issues.append(
                    VisualIssue(
                        severity="P0",
                        category="evidence",
                        route=item.route,
                        viewport=item.viewport.name,
                        evidence=(
                            "Screenshot file is missing."
                        ),
                        recommendation=(
                            "Re-run BrowserQA before visual scoring."
                        ),
                    )
                )
                continue

            current = cls.image_metrics(
                screenshot
            )

            current["route"] = (
                item.route
            )
            current["viewport"] = (
                item.viewport.name
            )

            metrics.append(
                current
            )

            is_transaction = (
                item.route
                in cls.TRANSACTION_ROUTES
            )

            # A light transactional screen is not a defect by itself.
            # Only flag it when the expected cart/checkout structure
            # is also missing. This avoids the old white-pixel false
            # positive that could never be fixed by a CSS overlay.
            if (
                current[
                    "white_ratio"
                ]
                > 0.90
                and (
                    not is_transaction
                    or not transaction_ok.get(
                        item.route,
                        False,
                    )
                )
            ):
                issues.append(
                    VisualIssue(
                        severity="P1",
                        category="composition",
                        route=item.route,
                        viewport=item.viewport.name,
                        evidence=(
                            "Near-white coverage is unusually high "
                            f"({current['white_ratio']:.2f}) and the "
                            "route lacks enough structural evidence "
                            "to treat the whitespace as intentional."
                        ),
                        recommendation=(
                            "Review page density, section rhythm and "
                            "visual anchors at the owning composition "
                            "or implementation stage."
                        ),
                    )
                )

            if (
                current[
                    "dark_ratio"
                ]
                > 0.72
            ):
                issues.append(
                    VisualIssue(
                        severity="P1",
                        category="surface",
                        route=item.route,
                        viewport=item.viewport.name,
                        evidence=(
                            "Dark surface coverage exceeds 72% "
                            f"({current['dark_ratio']:.2f})."
                        ),
                        recommendation=(
                            "Verify inverse-surface use against the "
                            "visual direction and foreground contract."
                        ),
                    )
                )

        if not metrics:
            return (
                {
                    "visual": 0,
                    "hierarchy": 0,
                    "spacing": 0,
                    "brand_fidelity": 0,
                    "generic_ai_feel": 100,
                },
                issues,
            )

        p0_count = sum(
            issue.severity
            == "P0"
            for issue in issues
        )

        p1_count = sum(
            issue.severity
            == "P1"
            for issue in issues
        )

        visual = cls.clamp(
            96
            - p0_count * 22
            - p1_count * 6
        )

        hierarchy = cls.clamp(
            95
            - p0_count * 18
            - p1_count * 5
        )

        spacing = cls.clamp(
            95
            - sum(
                issue.category
                in (
                    "composition",
                    "spacing",
                )
                for issue in issues
            )
            * 6
        )

        brand_fidelity = (
            cls.brand_token_score(
                project_dir
            )
        )

        family_count = (
            cls.composition_family_count(
                project_dir
            )
        )

        generic_ai_feel = (
            18
            if family_count >= 3
            else (
                28
                if family_count == 2
                else 38
            )
        )

        return (
            {
                "visual": visual,
                "hierarchy": hierarchy,
                "spacing": spacing,
                "brand_fidelity": brand_fidelity,
                "generic_ai_feel": generic_ai_feel,
            },
            issues,
        )

    @staticmethod
    def dedupe_issues(
        issues: list[VisualIssue],
    ) -> list[VisualIssue]:
        severity_rank = {
            "P0": 0,
            "P1": 1,
            "P2": 2,
        }

        grouped: dict[
            tuple[str, str],
            list[VisualIssue],
        ] = {}

        for issue in issues:
            key = (
                issue.route,
                issue.category,
            )

            grouped.setdefault(
                key,
                [],
            ).append(
                issue
            )

        deduped = []

        for (
            route,
            category,
        ), group in grouped.items():
            group = sorted(
                group,
                key=lambda issue: (
                    severity_rank[
                        issue.severity
                    ],
                    issue.viewport,
                ),
            )

            first = group[0]

            viewports = ", ".join(
                sorted(
                    {
                        issue.viewport
                        for issue in group
                    }
                )
            )

            evidence = first.evidence

            if len(group) > 1:
                evidence += (
                    " Reproduced at: "
                    f"{viewports}."
                )

            deduped.append(
                VisualIssue(
                    severity=(
                        first.severity
                    ),
                    category=category,
                    route=route,
                    viewport=(
                        viewports
                    ),
                    evidence=evidence,
                    recommendation=(
                        first.recommendation
                    ),
                )
            )

        return sorted(
            deduped,
            key=lambda issue: (
                severity_rank[
                    issue.severity
                ],
                issue.route,
                issue.category,
            ),
        )

    @staticmethod
    def directives_from_issues(
        issues: list[VisualIssue],
    ) -> list[RepairDirective]:
        directives = []

        for index, issue in enumerate(
            issues,
            start=1,
        ):
            directives.append(
                RepairDirective(
                    priority=index,
                    route=issue.route,
                    target=issue.category,
                    instruction=(
                        issue.recommendation
                    ),
                    success_criteria=(
                        "Re-run BrowserQA and VisualCritic; "
                        "the same route/category evidence must "
                        "no longer reproduce."
                    ),
                )
            )

        return directives[:12]

    async def run(
        self,
        instruction: str,
    ) -> str:
        payload = json.loads(
            instruction
        )

        report_path = Path(
            payload.get(
                "browser_report_path",
                "",
            )
        ).resolve()

        if not report_path.exists():
            raise FileNotFoundError(
                "Browser report not found: "
                f"{report_path}"
            )

        qa = (
            BrowserQAResult
            .model_validate_json(
                report_path.read_text(
                    encoding="utf-8"
                )
            )
        )

        project_dir = Path(
            qa.project_dir
        ).resolve()

        resolver = (
            SkillPolicyResolver()
        )

        required_paths = list(
            self.BASE_CRITIC_SKILLS
        )

        if any(
            route
            in self.TRANSACTION_ROUTES
            for route in qa.routes
        ):
            required_paths.append(
                self.ECOMMERCE_SKILL
            )

        skills_used = []

        for relative_path in (
            required_paths
        ):
            skill = resolver.load(
                relative_path
            )
            skills_used.append(
                skill.name
            )

        (
            browser_responsive,
            browser_accessibility,
            typography,
        ) = self.browser_scores(
            qa
        )

        (
            heuristic_scores,
            raw_issues,
        ) = self.visual_heuristics(
            qa,
            project_dir,
        )

        if not (
            qa.gates
            .no_horizontal_overflow
        ):
            raw_issues.append(
                VisualIssue(
                    severity="P0",
                    category="responsive",
                    route="*",
                    viewport="*",
                    evidence=(
                        "BrowserQA detected horizontal overflow."
                    ),
                    recommendation=(
                        "Repair the owning responsive layout/component."
                    ),
                )
            )

        if not (
            qa.gates
            .internal_links_valid
        ):
            raw_issues.append(
                VisualIssue(
                    severity="P0",
                    category="navigation",
                    route="*",
                    viewport="*",
                    evidence=(
                        "BrowserQA detected broken internal links."
                    ),
                    recommendation=(
                        "Repair route/link ownership before final QA."
                    ),
                )
            )

        if not (
            qa.gates
            .no_page_errors
        ):
            raw_issues.append(
                VisualIssue(
                    severity="P0",
                    category="runtime",
                    route="*",
                    viewport="*",
                    evidence=(
                        "BrowserQA reported runtime/page errors."
                    ),
                    recommendation=(
                        "Resolve browser runtime failures before "
                        "visual acceptance."
                    ),
                )
            )

        issues = self.dedupe_issues(
            raw_issues
        )

        # Recalculate score penalties from deduped, actionable issues.
        p0_count = sum(
            issue.severity == "P0"
            for issue in issues
        )

        p1_count = sum(
            issue.severity == "P1"
            for issue in issues
        )

        visual = self.clamp(
            heuristic_scores[
                "visual"
            ]
            - p0_count * 8
            - p1_count * 3
        )

        hierarchy = self.clamp(
            heuristic_scores[
                "hierarchy"
            ]
            - p0_count * 6
            - p1_count * 2
        )

        spacing = self.clamp(
            heuristic_scores[
                "spacing"
            ]
            - sum(
                issue.category
                in (
                    "composition",
                    "spacing",
                )
                for issue in issues
            )
            * 3
        )

        overall = self.clamp(
            (
                visual
                + hierarchy
                + typography
                + spacing
                + browser_responsive
                + heuristic_scores[
                    "brand_fidelity"
                ]
                + browser_accessibility
                + (
                    100
                    - heuristic_scores[
                        "generic_ai_feel"
                    ]
                )
            )
            / 8
        )

        score = VisualScore(
            visual=visual,
            hierarchy=hierarchy,
            typography=typography,
            spacing=spacing,
            responsive=(
                browser_responsive
            ),
            brand_fidelity=(
                heuristic_scores[
                    "brand_fidelity"
                ]
            ),
            accessibility=(
                browser_accessibility
            ),
            generic_ai_feel=(
                heuristic_scores[
                    "generic_ai_feel"
                ]
            ),
            overall=overall,
        )

        directives = (
            self.directives_from_issues(
                issues
            )
        )

        has_blocking_issue = any(
            issue.severity
            in (
                "P0",
                "P1",
            )
            for issue in issues
        )

        repair_required = (
            has_blocking_issue
            or overall < 90
        )

        screenshots_consumed = bool(
            qa.evidence
        ) and all(
            Path(
                item.screenshot
            ).exists()
            for item in qa.evidence
        )

        result = VisualCriticResult(
            status=(
                "repair_required"
                if repair_required
                else "passed"
            ),
            project_slug=(
                qa.project_slug
            ),
            score=score,
            issues=issues,
            repair_directives=directives,
            skills_used=skills_used,
            gates=VisualCriticGate(
                screenshots_consumed=(
                    screenshots_consumed
                ),
                browser_report_consumed=True,
                skills_loaded=(
                    len(skills_used)
                    == len(
                        required_paths
                    )
                ),
                score_generated=True,
                repair_directives_generated=(
                    bool(directives)
                ),
                ready_for_repair_agent=(
                    repair_required
                    and screenshots_consumed
                    and bool(directives)
                ),
            ),
            notes=[
                (
                    "VisualCritic v2 is deterministic and route-aware. "
                    "It no longer treats light cart/checkout surfaces "
                    "as defects when required transactional structure "
                    "is present."
                ),
                (
                    "Viewport duplicates are collapsed into one "
                    "actionable issue per route/category."
                ),
                (
                    "Typography, brand and generic-AI scores are "
                    "evidence-backed proxies in zero-cost mode; "
                    "human/vision review remains the richer option."
                ),
            ],
        )

        return result.model_dump_json(
            indent=2
        )
