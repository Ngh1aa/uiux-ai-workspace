from __future__ import annotations

import ast
import inspect
from pathlib import Path

from core.runtime.flow_os.free_tier_provider import OpenAICompatibleFreeTierProvider
from core.runtime.flow_os.provider_capabilities import (
    factory_free_provider_profile,
    managed_free_tier_provider_profile,
    reconcile_free_tier_provider_capabilities,
)
from core.runtime.free_provider import FreeProvider


FACTORY = Path(__file__).resolve().parents[1]


def test_a48_provider_profiles_match_current_entrypoint_shapes() -> None:
    factory = factory_free_provider_profile()
    managed = managed_free_tier_provider_profile()

    assert tuple(inspect.signature(FreeProvider.complete).parameters) == (
        "self",
        "stage",
        "system",
        "prompt",
        "json_mode",
    )
    assert tuple(inspect.signature(OpenAICompatibleFreeTierProvider.run_stage).parameters) == (
        "self",
        "request",
    )
    assert inspect.iscoroutinefunction(FreeProvider.complete) is True
    assert inspect.iscoroutinefunction(OpenAICompatibleFreeTierProvider.run_stage) is False
    assert factory.async_entrypoint is True
    assert managed.async_entrypoint is False
    assert factory.provider_names == managed.provider_names == ("groq", "gemini")


def test_a48_direct_provider_substitution_is_explicitly_not_safe() -> None:
    report = reconcile_free_tier_provider_capabilities()

    assert report.direct_substitution_safe is False
    assert report.adapter_required is True
    assert report.factory.interface_kind == "factory_complete"
    assert report.managed.interface_kind == "managed_stage"
    assert report.factory.response_contract == "raw provider text/artifact string"
    assert report.managed.response_contract.endswith("ProviderStageResponse")
    assert report.factory.structured_stage_status is False
    assert report.managed.structured_stage_status is True
    assert report.factory.multi_provider_fallback is True
    assert report.managed.multi_provider_fallback is False
    assert report.factory.per_run_call_budget is True
    assert report.managed.per_run_call_budget is False
    assert report.migration_blockers
    assert report.execution_effect == report.authority_effect == "none"
    assert report.gate_effect == report.evidence_effect == "none"


def test_a48_factory_provider_call_sites_are_explicit_migration_surface() -> None:
    call_sites = {
        "core/team/team_runner.py": "self.provider.complete(",
        "core/team/intelligent_team_runner.py": "self.provider.complete(",
        "core/orchestration/ai_frontend_builder.py": "self.provider.complete(",
    }
    for relative, needle in call_sites.items():
        source = (FACTORY / relative).read_text(encoding="utf-8")
        assert needle in source, relative

    manager = (FACTORY / "core/manager/provider_intelligent_manager.py").read_text(encoding="utf-8")
    assert "from core.runtime.free_provider import FreeProvider" in manager
    assert "FreeProvider.from_env(self.root)" in manager


def test_a48_capability_reconciliation_does_not_execute_either_provider() -> None:
    path = FACTORY / "core/runtime/flow_os/provider_capabilities.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    forbidden_calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Attribute) and function.attr in {"complete", "run_stage"}:
            forbidden_calls.append(function.attr)
    assert forbidden_calls == []


def test_a48_reconciliation_does_not_create_third_provider_execution_contract() -> None:
    source = (FACTORY / "core/runtime/flow_os/provider_capabilities.py").read_text(encoding="utf-8")
    assert "class ProviderStageRequest" not in source
    assert "class ProviderStageResponse" not in source
    assert "class ProviderRunner" not in source
    assert "run_target_command" not in source
    assert "gate_evidence_errors" not in source
    assert "merge_pull_request" not in source
