from __future__ import annotations

import json
import re
import shutil
from hashlib import sha256
from pathlib import Path

from core.skills.execution_context import SkillExecutionContext, SkillSelection, SkillSource


class SkillInstructionCompiler:
    """Compile exact skills_UIUX sources with mandatory-rule-first progressive disclosure."""

    STAGE_FOCUS: dict[str, tuple[str, ...]] = {
        "reference_analysis": ("reference", "audit", "measure", "evidence", "source", "screenshot"),
        "research": ("research", "evidence", "source", "benchmark", "discovery", "audience", "unknown", "metric", "baseline"),
        "ux_ia": ("journey", "task", "architecture", "navigation", "hierarchy", "findability", "page"),
        "art_direction": ("visual", "layout", "hierarchy", "brand", "type", "color", "media", "motion", "animation", "easing", "transition", "signature", "moment"),
        "design_contract": ("contract", "truth", "constraint", "system", "component", "token", "decision"),
        "design_system": ("token", "component", "state", "responsive", "accessibility", "pattern", "composition", "variant", "reuse"),
        "implementation_plan": ("implementation", "architecture", "dependency", "file", "route", "verification"),
        "visual_composition": ("composition", "layout", "hierarchy", "visual", "responsive", "media", "anti", "trust", "credibility", "heuristic", "law"),
        "implementation": ("implementation", "semantic", "responsive", "focus", "component", "verify", "code", "transition", "animation", "keyframe", "micro", "state", "feedback", "error", "loading"),
        "browser_qa": ("test", "browser", "visual", "responsive", "accessibility", "evidence", "performance", "vitals", "render"),
        "visual_qa": ("visual", "craft", "regression", "drift", "responsive", "accessibility", "generic", "brand"),
        "repair": ("repair", "preserve", "diagnose", "verify", "responsive", "accessibility", "visual", "root cause"),
    }

    MANDATORY_HEADING_MARKERS = (
        "hard rule",
        "coding rule",
        "decision rule",
        "guardrail",
        "acceptance",
        "anti-pattern",
        "anti pattern",
        "workflow",
        "when to use",
        "output",
        "definition of done",
        "gate",
        "must",
        "do not",
        "don't",
    )

    def __init__(self, skills_root: Path, max_chars_per_skill: int = 9000, max_total_chars: int = 48000) -> None:
        self.skills_root = Path(skills_root).resolve()
        self.max_chars_per_skill = max(1200, int(max_chars_per_skill))
        self.max_total_chars = max(8000, int(max_total_chars))
        if not self.skills_root.exists():
            raise FileNotFoundError(f"skills_UIUX clone is required: {self.skills_root}")

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
    def select_sections(cls, stage: str, content: str, budget: int = 9000) -> tuple[list[str], list[str], str]:
        sections = cls.split_sections(content)
        focus = cls.STAGE_FOCUS.get(stage, ())
        mandatory_rows = []
        ranked_rows = []
        for index, (heading, section) in enumerate(sections):
            lower_heading = heading.lower()
            haystack = f"{heading}\n{section[:2200]}".lower()
            score = sum(haystack.count(token) for token in focus)
            if index == 0:
                score += 2
            is_mandatory = any(marker in lower_heading for marker in cls.MANDATORY_HEADING_MARKERS)
            row = (index, heading, section, score)
            if is_mandatory:
                mandatory_rows.append(row)
            else:
                ranked_rows.append(row)

        ranked_rows.sort(key=lambda row: (-row[3], row[0]))
        ordered = mandatory_rows + ranked_rows
        selected: list[str] = []
        selected_headings: list[str] = []
        used = 0
        for index, heading, section, score in ordered:
            if not selected and index == 0:
                pass
            elif score <= 0 and (index, heading, section, score) not in mandatory_rows:
                continue
            remaining = budget - used
            if remaining <= 0:
                break
            excerpt = section[:remaining]
            if not excerpt.strip():
                continue
            selected.append(excerpt)
            selected_headings.append(heading)
            used += len(excerpt)

        if not selected:
            selected = [content[:budget]]
            selected_headings = ["document-start"]

        all_headings = [heading for heading, _ in sections]
        omitted = [heading for heading in all_headings if heading not in selected_headings]
        return selected_headings, omitted, "\n\n".join(selected)

    @staticmethod
    def rule_lines(content: str) -> list[str]:
        rules: list[str] = []
        active_priority = False
        for raw in content.splitlines():
            stripped = raw.strip()
            if stripped.startswith("#"):
                heading = stripped.lstrip("#").strip().lower()
                active_priority = any(marker in heading for marker in SkillInstructionCompiler.MANDATORY_HEADING_MARKERS)
                continue
            if stripped.startswith(("- ", "* ")):
                value = stripped[2:].strip()
                if 10 <= len(value) <= 700 and (active_priority or any(word in value.lower() for word in ("must", "should", "never", "avoid", "require", "verify"))):
                    rules.append(value)
        return list(dict.fromkeys(rules))[:160]

    @staticmethod
    def artifact_preview(path: Path, limit: int = 3200) -> str:
        try:
            if path.suffix.lower() in {".json", ".md", ".txt", ".html", ".css", ".js", ".ts", ".tsx"}:
                return path.read_text(encoding="utf-8", errors="replace")[:limit]
        except OSError:
            pass
        return f"<artifact:{path.name}>"

    def build(self, *, selection: SkillSelection, run_dir: Path, upstream_artifacts: dict[str, str] | None = None) -> SkillExecutionContext:
        stage_dir = Path(run_dir) / "skill-context" / selection.stage
        source_dir = stage_dir / "sources"
        source_dir.mkdir(parents=True, exist_ok=True)

        sources: list[SkillSource] = []
        compiled_parts: list[str] = []
        total_compiled = 0
        mandatory_set = set(selection.mandatory_paths)

        # Mandatory skills receive budget first. This prevents optional/domain skills
        # from starving hard policy out of the model context.
        ordered_paths = list(selection.mandatory_paths) + [
            path for path in selection.relative_paths if path not in mandatory_set
        ]

        for relative_path in ordered_paths:
            source_path = (self.skills_root / relative_path).resolve()
            if not source_path.is_relative_to(self.skills_root):
                raise PermissionError(f"Skill path escapes skills_UIUX: {relative_path}")
            if not source_path.is_file():
                raise FileNotFoundError(f"Selected real UIUX skill is missing: {source_path}")

            content = source_path.read_text(encoding="utf-8", errors="replace")
            digest = sha256(content.encode("utf-8")).hexdigest()
            skill_name = source_path.parent.name
            evidence_path = source_dir / f"{skill_name}-{digest[:10]}.md"
            shutil.copy2(source_path, evidence_path)

            remaining_total = max(0, self.max_total_chars - total_compiled)
            per_skill_budget = min(self.max_chars_per_skill, remaining_total)
            headings, omitted, excerpt = self.select_sections(selection.stage, content, per_skill_budget)
            excerpt = excerpt[:per_skill_budget]
            total_compiled += len(excerpt)
            all_headings = [heading for heading, _ in self.split_sections(content)]
            rules = self.rule_lines(content)
            coverage = min(1.0, len(excerpt) / max(1, len(content)))

            source = SkillSource(
                name=skill_name,
                relative_path=relative_path,
                absolute_path=str(source_path),
                sha256=digest,
                content_chars=len(content),
                all_sections=all_headings,
                selected_sections=headings,
                omitted_sections=omitted,
                rule_lines=rules,
                compiled_excerpt=excerpt,
                compiled_chars=len(excerpt),
                coverage_ratio=round(coverage, 4),
                full_source_preserved=True,
                mandatory=relative_path in mandatory_set,
            )
            sources.append(source)

            rules_text = "\n".join(f"- {rule}" for rule in rules[:40])
            compiled_parts.append(
                "### REAL SKILL: " + relative_path + "\n"
                f"SHA256: {digest}\n"
                f"MANDATORY: {str(relative_path in mandatory_set).lower()}\n"
                f"ROUTING REASON: {selection.reasons.get(relative_path, '')}\n"
                f"FULL SOURCE EVIDENCE: {evidence_path}\n"
                f"SELECTED SECTIONS: {', '.join(headings) or 'none'}\n"
                f"OMITTED SECTIONS: {', '.join(omitted) or 'none'}\n\n"
                "#### PRIORITY RULE DIGEST\n" + (rules_text or "- No explicit bullet rules detected; consult copied full source.") + "\n\n"
                "#### STAGE-RELEVANT SOURCE\n" + excerpt
            )

        artifact_summaries: dict[str, str] = {}
        for key, raw_path in (upstream_artifacts or {}).items():
            path = Path(raw_path)
            if path.exists():
                artifact_summaries[key] = self.artifact_preview(path)

        total_source_chars = sum(source.content_chars for source in sources)
        rule_count = sum(len(source.rule_lines) for source in sources)
        avg_coverage = (
            sum(source.coverage_ratio for source in sources) / len(sources)
            if sources else 0.0
        )
        compiled = (
            "# UIUX SKILL EXECUTION CONTEXT\n\n"
            "These exact local skills are execution policy. Mandatory skills and hard-rule sections are prioritized. "
            "Every full SKILL.md is copied into run evidence even when progressive disclosure omits sections from the immediate prompt. "
            "Never claim an omitted section was read by the model; use the rule digest and selected source below, and preserve traceability to the full copy.\n\n"
            f"Stage: {selection.stage}\nDomain: {selection.domain}\n"
            f"Selected skills: {len(sources)}\nMandatory skills: {len(mandatory_set)}\n"
            f"Full source characters: {total_source_chars}\nCompiled characters: {total_compiled}\n\n"
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
            selected_skill_count=len(sources),
            mandatory_skill_count=len(mandatory_set),
            total_source_chars=total_source_chars,
            compiled_chars=total_compiled,
            rule_count=rule_count,
            average_coverage_ratio=round(avg_coverage, 4),
            all_full_sources_preserved=all(source.full_source_preserved for source in sources),
        )

        (stage_dir / "skill-context.json").write_text(context.model_dump_json(indent=2), encoding="utf-8")
        (stage_dir / "compiled-skills.md").write_text(compiled, encoding="utf-8")
        (stage_dir / "routing.json").write_text(selection.model_dump_json(indent=2), encoding="utf-8")
        (stage_dir / "coverage.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "stage": selection.stage,
                    "domain": selection.domain,
                    "selected_skill_count": context.selected_skill_count,
                    "mandatory_skill_count": context.mandatory_skill_count,
                    "total_source_chars": total_source_chars,
                    "compiled_chars": total_compiled,
                    "rule_count": rule_count,
                    "average_coverage_ratio": context.average_coverage_ratio,
                    "all_full_sources_preserved": context.all_full_sources_preserved,
                    "sources": [
                        {
                            "path": source.relative_path,
                            "mandatory": source.mandatory,
                            "coverage_ratio": source.coverage_ratio,
                            "selected_sections": source.selected_sections,
                            "omitted_sections": source.omitted_sections,
                            "full_source_preserved": source.full_source_preserved,
                        }
                        for source in sources
                    ],
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return context

    @staticmethod
    def enrich_instruction(original: str, context: SkillExecutionContext) -> str:
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
                    "coverage": {
                        "selected_skill_count": context.selected_skill_count,
                        "mandatory_skill_count": context.mandatory_skill_count,
                        "rule_count": context.rule_count,
                        "average_coverage_ratio": context.average_coverage_ratio,
                        "all_full_sources_preserved": context.all_full_sources_preserved,
                    },
                    "skills": [
                        {
                            "name": source.name,
                            "path": source.relative_path,
                            "sha256": source.sha256,
                            "mandatory": source.mandatory,
                            "rules": source.rule_lines,
                        }
                        for source in context.sources
                    ],
                }
                return json.dumps(payload, ensure_ascii=False)
        return original.rstrip() + "\n\n" + context.compiled_instruction
