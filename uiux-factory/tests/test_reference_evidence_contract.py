from pathlib import Path

from core.contracts.reference_evidence_schema import (
    DOMNodeEvidence,
    EvidenceRect,
    EvidenceViewport,
    PaletteColorEvidence,
    ReferenceCaptureEvidence,
    ReferenceEvidenceBundle,
    ReferencePageEvidence,
)


ROOT = Path(__file__).resolve().parents[1]


def test_reference_evidence_v1_round_trip() -> None:
    capture = ReferenceCaptureEvidence(
        viewport=EvidenceViewport(label="desktop", width=1440, height=1000),
        page_url="https://example.com/",
        scroll_width=1440,
        scroll_height=2400,
        horizontal_overflow=False,
        dom=[
            DOMNodeEvidence(
                index=0,
                parent_index=None,
                tag="body",
                selector="body",
                visible=True,
                rect=EvidenceRect(x=0, y=0, width=1440, height=2400),
            )
        ],
        css_colors=[
            PaletteColorEvidence(
                value="rgb(17, 20, 17)",
                weight=0.5,
                evidence="VERIFIED",
                source="computed-style frequency",
            )
        ],
        visual_palette=[
            PaletteColorEvidence(
                value="#111411",
                weight=0.5,
                evidence="INFERRED",
                source="screenshot quantization",
            )
        ],
    )
    bundle = ReferenceEvidenceBundle(
        references=[
            ReferencePageEvidence(
                url="https://example.com/",
                role="reference",
                status="observed",
                captures=[capture],
            )
        ]
    )
    restored = ReferenceEvidenceBundle.model_validate_json(bundle.model_dump_json())
    assert restored.schema_version == "reference-evidence.v1"
    assert restored.references[0].captures[0].dom[0].evidence == "VERIFIED"
    assert restored.references[0].captures[0].visual_palette[0].evidence == "INFERRED"


def test_extractor_writes_deep_evidence_without_replacing_reference_board() -> None:
    source = (ROOT / "core" / "actions" / "analyze_references.py").read_text(encoding="utf-8")
    assert 'reference-evidence.v1.json' in source
    assert 'ReferenceBoard()' in source
    assert 'MEASURE_EVIDENCE' in source
    assert 'MAX_DOM = 900' in source
    assert 'MAX_STYLES = 260' in source
    assert 'screenshot quantization' in source


def test_deep_evidence_distinguishes_css_truth_from_visual_palette() -> None:
    source = (ROOT / "core" / "actions" / "analyze_references.py").read_text(encoding="utf-8")
    assert "css_colors" in source
    assert "computed-style frequency" in source
    assert 'evidence="INFERRED"' in source
    assert "screenshot pixels are" in source
