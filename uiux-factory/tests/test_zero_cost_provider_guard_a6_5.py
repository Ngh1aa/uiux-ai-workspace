from __future__ import annotations

import json

import pytest

from core.runtime.flow_os import free_tier_provider as free_module
from core.runtime.flow_os.free_tier_provider import OpenAICompatibleFreeTierProvider
from core.runtime.flow_os.provider import ProviderStageRequest
from core.runtime.flow_os.provider_access import ProviderAccessGuard
from core.runtime.flow_os.provider_routing import ROUTABLE_PROVIDERS, StageProviderRouter


def _free_env(provider: str = "groq") -> dict[str, str]:
    env = {
        "UIUX_FREE_TIER_CONFIRMED": "1",
        "UIUX_CLOUD_PROVIDERS": provider,
        "OPENAI_API_KEY": "paid-key-must-not-be-auto-selected",
        "ANTHROPIC_API_KEY": "paid-key-must-not-be-auto-selected",
    }
    if provider == "groq":
        env.update({"GROQ_API_KEY": "free-key", "UIUX_GROQ_MODEL": "free-groq-model"})
    else:
        env.update({"GEMINI_API_KEY": "free-key", "UIUX_GEMINI_MODEL": "free-gemini-model"})
    return env


def _request() -> ProviderStageRequest:
    return ProviderStageRequest(
        goal="Polish checkout UI",
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


def test_a6_5_auto_selects_only_confirmed_free_tier_even_when_paid_keys_exist() -> None:
    guard = ProviderAccessGuard({}, env=_free_env("groq"))

    decision = guard.resolve("auto")

    assert decision.provider == "groq"
    assert decision.access_class == "zero_cost_free_tier"
    assert decision.paid_opt_in is False


def test_a6_5_auto_never_falls_back_to_paid_provider() -> None:
    guard = ProviderAccessGuard(
        {},
        env={
            "OPENAI_API_KEY": "paid-key",
            "ANTHROPIC_API_KEY": "paid-key",
        },
    )

    with pytest.raises(ValueError, match="zero-cost-only"):
        guard.resolve("auto")


def test_a6_5_paid_provider_requires_policy_and_per_invocation_opt_in() -> None:
    blocked_policy = ProviderAccessGuard(
        {"provider_access": {"mode": "zero_cost", "allow_paid_providers": False}}
    )
    with pytest.raises(ValueError, match="disabled by zero-cost policy"):
        blocked_policy.resolve("openai", allow_paid_opt_in=True)

    allowed_policy = ProviderAccessGuard(
        {"provider_access": {"mode": "zero_cost", "allow_paid_providers": True}}
    )
    with pytest.raises(ValueError, match="--allow-paid-provider"):
        allowed_policy.resolve("anthropic", allow_paid_opt_in=False)

    decision = allowed_policy.resolve("anthropic", allow_paid_opt_in=True)
    assert decision.provider == "anthropic"
    assert decision.paid_opt_in is True
    assert decision.access_class == "paid_explicit_opt_in"


def test_a6_5_provider_classification_cannot_be_rewritten_by_policy_payload() -> None:
    guard = ProviderAccessGuard(
        {
            "provider_access": {
                "mode": "zero_cost",
                "allow_paid_providers": False,
                "zero_cost_providers": ["openai"],
            }
        }
    )

    with pytest.raises(ValueError, match="disabled by zero-cost policy"):
        guard.resolve("openai", allow_paid_opt_in=True)


def test_a6_5_groq_and_gemini_are_stage_routable() -> None:
    assert {"groq", "gemini"}.issubset(ROUTABLE_PROVIDERS)
    router = StageProviderRouter(
        {
            "provider_routing": {
                "enabled": True,
                "allow_provider_switch": True,
                "by_stage": {
                    "implementation": {"provider": "gemini", "model": "free-gemini-model"}
                },
            }
        }
    )

    selection = router.resolve(
        stage_id="implementation",
        agent="implementation",
        default_provider="groq",
        default_model="free-groq-model",
        requested_max_turns=8,
    )

    assert selection.provider == "gemini"
    assert selection.model == "free-gemini-model"


def test_a6_5_free_tier_adapter_requires_explicit_confirmation() -> None:
    with pytest.raises(ValueError, match="UIUX_FREE_TIER_CONFIRMED=1"):
        OpenAICompatibleFreeTierProvider(
            "groq",
            env={
                "UIUX_CLOUD_PROVIDERS": "groq",
                "GROQ_API_KEY": "key",
                "UIUX_GROQ_MODEL": "model",
            },
        )


def test_a6_5_free_tier_adapter_applies_hard_output_cap_and_ignores_usage_spoof(monkeypatch) -> None:
    captured: dict = {}

    def fake_http(url, headers, payload, timeout):
        captured.update({"url": url, "headers": headers, "payload": payload, "timeout": timeout})
        model_payload = {
            "status": "CONTINUE",
            "actions": [],
            "summary": "fixture",
            "evidence": [],
            "replan_signal": None,
            "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
        }
        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": json.dumps(model_payload)},
                }
            ],
            "usage": {"prompt_tokens": 9000, "completion_tokens": 8000},
        }

    monkeypatch.setattr(free_module, "_http_json", fake_http)
    provider = OpenAICompatibleFreeTierProvider("groq", env=_free_env("groq"))
    provider.max_output_tokens = 777

    response = provider.run_stage(_request())

    assert response.status == "CONTINUE"
    assert captured["payload"]["max_tokens"] == 777
    assert provider.last_reported_usage is None
    assert "paid-key-must-not-be-auto-selected" not in repr(captured)
