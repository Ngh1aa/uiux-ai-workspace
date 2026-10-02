from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from core.runtime.provider_lane import (
    LEGACY_PROVIDER_LANE,
    MANAGED_COMPAT_PROVIDER_LANE,
    PROVIDER_LANE_ENV,
    provider_lane_provenance,
    resolve_factory_provider_lane,
)


ROOT = Path(__file__).resolve().parents[1]
MANAGER = ROOT / "core/manager/provider_intelligent_manager.py"


def test_a48_provider_lane_defaults_to_legacy_without_opt_in() -> None:
    decision = resolve_factory_provider_lane({})

    assert decision.lane == LEGACY_PROVIDER_LANE
    assert decision.source == "default"
    assert decision.explicit_opt_in is False


def test_a48_provider_lane_requires_explicit_managed_compat_opt_in() -> None:
    decision = resolve_factory_provider_lane({PROVIDER_LANE_ENV: MANAGED_COMPAT_PROVIDER_LANE})

    assert decision.lane == MANAGED_COMPAT_PROVIDER_LANE
    assert decision.source == PROVIDER_LANE_ENV
    assert decision.explicit_opt_in is True


def test_a48_explicit_legacy_value_remains_non_opt_in() -> None:
    decision = resolve_factory_provider_lane({PROVIDER_LANE_ENV: LEGACY_PROVIDER_LANE})

    assert decision.lane == LEGACY_PROVIDER_LANE
    assert decision.source == PROVIDER_LANE_ENV
    assert decision.explicit_opt_in is False


def test_a48_unknown_provider_lane_fails_closed() -> None:
    with pytest.raises(ValueError, match=PROVIDER_LANE_ENV):
        resolve_factory_provider_lane({PROVIDER_LANE_ENV: "auto-migrate"})


def test_a48_provider_lane_provenance_is_secret_free_and_has_no_authority_effect() -> None:
    decision = resolve_factory_provider_lane({PROVIDER_LANE_ENV: MANAGED_COMPAT_PROVIDER_LANE})
    payload = provider_lane_provenance(decision)
    serialized = json.dumps(payload, sort_keys=True)

    assert payload["schema_version"] == "factory-provider-lane.v1"
    assert payload["lane"] == MANAGED_COMPAT_PROVIDER_LANE
    assert payload["explicit_opt_in"] is True
    assert payload["default_lane"] == LEGACY_PROVIDER_LANE
    assert payload["contains_credentials"] is False
    assert PROVIDER_LANE_ENV in payload["rollback"]
    assert "legacy" in payload["rollback"]
    assert payload["authority_effect"] == "none"
    assert payload["gate_effect"] == "none"
    assert payload["evidence_effect"] == "none"
    assert payload["release_effect"] == "none"
    assert "api_key" not in serialized.lower()
    assert "secret" not in serialized.lower()


def test_a48_manager_wiring_keeps_legacy_default_and_no_silent_fallback() -> None:
    source = MANAGER.read_text(encoding="utf-8")
    tree = ast.parse(source)

    assert "resolve_factory_provider_lane()" in source
    assert "lane_decision.lane == LEGACY_PROVIDER_LANE" in source
    assert "FreeProvider.from_env(self.root)" in source
    assert "lane_decision.lane == MANAGED_COMPAT_PROVIDER_LANE" in source
    assert "ManagedArtifactCompletionAdapter.from_env(self.root)" in source
    assert "provider-lane.json" in source
    assert '"provider.lane_selected"' in source
    assert 'payload["provider_lane"]' in source

    # Provider transports remain lazy imports inside run(); manager module import
    # itself must not acquire legacy/managed network dependencies.
    module_imports = [node for node in tree.body if isinstance(node, ast.ImportFrom)]
    assert all(node.module != "core.runtime.free_provider" for node in module_imports)
    assert all(
        node.module != "core.runtime.flow_os.factory_provider_adapter" for node in module_imports
    )

    # The integration must not silently catch managed-compat failure and switch
    # back to legacy. Rollback is an explicit feature-flag decision.
    managed_branch = source.index("lane_decision.lane == MANAGED_COMPAT_PROVIDER_LANE")
    implementation_call = source.index("self.team_runner.set_provider(provider)", managed_branch)
    branch_text = source[managed_branch:implementation_call]
    assert "except" not in branch_text
    assert "FreeProvider.from_env" not in branch_text


def test_a48_provider_lane_is_only_selected_for_ai_engine() -> None:
    source = MANAGER.read_text(encoding="utf-8")
    ai_guard = source.index('if engine == "ai":')
    lane_select = source.index("lane_decision = resolve_factory_provider_lane()")
    print_marker = source.index('print(f"\\n[DevelopmentManager] Run ID:', lane_select)

    assert ai_guard < lane_select < print_marker
