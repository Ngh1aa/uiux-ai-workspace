import hashlib
import json
from pathlib import Path

from core.contracts.design_context_schema import ReferenceBoard
from core.contracts.reference_evidence_schema import ReferenceEvidenceBundle
from core.provenance.evidence_lineage import (
    build_provenance_manifest,
    build_reference_catalog,
    load_verified_reference_catalog,
)


def _bundle_json() -> str:
    bundle = ReferenceEvidenceBundle.model_validate(
        {
            "references": [
                {
                    "url": "https://example.com",
                    "role": "reference",
                    "status": "observed",
                    "captured_at": "2026-09-27T00:00:00+00:00",
                    "document": {"title": "Example"},
                    "captures": [
                        {
                            "viewport": {"label": "desktop", "width": 1440, "height": 1000},
                            "page_url": "https://example.com",
                            "scroll_width": 1440,
                            "scroll_height": 1800,
                            "horizontal_overflow": False,
                            "computed_styles": [
                                {
                                    "node_index": 0,
                                    "selector": ".hero-title",
                                    "properties": {"font-size": "168px", "opacity": "1"},
                                    "custom_properties": {},
                                }
                            ],
                            "root_custom_properties": {"--ink": "#111111"},
                            "visual_palette": [
                                {
                                    "value": "#111111",
                                    "weight": 0.5,
                                    "evidence": "INFERRED",
                                    "source": "screenshot quantization",
                                }
                            ],
                        }
                    ],
                }
            ]
        }
    )
    return bundle.model_dump_json(indent=2)


def test_reference_catalog_ids_are_stable_across_artifact_paths() -> None:
    raw = _bundle_json()
    first = build_reference_catalog(
        raw,
        source_artifact="/tmp/run-a/reference-evidence.v1.json",
        source_sha256="a" * 64,
    )
    second = build_reference_catalog(
        raw,
        source_artifact="/tmp/run-b/reference-evidence.v1.json",
        source_sha256="b" * 64,
    )
    assert [row.evidence_id for row in first] == [row.evidence_id for row in second]
    assert any(row.selector == ".hero-title" and row.property_name == "font-size" for row in first)
    assert any(row.status == "INFERRED" and row.kind == "color" for row in first)


def test_manifest_links_frozen_spec_statement_to_evidence() -> None:
    raw = _bundle_json()
    records = build_reference_catalog(raw, source_artifact="evidence.json", source_sha256="a" * 64)
    target = next(row for row in records if row.selector == ".hero-title" and row.property_name == "font-size")
    spec = f"## 0. Mission\n\nVERIFIED — hero title is 168px. [[evidence:{target.evidence_id}]]\n"
    manifest = build_provenance_manifest(
        profile="pixel_faithful",
        source_artifact="evidence.json",
        source_sha256="a" * 64,
        records=records,
        spec_text=spec,
    )
    assert manifest.spec_links
    assert manifest.spec_links[0].evidence_ids == [target.evidence_id]
    assert "implementation" in manifest.downstream_consumers
    assert "visual_qa" in manifest.downstream_consumers


def test_declared_reference_artifact_hash_mismatch_is_rejected(tmp_path: Path) -> None:
    artifact = tmp_path / "reference-evidence.v1.json"
    artifact.write_text(_bundle_json(), encoding="utf-8")
    board = ReferenceBoard(
        evidence_artifact=str(artifact),
        evidence_sha256="0" * 64,
    )
    records, source, expected, warnings = load_verified_reference_catalog(board.model_dump_json())
    assert records == []
    assert source == str(artifact)
    assert expected == "0" * 64
    assert any("digest mismatch" in warning.lower() for warning in warnings)


def test_declared_reference_artifact_hash_match_is_accepted(tmp_path: Path) -> None:
    artifact = tmp_path / "reference-evidence.v1.json"
    raw = _bundle_json()
    artifact.write_text(raw, encoding="utf-8")
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    board = ReferenceBoard(evidence_artifact=str(artifact), evidence_sha256=digest)
    records, _source, actual, warnings = load_verified_reference_catalog(board.model_dump_json())
    assert records
    assert actual == digest
    assert warnings == []
