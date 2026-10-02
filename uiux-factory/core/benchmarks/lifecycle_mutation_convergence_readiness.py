from __future__ import annotations

import inspect
import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

from core.benchmarks.lifecycle_parity_regression import evaluate_lifecycle_parity_corpus
from core.runtime.flow_os.managed import ManagedFlowController, ManagedWebsiteRun
from core.runtime.lifecycle_reconciliation import current_lifecycle_reconciliation
from core.runtime.run_context import RunContext


SCHEMA_VERSION = 1
READINESS_SCOPE = "readiness_only_no_lifecycle_mutation"


class LifecycleMutationReadinessError(ValueError):
    pass


@dataclass(frozen=True)
class LifecycleMutationReadinessReport:
    decision: str
    lifecycle_projection_parity_clear: bool
    reconciliation_read_only: bool
    source_contract_clear: bool
    semantic_blockers: tuple[str, ...]
    semantic_blockers_match_contract: bool
    event_interop_proposal_allowed: bool
    mutation_governance_allowed: bool
    state_owner_replacement_allowed: bool
    shared_mutable_state_allowed: bool
    runtime_transition_change_allowed: bool
    routing_change_allowed: bool
    provider_default_change_allowed: bool
    evidence_authority_change_allowed: bool
    gate_authority_change_allowed: bool
    finalize_release_authority_change_allowed: bool
    product_evidence: bool


def _load_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LifecycleMutationReadinessError(f"readiness contract could not be loaded: {exc}") from exc
    if not isinstance(payload, dict):
        raise LifecycleMutationReadinessError("readiness contract must be an object")
    return payload


def _validate_contract(config: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "readiness_id",
        "version",
        "checked_on",
        "scope",
        "state_owners",
        "required_prerequisites",
        "current_semantic_blockers",
        "decision_policy",
        "governance",
    }
    if set(config) != required:
        raise LifecycleMutationReadinessError("readiness contract keys do not match v1")
    if config["schema_version"] != SCHEMA_VERSION:
        raise LifecycleMutationReadinessError(f"schema_version must be {SCHEMA_VERSION}")
    if config["scope"] != READINESS_SCOPE:
        raise LifecycleMutationReadinessError("A52.1 scope must remain readiness-only")
    if config["state_owners"] != {
        "factory": "core.runtime.run_context.RunContext",
        "managed": "core.runtime.flow_os.managed.ManagedWebsiteRun",
    }:
        raise LifecycleMutationReadinessError("A52.1 must preserve both current lifecycle state owners")
    if config["required_prerequisites"] != {
        "lifecycle_projection_parity_must_pass": True,
        "reconciliation_must_remain_read_only": True,
        "existing_state_owners_must_remain_distinct": True,
        "source_contracts_must_be_unambiguous": True,
    }:
        raise LifecycleMutationReadinessError("A52.1 prerequisite contract drifted")

    expected_blockers = [
        "distinct_state_models",
        "factory_append_only_chronology",
        "managed_checkpoint_and_stage_lineage",
        "managed_human_gate_semantics",
        "replan_invalidation_semantics_non_parity",
        "finalize_release_semantics_non_parity",
    ]
    if config["current_semantic_blockers"] != expected_blockers:
        raise LifecycleMutationReadinessError("A52.1 semantic blocker contract drifted")

    expected_policy = {
        "prerequisite_regression": "HOLD_LIFECYCLE_CONVERGENCE_EVIDENCE_REQUIRED",
        "semantic_blockers_present": "KEEP_SEPARATE_STATE_OWNERS_EVENT_INTEROP_REQUIRED",
        "blockers_cleared_without_explicit_governance": "HOLD_EXPLICIT_MUTATION_GOVERNANCE_REQUIRED",
        "blockers_cleared_with_explicit_governance": "READY_FOR_SEPARATE_MUTATION_GOVERNANCE",
    }
    if config["decision_policy"] != expected_policy:
        raise LifecycleMutationReadinessError("A52.1 decision policy drifted")

    governance = config["governance"]
    expected_keys = {
        "explicit_mutation_governance_opt_in",
        "event_interop_proposal_allowed_when_current_audit_clear",
        "state_owner_replacement_allowed_in_this_task",
        "shared_mutable_state_allowed_in_this_task",
        "runtime_transition_change_allowed_in_this_task",
        "routing_change_allowed",
        "provider_default_change_allowed",
        "evidence_authority_change_allowed",
        "gate_authority_change_allowed",
        "finalize_release_authority_change_allowed",
        "product_evidence",
        "final_owner_review_status",
    }
    if set(governance) != expected_keys:
        raise LifecycleMutationReadinessError("A52.1 governance keys do not match v1")
    if governance["explicit_mutation_governance_opt_in"] is not False:
        raise LifecycleMutationReadinessError("A52.1 cannot opt into mutation governance")
    if governance["event_interop_proposal_allowed_when_current_audit_clear"] is not True:
        raise LifecycleMutationReadinessError("A52.1 must keep the additive event-interop handoff explicit")
    false_keys = expected_keys - {
        "explicit_mutation_governance_opt_in",
        "event_interop_proposal_allowed_when_current_audit_clear",
        "final_owner_review_status",
    }
    if any(governance[key] is not False for key in false_keys):
        raise LifecycleMutationReadinessError("A52.1 cannot change lifecycle/authority/runtime semantics")
    if governance["final_owner_review_status"] != "DEFERRED_UNTIL_UPGRADE_COMPLETE":
        raise LifecycleMutationReadinessError("final owner review must remain deferred")


def _has_methods(owner: type[Any], names: set[str]) -> bool:
    return all(callable(getattr(owner, name, None)) for name in names)


def _source_contract() -> tuple[bool, bool, dict[str, bool]]:
    reconciliation = current_lifecycle_reconciliation()
    effects = (
        reconciliation.execution_effect,
        reconciliation.authority_effect,
        reconciliation.gate_effect,
        reconciliation.evidence_effect,
        reconciliation.release_effect,
    )
    reconciliation_read_only = reconciliation.adapter_required is True and effects == ("none",) * 5

    factory_fields = {item.name for item in fields(RunContext)}
    managed_fields = {item.name for item in fields(ManagedWebsiteRun)}
    factory_methods = {
        "initialize",
        "start_stage",
        "complete_stage",
        "add_error",
        "complete",
        "event_bus",
        "projected_state",
    }
    managed_methods = {
        "resume",
        "start_stage",
        "required_human_approvals",
        "approve_gate",
        "complete_stage",
        "replan",
        "_checkpoint_managed",
    }

    factory_source = inspect.getsource(RunContext)
    managed_source = inspect.getsource(ManagedFlowController)

    owner_paths_clear = (
        reconciliation.factory.state_model == "core.runtime.run_context.RunContext"
        and reconciliation.managed.state_model == "core.runtime.flow_os.managed.ManagedWebsiteRun"
    )
    methods_clear = _has_methods(RunContext, factory_methods) and _has_methods(ManagedFlowController, managed_methods)

    blockers = {
        "distinct_state_models": (
            reconciliation.factory.state_model != reconciliation.managed.state_model
            and factory_fields != managed_fields
        ),
        "factory_append_only_chronology": (
            "_event_bus" in factory_fields
            and "RunEventBus" in factory_source
            and "events.jsonl" in factory_source
            and "project_run_state" not in factory_source
            and callable(getattr(RunContext, "projected_state", None))
        ),
        "managed_checkpoint_and_stage_lineage": (
            {"stage_runs", "replan_history"}.issubset(managed_fields)
            and "self._checkpoint_managed(managed)" in managed_source
            and "flow_revision" in managed_source
        ),
        "managed_human_gate_semantics": (
            "approved_gates" in managed_fields
            and "AWAITING_APPROVAL" in managed_source
            and "required_human_approvals" in managed_source
        ),
        "replan_invalidation_semantics_non_parity": any(
            "Factory creative revision" in item and "managed replanning" in item
            for item in reconciliation.non_parity
        ),
        "finalize_release_semantics_non_parity": (
            reconciliation.factory.phase("RELEASE").support == "not_exposed"
            and reconciliation.managed.phase("RELEASE").support == "external_controller"
            and reconciliation.managed.phase("FINALIZE").support == "external_controller"
        ),
    }

    source_contract_clear = owner_paths_clear and methods_clear and reconciliation_read_only
    return source_contract_clear, reconciliation_read_only, blockers


def _derive_decision(
    *,
    parity_clear: bool,
    source_contract_clear: bool,
    reconciliation_read_only: bool,
    blockers: tuple[str, ...],
    explicit_mutation_governance_opt_in: bool,
    policy: dict[str, str],
) -> str:
    if not parity_clear or not source_contract_clear or not reconciliation_read_only:
        return policy["prerequisite_regression"]
    if blockers:
        return policy["semantic_blockers_present"]
    if not explicit_mutation_governance_opt_in:
        return policy["blockers_cleared_without_explicit_governance"]
    return policy["blockers_cleared_with_explicit_governance"]


def evaluate_lifecycle_mutation_convergence_readiness(
    readiness_path: Path,
    *,
    lifecycle_parity_path: Path,
) -> LifecycleMutationReadinessReport:
    config = _load_object(readiness_path)
    _validate_contract(config)

    parity = evaluate_lifecycle_parity_corpus(lifecycle_parity_path)
    parity_clear = parity.total > 0 and parity.passed == parity.total
    source_contract_clear, reconciliation_read_only, blocker_map = _source_contract()

    blocker_order = tuple(str(item) for item in config["current_semantic_blockers"])
    observed_blockers = tuple(key for key in blocker_order if blocker_map.get(key) is True)
    blockers_match_contract = observed_blockers == blocker_order

    governance = config["governance"]
    decision = _derive_decision(
        parity_clear=parity_clear,
        source_contract_clear=source_contract_clear,
        reconciliation_read_only=reconciliation_read_only,
        blockers=observed_blockers,
        explicit_mutation_governance_opt_in=bool(governance["explicit_mutation_governance_opt_in"]),
        policy=dict(config["decision_policy"]),
    )

    event_interop_allowed = (
        decision == config["decision_policy"]["semantic_blockers_present"]
        and parity_clear
        and source_contract_clear
        and reconciliation_read_only
        and blockers_match_contract
        and governance["event_interop_proposal_allowed_when_current_audit_clear"] is True
    )
    mutation_governance_allowed = decision == config["decision_policy"]["blockers_cleared_with_explicit_governance"]

    return LifecycleMutationReadinessReport(
        decision=decision,
        lifecycle_projection_parity_clear=parity_clear,
        reconciliation_read_only=reconciliation_read_only,
        source_contract_clear=source_contract_clear,
        semantic_blockers=observed_blockers,
        semantic_blockers_match_contract=blockers_match_contract,
        event_interop_proposal_allowed=event_interop_allowed,
        mutation_governance_allowed=mutation_governance_allowed,
        state_owner_replacement_allowed=False,
        shared_mutable_state_allowed=False,
        runtime_transition_change_allowed=False,
        routing_change_allowed=False,
        provider_default_change_allowed=False,
        evidence_authority_change_allowed=False,
        gate_authority_change_allowed=False,
        finalize_release_authority_change_allowed=False,
        product_evidence=False,
    )
