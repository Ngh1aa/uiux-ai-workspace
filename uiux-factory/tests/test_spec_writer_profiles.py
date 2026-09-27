from pathlib import Path

from core.contracts.spec_profile import infer_spec_profile


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
PROMPT_COMPILER = WORKSPACE / "skills_UIUX" / "prompt-compiler"


def test_prompt_compiler_declares_four_non_example_profiles() -> None:
    routing = (PROMPT_COMPILER / "PROFILE-ROUTING.md").read_text(encoding="utf-8")
    for profile in (
        "pixel_faithful",
        "preserve_and_extend",
        "redesign",
        "original_design",
    ):
        assert profile in routing
    assert "Do not infer `pixel_faithful` merely because a reference exists" in routing


def test_pixel_faithful_profile_is_specialized_not_universal() -> None:
    profile = (PROMPT_COMPILER / "profiles" / "pixel-faithful.md").read_text(encoding="utf-8")
    assert "11 sections numbered 0–10" in profile
    assert "Do not call this a universal schema" in profile
    assert "stacking contexts" in profile


def test_original_design_uses_proposed_for_deliberate_design_values() -> None:
    profile = (PROMPT_COMPILER / "profiles" / "original-design.md").read_text(encoding="utf-8")
    assert "labelled `PROPOSED`" in profile
    assert "Use `ASSUMED` for missing contextual facts" in profile


def test_prototype_rubric_treats_common_numbers_as_heuristics() -> None:
    rubric = (PROMPT_COMPILER / "PROTOTYPE-QUALITY-RUBRIC.md").read_text(encoding="utf-8")
    assert "guidance, not magic numbers" in rubric
    assert "useful defaults, not universal truth" in rubric
    assert "label it `SIMULATED`" in rubric


def test_spec_writer_source_requires_profile_routing() -> None:
    source = (ROOT / "core" / "agents" / "spec_writer.py").read_text(encoding="utf-8")
    assert "pixel_faithful, preserve_and_extend, redesign, or original_design" in source
    assert "A reference alone does not imply" in source
    assert "Deliberate design decisions are PROPOSED, not ASSUMED" in source
    assert "CreateProfileAwarePromptPack" in source


def test_profile_classifier_does_not_treat_reference_as_clone_authority() -> None:
    assert infer_spec_profile(
        {
            "goal": "Complete the current cultural prototype",
            "reference_analysis": "existing repository evidence",
        }
    ) == "preserve_and_extend"


def test_profile_classifier_routes_explicit_intent() -> None:
    assert infer_spec_profile({"goal": "Create a pixel-faithful 1:1 clone"}) == "pixel_faithful"
    assert infer_spec_profile({"goal": "Redesign this SaaS dashboard"}) == "redesign"
    assert infer_spec_profile({"goal": "Design a new editorial portfolio from scratch"}) == "original_design"
    assert infer_spec_profile(
        {
            "goal": "anything",
            "spec_profile": "original_design",
            "reference_analysis": "reference exists",
        }
    ) == "original_design"
