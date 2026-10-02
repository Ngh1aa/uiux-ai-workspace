from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from core.benchmarks.architecture_debt_closure_audit import (
    evaluate_architecture_debt_closure_audit,
)


EXPECTED_HOLD_IDS = (
    "provider_default_migration",
    "lifecycle_mutation_convergence",
    "genai_nist_expansion",
    "vector_semantic_retrieval",
    "compatibility_surface_removal",
)
EXPECTED_PROJECT_IDS = ("nova", "lumen", "cennext", "luxroom")


class FinalOwnerReviewClosureError(RuntimeError):
    pass


@dataclass(frozen=True)
class FinalOwnerReviewClosureReport:
    schema_version: str
    decision: str
    scope: str
    flow3_clear: bool
    flow4_report_present: bool
    flow4_clear: bool
    intentional_holds_preserved: bool
    intentional_hold_ids: tuple[str, ...]
    owner_delegation_clear: bool
    owner_review_source_clear: bool
    repository_hygiene_receipt_clear: bool
    governance_boundary_clear: bool
    final_owner_review_completed: bool
    upgrade_closed: bool
    future_hold_triggers_preserved: bool
    independent_human_review_claimed: bool
    provider_default_change_allowed: bool
    lifecycle_state_owner_change_allowed: bool
    routing_change_allowed: bool
    knowledge_index_mutation_allowed: bool
    vector_search_change_allowed: bool
    compatibility_shim_deletion_allowed: bool
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
        payload["intentional_hold_ids"] = list(self.intentional_hold_ids)
        return payload


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FinalOwnerReviewClosureError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise FinalOwnerReviewClosureError(f"expected JSON object at {path}")
    return payload


def _validate_contract(contract: dict[str, Any]) -> None:
    expected_keys = {
        "schema_version",
        "gate_id",
        "version",
        "phase",
        "checked_on",
        "scope",
        "flow3_contract",
        "owner_delegation_contract",
        "flow4_report",
        "required_flow3_state",
        "required_flow4_state",
        "required_intentional_hold_ids",
        "owner_review",
        "repository_hygiene_receipt",
        "decision_policy",
        "governance",
    }
    if set(contract) != expected_keys:
        raise FinalOwnerReviewClosureError("Flow 5 root keys do not match v1 contract")
    if contract["schema_version"] != 1:
        raise FinalOwnerReviewClosureError("Flow 5 schema_version must be 1")
    if contract["scope"] != "final_owner_governance_review_and_upgrade_closure_no_new_runtime_authority":
        raise FinalOwnerReviewClosureError("Flow 5 scope drifted")
    if contract["flow4_report"] != "flow4-final.json":
        raise FinalOwnerReviewClosureError("Flow 5 must consume the canonical Flow 4 A20 receipt")

    if contract["required_flow3_state"] != {
        "decision": "ARCHITECTURE_DEBT_LEDGER_CLOSED_FOR_UPGRADE",
        "closed_count": 4,
        "intentional_hold_count": 5,
        "actionable_debt_count": 0,
        "flow4_allowed": True,
    }:
        raise FinalOwnerReviewClosureError("Flow 5 required Flow 3 state drifted")

    if contract["required_flow4_state"] != {
        "decision": "WORKSPACE_UPGRADE_FINAL_REGRESSION_PASS",
        "flow3_clear": True,
        "contract_clear": True,
        "governance_boundary_clear": True,
        "evidence_complete": True,
        "release_audit_present": True,
        "release_audit_passed": True,
        "project_pass_count": 4,
        "required_project_count": 4,
        "final_owner_review_allowed": True,
    }:
        raise FinalOwnerReviewClosureError("Flow 5 required Flow 4 state drifted")

    if tuple(contract["required_intentional_hold_ids"]) != EXPECTED_HOLD_IDS:
        raise FinalOwnerReviewClosureError("Flow 5 intentional-hold set/order drifted")

    owner_review = contract["owner_review"]
    if owner_review != {
        "reviewer_login": "Haign12",
        "initiation": "explicit owner instruction through the connected ChatGPT session to execute Flow 5 after Flow 4 PASS",
        "review_kind": "retrospective_owner_governance_review_not_independent_human_validation",
        "decision_if_all_required_evidence_passed": "APPROVE_UPGRADE_CLOSURE_WITH_INTENTIONAL_HOLDS",
        "independent_human_review_claimed": False,
    }:
        raise FinalOwnerReviewClosureError("Flow 5 owner-review source drifted or fabricates human review")

    hygiene = contract["repository_hygiene_receipt"]
    if hygiene != {
        "observed_on": "2026-10-03",
        "open_pull_requests_before_flow5": 0,
        "stale_duplicate_issue_135": "CLOSED_DUPLICATE",
        "superseding_issue_136": "CLOSED_COMPLETED",
        "active_upgrade_issue": 152,
    }:
        raise FinalOwnerReviewClosureError("Flow 5 repository-hygiene receipt drifted")

    if contract["decision_policy"] != {
        "missing_flow4_evidence": "HOLD_FINAL_OWNER_REVIEW_EVIDENCE_REQUIRED",
        "boundary_or_governance_regression": "FINAL_OWNER_REVIEW_FAILED",
        "all_required_evidence_passed": "WORKSPACE_UPGRADE_CLOSED_WITH_INTENTIONAL_HOLDS",
    }:
        raise FinalOwnerReviewClosureError("Flow 5 decision policy drifted")


def _governance_clear(contract: dict[str, Any]) -> bool:
    governance = dict(contract.get("governance") or {})
    false_keys = (
        "provider_default_change_allowed",
        "lifecycle_state_owner_change_allowed",
        "routing_change_allowed",
        "knowledge_index_mutation_allowed",
        "vector_search_change_allowed",
        "compatibility_shim_deletion_allowed",
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
    return all(governance.get(key) is False for key in false_keys) and all(
        governance.get(key) == "none" for key in effect_keys
    )


def _owner_delegation_clear(payload: dict[str, Any]) -> bool:
    permissions = payload.get("permissions") if isinstance(payload.get("permissions"), dict) else {}
    boundaries = (
        payload.get("governance_boundaries")
        if isinstance(payload.get("governance_boundaries"), dict)
        else {}
    )
    final_review = payload.get("final_review") if isinstance(payload.get("final_review"), dict) else {}
    return all(
        (
            payload.get("schema_version") == 1,
            payload.get("owner_login") == "Haign12",
            payload.get("mode") == "preauthorized_continuation_after_required_gates_pass",
            permissions.get("continue_to_next_task_when_required_checks_pass") is True,
            permissions.get("record_model_or_owner_delegation_recommendations") is True,
            permissions.get("bypass_failed_or_missing_checks") is False,
            permissions.get("fabricate_independent_human_review") is False,
            permissions.get("rewrite_protected_history") is False,
            permissions.get("change_secrets_or_repository_permissions") is False,
            boundaries.get("independent_human_ledgers_remain_truthful") is True,
            boundaries.get("phase_specific_no_mutation_boundaries_remain_enforced") is True,
            boundaries.get("each_step_requires_auditable_evidence") is True,
            boundaries.get("final_retrospective_owner_review_required") is True,
            final_review.get("reviewer") == "Haign12",
            final_review.get("status") in {"DEFERRED_UNTIL_UPGRADE_COMPLETE", "COMPLETED_BY_FLOW5"},
        )
    )


def _flow4_clear(payload: dict[str, Any], required: dict[str, Any]) -> bool:
    for key, expected in required.items():
        if payload.get(key) != expected:
            return False
    if payload.get("schema_version") != "final-upgrade-regression.v1":
        return False
    if payload.get("scope") != "final_regression_and_cross_project_dogfood_no_release_authority":
        return False

    projects = payload.get("project_results")
    if not isinstance(projects, list) or len(projects) != len(EXPECTED_PROJECT_IDS):
        return False
    if tuple(str(item.get("project_id", "")) for item in projects) != EXPECTED_PROJECT_IDS:
        return False
    for item in projects:
        if not isinstance(item, dict):
            return False
        if not all(
            item.get(key) is True
            for key in ("report_present", "report_passed", "contract_clear", "truth_boundary_clear")
        ):
            return False

    false_keys = (
        "provider_default_change_allowed",
        "lifecycle_state_owner_change_allowed",
        "routing_change_allowed",
        "knowledge_index_mutation_allowed",
        "vector_search_change_allowed",
        "compatibility_shim_deletion_allowed",
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
    return all(payload.get(key) is False for key in false_keys) and all(
        payload.get(key) == "none" for key in effect_keys
    )


def evaluate_final_owner_review_closure(
    contract_path: Path,
    *,
    flow4_report_path: Path | None = None,
) -> FinalOwnerReviewClosureReport:
    contract_path = Path(contract_path).resolve()
    contract = _read_json(contract_path)
    _validate_contract(contract)
    repo_root = contract_path.parents[2]

    flow3 = evaluate_architecture_debt_closure_audit(
        repo_root / str(contract["flow3_contract"])
    )
    required_flow3 = dict(contract["required_flow3_state"])
    flow3_clear = all(
        (
            flow3.decision == required_flow3["decision"],
            flow3.closed_count == required_flow3["closed_count"],
            flow3.intentional_hold_count == required_flow3["intentional_hold_count"],
            flow3.actionable_debt_count == required_flow3["actionable_debt_count"],
            flow3.flow4_allowed is required_flow3["flow4_allowed"],
            flow3.source_contract_clear,
            flow3.area_contract_clear,
            flow3.governance_boundary_clear,
        )
    )

    hold_areas = tuple(item for item in flow3.areas if item.classification == "INTENTIONAL_HOLD")
    hold_ids = tuple(item.id for item in hold_areas)
    intentional_holds_preserved = all(
        (
            hold_ids == EXPECTED_HOLD_IDS,
            all(item.evidence_clear for item in hold_areas),
            all(item.upgrade_blocker is False for item in hold_areas),
            all(bool(item.trigger.strip()) for item in hold_areas),
        )
    )

    delegation_path = repo_root / str(contract["owner_delegation_contract"])
    owner_delegation_clear = delegation_path.is_file() and _owner_delegation_clear(
        _read_json(delegation_path)
    )
    owner_review_source_clear = contract["owner_review"]["independent_human_review_claimed"] is False
    repository_hygiene_receipt_clear = contract["repository_hygiene_receipt"] == {
        "observed_on": "2026-10-03",
        "open_pull_requests_before_flow5": 0,
        "stale_duplicate_issue_135": "CLOSED_DUPLICATE",
        "superseding_issue_136": "CLOSED_COMPLETED",
        "active_upgrade_issue": 152,
    }
    governance_boundary_clear = _governance_clear(contract)

    flow4_present = bool(flow4_report_path is not None and Path(flow4_report_path).is_file())
    flow4_clear = False
    if flow4_present and flow4_report_path is not None:
        flow4_clear = _flow4_clear(
            _read_json(Path(flow4_report_path).resolve()),
            dict(contract["required_flow4_state"]),
        )

    base_clear = all(
        (
            flow3_clear,
            intentional_holds_preserved,
            owner_delegation_clear,
            owner_review_source_clear,
            repository_hygiene_receipt_clear,
            governance_boundary_clear,
        )
    )
    policy = dict(contract["decision_policy"])
    if not base_clear:
        decision = policy["boundary_or_governance_regression"]
    elif not flow4_present:
        decision = policy["missing_flow4_evidence"]
    elif not flow4_clear:
        decision = policy["boundary_or_governance_regression"]
    else:
        decision = policy["all_required_evidence_passed"]

    completed = decision == "WORKSPACE_UPGRADE_CLOSED_WITH_INTENTIONAL_HOLDS"
    governance = dict(contract["governance"])
    return FinalOwnerReviewClosureReport(
        schema_version="final-owner-review-closure.v1",
        decision=decision,
        scope=str(contract["scope"]),
        flow3_clear=flow3_clear,
        flow4_report_present=flow4_present,
        flow4_clear=flow4_clear,
        intentional_holds_preserved=intentional_holds_preserved,
        intentional_hold_ids=hold_ids,
        owner_delegation_clear=owner_delegation_clear,
        owner_review_source_clear=owner_review_source_clear,
        repository_hygiene_receipt_clear=repository_hygiene_receipt_clear,
        governance_boundary_clear=governance_boundary_clear,
        final_owner_review_completed=completed,
        upgrade_closed=completed,
        future_hold_triggers_preserved=intentional_holds_preserved,
        independent_human_review_claimed=False,
        provider_default_change_allowed=bool(governance["provider_default_change_allowed"]),
        lifecycle_state_owner_change_allowed=bool(governance["lifecycle_state_owner_change_allowed"]),
        routing_change_allowed=bool(governance["routing_change_allowed"]),
        knowledge_index_mutation_allowed=bool(governance["knowledge_index_mutation_allowed"]),
        vector_search_change_allowed=bool(governance["vector_search_change_allowed"]),
        compatibility_shim_deletion_allowed=bool(governance["compatibility_shim_deletion_allowed"]),
        evidence_authority_change_allowed=bool(governance["evidence_authority_change_allowed"]),
        gate_authority_change_allowed=bool(governance["gate_authority_change_allowed"]),
        release_authority_change_allowed=bool(governance["release_authority_change_allowed"]),
        product_evidence=bool(governance["product_evidence"]),
        execution_effect=str(governance["execution_effect"]),
        authority_effect=str(governance["authority_effect"]),
        gate_effect=str(governance["gate_effect"]),
        evidence_effect=str(governance["evidence_effect"]),
        release_effect=str(governance["release_effect"]),
    )
