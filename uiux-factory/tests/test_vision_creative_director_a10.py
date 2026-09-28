from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from core.runtime.flow_os.evidence import EvidenceRecord
from core.runtime.flow_os.vision_director import (
    VisionCreativeDirectorAdapter,
    VisionCreativeDirectorError,
    configured_vision_creative_analyzer,
    sanitize_creative_output,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / "skills_UIUX"
POLICY = json.loads((SKILLS_ROOT / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))
PNG = b"\x89PNG\r\n\x1a\n" + b"a10-fixture"


def _record(root: Path, name: str, route: str, width: int, height: int) -> EvidenceRecord:
    path = root / name
    path.write_bytes(PNG + name.encode("utf-8"))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return EvidenceRecord(
        id=f"browser_{name}",
        type="browser_render",
        stage_id="visual_qa",
        tool="playwright",
        status="PASS",
        summary="fixture",
        data={
            "route": route,
            "title": "Fixture",
            "viewport": {"width": width, "height": height},
            "screenshot": name,
            "screenshot_sha256": digest,
        },
        origin="runtime",
        trusted=True,
    )


class ScriptedCreativeAnalyzer:
    name = "fixture-director"
    model = "fixture-model"
    cost_class = "zero_cost"

    def __init__(self, output: dict) -> None:
        self.output = output
        self.images: list[dict] = []
        self.context: dict = {}

    def analyze(self, images: list[dict], context: dict) -> dict:
        self.images = images
        self.context = context
        return self.output


def test_a10_zero_cost_default_validates_multi_screen_sources_without_fake_verdict(tmp_path: Path) -> None:
    records = [
        _record(tmp_path, "desktop.png", "/", 1440, 900),
        _record(tmp_path, "tablet.png", "/", 768, 1024),
        _record(tmp_path, "mobile.png", "/", 390, 844),
    ]
    result = VisionCreativeDirectorAdapter(tmp_path, POLICY).review(records, analyzer=None)

    assert result["status"] == "NOT_RUN"
    assert result["trusted"] is False
    assert result["advisory_only"] is True
    assert result["coverage"]["viewports"] == 3
    assert result["coverage"]["meets_recommended_viewport_coverage"] is True
    assert result["review"]["revise"] == []
    assert "PASS" not in json.dumps(result).upper()


def test_a10_valid_analyzer_emits_grounded_keep_revise_remove(tmp_path: Path) -> None:
    records = [
        _record(tmp_path, "desktop.png", "/", 1440, 900),
        _record(tmp_path, "mobile.png", "/", 390, 844),
    ]
    adapter = VisionCreativeDirectorAdapter(tmp_path, POLICY)
    sources = [adapter._source(record) for record in records]
    ref = sources[0]["evidence_ref"]
    analyzer = ScriptedCreativeAnalyzer(
        {
            "overall_direction": "Keep the clear hierarchy; tighten responsive composition.",
            "keep": [
                {"route": "/", "section": "hero", "summary": "Strong focal hierarchy", "evidence_refs": [ref]}
            ],
            "revise": [
                {
                    "priority": "P1",
                    "route": "/",
                    "section": "hero",
                    "earliest_owner": "visual_composition",
                    "problem": "Mobile rhythm becomes compressed.",
                    "instruction": "Increase separation between title and primary action.",
                    "success_criteria": "The action remains visually distinct at mobile width.",
                    "confidence": 0.91,
                    "evidence_refs": [ref],
                }
            ],
            "remove": [],
            "notes": ["Review crop behavior on the next iteration."],
        }
    )

    result = adapter.review(records, analyzer)

    assert result["status"] == "OBSERVED"
    assert result["trusted"] is False
    assert result["review"]["revise"][0]["earliest_owner"] == "visual_composition"
    assert result["review"]["revise"][0]["evidence_refs"] == [ref]
    assert analyzer.images[0]["image_path"].endswith("desktop.png")
    assert ref in analyzer.context["evidence_refs"]


def test_a10_unknown_evidence_ref_fails_closed() -> None:
    with pytest.raises(VisionCreativeDirectorError, match="unknown evidence ref"):
        sanitize_creative_output(
            {
                "overall_direction": "fixture",
                "keep": [
                    {"route": "/", "section": "hero", "summary": "fixture", "evidence_refs": ["invented"]}
                ],
                "revise": [],
                "remove": [],
                "notes": [],
            },
            allowed_refs={"real-ref"},
        )


def test_a10_authority_bearing_keys_are_rejected() -> None:
    with pytest.raises(VisionCreativeDirectorError, match="authority-bearing key"):
        sanitize_creative_output(
            {
                "overall_direction": "fixture",
                "approved": True,
                "keep": [],
                "revise": [],
                "remove": [],
                "notes": [],
            },
            allowed_refs={"real-ref"},
        )


def test_a10_external_analyzer_requires_explicit_policy_opt_in(tmp_path: Path) -> None:
    record = _record(tmp_path, "desktop.png", "/", 1440, 900)

    class ExternalAnalyzer(ScriptedCreativeAnalyzer):
        cost_class = "external"

    analyzer = ExternalAnalyzer(
        {
            "overall_direction": "fixture",
            "keep": [],
            "revise": [],
            "remove": [],
            "notes": [],
        }
    )
    with pytest.raises(VisionCreativeDirectorError, match="explicit runtime policy opt-in"):
        VisionCreativeDirectorAdapter(tmp_path, POLICY).review([record], analyzer)


def test_a10_screenshot_hash_mismatch_fails_closed(tmp_path: Path) -> None:
    record = _record(tmp_path, "desktop.png", "/", 1440, 900)
    tampered = EvidenceRecord(
        **{**record.to_dict(), "data": {**record.data, "screenshot_sha256": "0" * 64}}
    )
    with pytest.raises(Exception, match="hash does not match"):
        VisionCreativeDirectorAdapter(tmp_path, POLICY).review([tampered], None)


def test_a10_command_analyzer_is_not_implicitly_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UIUX_VISION_CREATIVE_COMMAND_JSON", raising=False)
    assert configured_vision_creative_analyzer(POLICY) is None
