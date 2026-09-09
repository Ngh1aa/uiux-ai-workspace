from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

from core.contracts.browser_qa_schema import BrowserQAResult


REVIEW_FILES = (
    "design-contract.json",
    "design-system.json",
    "implementation-plan.json",
    "visual-composition.json",
    "visual-brain.json",
    "browser-report.json",
    "quality-loop.json",
    "DESIGN.md",
    "tokens.css",
)


def _directive_template(source_run_id: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "source_run_id": source_run_id,
        "status": "revise",
        "reviewer": "ChatGPT Creative Director",
        "overall_direction": "",
        "keep": [],
        "revise": [
            {
                "priority": "P1",
                "route": "/",
                "section": "hero",
                "owner": "visual_composition",
                "problem": "",
                "instruction": "",
                "skills": [
                    "visual-design-direction",
                    "brand-distinctiveness-and-visual-signature",
                    "visual-taste-calibration",
                ],
                "success_criteria": "",
            }
        ],
        "remove": [],
        "notes": [],
    }


def _review_context(run_dir: Path, job: dict, project_slug: str | None) -> dict:
    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    return {
        "schema_version": "1.0.0",
        "source_run_id": run_dir.name,
        "goal": run.get("goal", job.get("prompt", "")),
        "engine": job.get("engine", "template"),
        "project_slug": project_slug,
        "review_mode": "senior_creative_director",
        "review_instructions": [
            "Inspect the supplied desktop/tablet/mobile screenshots before making visual claims.",
            "Use the design contract, design system, Visual Brain and QA reports as supporting evidence.",
            "Separate KEEP, REVISE and REMOVE decisions.",
            "Every REVISE item must name the owning Factory stage so the system can invalidate from the correct boundary.",
            "Prefer visual_composition for composition/hierarchy/density problems, art_direction for visual-language problems, design_system for token/component-system problems, and implementation for code-only defects.",
            "Return a CreativeDirective JSON object matching creative-directive-template.json.",
            "Do not invent business evidence, testimonials, metrics, awards, prices or brand claims.",
        ],
        "recommended_skills": [
            "visual-design-direction",
            "brand-distinctiveness-and-visual-signature",
            "visual-taste-calibration",
            "interaction-patterns-and-form-ux",
            "ui-craft-and-visual-qa",
        ],
    }


def _screenshot_paths(run_dir: Path) -> list[Path]:
    report_path = run_dir / "browser-report.json"
    if not report_path.is_file():
        return []
    try:
        report = BrowserQAResult.model_validate_json(report_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    paths: list[Path] = []
    for item in report.evidence:
        path = Path(item.screenshot).resolve()
        if path.is_file() and path not in paths:
            paths.append(path)
    return paths


def build_review_pack(run_dir: Path, job: dict, project_slug: str | None) -> Path:
    """Build a portable ZIP that can be uploaded to a senior design reviewer."""

    run_dir = run_dir.resolve()
    if not (run_dir / "run.json").is_file():
        raise FileNotFoundError("Run state is missing.")

    final_path = run_dir / "review-pack.zip"
    temp_path = run_dir / f".review-pack.{uuid4().hex}.tmp"
    context = _review_context(run_dir, job, project_slug)
    directive = _directive_template(run_dir.name)

    try:
        with ZipFile(temp_path, "w", compression=ZIP_DEFLATED, compresslevel=6) as archive:
            archive.writestr(
                "review-context.json",
                json.dumps(context, indent=2, ensure_ascii=False),
            )
            archive.writestr(
                "creative-directive-template.json",
                json.dumps(directive, indent=2, ensure_ascii=False),
            )

            for filename in REVIEW_FILES:
                source = run_dir / filename
                if source.is_file():
                    archive.write(source, arcname=f"artifacts/{filename}")

            for index, screenshot in enumerate(_screenshot_paths(run_dir), start=1):
                suffix = screenshot.suffix.lower() if screenshot.suffix else ".png"
                archive.write(
                    screenshot,
                    arcname=f"screenshots/{index:02d}-{screenshot.stem}{suffix}",
                )

        os.replace(temp_path, final_path)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    return final_path
