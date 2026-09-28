from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from core.runtime.flow_os.provider import (
    ProviderStageRequest,
    ProviderStageResponse,
    provider_response_schema,
    render_provider_prompt,
)


ENDPOINTS = {
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
}
KEY_NAMES = {"groq": "GROQ_API_KEY", "gemini": "GEMINI_API_KEY"}
MODEL_NAMES = {"groq": "UIUX_GROQ_MODEL", "gemini": "UIUX_GEMINI_MODEL"}


def _system_prompt() -> str:
    return (
        "You are a specialist execution agent inside skills_UIUX Flow Agent OS. "
        "Flow owns orchestration, stage order, skills, approvals and replanning. "
        "Use only provided tools. Return structured stage JSON only. "
        "A model claim is not evidence; PASS requires concrete gate evidence."
    )


def _http_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(4_000_001)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"free-tier provider HTTP {exc.code}; check key, model and account tier") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"free-tier provider network error: {exc.reason}") from exc
    if len(raw) > 4_000_000:
        raise RuntimeError("free-tier provider response exceeded 4 MB")
    decoded = json.loads(raw.decode("utf-8"))
    if not isinstance(decoded, dict):
        raise RuntimeError("free-tier provider response must be a JSON object")
    return decoded


class OpenAICompatibleFreeTierProvider:
    """Canonical managed adapter for explicitly confirmed Groq/Gemini free-tier accounts."""

    supports_hard_output_limit = True

    def __init__(
        self,
        name: str,
        *,
        model: str | None = None,
        api_key: str | None = None,
        timeout: int = 120,
        env: dict[str, str] | None = None,
    ) -> None:
        normalized = str(name).strip().lower()
        if normalized not in ENDPOINTS:
            raise ValueError(f"unsupported free-tier provider: {normalized}")
        source_env = dict(os.environ if env is None else env)
        if source_env.get("UIUX_FREE_TIER_CONFIRMED") != "1":
            raise ValueError(
                "free-tier provider requires UIUX_FREE_TIER_CONFIRMED=1 after verifying account billing/tier"
            )
        configured = [item.strip().lower() for item in source_env.get("UIUX_CLOUD_PROVIDERS", "").split(",") if item.strip()]
        if normalized not in configured:
            raise ValueError(f"provider={normalized} is not enabled in UIUX_CLOUD_PROVIDERS")

        resolved_key = api_key or source_env.get(KEY_NAMES[normalized], "")
        resolved_model = model or source_env.get(MODEL_NAMES[normalized], "")
        if not resolved_key or not resolved_model:
            raise ValueError(f"provider={normalized} requires {KEY_NAMES[normalized]} and {MODEL_NAMES[normalized]}")

        self.name = normalized
        self.model = str(resolved_model)
        self.api_key = str(resolved_key)
        self.timeout = int(timeout)
        self.max_output_tokens: int | None = 8192
        # A6.3 trusts billing usage only from canonical OpenAI/Anthropic transports.
        self.last_reported_usage = None

    def run_stage(self, request: ProviderStageRequest) -> ProviderStageResponse:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": _system_prompt()},
                {"role": "user", "content": render_provider_prompt(request)},
            ],
            "max_tokens": max(1, int(self.max_output_tokens or 8192)),
            "stream": False,
            "response_format": {"type": "json_object"},
        }
        data = _http_json(
            ENDPOINTS[self.name],
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            payload,
            self.timeout,
        )
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError("free-tier provider returned no choices")
        choice = choices[0]
        if not isinstance(choice, dict):
            raise RuntimeError("free-tier provider choice must be an object")
        finish_reason = choice.get("finish_reason")
        if finish_reason not in {"stop", None}:
            raise RuntimeError(f"free-tier provider response incomplete: {finish_reason}")
        message = choice.get("message")
        if not isinstance(message, dict):
            raise RuntimeError("free-tier provider response contained no message")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("free-tier provider returned empty content")
        decoded = json.loads(content)
        if not isinstance(decoded, dict):
            raise RuntimeError("free-tier provider structured output was not an object")
        return ProviderStageResponse.from_dict(decoded)


def create_free_tier_provider(name: str, model: str | None = None) -> OpenAICompatibleFreeTierProvider:
    return OpenAICompatibleFreeTierProvider(name, model=model)
