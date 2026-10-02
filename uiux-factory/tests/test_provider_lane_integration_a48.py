from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from core.runtime.provider_compat_contract import (
    FACTORY_PROVIDER_LANE_ENV,
    build_provider_lane_provenance,
    resolve_factory_provider_lane,
)


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


def _manager_source() -> str:
    path = (
        Path(__file__).resolve().parents[1]
        / "core/manager/provider_intelligent_manager.py"
    )
    return path.read_text(encoding="utf-8")


def _manager_tree() -> ast.Module:
    return ast.parse(_manager_source())


def _class_method(tree: ast.Module, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "ProviderIntelligentDevelopmentManager":
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == name:
                    return child
    raise AssertionError(f"manager method not found: {name}")


def test_a48_provider_lane_defaults_to_legacy_and_requires_explicit_managed_opt_in() -> None:
    assert resolve_factory_provider_lane({}) == ("legacy", "default")
    assert resolve_factory_provider_lane(
        {FACTORY_PROVIDER_LANE_ENV: "legacy"}
    ) == ("legacy", "explicit")
    assert resolve_factory_provider_lane(
        {FACTORY_PROVIDER_LANE_ENV: "managed_compat"}
    ) == ("managed_compat", "explicit")


def test_a48_provider_lane_rejects_unknown_values_fail_closed() -> None:
    with pytest.raises(ValueError, match="Unknown UIUX_FACTORY_PROVIDER_LANE"):
        resolve_factory_provider_lane({FACTORY_PROVIDER_LANE_ENV: "auto"})


def test_a48_provider_lane_provenance_is_secret_free_and_non_authoritative() -> None:
    payload = build_provider_lane_provenance(
        provider=_LegacyProvider(),
        lane="legacy",
        selection_source="default",
    )
    serialized = json.dumps(payload, ensure_ascii=False)

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
    assert "must-not-be-persisted" not in serialized


def test_a48_managed_lane_provenance_remains_non_authoritative() -> None:
    payload = build_provider_lane_provenance(
        provider=_ManagedAdapter(),
        lane="managed_compat",
        selection_source="explicit",
    )

    assert payload["lane"] == "managed_compat"
    assert payload["legacy_default_preserved"] is False
    assert payload["providers"] == [{"name": "groq", "model": "managed-model"}]
    assert payload["automatic_cross_lane_fallback"] is False
    assert payload["rollback"]["changes_current_run"] is False
    assert payload["authority_effect"] == payload["gate_effect"] == "none"
    assert payload["evidence_effect"] == payload["release_effect"] == "none"


def test_a48_provider_lane_provenance_rejects_unknown_lane_or_selection_source() -> None:
    with pytest.raises(ValueError, match="Cannot persist unknown provider lane"):
        build_provider_lane_provenance(
            provider=_LegacyProvider(),
            lane="auto",
            selection_source="explicit",
        )
    with pytest.raises(ValueError, match="Unknown provider lane selection source"):
        build_provider_lane_provenance(
            provider=_LegacyProvider(),
            lane="legacy",
            selection_source="implicit",
        )


def test_a48_manager_source_keeps_legacy_default_and_explicit_managed_lane() -> None:
    source = _manager_source()

    assert "resolve_factory_provider_lane" in source
    assert 'if lane == "legacy":' in source
    assert "FreeProvider.from_env(self.root)" in source
    assert "ManagedArtifactCompletionAdapter.from_env(self.root)" in source
    assert "build_provider_lane_provenance" in source
    assert '"provider-lane.json"' in source
    assert '"provider.lane_selected"' in source


def test_a48_manager_provider_creation_has_no_silent_cross_lane_fallback() -> None:
    method = _class_method(_manager_tree(), "_create_ai_provider")

    # No try/except in provider construction: a managed-lane failure propagates
    # instead of silently switching to the legacy lane.
    assert not any(isinstance(node, ast.Try) for node in ast.walk(method))
    returns = [node for node in ast.walk(method) if isinstance(node, ast.Return)]
    assert len(returns) >= 2


def test_a48_provider_lane_is_selected_only_for_ai_engine_runs() -> None:
    source = _manager_source()
    marker = 'if engine == "ai":\n                provider, provider_lane, provider_selection = self._create_ai_provider()'
    assert marker in source
    assert 'if engine == "external":' in source
