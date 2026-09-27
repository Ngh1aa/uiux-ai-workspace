from pathlib import Path

from core.benchmarks.prompt_os_v1 import PromptOSProfileBenchmark


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "benchmarks" / "prompt_os_v1_profiles.json"


def test_prompt_os_v1_four_profile_benchmark_passes() -> None:
    result = PromptOSProfileBenchmark(FIXTURE).run()
    assert result["case_count"] == 4
    assert result["failed_count"] == 0
    assert result["passed"] is True
    assert {row["profile"] for row in result["cases"]} == {
        "pixel_faithful",
        "preserve_and_extend",
        "redesign",
        "original_design",
    }


def test_benchmark_guards_reference_does_not_equal_clone() -> None:
    result = PromptOSProfileBenchmark(FIXTURE).run()
    preserve = next(row for row in result["cases"] if row["id"] == "preserve-and-extend-existing-product")
    assert preserve["profile"] == "preserve_and_extend"
    assert preserve["visual_mode"] == "protected_surfaces"
    assert preserve["blocking"] is False


def test_benchmark_keeps_redesign_and_original_spec_only() -> None:
    result = PromptOSProfileBenchmark(FIXTURE).run()
    for case_id in ("redesign-existing-product", "original-design-greenfield"):
        row = next(item for item in result["cases"] if item["id"] == case_id)
        assert row["visual_mode"] == "spec_only"
        assert row["status"] == "inapplicable"
        assert row["blocking"] is False
