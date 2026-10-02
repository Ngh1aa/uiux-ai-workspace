from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.benchmarks.provider_parity_regression import evaluate_provider_parity_benchmark
from core.runtime.flow_os.flow import FlowPlanner
from core.runtime.provider_compat_contract import (
    FACTORY_PROVIDER_LANE_ENV,
    FACTORY_PROVIDER_LANES,
    resolve_factory_provider_lane,
)


SCHEMA_VERSION = 1
READINESS_SCOPE = "readiness_contract_only_no_default_migration"
RECEIPT_STATUSES = {"NOT_RUN", "PARTIAL", "COMPLETE"}
FAILURE_CATEGORIES = {
    "provider_error",
    "network_or_timeout",
    "contract_invalid",
    "unexpected_error",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ProviderMigrationReadinessError(ValueError):
    pass


@dataclass(frozen=True)
class ProviderMigrationReadinessReport:
    decision: str
    offline_provider_parity_clear: bool
    default_lane_contract_clear: bool
    live_receipt_contract_clear: bool
    live_matrix_complete: bool
    live_matrix_all_passed: bool
    required_receipt_count: int
    observed_receipt_count: int
    missing_matrix: tuple[str, ...]
    failed_matrix: tuple[str, ...]
    default_change_allowed: bool
    provider_migration_allowed: bool
    auto_migration_allowed: bool
    migration_governance_allowed: bool
    product_evidence: bool


def _load_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderMigrationReadinessError(f"{label} could not be loaded: {exc}") from exc
    if not isinstance(payload, dict):
        raise ProviderMigrationReadinessError(f"{label} must be an object")
    return payload


def _mode_map(config: dict[str, Any]) -> dict[str, tuple[str, bool]]:
    raw_modes = config.get("trial_modes")
    if not isinstance(raw_modes, list) or not raw_modes:
        raise ProviderMigrationReadinessError("trial_modes are required")
    result: dict[str, tuple[str, bool]] = {}
    for raw in raw_modes:
        if not isinstance(raw, dict) or set(raw) != {"mode_id", "stage", "json_mode"}:
            raise ProviderMigrationReadinessError("trial mode keys do not match the v1 contract")
        mode_id = str(raw["mode_id"]).strip()
        stage = str(raw["stage"]).strip()
        json_mode = raw["json_mode"]
        if not mode_id or not stage or not isinstance(json_mode, bool):
            raise ProviderMigrationReadinessError("trial mode fields are invalid")
        if mode_id in result:
            raise ProviderMigrationReadinessError(f"duplicate trial mode: {mode_id}")
        result[mode_id] = (stage, json_mode)
    return result


def _validate_config(config: dict[str, Any]) -> tuple[list[str], dict[str, tuple[str, bool]]]:
    required = {
        "schema_version",
        "readiness_id",
        "version",
        "checked_on",
        "scope",
        "current_default_lane",
        "candidate_lane",
        "supported_providers",
        "trial_modes",
        "requirements",
        "decision_policy",
        "governance",
    }
    if set(config) != required:
        raise ProviderMigrationReadinessError("readiness config keys do not match the v1 contract")
    if config["schema_version"] != SCHEMA_VERSION:
        raise ProviderMigrationReadinessError(f"schema_version must be {SCHEMA_VERSION}")
    if config["scope"] != READINESS_SCOPE:
        raise ProviderMigrationReadinessError("readiness scope must forbid default migration")
    if config["current_default_lane"] != "legacy" or config["candidate_lane"] != "managed_compat":
        raise ProviderMigrationReadinessError("A51.1 must preserve legacy default and managed_compat candidate")

    providers = config["supported_providers"]
    if providers != ["groq", "gemini"]:
        raise ProviderMigrationReadinessError("A51.1 requires the full supported free-tier provider set: groq, gemini")

    requirements = config["requirements"]
    expected_requirements = {
        "offline_provider_parity_must_pass": True,
        "empty_env_must_resolve_to_legacy": True,
        "managed_compat_must_remain_explicit_opt_in": True,
        "invalid_lane_must_fail_closed": True,
        "automatic_cross_lane_fallback_must_remain_false": True,
        "all_provider_lane_mode_receipts_required": True,
        "all_live_receipts_must_pass_contract": True,
        "receipt_payloads_must_be_secret_and_content_free": True,
    }
    if requirements != expected_requirements:
        raise ProviderMigrationReadinessError("readiness requirements drifted from the fail-closed v1 contract")

    policy = config["decision_policy"]
    if policy != {
        "incomplete_or_failed_live_evidence": "KEEP_LEGACY_DEFAULT_LIVE_EVIDENCE_REQUIRED",
        "complete_live_contract_evidence": "READY_FOR_DEFAULT_MIGRATION_GOVERNANCE",
    }:
        raise ProviderMigrationReadinessError("decision policy drifted")

    governance = config["governance"]
    required_false = {
        "default_change_allowed_in_this_task",
        "provider_migration_allowed_in_this_task",
        "auto_migration_allowed",
        "billing_or_account_change_allowed",
        "routing_change_allowed",
        "skill_activation_change_allowed",
        "evidence_authority_change_allowed",
        "gate_authority_change_allowed",
        "release_authority_change_allowed",
        "product_evidence",
    }
    if any(governance.get(key) is not False for key in required_false):
        raise ProviderMigrationReadinessError("A51.1 governance must keep all migration/authority effects disabled")
    if governance.get("final_owner_review_status") != "DEFERRED_UNTIL_UPGRADE_COMPLETE":
        raise ProviderMigrationReadinessError("final owner review must remain deferred")

    return list(providers), _mode_map(config)


def _default_lane_contract_clear() -> bool:
    if FACTORY_PROVIDER_LANES != frozenset({"legacy", "managed_compat"}):
        return False
    if resolve_factory_provider_lane({}) != ("legacy", "default"):
        return False
    if resolve_factory_provider_lane({FACTORY_PROVIDER_LANE_ENV: "legacy"}) != ("legacy", "explicit"):
        return False
    if resolve_factory_provider_lane({FACTORY_PROVIDER_LANE_ENV: "managed_compat"}) != (
        "managed_compat",
        "explicit",
    ):
        return False
    try:
        resolve_factory_provider_lane({FACTORY_PROVIDER_LANE_ENV: "future-auto"})
    except ValueError:
        return True
    return False


def _matrix_key(provider: str, lane: str, mode_id: str) -> str:
    return f"{provider}:{lane}:{mode_id}"


def _validate_receipts(
    receipt_set: dict[str, Any],
    *,
    providers: list[str],
    modes: dict[str, tuple[str, bool]],
) -> tuple[bool, set[str], set[str], set[str]]:
    required_root = {
        "schema_version",
        "receipt_set_id",
        "version",
        "collected_on",
        "collection_status",
        "receipts",
    }
    if set(receipt_set) != required_root:
        raise ProviderMigrationReadinessError("live receipt ledger keys do not match the v1 contract")
    if receipt_set["schema_version"] != SCHEMA_VERSION:
        raise ProviderMigrationReadinessError(f"receipt schema_version must be {SCHEMA_VERSION}")
    status = receipt_set["collection_status"]
    if status not in RECEIPT_STATUSES:
        raise ProviderMigrationReadinessError("unknown live receipt collection_status")
    raw_receipts = receipt_set["receipts"]
    if not isinstance(raw_receipts, list):
        raise ProviderMigrationReadinessError("receipts must be an array")
    if status == "NOT_RUN" and (raw_receipts or receipt_set["collected_on"] is not None):
        raise ProviderMigrationReadinessError("NOT_RUN receipt ledger must be empty and undated")
    if status != "NOT_RUN" and not isinstance(receipt_set["collected_on"], str):
        raise ProviderMigrationReadinessError("collected_on is required after a live trial starts")

    expected = {
        _matrix_key(provider, lane, mode_id)
        for provider in providers
        for lane in ("legacy", "managed_compat")
        for mode_id in modes
    }
    observed: set[str] = set()
    passed: set[str] = set()
    failed: set[str] = set()

    receipt_keys = {
        "provider",
        "model",
        "lane",
        "mode_id",
        "stage",
        "json_mode",
        "success",
        "contract_valid",
        "request_sha256",
        "artifact_sha256",
        "artifact_chars",
        "error_category",
        "automatic_cross_lane_fallback",
        "authority_effect",
        "gate_effect",
        "evidence_effect",
        "release_effect",
    }

    for row in raw_receipts:
        if not isinstance(row, dict) or set(row) != receipt_keys:
            raise ProviderMigrationReadinessError("live receipt keys do not match the sanitized v1 contract")
        provider = str(row["provider"])
        lane = str(row["lane"])
        mode_id = str(row["mode_id"])
        if provider not in providers or lane not in {"legacy", "managed_compat"} or mode_id not in modes:
            raise ProviderMigrationReadinessError("live receipt references an unsupported provider/lane/mode")
        stage, json_mode = modes[mode_id]
        if row["stage"] != stage or row["json_mode"] is not json_mode:
            raise ProviderMigrationReadinessError("live receipt mode metadata does not match readiness contract")
        model = str(row["model"]).strip()
        if not model or len(model) > 256:
            raise ProviderMigrationReadinessError("live receipt model identifier is missing or too long")
        if not SHA256_RE.fullmatch(str(row["request_sha256"])):
            raise ProviderMigrationReadinessError("live receipt request_sha256 must be a lowercase SHA-256 digest")
        if row["automatic_cross_lane_fallback"] is not False:
            raise ProviderMigrationReadinessError("live receipt cannot permit automatic cross-lane fallback")
        if any(row[key] != "none" for key in ("authority_effect", "gate_effect", "evidence_effect", "release_effect")):
            raise ProviderMigrationReadinessError("live receipt cannot change authority/evidence/gate/release semantics")
        if not isinstance(row["success"], bool) or not isinstance(row["contract_valid"], bool):
            raise ProviderMigrationReadinessError("live receipt success/contract_valid must be booleans")

        key = _matrix_key(provider, lane, mode_id)
        if key in observed:
            raise ProviderMigrationReadinessError(f"duplicate live receipt matrix row: {key}")
        observed.add(key)

        if row["success"]:
            if row["contract_valid"] is not True:
                raise ProviderMigrationReadinessError("successful live receipt must have contract_valid=true")
            if not SHA256_RE.fullmatch(str(row["artifact_sha256"])):
                raise ProviderMigrationReadinessError("successful live receipt artifact_sha256 is invalid")
            if not isinstance(row["artifact_chars"], int) or row["artifact_chars"] <= 0:
                raise ProviderMigrationReadinessError("successful live receipt artifact_chars must be positive")
            if row["error_category"] is not None:
                raise ProviderMigrationReadinessError("successful live receipt cannot carry an error_category")
            passed.add(key)
        else:
            if row["artifact_sha256"] is not None or row["artifact_chars"] != 0:
                raise ProviderMigrationReadinessError("failed live receipt cannot persist artifact output metadata")
            if row["error_category"] not in FAILURE_CATEGORIES:
                raise ProviderMigrationReadinessError("failed live receipt requires a bounded error_category")
            failed.add(key)

    if status == "COMPLETE" and observed != expected:
        raise ProviderMigrationReadinessError("COMPLETE receipt ledger must contain the exact required matrix")
    if status == "PARTIAL" and (not observed or observed == expected):
        raise ProviderMigrationReadinessError("PARTIAL receipt ledger must contain a strict subset of the matrix")

    return True, expected, observed, passed - failed


def evaluate_provider_default_migration_readiness(
    readiness_path: Path,
    receipt_path: Path,
    *,
    parity_benchmark_path: Path,
    factory_root: Path,
    skills_root: Path,
    runtime_policy_path: Path,
) -> ProviderMigrationReadinessReport:
    config = _load_object(readiness_path, label="provider migration readiness config")
    providers, modes = _validate_config(config)
    receipt_set = _load_object(receipt_path, label="provider live receipt ledger")

    policy = json.loads(runtime_policy_path.read_text(encoding="utf-8"))
    planner = FlowPlanner(skills_root, policy)
    parity_results = evaluate_provider_parity_benchmark(
        parity_benchmark_path,
        factory_root=factory_root,
        planner=planner,
    )
    offline_provider_parity_clear = bool(parity_results) and all(item.passed for item in parity_results)
    default_lane_contract_clear = _default_lane_contract_clear()

    live_receipt_contract_clear, expected, observed, passed = _validate_receipts(
        receipt_set,
        providers=providers,
        modes=modes,
    )
    missing = expected - observed
    failed = observed - passed
    live_matrix_complete = observed == expected
    live_matrix_all_passed = live_matrix_complete and passed == expected

    ready = all(
        (
            offline_provider_parity_clear,
            default_lane_contract_clear,
            live_receipt_contract_clear,
            live_matrix_complete,
            live_matrix_all_passed,
        )
    )
    decision = (
        config["decision_policy"]["complete_live_contract_evidence"]
        if ready
        else config["decision_policy"]["incomplete_or_failed_live_evidence"]
    )

    return ProviderMigrationReadinessReport(
        decision=decision,
        offline_provider_parity_clear=offline_provider_parity_clear,
        default_lane_contract_clear=default_lane_contract_clear,
        live_receipt_contract_clear=live_receipt_contract_clear,
        live_matrix_complete=live_matrix_complete,
        live_matrix_all_passed=live_matrix_all_passed,
        required_receipt_count=len(expected),
        observed_receipt_count=len(observed),
        missing_matrix=tuple(sorted(missing)),
        failed_matrix=tuple(sorted(failed)),
        default_change_allowed=False,
        provider_migration_allowed=False,
        auto_migration_allowed=False,
        migration_governance_allowed=ready,
        product_evidence=False,
    )
