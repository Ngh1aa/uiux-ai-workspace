from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.manager.provider_intelligent_manager import (
    FACTORY_PROVIDER_LANE_ENV,
    ProviderIntelligentDevelopmentManager,
)


class _EventBus:
    def __init__(self) -> None:
        self.rows: list[tuple[str, dict]] = []

    def emit(self, event: str, *, data: dict) -> None:
        self.rows.append((event, data))


class _Context:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.artifacts: dict[str, str] = {}
        self._bus = _EventBus()

    def add_artifact(self, key: str, path: Path) -> None:
        self.artifacts[key] = str(path)

    def event_bus(self) -> _EventBus:
        return self._bus


class _Config:
    def __init__(self, name: str, model: str) -> None:
        self.name = name
        self.model = model
        self.key = "must-not-be-persisted"


class _LegacyProvider:
    def __init__(self) -> None:
        self.configs = [_Config("groq", "legacy-model")]


class _ManagedProvider:
    name = "groq"
    model = "managed-model"


class _ManagedAdapter:
    def __init__(self) -> None:
        self.providers = [_ManagedProvider()]


def _manager(tmp_path: Path) -> ProviderIntelligentDevelopmentManager:
    manager = object.__new__(ProviderIntelligentDevelopmentManager)
    manager.root = tmp_path
    return manager


def test_a48_provider_lane_defaults_to_legacy_and_requires_explicit_managed_opt_in() -> None:
    assert ProviderIntelligentDevelopmentManager._resolve_provider_lane({}) == ("legacy", "default")
    assert ProviderIntelligentDevelopmentManager._resolve_provider_lane(
        {FACTORY_PROVIDER_LANE_ENV: "legacy"}
    ) == ("legacy", "explicit")
    assert ProviderIntelligentDevelopmentManager._resolve_provider_lane(
        {FACTORY_PROVIDER_LANE_ENV: "managed_compat"}
    ) == ("managed_compat", "explicit")


def test_a48_provider_lane_rejects_unknown_values_fail_closed() -> None:
    with pytest.raises(ValueError, match="Unknown UIUX_FACTORY_PROVIDER_LANE"):
        ProviderIntelligentDevelopmentManager._resolve_provider_lane(
            {FACTORY_PROVIDER_LANE_ENV: "auto"}
        )


def test_a48_manager_builds_legacy_provider_by_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = _manager(tmp_path)
    legacy = _LegacyProvider()
    monkeypatch.delenv(FACTORY_PROVIDER_LANE_ENV, raising=False)
    monkeypatch.setattr(
        "core.runtime.free_provider.FreeProvider.from_env",
        lambda root: legacy,
    )

    provider, lane, source = manager._create_ai_provider()

    assert provider is legacy
    assert lane == "legacy"
    assert source == "default"


def test_a48_manager_builds_managed_adapter_only_when_explicitly_selected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = _manager(tmp_path)
    managed = _ManagedAdapter()
    monkeypatch.setenv(FACTORY_PROVIDER_LANE_ENV, "managed_compat")
    monkeypatch.setattr(
        "core.runtime.flow_os.factory_provider_adapter.ManagedArtifactCompletionAdapter.from_env",
        lambda root: managed,
    )

    provider, lane, source = manager._create_ai_provider()

    assert provider is managed
    assert lane == "managed_compat"
    assert source == "explicit"


def test_a48_managed_selection_failure_never_falls_back_to_legacy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager = _manager(tmp_path)
    legacy_calls: list[Path] = []
    monkeypatch.setenv(FACTORY_PROVIDER_LANE_ENV, "managed_compat")

    def managed_failure(root: Path):
        raise RuntimeError("managed compatibility unavailable")

    def legacy_factory(root: Path):
        legacy_calls.append(root)
        return _LegacyProvider()

    monkeypatch.setattr(
        "core.runtime.flow_os.factory_provider_adapter.ManagedArtifactCompletionAdapter.from_env",
        managed_failure,
    )
    monkeypatch.setattr(
        "core.runtime.free_provider.FreeProvider.from_env",
        legacy_factory,
    )

    with pytest.raises(RuntimeError, match="managed compatibility unavailable"):
        manager._create_ai_provider()
    assert legacy_calls == []


def test_a48_provider_lane_provenance_is_secret_free_and_non_authoritative(tmp_path: Path) -> None:
    manager = _manager(tmp_path)
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    context = _Context(run_dir)
    provider = _LegacyProvider()

    path = manager._write_provider_lane_provenance(
        context,
        provider=provider,
        lane="legacy",
        selection_source="default",
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "provider-lane.v1"
    assert payload["lane"] == "legacy"
    assert payload["selection_source"] == "default"
    assert payload["legacy_default_preserved"] is True
    assert payload["automatic_cross_lane_fallback"] is False
    assert payload["providers"] == [{"name": "groq", "model": "legacy-model"}]
    assert payload["authority_effect"] == "none"
    assert payload["gate_effect"] == "none"
    assert payload["evidence_effect"] == "none"
    assert payload["release_effect"] == "none"
    assert "must-not-be-persisted" not in path.read_text(encoding="utf-8")
    assert context.artifacts["provider_lane"] == str(path)
    assert context._bus.rows[0][0] == "provider.lane_selected"
    assert context._bus.rows[0][1]["automatic_cross_lane_fallback"] is False


def test_a48_provider_lane_provenance_records_managed_adapter_without_claiming_gate_truth(tmp_path: Path) -> None:
    manager = _manager(tmp_path)
    run_dir = tmp_path / "run-managed"
    run_dir.mkdir()
    context = _Context(run_dir)

    path = manager._write_provider_lane_provenance(
        context,
        provider=_ManagedAdapter(),
        lane="managed_compat",
        selection_source="explicit",
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["lane"] == "managed_compat"
    assert payload["legacy_default_preserved"] is False
    assert payload["providers"] == [{"name": "groq", "model": "managed-model"}]
    assert payload["automatic_cross_lane_fallback"] is False
    assert payload["rollback"]["changes_current_run"] is False
    assert payload["authority_effect"] == payload["gate_effect"] == "none"
    assert payload["evidence_effect"] == payload["release_effect"] == "none"
