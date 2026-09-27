import hashlib
import json
from pathlib import Path

from core.contracts.browser_qa_schema import BrowserQAResult
from core.contracts.design_context_schema import ReferenceBoard
from core.verification.reference_aware_visual_qa import ReferenceAwareVisualQA


ROOT = Path(__file__).resolve().parents[1]


def _full_spec(tmp_path: Path, profile: str, extra: str = "") -> Path:
    path = tmp_path / "02-FULL-BUILD-SPEC.md"
    path.write_text(
        f"## Specification profile\n\n- Profile: `{profile}`\n\n## 0. Mission\n{extra}\n",
        encoding="utf-8",
    )
    return path


def _browser_report(tmp_path: Path) -> Path:
    payload = BrowserQAResult.model_validate(
        {
            "status": "passed",
            "project_slug": "fixture",
            "project_dir": str(tmp_path),
            "base_url": "http://127.0.0.1:4173",
            "routes": ["/"],
            "viewports": [{"name": "desktop", "width": 1440, "height": 1000}],
            "evidence": [],
            "gates": {
                "routes_discovered": True,
                "screenshots_created": True,
                "no_page_errors": True,
                "no_console_errors": True,
                "no_horizontal_overflow": True,
                "internal_links_valid": True,
                "semantic_smoke_passed": True,
                "image_alt_smoke_passed": True,
                "accessible_name_smoke_passed": True,
                "control_target_smoke_passed": True,
                "focus_visibility_smoke_passed": True,
                "elementary_visual_sanity_passed": True,
                "ready_for_visual_critic": True,
            },
        }
    )
    path = tmp_path / "browser-report.json"
    path.write_text(payload.model_dump_json(indent=2), encoding="utf-8")
    return path


def _empty_reference_board(tmp_path: Path) -> Path:
    path = tmp_path / "reference-dna.json"
    path.write_text(ReferenceBoard().model_dump_json(indent=2), encoding="utf-8")
    return path


def test_original_design_never_turns_reference_similarity_into_gate(tmp_path: Path) -> None:
    result = ReferenceAwareVisualQA.evaluate(
        browser_report_path=_browser_report(tmp_path),
        reference_analysis_path=_empty_reference_board(tmp_path),
        full_spec_path=_full_spec(tmp_path, "original_design"),
    )
    assert result.mode == "spec_only"
    assert result.status == "inapplicable"
    assert result.blocking is False


def test_redesign_does_not_reward_old_ui_pixel_similarity(tmp_path: Path) -> None:
    result = ReferenceAwareVisualQA.evaluate(
        browser_report_path=_browser_report(tmp_path),
        reference_analysis_path=_empty_reference_board(tmp_path),
        full_spec_path=_full_spec(tmp_path, "redesign"),
    )
    assert result.mode == "spec_only"
    assert result.status == "inapplicable"
    assert result.blocking is False


def test_preserve_and_extend_without_explicit_visual_exact_surface_is_nonblocking(tmp_path: Path) -> None:
    result = ReferenceAwareVisualQA.evaluate(
        browser_report_path=_browser_report(tmp_path),
        reference_analysis_path=_empty_reference_board(tmp_path),
        full_spec_path=_full_spec(tmp_path, "preserve_and_extend"),
    )
    assert result.mode == "protected_surfaces"
    assert result.status == "cantTell"
    assert result.blocking is False
    assert "whole-page" in " ".join(result.notes).lower()


def test_pixel_faithful_without_authoritative_capture_blocks_as_cant_tell(tmp_path: Path) -> None:
    result = ReferenceAwareVisualQA.evaluate(
        browser_report_path=_browser_report(tmp_path),
        reference_analysis_path=_empty_reference_board(tmp_path),
        full_spec_path=_full_spec(tmp_path, "pixel_faithful"),
    )
    assert result.mode == "strict_reference"
    assert result.status == "cantTell"
    assert result.blocking is True


def test_quality_loop_wires_reference_visual_artifact_into_visual_and_repair() -> None:
    source = (ROOT / "core" / "orchestration" / "quality_loop.py").read_text(encoding="utf-8")
    assert "ReferenceAwareVisualQA.evaluate" in source
    assert '"reference_visual_qa_path"' in source
    assert "pixel_faithful_reference_evidence_cantTell" in source
    assert "Strict pixel-faithful reference gate failed" in source


def test_policy_document_never_makes_reference_presence_clone_permission() -> None:
    policy = (ROOT.parent / "skills_UIUX" / "prompt-compiler" / "REFERENCE-AWARE-VISUAL-QA.md").read_text(encoding="utf-8")
    assert "A reference is evidence, not permission to clone" in policy
    assert "Whole-page pixel similarity" in policy
    assert "redesign" in policy
    assert "original_design" in policy
