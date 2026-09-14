import ast
from pathlib import Path


SOURCE_PATH = Path(__file__).resolve().parents[1] / "core" / "actions" / "create_ux_ia_v1.py"


def _source() -> str:
    return SOURCE_PATH.read_text(encoding="utf-8")


def test_mid_level_reasoning_contract_contains_required_gates():
    source = _source()

    required_sections = (
        "## UX Reasoning Frame",
        "## Product Thinking Ledger",
        "## Validation Contract",
        "## Accessibility & State Reasoning",
        "## Case Study Capture Contract",
        "## Mid-level UX Gate",
    )

    for section in required_sections:
        assert section in source

    assert "A target is not a measured result" in source
    assert "Never fabricate interviews" in source
    assert "PLANNED VALIDATION" in source
    assert "options/trade-off" in source


def test_mid_level_reasoning_source_is_valid_and_preserves_truth_labels():
    source = _source()

    ast.parse(source)

    assert "INFERRED from brief until verified" in source
    assert "polished UI is not validation" in source
    assert "working hypothesis, not validated user research" not in source
    assert "fragrance" in source.lower()
