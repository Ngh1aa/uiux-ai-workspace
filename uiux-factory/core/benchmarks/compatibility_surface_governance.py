from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

from core.benchmarks.runtime_compatibility_convergence import (
    evaluate_runtime_compatibility_convergence,
)


class CompatibilitySurfaceGovernanceError(RuntimeError):
    pass


@dataclass(frozen=True)
class CompatibilitySurfaceGovernanceReport:
    schema_version: str
    decision: str
    scope: str
    flow1_clear: bool
    zero_internal_consumers: bool
    shim_count: int
    retain_indefinitely_count: int
    deprecate_with_sunset_count: int
    open_removal_governance_count: int
    public_notice_clear: bool
    canonical_public_guidance_only: bool
    external_usage_status: str
    public_code_search_hits: int
    zero_search_hits_prove_zero_external_users: bool
    observation_window_days: int
    earliest_removal_review_date: str
    observation_window_elapsed: bool
    external_usage_audit_complete: bool
    no_known_supported_downstream_dependency: bool
    explicit_owner_removal_task: bool
    removal_requirements_clear: bool
    removal_governance_open: bool
    shim_deletion_allowed: bool
    external_removal_safety_inferred: bool
    governance_boundary_clear: bool
    execution_effect: str
    authority_effect: str
    gate_effect: str
    evidence_effect: str
    release_effect: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CompatibilitySurfaceGovernanceError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CompatibilitySurfaceGovernanceError(f"expected JSON object at {path}")
    return payload


def _legacy_import_guidance(source: str) -> bool:
    return bool(
        re.search(r"^\s*from\s+runtime(?:\.[A-Za-z0-9_]+)+\s+import\s+", source, re.MULTILINE)
        or re.search(r"^\s*import\s+runtime(?:\.[A-Za-z0-9_]+)+", source, re.MULTILINE)
    )


def evaluate_compatibility_surface_governance(
    contract_path: Path,
) -> CompatibilitySurfaceGovernanceReport:
    contract_path = Path(contract_path).resolve()
    contract = _read_json(contract_path)
    repo_root = contract_path.parents[2]

    if contract.get("scope") != "public_compatibility_surface_deprecation_governance_no_deletion":
        raise CompatibilitySurfaceGovernanceError("Flow 2 scope drifted")

    flow1_path = repo_root / str(contract.get("flow1_input", ""))
    flow1 = evaluate_runtime_compatibility_convergence(flow1_path)
    flow1_clear = (
        flow1.decision == "FIRST_PARTY_RUNTIME_COMPAT_CONVERGENCE_PASS"
        and flow1.zero_internal_consumers
        and flow1.shim_count == 8
        and flow1.shim_contract_clear
        and flow1.identity_checks_clear
    )

    shims = list(contract.get("compatibility_shims") or [])
    if len(shims) != 8:
        raise CompatibilitySurfaceGovernanceError("Flow 2 must govern exactly eight shims")
    classes = [str(item.get("classification", "")) for item in shims]
    allowed = {"RETAIN_INDEFINITELY", "DEPRECATE_WITH_SUNSET", "OPEN_REMOVAL_GOVERNANCE"}
    if any(item not in allowed for item in classes):
        raise CompatibilitySurfaceGovernanceError("unknown shim governance classification")

    retain_count = classes.count("RETAIN_INDEFINITELY")
    deprecate_count = classes.count("DEPRECATE_WITH_SUNSET")
    open_count = classes.count("OPEN_REMOVAL_GOVERNANCE")

    policy = dict(contract.get("deprecation_policy") or {})
    notice_path = repo_root / str(policy.get("public_notice_path", ""))
    notice_source = notice_path.read_text(encoding="utf-8") if notice_path.is_file() else ""
    markers = [str(item) for item in policy.get("required_notice_markers", [])]
    public_notice_clear = bool(markers) and all(marker in notice_source for marker in markers)

    guidance_paths = [str(item) for item in contract.get("public_guidance_paths", [])]
    canonical_public_guidance_only = bool(guidance_paths)
    for path in guidance_paths:
        target = repo_root / path
        if not target.is_file() or _legacy_import_guidance(target.read_text(encoding="utf-8")):
            canonical_public_guidance_only = False
            break

    notice_date = date.fromisoformat(str(policy.get("governance_notice_date")))
    earliest_date = date.fromisoformat(str(policy.get("earliest_removal_review_date")))
    observation_days = (earliest_date - notice_date).days
    minimum_days = int(policy.get("minimum_public_observation_days", -1))
    if observation_days < minimum_days or minimum_days < 1:
        raise CompatibilitySurfaceGovernanceError("sunset review window is shorter than policy minimum")

    exposure = dict(contract.get("repository_exposure") or {})
    search = dict(exposure.get("public_code_search") or {})
    external_usage_status = str(exposure.get("external_usage_status", ""))
    search_hits = int(search.get("hit_count", -1))
    zero_hits_prove_zero = bool(search.get("zero_hits_prove_zero_external_users"))
    exposure_clear = (
        exposure.get("visibility") == "public"
        and exposure.get("github_releases_observed") == 0
        and exposure.get("root_python_package_metadata_present") is False
        and external_usage_status == "UNKNOWN"
        and search.get("evidence_class") == "NON_AUTHORITATIVE_DISCOVERY_ONLY"
        and search_hits == 0
        and zero_hits_prove_zero is False
    )

    removal = dict(contract.get("removal_governance") or {})
    observation_window_elapsed = bool(removal.get("observation_window_elapsed"))
    external_usage_audit_complete = bool(removal.get("external_usage_audit_complete"))
    no_known_downstream = bool(removal.get("no_known_supported_downstream_dependency"))
    explicit_owner_task = bool(removal.get("explicit_owner_removal_task"))
    explicit_opt_in = bool(removal.get("explicit_removal_governance_opt_in"))
    automatic_open_allowed = bool(removal.get("automatic_open_allowed"))

    removal_requirements_clear = all(
        (
            flow1_clear,
            canonical_public_guidance_only,
            observation_window_elapsed,
            external_usage_audit_complete,
            no_known_downstream,
            explicit_owner_task,
            explicit_opt_in,
        )
    )

    governance = dict(contract.get("governance") or {})
    false_keys = (
        "shim_deletion_allowed",
        "removal_governance_open",
        "external_removal_safety_inferred",
        "runtime_behavior_change_allowed",
        "import_warning_behavior_change_allowed",
        "provider_default_change_allowed",
        "lifecycle_state_owner_change_allowed",
        "routing_change_allowed",
        "evidence_authority_change_allowed",
        "gate_authority_change_allowed",
        "release_authority_change_allowed",
        "product_evidence",
    )
    effect_keys = ("execution_effect", "authority_effect", "gate_effect", "evidence_effect", "release_effect")
    governance_boundary_clear = (
        all(governance.get(key) is False for key in false_keys)
        and all(governance.get(key) == "none" for key in effect_keys)
        and automatic_open_allowed is False
    )

    current_policy_clear = all(
        (
            flow1_clear,
            exposure_clear,
            public_notice_clear,
            canonical_public_guidance_only,
            retain_count == 0,
            deprecate_count == 8,
            open_count == 0,
            observation_window_elapsed is False,
            external_usage_audit_complete is False,
            no_known_downstream is False,
            explicit_owner_task is False,
            explicit_opt_in is False,
            removal_requirements_clear is False,
            governance_boundary_clear,
        )
    )

    decision = (
        "DEPRECATE_WITH_SUNSET_REMOVAL_GOVERNANCE_CLOSED"
        if current_policy_clear
        else "HOLD_COMPATIBILITY_SURFACE_GOVERNANCE_REGRESSION"
    )

    return CompatibilitySurfaceGovernanceReport(
        schema_version="compatibility-surface-governance.v1",
        decision=decision,
        scope=str(contract["scope"]),
        flow1_clear=flow1_clear,
        zero_internal_consumers=flow1.zero_internal_consumers,
        shim_count=len(shims),
        retain_indefinitely_count=retain_count,
        deprecate_with_sunset_count=deprecate_count,
        open_removal_governance_count=open_count,
        public_notice_clear=public_notice_clear,
        canonical_public_guidance_only=canonical_public_guidance_only,
        external_usage_status=external_usage_status,
        public_code_search_hits=search_hits,
        zero_search_hits_prove_zero_external_users=zero_hits_prove_zero,
        observation_window_days=observation_days,
        earliest_removal_review_date=earliest_date.isoformat(),
        observation_window_elapsed=observation_window_elapsed,
        external_usage_audit_complete=external_usage_audit_complete,
        no_known_supported_downstream_dependency=no_known_downstream,
        explicit_owner_removal_task=explicit_owner_task,
        removal_requirements_clear=removal_requirements_clear,
        removal_governance_open=bool(governance.get("removal_governance_open")),
        shim_deletion_allowed=bool(governance.get("shim_deletion_allowed")),
        external_removal_safety_inferred=bool(governance.get("external_removal_safety_inferred")),
        governance_boundary_clear=governance_boundary_clear,
        execution_effect=str(governance.get("execution_effect", "")),
        authority_effect=str(governance.get("authority_effect", "")),
        gate_effect=str(governance.get("gate_effect", "")),
        evidence_effect=str(governance.get("evidence_effect", "")),
        release_effect=str(governance.get("release_effect", "")),
    )
