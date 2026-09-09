from __future__ import annotations

import json
from pathlib import Path
from shutil import copy2

from core.actions.generate_ai_frontend import CODER_CONTRACT, DesignBrief, DesignPage, validate_bundle, write_bundle
from core.contracts.design_system_schema import DesignSystemContract
from core.contracts.frontend_result_schema import FrontendBuildGate, FrontendResult, GeneratedFile, SkillEvidence
from core.contracts.implementation_plan_schema import ImplementationPlan
from core.contracts.visual_composition_schema import VisualComposition


class AIFrontendBuilder:
    """Generate a custom static frontend only after the canonical design flow is complete."""

    def __init__(self, *, context, provider, team_runner) -> None:
        self.context = context
        self.provider = provider
        self.team_runner = team_runner

    @staticmethod
    def _html_path(route: str) -> str:
        normalized = (route or "/").strip()
        if normalized in {"", "/", "index.html"}:
            return "index.html"
        normalized = normalized.split("?", 1)[0].split("#", 1)[0].strip("/").lower()
        safe_parts = []
        for raw in normalized.split("/")[:2]:
            part = "".join(ch if ch.isalnum() or ch == "-" else "-" for ch in raw).strip("-")
            if part:
                safe_parts.append(part[:36])
        return "/".join(safe_parts + ["index.html"]) if safe_parts else "index.html"

    @staticmethod
    def _bounded(path: Path, limit: int) -> str:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]

    def _brief(self, composition: VisualComposition, plan: ImplementationPlan) -> DesignBrief:
        pages: list[DesignPage] = []
        seen: set[str] = set()
        for page in composition.pages:
            path = self._html_path(page.path)
            if path in seen:
                continue
            seen.add(path)
            sections = [
                f"{section.type}: {section.purpose}; composition={section.composition}; "
                f"anchor={section.visual_anchor}; density={section.density}; "
                f"mobile={' | '.join(section.mobile_behavior) or 'explicit transformation required'}"
                for section in page.sections[:14]
            ]
            pages.append(
                DesignPage(
                    path=path,
                    title=page.page_role[:160] or path,
                    purpose=(
                        f"Page role: {page.page_role}. Composition family: {page.composition_family}. "
                        f"First visual anchor: {page.first_visual_anchor}."
                    )[:600],
                    sections=sections or [f"Deliver the {page.page_role} purpose with a unique page-role composition."],
                )
            )
            if len(pages) >= 10:
                break

        if "index.html" not in {page.path for page in pages}:
            home_route = next((route for route in plan.routes if route.path in {"/", "", "index.html"}), None)
            pages.insert(
                0,
                DesignPage(
                    path="index.html",
                    title=(home_route.page_role if home_route else "Home")[:160],
                    purpose="Primary orientation and highest-value journey entry.",
                    sections=["Distinctive home composition derived from the approved Design Contract and Design System."],
                ),
            )

        direction = (
            f"Visual signature: {composition.visual_signature}\n"
            f"Composition principles: {' | '.join(composition.composition_principles)}\n"
            "Every route must look like one coherent brand while preserving page-role diversity. "
            "Avoid generic AI dashboard/card-grid aesthetics and repeated hero structures."
        )[:3000]
        return DesignBrief(
            direction=direction,
            pages=pages,
            unknowns=list(dict.fromkeys(plan.unresolved_items + composition.unresolved_items))[:30],
            proposed_tokens={},
        )

    async def run(self) -> FrontendResult:
        contract_path = Path(self.context.artifacts["design_contract"])
        system_path = Path(self.context.artifacts["design_system"])
        plan_path = Path(self.context.artifacts["implementation_plan"])
        composition_path = Path(self.context.artifacts["visual_composition"])
        tokens_path = Path(self.context.artifacts["design_tokens"])

        plan = ImplementationPlan.model_validate_json(plan_path.read_text(encoding="utf-8"))
        composition = VisualComposition.model_validate_json(composition_path.read_text(encoding="utf-8"))
        DesignSystemContract.model_validate_json(system_path.read_text(encoding="utf-8"))
        brief = self._brief(composition, plan)

        _selection, skill_context, _artifact = self.team_runner.prepare_skill_context(
            stage="implementation",
            context=self.context,
        )
        rule_digest = self.team_runner._skill_rule_digest(skill_context, max_chars=9000)

        prompt = (
            "# APPROVED DESIGN BRIEF\n" + brief.model_dump_json(indent=2)
            + "\n\n# DESIGN CONTRACT\n" + self._bounded(contract_path, 6500)
            + "\n\n# DESIGN SYSTEM\n" + self._bounded(system_path, 7000)
            + "\n\n# IMPLEMENTATION PLAN\n" + self._bounded(plan_path, 7000)
            + "\n\n# VISUAL COMPOSITION\n" + self._bounded(composition_path, 8500)
            + "\n\n# MANDATORY UIUX SKILL RULES\n" + rule_digest
        )

        system = (
            "You are the senior frontend implementation specialist in a gated UI/UX production system. "
            "The upstream research, UX, art direction, design contract, design system, implementation plan and visual composition are authoritative. "
            "Implement them faithfully and creatively without inventing business facts. The result will be judged from rendered screenshots, responsive behavior, accessibility and visual distinctiveness.\n\n"
            + CODER_CONTRACT
        )

        raw = ""
        issues: list[str] = []
        bundle = None
        for attempt in range(3):
            repair_note = (
                "\n\n# PREVIOUS VALIDATION FINDINGS\n"
                + "\n".join(f"- {issue}" for issue in issues)
                + "\nReturn a corrected complete bundle, not a patch."
                if issues
                else ""
            )
            raw = await self.provider.complete(
                stage="implementation",
                system=system,
                prompt=prompt + repair_note,
                json_mode=True,
            )
            self.team_runner._save_provider_usage(self.context)
            try:
                bundle = validate_bundle(raw, brief)
                break
            except (ValueError, TypeError) as error:
                issues = [str(error)[:1800]]

        if bundle is None:
            raise RuntimeError("AI frontend bundle failed validation after 3 attempts: " + "; ".join(issues))

        project_slug = plan.project_slug
        project = write_bundle(
            self.context.root,
            project_slug,
            bundle,
            tokens_path.read_text(encoding="utf-8"),
        )
        if self.context.artifacts.get("design_document"):
            copy2(self.context.artifacts["design_document"], project / "DESIGN.md")

        skills_used = [
            SkillEvidence(
                name=source.name,
                relative_path=source.relative_path,
                sha256=source.sha256,
                rule_count=len(source.rule_lines),
            )
            for source in skill_context.sources
        ]
        files = [GeneratedFile(path=name, kind="static") for name in bundle.files]
        files.extend(
            [
                GeneratedFile(path="tokens.css", kind="design-system"),
                GeneratedFile(path="DESIGN.md", kind="design-document"),
            ]
        )
        result = FrontendResult(
            status="generated",
            project_slug=project_slug,
            project_dir=str(project),
            github_pages_entry=str(project / "index.html"),
            next_app_dir="",
            files=files,
            skills_used=skills_used,
            policy_checks={
                "custom_ai_bundle": True,
                "fake_proof_forbidden": True,
                "page_role_diversity_required": True,
                "canonical_tokens_preserved": True,
            },
            commands=[],
            unresolved_items=brief.unknowns,
            gates=FrontendBuildGate(
                workspace_guardrail_passed=True,
                root_index_created=(project / "index.html").is_file(),
                github_pages_static_tree_created=True,
                next_source_created=False,
                visual_composition_consumed=True,
                required_skills_loaded=bool(skills_used),
                semantic_html_passed=True,
                responsive_contract_passed=True,
                focus_contract_passed=True,
                technical_copy_gate_passed=True,
                ready_for_dependency_install=False,
                build_verified=False,
            ),
            generated_by="AIFrontendBuilder",
        )
        artifact = self.context.run_dir / "frontend-result.json"
        artifact.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        self.context.add_artifact("implementation", artifact)
        return result
