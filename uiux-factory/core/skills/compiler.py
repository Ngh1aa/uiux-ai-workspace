from __future__ import annotations

import json
import re
import shutil
from hashlib import sha256
from pathlib import Path

from core.skills.execution_context import (
    SkillExecutionContext,
    SkillSelection,
    SkillSource,
)


class SkillInstructionCompiler:
    """Compile exact local SKILL.md sources into one stage context."""

    STAGE_FOCUS: dict[str, tuple[str, ...]] = {
        "research": ("research", "evidence", "source", "benchmark", "discovery", "unknown"),
        "ux_ia": ("journey", "task", "architecture", "navigation", "hierarchy", "findability", "page"),
        "art_direction": ("visual", "layout", "hierarchy", "brand", "type", "color", "media"),
        "design_contract": ("contract", "truth", "constraint", "system", "component", "token"),
        "design_system": ("token", "component", "state", "responsive", "accessibility", "pattern"),
        "implementation_plan": ("implementation", "architecture", "dependency", "file", "route", "verification"),
        "visual_composition": ("composition", "layout", "hierarchy", "visual", "responsive", "media", "anti"),
        "implementation": ("implementation", "semantic", "responsive", "focus", "component", "verify", "code"),
        "browser_qa": ("test", "browser", "visual", "responsive", "accessibility", "evidence"),
        "visual_qa": ("visual", "craft", "regression", "drift", "responsive", "accessibility", "generic"),
        "repair": ("repair", "preserve", "diagnose", "verify", "responsive", "accessibility", "visual"),
    }

    def __init__(
        self,
        skills_root: Path,
        max_chars_per_skill: int = 7000,
        max_total_chars: int = 36000,
    ) -> None:
        self.skills_root = Path(skills_root).resolve()
        self.max_chars_per_skill = max_chars_per_skill
        self.max_total_chars = max_total_chars

        if not self.skills_root.exists():
            raise FileNotFoundError(
                f"skills_UIUX clone is required: {self.skills_root}"
            )

    @staticmethod
    def split_sections(content: str) -> list[tuple[str, str]]:
        lines = content.splitlines()
        sections: list[tuple[str, list[str]]] = []
        current_heading = "document-start"
        current_lines: list[str] = []

        for line in lines:
            match = re.match(r"^(#{1,4})\s+(.+?)\s*$", line)

            if match:
                if current_lines:
                    sections.append((current_heading, current_lines))
                current_heading = match.group(2).strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_heading, current_lines))

        return [
            (heading, "\n".join(section_lines).strip())
            for heading, section_lines in sections
            if any(line.strip() for line in section_lines)
        ]

    @classmethod
    def select_sections(cls, stage: str, content: str) -> tuple[list[str], str]:
        sections = cls.split_sections(content)
        focus = cls.STAGE_FOCUS.get(stage, ())
        ranked = []

        for index, (heading, section) in enumerate(sections):
            haystack = f"{heading}\n{section[:1800]}".lower()
            score = sum(haystack.count(token) for token in focus)

            if index == 0:
                score += 2

            if any(
                marker in heading.lower()
                for marker in (
                    "goal", "when to use", "rules", "workflow",
                    "acceptance", "guardrail", "anti-pattern",
                    "output", "decision",
                )
            ):
                score += 3

            ranked.append((score, index, heading, section))

        ranked.sort(key=lambda row: (-row[0], row[1]))

        selected: list[str] = []
        selected_headings: list[str] = []
        char_budget = 0

        for score, _index, heading, section in ranked:
            if score <= 0 and selected:
                continue

            if char_budget + len(section) > 7000 and selected:
                continue

            selected.append(section)
            selected_headings.append(heading)
            char_budget += len(section)

            if char_budget >= 6500:
                break

        if not selected:
            selected = [content[:7000]]
            selected_headings = ["document-start"]

        return selected_headings, "\n\n".join(selected)

    @staticmethod
    def rule_lines(content: str) -> list[str]:
        lines = []
        for raw in content.splitlines():
            stripped = raw.strip()
            if stripped.startswith(("- ", "* ")):
                value = stripped[2:].strip()
                if 10 <= len(value) <= 500:
                    lines.append(value)
        return lines[:120]

    @staticmethod
    def artifact_preview(path: Path, limit: int = 2600) -> str:
        try:
            if path.suffix.lower() in {
                ".json", ".md", ".txt", ".html", ".css", ".js", ".ts", ".tsx"
            }:
                return path.read_text(
                    encoding="utf-8",
                    errors="replace",
                )[:limit]
        except OSError:
            pass
        return f"<artifact:{path.name}>"

    def build(
        self,
        *,
        selection: SkillSelection,
        run_dir: Path,
        upstream_artifacts: dict[str, str] | None = None,
    ) -> SkillExecutionContext:
        stage_dir = Path(run_dir) / "skill-context" / selection.stage
        source_dir = stage_dir / "sources"
        source_dir.mkdir(parents=True, exist_ok=True)

        sources: list[SkillSource] = []
        compiled_parts: list[str] = []
        total_chars = 0

        for relative_path in selection.relative_paths:
            source_path = (self.skills_root / relative_path).resolve()

            if not source_path.is_relative_to(self.skills_root):
                raise PermissionError(
                    f"Skill path escapes skills_UIUX: {relative_path}"
                )

            if not source_path.exists():
                raise FileNotFoundError(
                    f"Selected real UIUX skill is missing: {source_path}"
                )

            content = source_path.read_text(
                encoding="utf-8",
                errors="replace",
            )
            digest = sha256(content.encode("utf-8")).hexdigest()
            skill_name = source_path.parent.name
            evidence_path = source_dir / f"{skill_name}-{digest[:10]}.md"
            shutil.copy2(source_path, evidence_path)

            selected_headings, excerpt = self.select_sections(
                selection.stage,
                content,
            )

            excerpt = excerpt[: self.max_chars_per_skill]
            remaining = self.max_total_chars - total_chars
            excerpt = excerpt[: max(0, remaining)]
            total_chars += len(excerpt)

            source = SkillSource(
                name=skill_name,
                relative_path=relative_path,
                absolute_path=str(source_path),
                sha256=digest,
                content_chars=len(content),
                selected_sections=selected_headings,
                rule_lines=self.rule_lines(content),
                compiled_excerpt=excerpt,
            )
            sources.append(source)

            compiled_parts.append(
                "### REAL SKILL: "
                f"{relative_path}\n"
                f"SHA256: {digest}\n"
                "ROUTING REASON: "
                f"{selection.reasons.get(relative_path, '')}\n\n"
                f"{excerpt}"
            )

        artifact_summaries: dict[str, str] = {}
        for key, raw_path in (upstream_artifacts or {}).items():
            path = Path(raw_path)
            if path.exists():
                artifact_summaries[key] = self.artifact_preview(path)

        compiled = (
            "# UIUX SKILL EXECUTION CONTEXT\n\n"
            "This stage MUST treat the following copied skills_UIUX "
            "sources as execution policy. Do not invent a skill, rule, "
            "source, metric, reference or project fact not supported by "
            "the goal, upstream artifacts or these sources.\n\n"
            f"Stage: {selection.stage}\n"
            f"Domain: {selection.domain}\n\n"
            + "\n\n---\n\n".join(compiled_parts)
        )

        context = SkillExecutionContext(
            stage=selection.stage,
            domain=selection.domain,
            goal=selection.goal,
            goal_sha256=SkillExecutionContext.goal_hash(selection.goal),
            skills_root=str(self.skills_root),
            selection=selection,
            sources=sources,
            upstream_artifacts=artifact_summaries,
            compiled_instruction=compiled,
            evidence_dir=str(stage_dir),
        )

        (stage_dir / "skill-context.json").write_text(
            context.model_dump_json(indent=2),
            encoding="utf-8",
        )
        (stage_dir / "compiled-skills.md").write_text(
            compiled,
            encoding="utf-8",
        )
        (stage_dir / "routing.json").write_text(
            selection.model_dump_json(indent=2),
            encoding="utf-8",
        )

        return context

    @staticmethod
    def enrich_instruction(
        original: str,
        context: SkillExecutionContext,
    ) -> str:
        stripped = original.lstrip()

        if stripped.startswith("{"):
            try:
                payload = json.loads(original)
            except json.JSONDecodeError:
                payload = None

            if isinstance(payload, dict):
                payload["_uiux_skill_execution"] = {
                    "stage": context.stage,
                    "domain": context.domain,
                    "compiled_policy": context.compiled_instruction,
                    "skills": [
                        {
                            "name": source.name,
                            "path": source.relative_path,
                            "sha256": source.sha256,
                            "rules": source.rule_lines,
                        }
                        for source in context.sources
                    ],
                }
                return json.dumps(payload, ensure_ascii=False)

        return original.rstrip() + "\n\n" + context.compiled_instruction
