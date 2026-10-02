from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from core.benchmarks.final_owner_review_closure import (
    EXPECTED_HOLD_IDS,
    FinalOwnerReviewClosureError,
    _validate_contract,
    evaluate_final_owner_review_closure,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "uiux-factory/benchmarks/final-owner-review-closure-v1.json"
FLOW4_CONTRACT = ROOT / "uiux-factory/benchmarks/final-upgrade-regression-v1.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def _flow4_payload() -> dict:
    flow4_contract = json.loads(FLOW4_CONTRACT.read_text(encoding="utf-8"))
    projects = [
        {
            "project_id": item["project_id"],
            "expected_target_sha": item["expected_target_sha"],
            "report_present": True,
            "report_passed": True,
            "contract_clear": True,
            "truth_boundary_clear": True,
        }
        for item in flow4_contract["projects"]
    ]
    return {
        "schema_version": "final-upgrade-regression.v1",
        "decision": "WORKSPACE_UPGRADE_FINAL_REGRESSION_PASS",
        "scope": "final_regression_and_cross_project_dogfood_no_release_authority",
        "flow3_clear": True,
        "contract_clear": True,
        "governance_boundary_clear": True,
        "evidence_complete": True,
        "release_audit_present": True,
        "release_audit_passed": True,
        "project_results": projects,
        "project_pass_count": 4,
        "required_project_count": 4,
        "final_owner_review_allowed": True,
        "provider_default_change_allowed": False,
        "lifecycle_state_owner_change_allowed": False,
        "routing_change_allowed": False,
        "knowledge_index_mutation_allowed": False,
        "vector_search_change_allowed": False,
        "compatibility_shim_deletion_allowed": False,
        "evidence_authority_change_allowed": False,
        "gate_authority_change_allowed": False,
        "release_authority_change_allowed": False,
        "product_evidence": False,
        "execution_effect": "none",
        "authority_effect": "none",
        "gate_effect": "none",
        "evidence_effect": "none",
        "release_effect": "none",
    }


def _write_flow4(tmp_path: Path, payload: dict | None = None) -> Path:
    path = tmp_path / "flow4-final.json"
    path.write_text(json.dumps(payload or _flow4_payload()), encoding="utf-8")
    return path


def test_flow5_repository_only_validation_holds_fail_closed() -> None:
    report = evaluate_final_owner_review_closure(CONTRACT)

    assert report.decision == "HOLD_FINAL_OWNER_REVIEW_EVIDENCE_REQUIRED"
    assert report.flow3_clear is True
    assert report.flow4_contract_clear is True
    assert report.flow4_report_present is False
    assert report.flow4_clear is False
    assert report.intentional_holds_preserved is True
    assert report.intentional_hold_ids == EXPECTED_HOLD_IDS
    assert report.owner_delegation_clear is True
    assert report.owner_review_source_clear is True
    assert report.repository_hygiene_receipt_clear is True
    assert report.governance_boundary_clear is True
    assert report.final_owner_review_completed is False
    assert report.upgrade_closed is False


def test_flow5_closes_only_with_clean_flow4_receipt(tmp_path: Path) -> None:
    report = evaluate_final_owner_review_closure(
        CONTRACT,
        flow4_report_path=_write_flow4(tmp_path),
    )

    assert report.decision == "WORKSPACE_UPGRADE_CLOSED_WITH_INTENTIONAL_HOLDS"
    assert report.flow4_clear is True
    assert report.intentional_holds_preserved is True
    assert report.future_hold_triggers_preserved is True
    assert report.final_owner_review_completed is True
    assert report.upgrade_closed is True
    assert report.independent_human_review_claimed is False


def test_flow5_rejects_non_pass_flow4_decision(tmp_path: Path) -> None:
    payload = _flow4_payload()
    payload["decision"] = "FINAL_REGRESSION_FAILED"
    report = evaluate_final_owner_review_closure(
        CONTRACT,
        flow4_report_path=_write_flow4(tmp_path, payload),
    )

    assert report.decision == "FINAL_OWNER_REVIEW_FAILED"
    assert report.flow4_clear is False
    assert report.final_owner_review_completed is False
    assert report.upgrade_closed is False


def test_flow5_rejects_flow4_pinned_sha_drift(tmp_path: Path) -> None:
    payload = _flow4_payload()
    payload["project_results"][3]["expected_target_sha"] = "0" * 40
    report = evaluate_final_owner_review_closure(
        CONTRACT,
        flow4_report_path=_write_flow4(tmp_path, payload),
    )

    assert report.decision == "FINAL_OWNER_REVIEW_FAILED"
    assert report.flow4_clear is False


def test_flow5_rejects_weakened_flow4_truth_boundary(tmp_path: Path) -> None:
    payload = _flow4_payload()
    payload["project_results"][0]["truth_boundary_clear"] = False
    report = evaluate_final_owner_review_closure(
        CONTRACT,
        flow4_report_path=_write_flow4(tmp_path, payload),
    )

    assert report.decision == "FINAL_OWNER_REVIEW_FAILED"
    assert report.flow4_clear is False


def test_flow5_rejects_authority_escalation_in_flow4_receipt(tmp_path: Path) -> None:
    payload = _flow4_payload()
    payload["release_authority_change_allowed"] = True
    report = evaluate_final_owner_review_closure(
        CONTRACT,
        flow4_report_path=_write_flow4(tmp_path, payload),
    )

    assert report.decision == "FINAL_OWNER_REVIEW_FAILED"
    assert report.flow4_clear is False
    assert report.upgrade_closed is False


def test_flow5_contract_cannot_claim_independent_human_review() -> None:
    contract = copy.deepcopy(_contract())
    contract["owner_review"]["independent_human_review_claimed"] = True

    with pytest.raises(FinalOwnerReviewClosureError):
        _validate_contract(contract)


def test_flow5_contract_requires_resolved_repository_hygiene() -> None:
    contract = copy.deepcopy(_contract())
    contract["repository_hygiene_receipt"]["stale_duplicate_issue_135"] = "OPEN"

    with pytest.raises(FinalOwnerReviewClosureError):
        _validate_contract(contract)


def test_flow5_never_changes_runtime_or_release_authority(tmp_path: Path) -> None:
    report = evaluate_final_owner_review_closure(
        CONTRACT,
        flow4_report_path=_write_flow4(tmp_path),
    )

    assert report.provider_default_change_allowed is False
    assert report.lifecycle_state_owner_change_allowed is False
    assert report.routing_change_allowed is False
    assert report.knowledge_index_mutation_allowed is False
    assert report.vector_search_change_allowed is False
    assert report.compatibility_shim_deletion_allowed is False
    assert report.evidence_authority_change_allowed is False
    assert report.gate_authority_change_allowed is False
    assert report.release_authority_change_allowed is False
    assert report.product_evidence is False
    assert (
        report.execution_effect,
        report.authority_effect,
        report.gate_effect,
        report.evidence_effect,
        report.release_effect,
    ) == ("none",) * 5
