from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any, Mapping


ZERO_COST_PROVIDERS = frozenset({"groq", "gemini"})
PAID_PROVIDERS = frozenset({"openai", "anthropic"})
OPERATOR_MANAGED_PROVIDERS = frozenset({"command"})
SUPPORTED_MANAGED_PROVIDERS = ZERO_COST_PROVIDERS | PAID_PROVIDERS | OPERATOR_MANAGED_PROVIDERS
_KEY_NAMES = {"groq": "GROQ_API_KEY", "gemini": "GEMINI_API_KEY"}
_MODEL_NAMES = {"groq": "UIUX_GROQ_MODEL", "gemini": "UIUX_GEMINI_MODEL"}


@dataclass(frozen=True)
class ProviderAccessDecision:
    provider: str
    access_class: str
    source: str
    paid_opt_in: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ProviderAccessGuard:
    """Fail-closed managed-provider access policy with a zero-cost default.

    Provider class membership is code-owned so task/model output cannot reclassify a
    paid provider as free. Runtime policy may allow paid transports, but a caller must
    still pass an explicit paid-provider opt-in for the invocation.
    """

    def __init__(self, policy_doc: Mapping[str, Any], env: Mapping[str, str] | None = None) -> None:
        raw = policy_doc.get("provider_access", {})
        if raw is None:
            raw = {}
        if not isinstance(raw, dict):
            raise ValueError("runtime provider_access policy must be an object")
        self.policy = dict(raw)
        self.env = dict(os.environ if env is None else env)
        mode = str(self.policy.get("mode", "zero_cost")).strip().lower()
        if mode != "zero_cost":
            raise ValueError("provider_access.mode currently supports only zero_cost")

    def _free_tier_confirmed(self) -> bool:
        return self.env.get("UIUX_FREE_TIER_CONFIRMED") == "1"

    def _configured_free_providers(self) -> list[str]:
        names = [
            item.strip().lower()
            for item in str(self.env.get("UIUX_CLOUD_PROVIDERS", "")).split(",")
            if item.strip()
        ]
        result: list[str] = []
        for name in names:
            if name not in ZERO_COST_PROVIDERS or name in result:
                continue
            if not self.env.get(_KEY_NAMES[name]) or not self.env.get(_MODEL_NAMES[name]):
                continue
            result.append(name)
        return result

    def resolve(
        self,
        requested_provider: str,
        *,
        allow_paid_opt_in: bool = False,
    ) -> ProviderAccessDecision:
        requested = str(requested_provider or "").strip().lower()
        if not requested:
            raise ValueError("managed provider is required")

        if requested == "auto":
            if not self._free_tier_confirmed():
                raise ValueError(
                    "provider=auto is zero-cost-only and requires UIUX_FREE_TIER_CONFIRMED=1; "
                    "it never falls back to OpenAI or Anthropic"
                )
            configured = self._configured_free_providers()
            if not configured:
                raise ValueError(
                    "provider=auto found no confirmed Groq/Gemini free-tier provider; "
                    "configure UIUX_CLOUD_PROVIDERS plus its key/model explicitly"
                )
            return ProviderAccessDecision(
                provider=configured[0],
                access_class="zero_cost_free_tier",
                source="zero_cost_auto",
            )

        if requested not in SUPPORTED_MANAGED_PROVIDERS:
            raise ValueError(f"unsupported managed provider: {requested}")

        if requested in ZERO_COST_PROVIDERS:
            if not self._free_tier_confirmed():
                raise ValueError(
                    f"provider={requested} requires UIUX_FREE_TIER_CONFIRMED=1 after checking the account is on free tier"
                )
            configured = self._configured_free_providers()
            if requested not in configured:
                raise ValueError(
                    f"provider={requested} is not fully configured in UIUX_CLOUD_PROVIDERS with its key/model"
                )
            return ProviderAccessDecision(
                provider=requested,
                access_class="zero_cost_free_tier",
                source="explicit_free_tier",
            )

        if requested in PAID_PROVIDERS:
            if not bool(self.policy.get("allow_paid_providers", False)):
                raise ValueError(
                    f"provider={requested} is disabled by zero-cost policy; provider_access.allow_paid_providers is false"
                )
            if not allow_paid_opt_in:
                raise ValueError(
                    f"provider={requested} requires explicit --allow-paid-provider opt-in for this invocation"
                )
            return ProviderAccessDecision(
                provider=requested,
                access_class="paid_explicit_opt_in",
                source="explicit_paid_opt_in",
                paid_opt_in=True,
            )

        if not bool(self.policy.get("allow_command_provider", True)):
            raise ValueError("provider=command is disabled by provider_access.allow_command_provider")
        return ProviderAccessDecision(
            provider=requested,
            access_class="operator_managed",
            source="explicit_command",
        )
