from pathlib import Path

from core.contracts.reference_evidence_schema import (
    EvidenceRect,
    MotionCheckpointEvidence,
    MotionElementStateEvidence,
    ReferenceMotionEvidence,
)


ROOT = Path(__file__).resolve().parents[1]


def test_motion_evidence_round_trip() -> None:
    motion = ReferenceMotionEvidence(
        viewport={"label": "desktop-motion", "width": 1440, "height": 1000},
        max_scroll_y=2700,
        checkpoints=[
            MotionCheckpointEvidence(
                label="scroll-50",
                scroll_y=1350,
                scroll_progress=0.5,
                elements=[
                    MotionElementStateEvidence(
                        selector="#hero",
                        opacity="0.5",
                        transform="matrix(1, 0, 0, 1, 0, -120)",
                        position="fixed",
                        filter="none",
                        rect=EvidenceRect(x=0, y=0, width=1440, height=1000),
                    )
                ],
            )
        ],
    )
    restored = ReferenceMotionEvidence.model_validate_json(motion.model_dump_json())
    assert restored.checkpoints[0].evidence == "VERIFIED"
    assert restored.checkpoints[0].elements[0].selector == "#hero"


def test_motion_sampler_is_non_destructive_and_samples_runtime() -> None:
    source = (ROOT / "core" / "actions" / "analyze_references_with_motion.py").read_text(encoding="utf-8")
    assert "document.getAnimations()" in source
    assert "window.__uiuxReferenceListeners" in source
    assert "[0.0, 0.125, 0.25, 0.5, 0.75, 0.875, 1.0]" in source
    assert "hover/focus only" in source
    assert ".click(" not in source
    assert ".press(" not in source
    assert ".fill(" not in source
    assert ".check(" not in source


def test_reference_analyzer_keeps_motion_sampling_through_provenance_wrapper() -> None:
    agent_source = (ROOT / "core" / "agents" / "reference_analyzer.py").read_text(encoding="utf-8")
    wrapper_source = (ROOT / "core" / "actions" / "analyze_references_with_provenance.py").read_text(encoding="utf-8")
    assert "AnalyzeReferencesWithProvenance" in agent_source
    assert "AnalyzeReferencesWithMotion" in wrapper_source
    assert "await AnalyzeReferencesWithMotion().run(instruction)" in wrapper_source
    assert "Runtime motion values may be VERIFIED" in agent_source
    assert "choreography interpretation must remain INFERRED" in agent_source
