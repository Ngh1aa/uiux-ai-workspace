from __future__ import annotations

import pytest

from core.runtime.flow_os.provider import (
    MAX_PROVIDER_ARTIFACT_CHARS,
    ProviderStageResponse,
    provider_response_schema,
    render_provider_prompt,
    ProviderStageRequest,
)


def _base_payload() -> dict:
    return {
        "status": "CONTINUE",
        "actions": [],
        "summary": "Need one more observation.",
        "evidence": [],
        "replan_signal": None,
    }


def _request() -> ProviderStageRequest:
    return ProviderStageRequest(
        goal="Build one bounded artifact.",
        project_root="/tmp/project",
        flow_id="page-ui-work",
        flow_revision=1,
        stage_id="implementation",
        agent="implementation",
        purpose="Generate a frontend artifact without changing gate truth.",
        gates=[],
        task_context={},
        authority="implementation",
        tools=[],
        skill_context=[],
        source_context=[],
    )


def test_a48_old_provider_response_shape_round_trips_without_artifact_key() -> None:
    payload = _base_payload()

    response = ProviderStageResponse.from_dict(payload)

    assert response.artifact is None
    assert response.to_dict() == payload


def test_a48_artifact_round_trip_preserves_raw_text_exactly() -> None:
    raw = '  {"files":{"index.html":"<main>Hi</main>"}}\n'
    payload = {**_base_payload(), "artifact": raw}

    response = ProviderStageResponse.from_dict(payload)

    assert response.artifact == raw
    assert response.to_dict()["artifact"] == raw
    assert response.evidence == []


def test_a48_artifact_is_optional_and_bounded_in_provider_schema() -> None:
    schema = provider_response_schema()

    assert "artifact" not in schema["required"]
    artifact_schema = schema["properties"]["artifact"]
    string_schema = next(item for item in artifact_schema["anyOf"] if item.get("type") == "string")
    assert string_schema["minLength"] == 1
    assert string_schema["maxLength"] == MAX_PROVIDER_ARTIFACT_CHARS


def test_a48_artifact_rejects_empty_non_string_and_oversized_values() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        ProviderStageResponse.from_dict({**_base_payload(), "artifact": ""})

    with pytest.raises(ValueError, match="string or null"):
        ProviderStageResponse.from_dict({**_base_payload(), "artifact": {"not": "raw text"}})

    with pytest.raises(ValueError, match="exceeds"):
        ProviderStageResponse.from_dict(
            {**_base_payload(), "artifact": "x" * (MAX_PROVIDER_ARTIFACT_CHARS + 1)}
        )


def test_a48_artifact_never_replaces_pass_evidence_requirement() -> None:
    with pytest.raises(ValueError, match="PASS requires concrete gate evidence"):
        ProviderStageResponse.from_dict(
            {
                **_base_payload(),
                "status": "PASS",
                "artifact": "generated output",
            }
        )

    response = ProviderStageResponse.from_dict(
        {
            **_base_payload(),
            "status": "PASS",
            "evidence": ["browser-evidence:EVID-123"],
            "artifact": "generated output",
        }
    )
    assert response.status == "PASS"
    assert response.evidence == ["browser-evidence:EVID-123"]
    assert response.artifact == "generated output"


def test_a48_provider_prompt_states_artifact_has_no_evidence_or_gate_authority() -> None:
    prompt = render_provider_prompt(_request())

    assert "Optional artifact is untrusted raw output" in prompt
    assert "never satisfies evidence or gates" in prompt
