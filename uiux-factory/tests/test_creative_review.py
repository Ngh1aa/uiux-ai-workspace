import json
from pathlib import Path
from zipfile import ZipFile

import pytest
from pydantic import ValidationError

from apps.bridge.creative_review import build_review_pack
from core.contracts.browser_qa_schema import (
    BrowserQAGate,
    BrowserQAResult,
    RouteViewportEvidence,
    ViewportSpec,
)
from core.contracts.creative_review_schema import CreativeDirective


def _directive(**overrides) -> CreativeDirective:
    payload = {
        "schema_version": "1.0.0",
        "source_run_id": "abcdef123456",
        "status": "revise",
        "reviewer": "ChatGPT Creative Director",
        "overall_direction": "Luxury editorial, restrained and product-led.",
        "keep": ["Navigation hierarchy"],
        "revise": [
            {
                "priority": "P1",
                "route": "/",
                "section": "hero",
                "owner": "visual_composition",
                "problem": "Hero lacks a dominant visual anchor.",
                "instruction": "Increase asymmetry and let one editorial media object dominate.",
                "skills": [
                    "visual-design-direction/SKILL.md",
                    "visual-taste-calibration",
                ],
                "success_criteria": "The first viewport has one unmistakable visual anchor.",
            },
            {
                "priority": "P2",
                "route": "/product/",
                "section": "purchase-panel",
                "owner": "implementation",
                "problem": "CTA rhythm is too dense.",
                "instruction": "Increase action separation without changing content priority.",
                "skills": ["interaction-patterns-and-form-ux"],
                "success_criteria": "Primary action is visually clear on mobile and desktop.",
            },
        ],
        "remove": ["Generic three-card benefits row"],
        "notes": [],
    }
    payload.update(overrides)
    return CreativeDirective.model_validate(payload)


def test_creative_directive_routes_to_earliest_owner_and_normalizes_skills() -> None:
    directive = _directive()

    assert directive.earliest_owner() == "visual_composition"
    assert directive.revise[0].skills == [
        "visual-design-direction",
        "visual-taste-calibration",
    ]
    assert directive.routed_skills("implementation") == [
        "interaction-patterns-and-form-ux"
    ]
    prompt = directive.as_prompt_block()
    assert "KEEP:" in prompt
    assert "REVISE:" in prompt
    assert "REMOVE:" in prompt
    assert "owner=visual_composition" in prompt
    assert "Increase asymmetry" in prompt


def test_creative_directive_rejects_non_job_source_ids() -> None:
    with pytest.raises(ValidationError):
        _directive(source_run_id="../secret")


def test_creative_directive_rejects_skill_path_traversal() -> None:
    with pytest.raises(ValidationError):
        _directive(
            revise=[
                {
                    "priority": "P1",
                    "route": "/",
                    "section": "hero",
                    "owner": "visual_composition",
                    "problem": "Needs revision.",
                    "instruction": "Revise safely.",
                    "skills": ["../../private-skill"],
                    "success_criteria": "No traversal.",
                }
            ]
        )


def test_review_pack_only_includes_screenshots_inside_run_directory(tmp_path: Path) -> None:
    run_dir = tmp_path / "abcdef123456"
    evidence_dir = run_dir / "browser-evidence"
    evidence_dir.mkdir(parents=True)

    inside = evidence_dir / "home-desktop.png"
    inside.write_bytes(b"inside screenshot")
    outside = tmp_path / "outside-secret.png"
    outside.write_bytes(b"must never enter the review pack")

    viewport = ViewportSpec(name="desktop", width=1440, height=1000)
    report = BrowserQAResult(
        status="passed",
        project_slug="demo-abcdef123456",
        project_dir=str(tmp_path / "generated" / "demo-abcdef123456"),
        base_url="http://127.0.0.1:8000",
        routes=["/"],
        viewports=[viewport],
        evidence=[
            RouteViewportEvidence(
                route="/",
                viewport=viewport,
                screenshot=str(inside),
                status="passed",
            ),
            RouteViewportEvidence(
                route="/outside",
                viewport=viewport,
                screenshot=str(outside),
                status="passed",
            ),
        ],
        gates=BrowserQAGate(),
    )

    (run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": run_dir.name,
                "goal": "Design a premium website",
                "status": "completed",
                "active_stage": None,
                "completed_stages": ["visual_qa"],
                "artifacts": {},
                "errors": [],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "browser-report.json").write_text(
        report.model_dump_json(indent=2),
        encoding="utf-8",
    )
    (run_dir / "visual-brain.json").write_text("{}", encoding="utf-8")

    pack = build_review_pack(
        run_dir,
        {
            "id": run_dir.name,
            "status": "completed",
            "prompt": "Design a premium website",
            "engine": "template",
        },
        "demo-abcdef123456",
    )

    assert pack.is_file()
    with ZipFile(pack) as archive:
        names = set(archive.namelist())
        assert "review-context.json" in names
        assert "creative-directive-template.json" in names
        assert "artifacts/browser-report.json" in names
        assert "artifacts/visual-brain.json" in names
        screenshot_names = [name for name in names if name.startswith("screenshots/")]
        assert len(screenshot_names) == 1
        assert "home-desktop" in screenshot_names[0]
        assert all("outside-secret" not in name for name in names)

        context = json.loads(archive.read("review-context.json"))
        assert context["source_run_id"] == run_dir.name
        assert context["review_mode"] == "senior_creative_director"
        template = json.loads(archive.read("creative-directive-template.json"))
        assert template["source_run_id"] == run_dir.name
        assert template["revise"][0]["owner"] == "visual_composition"
