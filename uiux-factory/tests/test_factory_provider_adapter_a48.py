from __future__ import annotations

import ast
import asyncio
import threading
from pathlib import Path

import pytest

from core.runtime.flow_os.factory_provider_adapter import ManagedArtifactCompletionAdapter
from core.runtime.flow_os.provider import ProviderStageResponse
from core.runtime.provider_compat_contract import (
    PROVIDER_MAX_CALLS_PER_RUN,
    PROVIDER_STAGE_MAX_TOKENS,
    PROVIDER_STAGE_TIMEOUT,
    ProviderError,
)


class FakeManagedProvider:
    def __init__(self, name: str, responses: list[ProviderStageResponse | BaseException]) -> None:
        self.name = name
        self.model = f"{name}-model"
        self.responses = list(responses)
        self.requests = []
        self.thread_ids: list[int] = []
        self.observed_limits: list[tuple[int | None, int | None]] = []
        self.max_output_tokens = 111
        self.timeout = 222

    def run_stage(self, request):
        self.requests.append(request)
        self.thread_ids.append(threading.get_ident())
        self.observed_limits.append((self.max_output_tokens, self.timeout))
        if not self.responses:
            raise RuntimeError("no fake response")
        value = self.responses.pop(0)
        if isinstance(value, BaseException):
            raise value
        return value


def _carrier(artifact: str) -> ProviderStageResponse:
    return ProviderStageResponse(
        status="CONTINUE",
        actions=[],
        summary="compatibility carrier",
        evidence=[],
        replan_signal=None,
        artifact=artifact,
    )


def test_a48_adapter_preserves_async_complete_contract_and_offloads_sync_provider(tmp_path: Path) -> None:
    provider = FakeManagedProvider("groq", [_carrier("raw artifact")])
    adapter = ManagedArtifactCompletionAdapter([provider], project_root=tmp_path)
    main_thread = threading.get_ident()

    result = asyncio.run(
        adapter.complete(
            stage="implementation",
            system="system instruction",
            prompt="user prompt",
        )
    )

    assert result == "raw artifact"
    assert provider.thread_ids and provider.thread_ids[0] != main_thread
    assert adapter.calls == 1
    assert adapter.history[0]["status"] == "completed"
    assert adapter.history[0]["artifact_chars"] == len("raw artifact")

    request = provider.requests[0]
    assert request.stage_id == "implementation"
    assert request.flow_id == "factory-provider-compatibility"
    assert request.task_context["original_system"] == "system instruction"
    assert request.task_context["original_prompt"] == "user prompt"
    assert request.task_context["artifact_is_evidence"] is False
    assert request.task_context["authority_effect"] == "none"
    assert request.task_context["gate_effect"] == "none"
    assert request.task_context["evidence_effect"] == "none"


def test_a48_adapter_applies_factory_stage_limits_only_during_managed_call(tmp_path: Path) -> None:
    provider = FakeManagedProvider("groq", [_carrier("bundle")])
    adapter = ManagedArtifactCompletionAdapter([provider], project_root=tmp_path)

    asyncio.run(adapter.complete("implementation", "system", "prompt"))

    assert provider.observed_limits == [
        (
            PROVIDER_STAGE_MAX_TOKENS["implementation"],
            PROVIDER_STAGE_TIMEOUT["implementation"],
        )
    ]
    assert provider.max_output_tokens == 111
    assert provider.timeout == 222


def test_a48_adapter_preserves_json_object_mode(tmp_path: Path) -> None:
    provider = FakeManagedProvider("groq", [_carrier('{"files":{"index.html":"<main/>"}}')])
    adapter = ManagedArtifactCompletionAdapter([provider], project_root=tmp_path)

    raw = asyncio.run(adapter.complete("implementation", "system", "prompt", json_mode=True))

    assert raw.startswith("{")
    assert provider.requests[0].task_context["json_mode"] is True

    invalid = FakeManagedProvider("groq", [_carrier("[]")])
    invalid_adapter = ManagedArtifactCompletionAdapter([invalid], project_root=tmp_path)
    with pytest.raises(ProviderError, match="JSON artifact must be an object"):
        asyncio.run(invalid_adapter.complete("implementation", "system", "prompt", json_mode=True))


def test_a48_adapter_rejects_lifecycle_authority_in_carrier_response(tmp_path: Path) -> None:
    bad = FakeManagedProvider(
        "groq",
        [
            ProviderStageResponse(
                status="PASS",
                actions=[],
                summary="not a carrier",
                evidence=["provider-claim:not-trusted-here"],
                artifact="raw output",
            )
        ],
    )
    fallback = FakeManagedProvider("gemini", [_carrier("must not be used")])
    adapter = ManagedArtifactCompletionAdapter([bad, fallback], project_root=tmp_path)

    with pytest.raises(ProviderError, match="must return CONTINUE"):
        asyncio.run(adapter.complete("research", "system", "prompt"))

    assert len(bad.requests) == 1
    assert fallback.requests == []
    assert adapter.history[0]["status"] == "invalid_contract"


@pytest.mark.parametrize(
    "response, message",
    [
        (
            ProviderStageResponse(
                status="CONTINUE",
                actions=[{"tool": "read_file", "args": {}}],
                artifact="raw output",
            ),
            "cannot request tool actions",
        ),
        (
            ProviderStageResponse(
                status="CONTINUE",
                actions=[],
                evidence=["claim"],
                artifact="raw output",
            ),
            "cannot be promoted into evidence",
        ),
        (
            ProviderStageResponse(
                status="CONTINUE",
                actions=[],
                replan_signal="GATE_FAIL",
                artifact="raw output",
            ),
            "cannot emit a replan signal",
        ),
        (
            ProviderStageResponse(status="CONTINUE", actions=[], artifact=None),
            "returned no artifact",
        ),
    ],
)
def test_a48_adapter_rejects_non_neutral_carrier_fields(
    tmp_path: Path,
    response: ProviderStageResponse,
    message: str,
) -> None:
    adapter = ManagedArtifactCompletionAdapter(
        [FakeManagedProvider("groq", [response])],
        project_root=tmp_path,
    )
    with pytest.raises(ProviderError, match=message):
        asyncio.run(adapter.complete("research", "system", "prompt"))


def test_a48_adapter_retries_transient_then_falls_back_in_factory_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = FakeManagedProvider(
        "groq",
        [
            RuntimeError("free-tier provider HTTP 503; retry"),
            RuntimeError("free-tier provider HTTP 503; retry"),
        ],
    )
    second = FakeManagedProvider("gemini", [_carrier("fallback artifact")])
    adapter = ManagedArtifactCompletionAdapter([first, second], project_root=tmp_path)

    async def no_sleep(_seconds: float) -> None:
        return None

    monkeypatch.setattr("core.runtime.flow_os.factory_provider_adapter.asyncio.sleep", no_sleep)
    result = asyncio.run(adapter.complete("research", "system", "prompt"))

    assert result == "fallback artifact"
    assert len(first.requests) == 2
    assert len(second.requests) == 1
    assert adapter.calls == 3
    assert [row["provider"] for row in adapter.history] == ["groq", "groq", "gemini"]


def test_a48_adapter_honors_existing_stage_preference_and_call_budget(tmp_path: Path) -> None:
    groq = FakeManagedProvider("groq", [_carrier("groq")])
    gemini = FakeManagedProvider("gemini", [_carrier("gemini")])
    adapter = ManagedArtifactCompletionAdapter(
        [groq, gemini],
        env={"UIUX_PROVIDER_RESEARCH": "gemini"},
        project_root=tmp_path,
    )

    result = asyncio.run(adapter.complete("research", "system", "prompt"))
    assert result == "gemini"
    assert groq.requests == []
    assert len(gemini.requests) == 1
    assert adapter.MAX_CALLS_PER_RUN == PROVIDER_MAX_CALLS_PER_RUN

    adapter.calls = adapter.MAX_CALLS_PER_RUN
    with pytest.raises(ProviderError, match="giới hạn"):
        asyncio.run(adapter.complete("research", "system", "prompt"))


def test_a48_adapter_rejects_context_over_factory_limit(tmp_path: Path) -> None:
    provider = FakeManagedProvider("groq", [_carrier("unused")])
    adapter = ManagedArtifactCompletionAdapter([provider], project_root=tmp_path)

    with pytest.raises(ProviderError, match="80.000"):
        asyncio.run(adapter.complete("research", "s" * 40001, "p" * 40000))
    assert provider.requests == []


def test_a48_adapter_module_does_not_import_legacy_transport_at_module_scope() -> None:
    adapter_path = (
        Path(__file__).resolve().parents[1]
        / "core/runtime/flow_os/factory_provider_adapter.py"
    )
    tree = ast.parse(adapter_path.read_text(encoding="utf-8"))
    module_imports = [node for node in tree.body if isinstance(node, ast.ImportFrom)]

    assert all(node.module != "core.runtime.free_provider" for node in module_imports)
    source = adapter_path.read_text(encoding="utf-8")
    assert "from core.runtime.provider_compat_contract import" in source
    assert "from core.runtime.free_provider import FreeProvider" in source


def test_a48_adapter_manager_integration_remains_explicit_opt_in_with_legacy_default() -> None:
    manager_source = (
        Path(__file__).resolve().parents[1]
        / "core/manager/provider_intelligent_manager.py"
    ).read_text(encoding="utf-8")

    assert 'FACTORY_PROVIDER_LANE_ENV = "UIUX_FACTORY_PROVIDER_LANE"' in manager_source
    assert 'return "legacy", "default"' in manager_source
    assert 'if lane == "legacy":' in manager_source
    assert "FreeProvider.from_env(self.root)" in manager_source
    assert "ManagedArtifactCompletionAdapter.from_env(self.root)" in manager_source
    assert "automatic_cross_lane_fallback" in manager_source
