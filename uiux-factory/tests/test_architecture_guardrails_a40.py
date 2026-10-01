from __future__ import annotations

import ast
from pathlib import Path

import pytest

from core.runtime.flow_os import CANONICAL_RUNTIME_OWNER
from core.runtime.flow_os.evidence import (
    EvidenceRecord,
    gate_evidence_errors,
    provider_claim_records,
)


FACTORY = Path(__file__).resolve().parents[1]
WORKSPACE = FACTORY.parent
SKILLS = WORKSPACE / "skills_UIUX"
BRAIN_ROOT = FACTORY / "core" / "brain_os"

LEGACY_RUNTIME_SHIMS = {
    "adaptive_surface.py": "core.runtime.flow_os.adaptive_surface",
    "agent.py": "core.runtime.flow_os.agent",
    "flow.py": "core.runtime.flow_os.flow",
    "manager.py": "core.runtime.flow_os.managed",
    "mcp_server.py": "core.runtime.flow_os.mcp_server",
    "provider.py": "core.runtime.flow_os.provider",
    "provider_runner.py": "core.runtime.flow_os.provider_runner",
    "task_context.py": "core.runtime.flow_os.task_context",
}

FORBIDDEN_BRAIN_EXECUTION_IMPORTS = (
    "core.runtime.free_provider",
    "core.runtime.flow_os.file_tools",
    "core.runtime.flow_os.provider",
    "core.runtime.flow_os.provider_runner",
    "core.runtime.flow_os.release",
    "core.runtime.flow_os.sandbox",
    "core.runtime.flow_os.target_runner",
    "core.runtime.flow_os.workspace",
)

FORBIDDEN_BRAIN_OWNER_SYMBOLS = {
    "EvidenceRecord",
    "FlowPlanner",
    "GoalInterpreter",
    "ManagedFlowController",
    "ProductionReleaseController",
    "ProviderManagedRunner",
    "ProviderNeutralAgentHarness",
    "TaskContract",
}


def _python_sources(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(path for path in root.rglob("*.py") if path.is_file())


def _defined_symbols(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_a40_single_executable_flow_os_owner_is_factory() -> None:
    assert CANONICAL_RUNTIME_OWNER == "uiux-factory/core/runtime/flow_os"
    assert (FACTORY / "core" / "runtime" / "flow_os").is_dir()


def test_a40_legacy_runtime_python_surface_is_compatibility_only() -> None:
    runtime_root = SKILLS / "runtime"
    for filename, canonical_module in LEGACY_RUNTIME_SHIMS.items():
        path = runtime_root / filename
        source = path.read_text(encoding="utf-8")
        assert canonical_module in source, filename
        assert not _defined_symbols(path), (
            filename,
            "legacy runtime compatibility shims must not define executable classes/functions",
        )


def test_a40_provider_claims_cannot_satisfy_trusted_gate_evidence() -> None:
    claims = provider_claim_records("qa", ["The rendered UI looks correct."])
    assert claims
    assert all(record["type"] == "provider_claim" for record in claims)
    assert all(record["origin"] == "provider" for record in claims)
    assert all(record["trusted"] is False for record in claims)

    errors = gate_evidence_errors(
        [{"id": "rendered-ui", "evidence_types": ["browser_render"]}],
        "qa",
        claims,
        agent="qa",
    )
    assert any("missing typed evidence: browser_render" in error for error in errors)


def test_a40_non_runtime_memory_cannot_be_promoted_to_trusted_evidence() -> None:
    memory_claim = {
        "id": "memory_previous_pass",
        "type": "evaluation_memory",
        "stage_id": "qa",
        "tool": "memory",
        "status": "PASS",
        "summary": "A previous run passed.",
        "data": {"advisory_only": True},
        "origin": "memory",
        "trusted": True,
    }

    with pytest.raises(ValueError, match="trusted evidence must be emitted by the runtime"):
        EvidenceRecord.from_dict(memory_claim)

    errors = gate_evidence_errors(
        [{"id": "validator", "evidence_types": ["validator_result"]}],
        "qa",
        [memory_claim],
        agent="qa",
    )
    assert any("missing typed evidence: validator_result" in error for error in errors)


def test_a40_future_brain_os_cannot_redefine_canonical_runtime_owners() -> None:
    for path in _python_sources(BRAIN_ROOT):
        duplicates = FORBIDDEN_BRAIN_OWNER_SYMBOLS.intersection(_defined_symbols(path))
        assert not duplicates, (
            str(path.relative_to(FACTORY)),
            f"Brain OS must adapt canonical owners instead of redefining: {sorted(duplicates)}",
        )


def test_a40_future_brain_os_cannot_import_execution_authority_surfaces_directly() -> None:
    for path in _python_sources(BRAIN_ROOT):
        source = path.read_text(encoding="utf-8")
        forbidden = [module for module in FORBIDDEN_BRAIN_EXECUTION_IMPORTS if module in source]
        assert not forbidden, (
            str(path.relative_to(FACTORY)),
            "Brain OS is a reasoning/control layer; execution/release/provider authority must stay behind canonical adapters: "
            + ", ".join(forbidden),
        )


def test_a40_future_brain_evidence_graph_must_adapter_existing_evidence_primitives() -> None:
    evidence_graph = BRAIN_ROOT / "reasoning" / "evidence_graph.py"
    if not evidence_graph.is_file():
        return

    adapter = BRAIN_ROOT / "adapters" / "evidence.py"
    assert adapter.is_file(), "Brain Evidence Graph must use a dedicated adapter over existing evidence primitives"

    adapter_source = adapter.read_text(encoding="utf-8")
    assert "core.runtime.flow_os.evidence" in adapter_source
    assert (
        "core.provenance.evidence_lineage" in adapter_source
        or "core.provenance.release_evidence_registry" in adapter_source
    )

    all_brain_source = "\n".join(path.read_text(encoding="utf-8") for path in _python_sources(BRAIN_ROOT))
    assert "TRUSTED_EVIDENCE_TYPES =" not in all_brain_source
    assert "class EvidenceRecord" not in all_brain_source


def test_a40_brain_os_does_not_create_a_third_runtime_policy_file() -> None:
    if not BRAIN_ROOT.exists():
        return
    policy_files = [
        path
        for path in BRAIN_ROOT.rglob("*.json")
        if path.name in {"runtime-policy.json", "provider-policy.json", "release-policy.json"}
    ]
    assert not policy_files, (
        "Brain OS must consume canonical policy/authority through adapters, not create a third policy surface: "
        + ", ".join(str(path.relative_to(FACTORY)) for path in policy_files)
    )
