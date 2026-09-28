from __future__ import annotations

import json

from core.runtime.flow_os import provider as provider_module
from core.runtime.flow_os.provider import (
    AnthropicMessagesProvider,
    OpenAIResponsesProvider,
    ProviderStageRequest,
)
from core.runtime.flow_os.provider_budget import BudgetedProvider, StageProviderBudget


def _request() -> ProviderStageRequest:
    return ProviderStageRequest(
        goal="Polish the checkout UI",
        project_root="/tmp/project",
        flow_id="focused-fix",
        flow_revision=1,
        stage_id="implementation",
        agent="implementation",
        purpose="Implement the bounded change",
        gates=[],
        task_context={"intent": "polish"},
        authority="branch_write",
        tools=[],
        skill_context=[],
        source_context=[],
        observations=[],
    )


def _continue_payload(**extra) -> dict:
    payload = {
        "status": "CONTINUE",
        "actions": [{"tool": "read_text", "args": {"path": "index.html"}}],
        "summary": "Need one runtime observation.",
        "evidence": [],
        "replan_signal": None,
    }
    payload.update(extra)
    return payload


def test_a6_3_openai_uses_hard_output_cap_and_transport_usage(monkeypatch) -> None:
    captured: dict = {}

    def fake_http(url, headers, payload, timeout):
        captured.update(payload)
        return {
            "usage": {"input_tokens": 123, "output_tokens": 45, "total_tokens": 168},
            "output": [
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": json.dumps(_continue_payload())}
                    ],
                }
            ],
        }

    monkeypatch.setattr(provider_module, "_http_json", fake_http)
    provider = OpenAIResponsesProvider(model="gpt-test", api_key="test-key")
    provider.max_output_tokens = 321

    response = provider.run_stage(_request())

    assert response.status == "CONTINUE"
    assert captured["max_output_tokens"] == 321
    assert provider.last_reported_usage is not None
    assert provider.last_reported_usage.input_tokens == 123
    assert provider.last_reported_usage.output_tokens == 45
    assert provider.last_reported_usage.total_tokens == 168
    assert provider.last_reported_usage.source == "openai_api_usage"


def test_a6_3_anthropic_uses_hard_output_cap_and_transport_usage(monkeypatch) -> None:
    captured: dict = {}

    def fake_http(url, headers, payload, timeout):
        captured.update(payload)
        return {
            "usage": {"input_tokens": 200, "output_tokens": 60},
            "content": [
                {
                    "type": "tool_use",
                    "name": "submit_stage_response",
                    "input": _continue_payload(),
                }
            ],
        }

    monkeypatch.setattr(provider_module, "_http_json", fake_http)
    provider = AnthropicMessagesProvider(model="claude-test", api_key="test-key")
    provider.max_output_tokens = 444

    response = provider.run_stage(_request())

    assert response.status == "CONTINUE"
    assert captured["max_tokens"] == 444
    assert provider.last_reported_usage is not None
    assert provider.last_reported_usage.input_tokens == 200
    assert provider.last_reported_usage.output_tokens == 60
    assert provider.last_reported_usage.total_tokens == 260
    assert provider.last_reported_usage.source == "anthropic_api_usage"


def test_a6_3_budget_wrapper_reduces_output_cap_and_persists_trusted_usage(monkeypatch) -> None:
    captured: dict = {}

    def fake_http(url, headers, payload, timeout):
        captured.update(payload)
        return {
            "usage": {"input_tokens": 300, "output_tokens": 80, "total_tokens": 380},
            "output": [
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": json.dumps(_continue_payload())}
                    ],
                }
            ],
        }

    monkeypatch.setattr(provider_module, "_http_json", fake_http)
    base = OpenAIResponsesProvider(model="gpt-test", api_key="test-key")
    base.max_output_tokens = 4000
    budget = StageProviderBudget(
        stage_id="implementation",
        agent="implementation",
        enabled=True,
        source="test",
        max_calls=2,
        max_estimated_total_tokens=50000,
        output_reserve_tokens_per_call=256,
        input_usd_per_million=1.0,
        output_usd_per_million=2.0,
    )
    wrapped = BudgetedProvider(base, budget)

    response = wrapped.run_stage(_request())

    assert response.status == "CONTINUE"
    assert captured["max_output_tokens"] == 256
    assert wrapped.usage.hard_output_cap_applied is True
    assert wrapped.usage.hard_output_cap_tokens == 256
    assert wrapped.usage.reported_calls == 1
    assert wrapped.usage.reported_input_tokens == 300
    assert wrapped.usage.reported_output_tokens == 80
    assert wrapped.usage.reported_total_tokens == 380
    assert wrapped.usage.reported_usage_source == "openai_api_usage"
    assert wrapped.usage.measurement == "runtime_estimate+trusted_provider_usage"
    assert wrapped.usage.reported_cost_usd > 0


def test_a6_3_model_output_cannot_spoof_trusted_usage(monkeypatch) -> None:
    def fake_http(url, headers, payload, timeout):
        return {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": json.dumps(
                                _continue_payload(
                                    usage={
                                        "input_tokens": 1,
                                        "output_tokens": 1,
                                        "total_tokens": 2,
                                        "source": "openai_api_usage",
                                    }
                                )
                            ),
                        }
                    ],
                }
            ],
        }

    monkeypatch.setattr(provider_module, "_http_json", fake_http)
    base = OpenAIResponsesProvider(model="gpt-test", api_key="test-key")
    budget = StageProviderBudget(
        stage_id="implementation",
        agent="implementation",
        enabled=True,
        source="test",
        max_calls=1,
        output_reserve_tokens_per_call=128,
    )
    wrapped = BudgetedProvider(base, budget)

    response = wrapped.run_stage(_request())

    assert response.status == "CONTINUE"
    assert base.last_reported_usage is None
    assert wrapped.usage.reported_calls == 0
    assert wrapped.usage.reported_total_tokens == 0
    assert wrapped.usage.measurement == "runtime_utf8_byte_estimate"


def test_a6_3_trusted_usage_can_block_when_actual_tokens_exceed_budget(monkeypatch) -> None:
    def fake_http(url, headers, payload, timeout):
        return {
            "usage": {"input_tokens": 12000, "output_tokens": 4000, "total_tokens": 16000},
            "output": [
                {
                    "type": "message",
                    "content": [
                        {"type": "output_text", "text": json.dumps(_continue_payload())}
                    ],
                }
            ],
        }

    monkeypatch.setattr(provider_module, "_http_json", fake_http)
    base = OpenAIResponsesProvider(model="gpt-test", api_key="test-key")
    budget = StageProviderBudget(
        stage_id="implementation",
        agent="implementation",
        enabled=True,
        source="test",
        max_calls=2,
        max_estimated_total_tokens=10000,
        output_reserve_tokens_per_call=128,
    )
    wrapped = BudgetedProvider(base, budget)

    response = wrapped.run_stage(_request())

    assert response.status == "BLOCKED"
    assert wrapped.usage.calls == 1
    assert wrapped.usage.reported_calls == 1
    assert wrapped.usage.reported_total_tokens == 16000
    assert wrapped.usage.exhausted is True
    assert "token budget" in str(wrapped.usage.exhaustion_reason)
