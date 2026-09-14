from core.actions.create_ux_ia_v1 import CreateUXIAV1


def test_mid_level_reasoning_contract_contains_required_gates():
    profile = {
        "audience": "Prospective users",
        "task": "Complete a high-value task",
        "conversion": "Evaluate → act",
    }

    artifact = CreateUXIAV1.maturity_layer(profile)

    required_sections = (
        "## UX Reasoning Frame",
        "## Product Thinking Ledger",
        "## Validation Contract",
        "## Accessibility & State Reasoning",
        "## Case Study Capture Contract",
        "## Mid-level UX Gate",
    )

    for section in required_sections:
        assert section in artifact

    assert "target is not a measured result" in artifact.lower()
    assert "never fabricate interviews" in artifact.lower()
    assert "planned validation" in artifact.lower()
    assert "options/trade-off" in artifact


def test_mid_level_reasoning_preserves_inferred_brief_status():
    profile = CreateUXIAV1.assumption_profile(
        "Design a perfume ecommerce experience",
        "ecommerce",
    )

    artifact = CreateUXIAV1.maturity_layer(profile)

    assert "fragrance" in profile["audience"].lower()
    assert "INFERRED from brief until verified" in artifact
    assert "polished UI is not validation" in artifact
