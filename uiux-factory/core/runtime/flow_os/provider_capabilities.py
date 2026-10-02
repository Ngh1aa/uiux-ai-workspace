from __future__ import annotations

import inspect
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from core.runtime.flow_os.free_tier_provider import OpenAICompatibleFreeTierProvider
from core.runtime.free_provider import FreeProvider


class ProviderCapabilityModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProviderCapabilityProfile(ProviderCapabilityModel):
    """Read-only description of an existing provider entry path.

    This contract describes capabilities only. It does not execute providers, route
    stages, own model policy or authorize evidence/gates/releases.
    """

    profile_id: str = Field(min_length=1, max_length=128)
    owner: str = Field(min_length=1, max_length=256)
    entrypoint: str = Field(min_length=1, max_length=256)
    interface_kind: Literal["factory_complete", "managed_stage"]
    request_contract: str = Field(min_length=1, max_length=512)
    response_contract: str = Field(min_length=1, max_length=512)
    provider_names: tuple[str, ...]
    structured_stage_status: bool
    explicit_tool_actions: bool
    explicit_evidence_envelope: bool
    json_object_transport: Literal["optional", "required"]
    stage_specific_output_budget: bool
    multi_provider_fallback: bool
    per_run_call_budget: bool
    provider_call_history: bool
    declares_hard_output_limit: bool
    transport: str = Field(min_length=1, max_length=128)
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"


class ProviderCapabilityReconciliation(ProviderCapabilityModel):
    schema_version: Literal["provider-capability-reconciliation.v1"] = (
        "provider-capability-reconciliation.v1"
    )
    factory: ProviderCapabilityProfile
    managed: ProviderCapabilityProfile
    shared_capabilities: tuple[str, ...]
    factory_only_capabilities: tuple[str, ...]
    managed_only_capabilities: tuple[str, ...]
    migration_blockers: tuple[str, ...]
    direct_substitution_safe: Literal[False] = False
    adapter_required: Literal[True] = True
    execution_effect: Literal["none"] = "none"
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"

    @model_validator(mode="after")
    def _require_distinct_interfaces(self) -> "ProviderCapabilityReconciliation":
        if self.factory.interface_kind == self.managed.interface_kind:
            raise ValueError("provider reconciliation requires distinct current interface kinds")
        if not self.migration_blockers:
            raise ValueError("provider reconciliation must record migration blockers")
        return self


def _assert_current_entrypoints() -> None:
    """Fail closed if source interfaces drift away from the audited contracts."""

    factory_signature = inspect.signature(FreeProvider.complete)
    factory_params = tuple(factory_signature.parameters)
    if factory_params != ("self", "stage", "system", "prompt", "json_mode"):
        raise RuntimeError(
            "FreeProvider.complete signature changed; refresh provider capability reconciliation"
        )

    managed_signature = inspect.signature(OpenAICompatibleFreeTierProvider.run_stage)
    managed_params = tuple(managed_signature.parameters)
    if managed_params != ("self", "request"):
        raise RuntimeError(
            "OpenAICompatibleFreeTierProvider.run_stage signature changed; refresh provider capability reconciliation"
        )


def factory_free_provider_profile() -> ProviderCapabilityProfile:
    _assert_current_entrypoints()
    return ProviderCapabilityProfile(
        profile_id="factory-free-provider",
        owner="core.runtime.free_provider.FreeProvider",
        entrypoint="core.runtime.free_provider.FreeProvider.complete",
        interface_kind="factory_complete",
        request_contract="stage + system + prompt + optional json_mode",
        response_contract="raw provider text/artifact string",
        provider_names=("groq", "gemini"),
        structured_stage_status=False,
        explicit_tool_actions=False,
        explicit_evidence_envelope=False,
        json_object_transport="optional",
        stage_specific_output_budget=True,
        multi_provider_fallback=True,
        per_run_call_budget=True,
        provider_call_history=True,
        declares_hard_output_limit=False,
        transport="aiohttp",
    )


def managed_free_tier_provider_profile() -> ProviderCapabilityProfile:
    _assert_current_entrypoints()
    return ProviderCapabilityProfile(
        profile_id="managed-free-tier-provider",
        owner="core.runtime.flow_os.free_tier_provider.OpenAICompatibleFreeTierProvider",
        entrypoint=(
            "core.runtime.flow_os.free_tier_provider."
            "OpenAICompatibleFreeTierProvider.run_stage"
        ),
        interface_kind="managed_stage",
        request_contract="core.runtime.flow_os.provider.ProviderStageRequest",
        response_contract="core.runtime.flow_os.provider.ProviderStageResponse",
        provider_names=("groq", "gemini"),
        structured_stage_status=True,
        explicit_tool_actions=True,
        explicit_evidence_envelope=True,
        json_object_transport="required",
        stage_specific_output_budget=False,
        multi_provider_fallback=False,
        per_run_call_budget=False,
        provider_call_history=False,
        declares_hard_output_limit=bool(
            getattr(OpenAICompatibleFreeTierProvider, "supports_hard_output_limit", False)
        ),
        transport="urllib.request",
    )


def reconcile_free_tier_provider_capabilities() -> ProviderCapabilityReconciliation:
    """Describe parity/gaps without calling a provider or changing either execution lane."""

    factory = factory_free_provider_profile()
    managed = managed_free_tier_provider_profile()
    return ProviderCapabilityReconciliation(
        factory=factory,
        managed=managed,
        shared_capabilities=(
            "explicit free-tier opt-in",
            "Groq/Gemini OpenAI-compatible chat transport",
            "bounded response size",
            "non-streaming completion",
            "stage identity available to provider layer",
            "provider/model output has no gate or release authority",
        ),
        factory_only_capabilities=(
            "raw artifact completion interface",
            "optional json response mode",
            "stage-specific token/time budgets",
            "ordered multi-provider fallback",
            "per-run provider call budget",
            "provider call history used by Factory artifacts",
        ),
        managed_only_capabilities=(
            "typed ProviderStageRequest",
            "typed ProviderStageResponse",
            "structured CONTINUE/PASS/FAIL/BLOCKED status",
            "explicit bounded tool actions",
            "explicit evidence envelope",
            "managed replan signal contract",
            "declared hard output-limit capability",
        ),
        migration_blockers=(
            "Factory callers depend on async complete(stage, system, prompt, json_mode) returning raw artifact text",
            "Managed providers consume ProviderStageRequest and return structured ProviderStageResponse",
            "Factory observation/refinement loops parse their own response contracts above complete()",
            "AIFrontendBuilder expects a complete JSON frontend bundle rather than a managed-stage envelope",
            "Factory provider budget/history semantics are currently stored on the provider instance",
        ),
    )
