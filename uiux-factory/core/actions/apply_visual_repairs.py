import json
import os
import re
import shutil
from pathlib import Path
from typing import ClassVar

from metagpt.actions import Action

from core.contracts.browser_qa_schema import BrowserQAResult
from core.contracts.repair_result_schema import (
    RepairActionLog,
    RepairGate,
    RepairResult,
)
from core.contracts.visual_critic_schema import VisualCriticResult
from core.skills.policy_resolver import SkillPolicyResolver


class ApplyVisualRepairs(Action):
    name: str = "ApplyVisualRepairs"

    desc: str = (
        "Apply conservative, auditable visual repairs from VisualCritic "
        "directives to the generated static project, preserving backups "
        "and deferring unsafe creative changes."
    )

    REPAIR_SKILLS: ClassVar[tuple[str, ...]] = (
        "ui-improvement/SKILL.md",
        "ui-craft-and-visual-qa/SKILL.md",
        "frontend-implementation/SKILL.md",
        "ai-agent-coding-guardrails/SKILL.md",
        "visual-taste-calibration/SKILL.md",
        "responsive-and-device-strategy/SKILL.md",
        "accessibility/SKILL.md",
    )

    SAFE_TARGETS: ClassVar[tuple[str, ...]] = (
        "composition",
        "spacing",
        "responsive",
        "typography",
        "surface",
        "accessibility",
    )

    @staticmethod
    def discover_html(
        project_dir: Path,
    ) -> list[Path]:
        results = []

        for path in sorted(
            project_dir.rglob("*.html")
        ):
            if "next-app" in (
                part.lower()
                for part in path.parts
            ):
                continue

            results.append(path)

        return results

    @staticmethod
    def discover_classes(
        html_files: list[Path],
    ) -> set[str]:
        classes: set[str] = set()

        pattern = re.compile(
            r'class=["\']([^"\']+)["\']'
        )

        for path in html_files:
            text = path.read_text(
                encoding="utf-8"
            )

            for match in pattern.finditer(text):
                for name in match.group(1).split():
                    if re.fullmatch(
                        r"[A-Za-z_][A-Za-z0-9_-]*",
                        name,
                    ):
                        classes.add(name)

        return classes

    @staticmethod
    def selector_list(
        classes: set[str],
        keywords: tuple[str, ...],
        limit: int = 24,
    ) -> str:
        matched = sorted(
            name
            for name in classes
            if any(
                keyword in name.lower()
                for keyword in keywords
            )
        )[:limit]

        return ",\n".join(
            f".{name}"
            for name in matched
        )

    @classmethod
    def build_overlay(
        cls,
        critic: VisualCriticResult,
        html_files: list[Path],
    ) -> tuple[
        str,
        set[str],
    ]:
        classes = cls.discover_classes(
            html_files
        )

        targets = {
            directive.target.lower().strip()
            for directive in critic.repair_directives
        }

        chunks = [
            "/* UIUX Factory Repair Overlay v1",
            "   Generated from visual-critic.json.",
            "   Conservative rules only; creative changes are deferred. */",
            "",
            "html {",
            "  overflow-x: clip;",
            "}",
            "",
            "img, svg, video, canvas {",
            "  max-width: 100%;",
            "}",
            "",
            ":where(h1, h2, h3, p, a, button) {",
            "  overflow-wrap: break-word;",
            "}",
        ]

        applied: set[str] = set()

        if (
            "composition" in targets
            or "spacing" in targets
        ):
            section_selector = cls.selector_list(
                classes,
                (
                    "section",
                    "hero",
                    "featured",
                    "category",
                    "brand",
                    "proof",
                    "story",
                    "collection",
                    "browse",
                    "product",
                    "checkout",
                    "cart",
                ),
            )

            if section_selector:
                chunks.extend([
                    "",
                    "/* Composition / spacing remediation */",
                    section_selector + " {",
                    "  min-height: auto;",
                    "}",
                    "",
                    "@media (min-width: 1024px) {",
                    section_selector + " {",
                    "  max-width: 100%;",
                    "}",
                    "}",
                ])

            hero_selector = cls.selector_list(
                classes,
                ("hero",),
            )

            if hero_selector:
                chunks.extend([
                    "",
                    hero_selector + " {",
                    "  min-height: auto !important;",
                    "}",
                ])

            applied.update(
                target
                for target in (
                    "composition",
                    "spacing",
                )
                if target in targets
            )

        if "typography" in targets:
            chunks.extend([
                "",
                "/* Typography remediation */",
                "h1 {",
                "  font-size: clamp(2.5rem, 6vw, 5.75rem) !important;",
                "  line-height: 0.98 !important;",
                "  text-wrap: balance;",
                "}",
                "",
                "h2 {",
                "  font-size: clamp(2rem, 4vw, 4rem);",
                "  line-height: 1.05;",
                "  text-wrap: balance;",
                "}",
                "",
                "p {",
                "  max-width: 72ch;",
                "}",
            ])
            applied.add("typography")

        if "responsive" in targets:
            grid_selector = cls.selector_list(
                classes,
                (
                    "grid",
                    "layout",
                    "cards",
                    "products",
                ),
            )

            chunks.extend([
                "",
                "/* Responsive remediation */",
                "@media (max-width: 767px) {",
                "  body {",
                "    overflow-x: clip;",
                "  }",
                "  h1 {",
                "    font-size: clamp(2.25rem, 12vw, 4rem) !important;",
                "  }",
            ])

            if grid_selector:
                chunks.extend([
                    grid_selector + " {",
                    "  min-width: 0;",
                    "}",
                ])

            chunks.append("}")
            applied.add("responsive")

        if "accessibility" in targets:
            chunks.extend([
                "",
                "/* Accessibility remediation */",
                ":where(a, button, input, select, textarea):focus-visible {",
                "  outline: 3px solid currentColor !important;",
                "  outline-offset: 3px !important;",
                "}",
                "",
                "@media (prefers-reduced-motion: reduce) {",
                "  *, *::before, *::after {",
                "    animation-duration: 0.01ms !important;",
                "    animation-iteration-count: 1 !important;",
                "    transition-duration: 0.01ms !important;",
                "    scroll-behavior: auto !important;",
                "  }",
                "}",
            ])
            applied.add("accessibility")

        if "surface" in targets:
            chunks.extend([
                "",
                "/* Surface safety: preserve readable foregrounds. */",
                ":where([class*=\"dark\"], [class*=\"inverse\"]) {",
                "  color-scheme: dark;",
                "}",
            ])
            applied.add("surface")

        chunks.append("")

        return (
            "\n".join(chunks),
            applied,
        )

    @staticmethod
    def inject_css_link(
        html_path: Path,
        css_path: Path,
    ) -> bool:
        text = html_path.read_text(
            encoding="utf-8"
        )

        if "factory-repair.css" in text:
            return False

        relative = os.path.relpath(
            css_path,
            start=html_path.parent,
        ).replace(
            "\\",
            "/",
        )

        link = (
            f'<link rel="stylesheet" '
            f'href="{relative}" '
            f'data-uiux-factory-repair="v1">'
        )

        if "</head>" not in text:
            return False

        updated = text.replace(
            "</head>",
            f"  {link}\n</head>",
            1,
        )

        html_path.write_text(
            updated,
            encoding="utf-8",
        )

        return True

    async def run(
        self,
        instruction: str,
    ) -> str:
        payload = json.loads(
            instruction
        )

        critic_path = Path(
            payload.get(
                "visual_critic_path",
                "",
            )
        ).resolve()

        browser_report_path = Path(
            payload.get(
                "browser_report_path",
                critic_path.parent
                / "browser-report.json",
            )
        ).resolve()

        output_dir = Path(
            payload.get(
                "output_dir",
                critic_path.parent,
            )
        ).resolve()

        if not critic_path.exists():
            raise FileNotFoundError(
                "VisualCritic artifact missing: "
                f"{critic_path}"
            )

        if not browser_report_path.exists():
            raise FileNotFoundError(
                "BrowserQA artifact missing: "
                f"{browser_report_path}"
            )

        critic = VisualCriticResult.model_validate_json(
            critic_path.read_text(
                encoding="utf-8"
            )
        )

        qa = BrowserQAResult.model_validate_json(
            browser_report_path.read_text(
                encoding="utf-8"
            )
        )

        if critic.status == "passed":
            result = RepairResult(
                status="noop",
                project_slug=qa.project_slug,
                project_dir=qa.project_dir,
                skills_used=[],
                gates=RepairGate(
                    critic_consumed=True,
                    browser_report_consumed=True,
                    regression_required=False,
                ),
                notes=[
                    "VisualCritic already passed; no repair was applied."
                ],
            )

            return result.model_dump_json(
                indent=2
            )

        if not critic.gates.ready_for_repair_agent:
            raise RuntimeError(
                "VisualCritic is not ready for RepairAgent."
            )

        resolver = SkillPolicyResolver()
        skills_used = []

        for relative_path in self.REPAIR_SKILLS:
            skill = resolver.load(
                relative_path
            )
            skills_used.append(
                skill.name
            )

        project_dir = Path(
            qa.project_dir
        ).resolve()

        if not project_dir.exists():
            raise FileNotFoundError(
                "Generated project missing: "
                f"{project_dir}"
            )

        html_files = self.discover_html(
            project_dir
        )

        if not html_files:
            raise RuntimeError(
                "RepairAgent found no static HTML files."
            )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        backup_dir = (
            output_dir
            / "repair-backup"
        )

        backup_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        repair_css = (
            project_dir
            / "assets"
            / "factory-repair.css"
        )

        repair_css.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        overlay, applied_targets = self.build_overlay(
            critic,
            html_files,
        )

        modified_files = []
        backup_files = []

        files_to_backup = list(
            html_files
        )

        if repair_css.exists():
            files_to_backup.append(
                repair_css
            )

        for source in files_to_backup:
            relative = source.relative_to(
                project_dir
            )

            target = (
                backup_dir
                / relative
            )

            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                source,
                target,
            )

            backup_files.append(
                str(target)
            )

        repair_css.write_text(
            overlay,
            encoding="utf-8",
        )

        modified_files.append(
            str(repair_css)
        )

        injected_count = 0

        for html_path in html_files:
            if self.inject_css_link(
                html_path,
                repair_css,
            ):
                injected_count += 1
                modified_files.append(
                    str(html_path)
                )

        actions = []

        applied_count = 0
        deferred_count = 0

        for directive in critic.repair_directives:
            target = (
                directive.target
                .lower()
                .strip()
            )

            if (
                target in self.SAFE_TARGETS
                and target in applied_targets
            ):
                status = "applied"
                action_text = (
                    "Applied conservative repair overlay "
                    f"for target '{target}'."
                )
                applied_count += 1
            else:
                status = "deferred"
                action_text = (
                    "Deferred creative or unsafe automatic "
                    f"repair target '{target}' to upstream "
                    "regeneration / richer vision repair."
                )
                deferred_count += 1

            actions.append(
                RepairActionLog(
                    directive_priority=(
                        directive.priority
                    ),
                    route=directive.route,
                    target=directive.target,
                    action=action_text,
                    status=status,
                    evidence=(
                        directive.success_criteria
                    ),
                )
            )

        result = RepairResult(
            status=(
                "applied"
                if applied_count
                and not deferred_count
                else (
                    "partial"
                    if applied_count
                    else "blocked"
                )
            ),
            project_slug=(
                qa.project_slug
            ),
            project_dir=str(
                project_dir
            ),
            repair_css=str(
                repair_css
            ),
            modified_files=sorted(
                set(
                    modified_files
                )
            ),
            backup_files=sorted(
                set(
                    backup_files
                )
            ),
            actions=actions,
            applied_directives=(
                applied_count
            ),
            deferred_directives=(
                deferred_count
            ),
            skills_used=skills_used,
            gates=RepairGate(
                critic_consumed=True,
                browser_report_consumed=True,
                required_skills_loaded=(
                    len(skills_used)
                    == len(
                        self.REPAIR_SKILLS
                    )
                ),
                backups_created=(
                    bool(
                        backup_files
                    )
                ),
                repair_overlay_created=(
                    repair_css.exists()
                ),
                html_links_injected=(
                    injected_count
                    > 0
                    or all(
                        "factory-repair.css"
                        in path.read_text(
                            encoding="utf-8"
                        )
                        for path in html_files
                    )
                ),
                regression_required=True,
            ),
            notes=[
                (
                    "RepairAgent v1 only auto-applies conservative "
                    "CSS/layout/accessibility repairs."
                ),
                (
                    "Brand-direction and generic-AI-feel changes are "
                    "deferred because deterministic mode cannot safely "
                    "invent a new creative direction."
                ),
                (
                    "BrowserQA and VisualCritic must run again after "
                    "every applied repair."
                ),
            ],
        )

        return result.model_dump_json(
            indent=2
        )
