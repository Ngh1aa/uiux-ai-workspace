from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from core.runtime.flow_os.free_tier_provider import OpenAICompatibleFreeTierProvider
from core.runtime.flow_os.provider import (
    MAX_PROVIDER_ARTIFACT_CHARS,
    ModelProvider,
    ProviderStageRequest,
    ProviderStageResponse,
)
from core.runtime.free_provider import FreeProvider, ProviderError


_TRANSIENT_ERROR_MARKERS = (
    "http 429",
    "http 502",
    "http 503",
    "http 504",
    "network error",
    "connection",
    "timeout",
)


class ManagedArtifactCompletionAdapter:
    """Opt-in bridge from Factory ``complete`` callers to managed providers.

    The adapter preserves the Factory async/raw-artifact caller contract while
    delegating provider execution through an existing managed ``ModelProvider``.
    It is not a provider transport, does not own routing/gates/evidence, and is
    deliberately not wired into the Factory manager by A48.4.
    """

    MAX_CALLS_PER_RUN = FreeProvider.MAX_CALLS_PER_RUN

    def __init__(
        self,
        providers: list[ModelProvider],
        *,
        env: dict[str, str] | None = None,
        project_root: Path | str = ".",
    ) -> None:
        if not providers:
            raise ProviderError("Managed compatibility adapter requires at least one provider.")
        self.providers = list(providers)
        self.env = dict(env or {})
        self.project_root = Path(project_root).resolve()
        self.calls = 0
        self.history: list[dict[str, Any]] = []

    @classmethod
    def from_env(cls, root: Path) -> "ManagedArtifactCompletionAdapter":
        """Reuse the existing Factory free-tier configuration policy.

        This performs no provider network call. ``FreeProvider.from_env`` remains
        the current owner of free-tier opt-in/model/key validation during the
        migration window; A48.4 only converts the validated configs into the
        canonical managed Groq/Gemini provider adapters.
        """

        legacy = FreeProvider.from_env(root)
        providers: list[ModelProvider] = [
            OpenAICompatibleFreeTierProvider(
                config.name,
                model=config.model,
                api_key=config.key,
                env=legacy.env,
            )
            for config in legacy.configs
        ]
        return cls(providers, env=legacy.env, project_root=root)

    def _ordered_providers(self, stage: str) -> list[ModelProvider]:
        providers = list(self.providers)
        preferred = self.env.get(f"UIUX_PROVIDER_{stage.upper()}")
        if not preferred:
            return providers
        names = {str(getattr(provider, "name", "")) for provider in providers}
        if preferred not in names:
            raise ProviderError(f"Provider cho stage {stage} chưa được bật.")
        providers.sort(key=lambda provider: str(getattr(provider, "name", "")) != preferred)
        return providers

    def _request(
        self,
        *,
        stage: str,
        system: str,
        prompt: str,
        json_mode: bool,
    ) -> ProviderStageRequest:
        output_rule = (
            "Artifact must be a JSON object encoded as raw text."
            if json_mode
            else "Artifact must be the raw requested completion text."
        )
        purpose = (
            "Factory compatibility artifact-carrier mode. Execute the supplied original system/prompt request. "
            "Return status CONTINUE, actions=[], evidence=[], replan_signal=null, and place only the requested "
            f"completion in artifact. {output_rule} This carrier status is consumed by the compatibility adapter "
            "and is not a managed lifecycle decision; artifact is not evidence."
        )
        return ProviderStageRequest(
            goal="Preserve the existing Factory provider completion contract during provider convergence.",
            project_root=str(self.project_root),
            flow_id="factory-provider-compatibility",
            flow_revision=1,
            stage_id=stage,
            agent="factory-provider-compatibility",
            purpose=purpose,
            gates=[],
            task_context={
                "factory_compatibility_mode": "artifact_carrier",
                "original_system": system,
                "original_prompt": prompt,
                "json_mode": bool(json_mode),
                "artifact_is_evidence": False,
                "authority_effect": "none",
                "gate_effect": "none",
                "evidence_effect": "none",
            },
            authority="factory-provider-compatibility-only",
            tools=[],
            skill_context=[],
            source_context=[],
            observations=[],
        )

    @staticmethod
    def _is_transient(error: BaseException) -> bool:
        text = str(error).lower()
        return isinstance(error, (asyncio.TimeoutError, TimeoutError)) or any(
            marker in text for marker in _TRANSIENT_ERROR_MARKERS
        )

    @staticmethod
    def _validate_carrier(response: ProviderStageResponse, *, json_mode: bool) -> str:
        if response.status != "CONTINUE":
            raise ProviderError(
                "Managed compatibility carrier must return CONTINUE; lifecycle PASS/FAIL/BLOCKED "
                "cannot be reinterpreted as a Factory completion."
            )
        if response.actions:
            raise ProviderError("Managed compatibility carrier cannot request tool actions.")
        if response.evidence:
            raise ProviderError("Managed compatibility artifact cannot be promoted into evidence.")
        if response.replan_signal is not None:
            raise ProviderError("Managed compatibility carrier cannot emit a replan signal.")
        artifact = response.artifact
        if not isinstance(artifact, str) or not artifact.strip():
            raise ProviderError("Managed compatibility carrier returned no artifact.")
        if len(artifact) > MAX_PROVIDER_ARTIFACT_CHARS:
            raise ProviderError("Managed compatibility artifact exceeded the canonical size bound.")
        if json_mode:
            try:
                decoded = json.loads(artifact)
            except json.JSONDecodeError as error:
                raise ProviderError("Managed compatibility JSON artifact is invalid.") from error
            if not isinstance(decoded, dict):
                raise ProviderError("Managed compatibility JSON artifact must be an object.")
        return artifact

    async def _run_provider(
        self,
        provider: ModelProvider,
        request: ProviderStageRequest,
        *,
        stage: str,
    ) -> ProviderStageResponse:
        max_tokens = FreeProvider.STAGE_MAX_TOKENS.get(stage, 8000)
        timeout_sec = FreeProvider.STAGE_TIMEOUT.get(stage, 120)

        def invoke() -> ProviderStageResponse:
            previous_tokens = getattr(provider, "max_output_tokens", None)
            previous_timeout = getattr(provider, "timeout", None)
            has_tokens = hasattr(provider, "max_output_tokens")
            has_timeout = hasattr(provider, "timeout")
            try:
                if has_tokens:
                    setattr(provider, "max_output_tokens", max_tokens)
                if has_timeout:
                    setattr(provider, "timeout", timeout_sec)
                return provider.run_stage(request)
            finally:
                if has_tokens:
                    setattr(provider, "max_output_tokens", previous_tokens)
                if has_timeout:
                    setattr(provider, "timeout", previous_timeout)

        # Managed providers are synchronous today. Always offload them so the
        # existing Factory async lifecycle/event loop cannot be blocked.
        return await asyncio.wait_for(
            asyncio.to_thread(invoke),
            timeout=timeout_sec + 5,
        )

    async def complete(
        self,
        stage: str,
        system: str,
        prompt: str,
        *,
        json_mode: bool = False,
    ) -> str:
        if len(system) + len(prompt) > 80000:
            raise ProviderError("Context vượt giới hạn 80.000 ký tự; hãy rút gọn brief/context.")

        request = self._request(
            stage=stage,
            system=system,
            prompt=prompt,
            json_mode=json_mode,
        )
        failures: list[str] = []
        for provider in self._ordered_providers(stage):
            name = str(getattr(provider, "name", "managed"))
            model = str(getattr(provider, "model", "unknown"))
            for retry in range(2):
                if self.calls >= self.MAX_CALLS_PER_RUN:
                    raise ProviderError(
                        f"Đã đạt giới hạn {self.MAX_CALLS_PER_RUN} yêu cầu AI cho run này."
                    )
                self.calls += 1
                record: dict[str, Any] = {
                    "stage": stage,
                    "provider": name,
                    "model": model,
                    "attempt": self.calls,
                    "compatibility_mode": "managed_artifact_carrier",
                }
                self.history.append(record)
                try:
                    response = await self._run_provider(provider, request, stage=stage)
                    artifact = self._validate_carrier(response, json_mode=json_mode)
                    record["status"] = "completed"
                    record["artifact_chars"] = len(artifact)
                    return artifact
                except ProviderError:
                    record["status"] = "invalid_contract"
                    raise
                except (RuntimeError, ValueError, asyncio.TimeoutError, TimeoutError) as error:
                    if not self._is_transient(error):
                        record["status"] = "provider_failed"
                        raise ProviderError(
                            f"{name}: managed provider failed; response was not accepted."
                        ) from None
                    record["status"] = "connection_failed"
                    failures.append(f"{name}: connection/timeout/transient")
                    if retry == 0:
                        await asyncio.sleep(2)
                        continue
                    break

        raise ProviderError(
            "Không có provider khả dụng trong danh sách đã bật: " + "; ".join(failures)
        )
