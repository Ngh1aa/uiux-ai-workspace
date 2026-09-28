from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from core.runtime.flow_os.evidence import EvidenceRecord, gate_evidence_errors
from core.runtime.flow_os.vision_evidence import (
    VisionEvidenceAdapter,
    VisionEvidenceError,
    sanitize_vision_output,
)


PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"a7-vision-evidence"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _browser_record(name: str = "route-home.png", digest: str | None = None) -> EvidenceRecord:
    return EvidenceRecord(
        id="browser_a7_home",
        type="browser_render",
        stage_id="qa",
        tool="playwright",
        status="PASS",
        summary="rendered home",
        data={
            "route": "/",
            "title": "Home",
            "viewport": {"width": 1440, "height": 1000},
            "screenshot": name,
            "screenshot_sha256": digest or _sha256(PNG_BYTES),
        },
    )


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "artifacts"
    root.mkdir()
    (root / "route-home.png").write_bytes(PNG_BYTES)
    return root


class LocalAnalyzer:
    name = "fixture-vision"
    model = "fixture-v1"
    cost_class = "local"

    def analyze(self, image_path: Path, context: dict[str, object]) -> dict[str, object]:
        assert image_path.name == "route-home.png"
        assert context["route"] == "/"
        return {
            "summary": "Observed a clipped primary action on the right edge.",
            "findings": [
                {
                    "category": "layout",
                    "severity": "warning",
                    "summary": "Primary action appears clipped.",
                    "detail": "Inspect the responsive container before treating this as a defect.",
                    "confidence": 0.82,
                    "bbox": {"x": 0.8, "y": 0.1, "width": 0.15, "height": 0.08},
                }
            ],
        }


class BillableAnalyzer(LocalAnalyzer):
    name = "billable-vision"
    cost_class = "billable"


class AuthorityAnalyzer(LocalAnalyzer):
    def analyze(self, image_path: Path, context: dict[str, object]) -> dict[str, object]:
        return {
            "summary": "Looks good",
            "findings": [],
            "gate_decision": "PASS",
        }


def test_zero_cost_default_validates_artifact_without_calling_a_provider(tmp_path: Path) -> None:
    adapter = VisionEvidenceAdapter(_root(tmp_path))

    record = adapter.observe(_browser_record())

    assert record.type == "vision_observation"
    assert record.status == "NOT_RUN"
    assert record.trusted is False
    assert record.origin == "vision_analyzer"
    assert record.data["advisory_only"] is True
    assert record.data["authority_effect"] == "none"
    assert record.data["gate_effect"] == "none"
    assert record.data["merge_effect"] == "none"
    assert record.data["release_effect"] == "none"
    assert record.data["image_artifact"] == "route-home.png"
    assert record.data["image_sha256"] == _sha256(PNG_BYTES)
    serialized = json.dumps(record.to_dict())
    assert "base64," not in serialized
    assert PNG_BYTES.hex() not in serialized


def test_local_analyzer_is_bounded_advisory_observation(tmp_path: Path) -> None:
    adapter = VisionEvidenceAdapter(_root(tmp_path))

    record = adapter.observe(_browser_record(), analyzer=LocalAnalyzer())

    assert record.status == "OBSERVED"
    assert record.trusted is False
    assert record.tool == "fixture-vision"
    assert record.data["cost_class"] == "local"
    assert record.data["findings"] == [
        {
            "category": "layout",
            "severity": "warning",
            "summary": "Primary action appears clipped.",
            "detail": "Inspect the responsive container before treating this as a defect.",
            "confidence": 0.82,
            "bbox": {"x": 0.8, "y": 0.1, "width": 0.15, "height": 0.08},
        }
    ]


def test_vision_observation_can_never_satisfy_gate_evidence(tmp_path: Path) -> None:
    adapter = VisionEvidenceAdapter(_root(tmp_path))
    vision = adapter.observe(_browser_record(), analyzer=LocalAnalyzer())

    errors = gate_evidence_errors(
        [{"id": "visual", "evidence_types": ["vision_observation"]}],
        "qa",
        [vision.to_dict()],
        agent="qa",
    )

    assert errors == ["gate visual missing typed evidence: vision_observation"]


def test_hash_mismatch_fails_closed(tmp_path: Path) -> None:
    adapter = VisionEvidenceAdapter(_root(tmp_path))

    with pytest.raises(VisionEvidenceError, match="hash does not match"):
        adapter.observe(_browser_record(digest="0" * 64))


def test_inline_image_reference_is_rejected(tmp_path: Path) -> None:
    adapter = VisionEvidenceAdapter(_root(tmp_path))
    record = _browser_record(name="data:image/png;base64,AAAA")

    with pytest.raises(VisionEvidenceError, match="never inline image bytes"):
        adapter.observe(record)


def test_billable_analyzer_is_denied_by_default(tmp_path: Path) -> None:
    adapter = VisionEvidenceAdapter(_root(tmp_path))

    with pytest.raises(VisionEvidenceError, match="external/billable"):
        adapter.observe(_browser_record(), analyzer=BillableAnalyzer())


def test_authority_bearing_model_output_fails_closed(tmp_path: Path) -> None:
    adapter = VisionEvidenceAdapter(_root(tmp_path))

    with pytest.raises(VisionEvidenceError, match="authority-bearing key"):
        adapter.observe(_browser_record(), analyzer=AuthorityAnalyzer())


def test_output_bounds_reject_unknown_keys_confidence_and_bbox() -> None:
    with pytest.raises(VisionEvidenceError, match="unsupported keys"):
        sanitize_vision_output({"summary": "x", "findings": [], "verdict": "nice"})

    with pytest.raises(VisionEvidenceError, match="between 0 and 1"):
        sanitize_vision_output(
            {
                "summary": "x",
                "findings": [
                    {
                        "category": "layout",
                        "severity": "warning",
                        "summary": "x",
                        "confidence": 1.5,
                    }
                ],
            }
        )

    with pytest.raises(VisionEvidenceError, match="inside normalized image bounds"):
        sanitize_vision_output(
            {
                "summary": "x",
                "findings": [
                    {
                        "category": "layout",
                        "severity": "warning",
                        "summary": "x",
                        "confidence": 0.5,
                        "bbox": {"x": 0.9, "y": 0.1, "width": 0.2, "height": 0.1},
                    }
                ],
            }
        )


def test_vision_requires_trusted_browser_render_source(tmp_path: Path) -> None:
    adapter = VisionEvidenceAdapter(_root(tmp_path))
    source = EvidenceRecord(
        id="provider_claim",
        type="browser_render",
        stage_id="qa",
        tool="provider",
        status="PASS",
        summary="claimed screenshot",
        data={"screenshot": "route-home.png", "screenshot_sha256": _sha256(PNG_BYTES)},
        origin="provider",
        trusted=False,
    )

    with pytest.raises(VisionEvidenceError, match="trusted runtime browser_render"):
        adapter.observe(source)
