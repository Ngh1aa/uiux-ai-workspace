from __future__ import annotations

import importlib
import importlib.util
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from core.benchmarks.post_interop_executable_debt_audit import (
    ConsumerRef,
    discover_runtime_shim_consumers,
    validate_compatibility_shim,
)


class RuntimeCompatibilityConvergenceError(RuntimeError):
    pass


@dataclass(frozen=True)
class IdentityCheck:
    shim_path: str
    shim_symbol: str
    canonical_module: str
    canonical_symbol: str
    identical: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeCompatibilityConvergenceReport:
    schema_version: str
    decision: str
    scope: str
    historical_baseline_clear: bool
    historical_consumer_files: int
    historical_consumer_imports: int
    shim_count: int
    shim_contract_clear: bool
    identity_checks_clear: bool
    identity_checks: tuple[IdentityCheck, ...]
    migrated_consumer_contract_clear: bool
    script_bootstrap_clear: bool
    internal_consumer_file_count: int
    internal_consumer_import_count: int
    internal_consumers: tuple[ConsumerRef, ...]
    zero_internal_consumers: bool
    governance_boundary_clear: bool
    shim_deletion_allowed: bool
    external_removal_safety_inferred: bool
    runtime_behavior_change_allowed: bool
    provider_default_change_allowed: bool
    lifecycle_state_owner_change_allowed: bool
    routing_change_allowed: bool
    evidence_authority_change_allowed: bool
    gate_authority_change_allowed: bool
    release_authority_change_allowed: bool
    product_evidence: bool
    execution_effect: str
    authority_effect: str
    gate_effect: str
    evidence_effect: str
    release_effect: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["identity_checks"] = [item.to_dict() for item in self.identity_checks]
        payload["internal_consumers"] = [item.to_dict() for item in self.internal_consumers]
        return payload


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeCompatibilityConvergenceError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeCompatibilityConvergenceError(f"expected JSON object at {path}")
    return payload


def _load_shim(path: Path, synthetic_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(synthetic_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeCompatibilityConvergenceError(f"cannot load compatibility shim {path}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(synthetic_name)
    sys.modules[synthetic_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        if previous is None:
            sys.modules.pop(synthetic_name, None)
        else:
            sys.modules[synthetic_name] = previous
    return module


def _identity_checks(repo_root: Path, shims: list[dict[str, Any]]) -> tuple[IdentityCheck, ...]:
    checks: list[IdentityCheck] = []
    for index, item in enumerate(shims):
        shim_path = str(item.get("path", ""))
        canonical_module = str(item.get("canonical_module", ""))
        if not shim_path or not canonical_module:
            raise RuntimeCompatibilityConvergenceError("invalid shim identity declaration")
        shim = _load_shim(repo_root / shim_path, f"_flow1_compat_{index}")
        canonical = importlib.import_module(canonical_module)
        for pair in item.get("identity_pairs", []):
            if not isinstance(pair, list) or len(pair) != 2:
                raise RuntimeCompatibilityConvergenceError("identity pair must contain shim and canonical symbol")
            shim_symbol, canonical_symbol = (str(pair[0]), str(pair[1]))
            shim_value = getattr(shim, shim_symbol, None)
            canonical_value = getattr(canonical, canonical_symbol, None)
            checks.append(
                IdentityCheck(
                    shim_path=shim_path,
                    shim_symbol=shim_symbol,
                    canonical_module=canonical_module,
                    canonical_symbol=canonical_symbol,
                    identical=shim_value is not None and shim_value is canonical_value,
                )
            )
    return tuple(checks)


def evaluate_runtime_compatibility_convergence(
    contract_path: Path,
) -> RuntimeCompatibilityConvergenceReport:
    contract_path = Path(contract_path).resolve()
    contract = _read_json(contract_path)
    repo_root = contract_path.parents[2]

    if contract.get("scope") != "first_party_import_convergence_no_shim_removal":
        raise RuntimeCompatibilityConvergenceError("Flow 1 scope drifted")

    baseline = dict(contract.get("historical_baseline") or {})
    historical = _read_json(repo_root / str(baseline.get("audit_path", "")))
    compatibility = dict(historical.get("compatibility_shims") or {})
    historical_files = int(compatibility.get("expected_internal_consumer_file_count", -1))
    historical_imports = int(compatibility.get("expected_internal_consumer_import_count", -1))
    historical_baseline_clear = (
        historical_files == int(baseline.get("expected_consumer_files", -2)) == 8
        and historical_imports == int(baseline.get("expected_consumer_imports", -2)) == 19
    )

    shims = list(contract.get("compatibility_shims") or [])
    if len(shims) != 8:
        raise RuntimeCompatibilityConvergenceError("Flow 1 must retain exactly eight compatibility shims")

    shim_contract_clear = True
    shim_modules: list[str] = []
    shim_paths: list[str] = []
    for item in shims:
        path = str(item.get("path", ""))
        module = str(item.get("module", ""))
        canonical_module = str(item.get("canonical_module", ""))
        clear, _reasons = validate_compatibility_shim(repo_root / path, canonical_module)
        shim_contract_clear = shim_contract_clear and clear
        shim_modules.append(module)
        shim_paths.append(path)

    consumers = discover_runtime_shim_consumers(
        repo_root,
        [str(item) for item in contract.get("scan_roots", [])],
        shim_modules,
        shim_paths,
    )
    current_file_count = len(consumers)
    current_import_count = sum(len(item.modules) for item in consumers)
    zero_internal_consumers = (
        current_file_count == int(contract.get("expected_current_consumer_files", -1)) == 0
        and current_import_count == int(contract.get("expected_current_consumer_imports", -1)) == 0
    )

    migrated_paths = [str(item) for item in contract.get("migrated_consumers", [])]
    migrated_consumer_contract_clear = len(migrated_paths) == 8 and all(
        (repo_root / path).is_file() for path in migrated_paths
    ) and not {item.path for item in consumers}.intersection(migrated_paths)

    bootstrap_paths = [str(item) for item in contract.get("script_consumers_requiring_factory_bootstrap", [])]
    script_bootstrap_clear = len(bootstrap_paths) == 4
    for path in bootstrap_paths:
        source = (repo_root / path).read_text(encoding="utf-8")
        script_bootstrap_clear = script_bootstrap_clear and all(
            marker in source
            for marker in (
                'FACTORY_ROOT = ROOT.parent / "uiux-factory"',
                "if str(FACTORY_ROOT) not in sys.path:",
                "sys.path.insert(0, str(FACTORY_ROOT))",
                "from core.runtime.flow_os.",
            )
        )

    identity_checks = _identity_checks(repo_root, shims)
    identity_checks_clear = bool(identity_checks) and all(item.identical for item in identity_checks)

    governance = dict(contract.get("governance") or {})
    false_keys = (
        "shim_deletion_allowed",
        "external_removal_safety_inferred",
        "runtime_behavior_change_allowed",
        "provider_default_change_allowed",
        "lifecycle_state_owner_change_allowed",
        "routing_change_allowed",
        "evidence_authority_change_allowed",
        "gate_authority_change_allowed",
        "release_authority_change_allowed",
        "product_evidence",
    )
    effect_keys = (
        "execution_effect",
        "authority_effect",
        "gate_effect",
        "evidence_effect",
        "release_effect",
    )
    governance_boundary_clear = all(governance.get(key) is False for key in false_keys) and all(
        governance.get(key) == "none" for key in effect_keys
    )

    ready = all(
        (
            historical_baseline_clear,
            shim_contract_clear,
            identity_checks_clear,
            migrated_consumer_contract_clear,
            script_bootstrap_clear,
            zero_internal_consumers,
            governance_boundary_clear,
        )
    )
    decision = (
        "FIRST_PARTY_RUNTIME_COMPAT_CONVERGENCE_PASS"
        if ready
        else "HOLD_RUNTIME_COMPAT_CONVERGENCE_REGRESSION"
    )

    return RuntimeCompatibilityConvergenceReport(
        schema_version="runtime-compatibility-convergence.v1",
        decision=decision,
        scope=str(contract["scope"]),
        historical_baseline_clear=historical_baseline_clear,
        historical_consumer_files=historical_files,
        historical_consumer_imports=historical_imports,
        shim_count=len(shims),
        shim_contract_clear=shim_contract_clear,
        identity_checks_clear=identity_checks_clear,
        identity_checks=identity_checks,
        migrated_consumer_contract_clear=migrated_consumer_contract_clear,
        script_bootstrap_clear=script_bootstrap_clear,
        internal_consumer_file_count=current_file_count,
        internal_consumer_import_count=current_import_count,
        internal_consumers=consumers,
        zero_internal_consumers=zero_internal_consumers,
        governance_boundary_clear=governance_boundary_clear,
        shim_deletion_allowed=bool(governance.get("shim_deletion_allowed")),
        external_removal_safety_inferred=bool(governance.get("external_removal_safety_inferred")),
        runtime_behavior_change_allowed=bool(governance.get("runtime_behavior_change_allowed")),
        provider_default_change_allowed=bool(governance.get("provider_default_change_allowed")),
        lifecycle_state_owner_change_allowed=bool(governance.get("lifecycle_state_owner_change_allowed")),
        routing_change_allowed=bool(governance.get("routing_change_allowed")),
        evidence_authority_change_allowed=bool(governance.get("evidence_authority_change_allowed")),
        gate_authority_change_allowed=bool(governance.get("gate_authority_change_allowed")),
        release_authority_change_allowed=bool(governance.get("release_authority_change_allowed")),
        product_evidence=bool(governance.get("product_evidence")),
        execution_effect=str(governance.get("execution_effect", "")),
        authority_effect=str(governance.get("authority_effect", "")),
        gate_effect=str(governance.get("gate_effect", "")),
        evidence_effect=str(governance.get("evidence_effect", "")),
        release_effect=str(governance.get("release_effect", "")),
    )
