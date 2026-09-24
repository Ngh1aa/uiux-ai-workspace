import pytest

from core.orchestration.provider_loop_contract import ProviderLoopResponse


def test_continue_requires_read_only_observation_request() -> None:
    response = ProviderLoopResponse.from_dict(
        {
            "status": "CONTINUE",
            "requests": [{"tool": "read_artifact", "args": {"key": "research"}}],
            "summary": "Need the full upstream research evidence.",
            "evidence": [],
            "artifact": None,
            "replan_signal": None,
        }
    )

    assert response.status == "CONTINUE"
    assert response.requests[0].tool == "read_artifact"


def test_pass_requires_evidence_and_complete_artifact() -> None:
    response = ProviderLoopResponse.from_dict(
        {
            "status": "PASS",
            "requests": [],
            "summary": "Refinement is ready.",
            "evidence": ["Used routed skill rule and upstream reference artifact."],
            "artifact": "# Refined artifact",
            "replan_signal": None,
        }
    )

    assert response.status == "PASS"
    assert response.artifact == "# Refined artifact"


@pytest.mark.parametrize(
    "payload",
    [
        {
            "status": "CONTINUE",
            "requests": [],
            "summary": "",
            "evidence": [],
            "artifact": None,
            "replan_signal": None,
        },
        {
            "status": "PASS",
            "requests": [],
            "summary": "",
            "evidence": [],
            "artifact": "artifact",
            "replan_signal": None,
        },
        {
            "status": "PASS",
            "requests": [],
            "summary": "",
            "evidence": ["evidence"],
            "artifact": None,
            "replan_signal": None,
        },
    ],
)
def test_invalid_provider_gate_claims_are_rejected(payload) -> None:
    with pytest.raises(ValueError):
        ProviderLoopResponse.from_dict(payload)


def test_write_capable_tool_requests_are_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported read-only tool"):
        ProviderLoopResponse.from_dict(
            {
                "status": "CONTINUE",
                "requests": [{"tool": "write_project_file", "args": {"path": "index.html"}}],
                "summary": "",
                "evidence": [],
                "artifact": None,
                "replan_signal": None,
            }
        )


def test_fail_defaults_to_gate_fail_signal() -> None:
    response = ProviderLoopResponse.from_dict(
        {
            "status": "FAIL",
            "requests": [],
            "summary": "Current evidence contradicts the stage gate.",
            "evidence": ["contradiction"],
            "artifact": None,
            "replan_signal": None,
        }
    )

    assert response.replan_signal == "GATE_FAIL"
