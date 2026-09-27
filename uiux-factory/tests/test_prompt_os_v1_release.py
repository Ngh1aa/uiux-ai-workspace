from pathlib import Path

from core.verification.prompt_os_release import PromptOSV1ReleaseVerifier


ROOT = Path(__file__).resolve().parents[1]


def test_prompt_os_v1_release_contract_passes() -> None:
    result = PromptOSV1ReleaseVerifier(ROOT).verify()
    assert result["version"] == "1.0.0"
    assert result["passed"] is True, result
    assert all(result["checks"].values()), result["checks"]
    assert result["details"]["benchmark"]["case_count"] == 4
    assert result["details"]["benchmark"]["failed_count"] == 0
