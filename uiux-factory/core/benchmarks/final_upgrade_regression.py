from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from core.benchmarks.architecture_debt_closure_audit import (
    evaluate_architecture_debt_closure_audit,
)
from core.dogfood.cross_project import project_profile


EXPECTED_PROJECT_IDS = ("nova", "lumen", "cennext", "luxroom")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class FinalUpgradeRegressionError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProjectFinalResult:
    project_id: str
    expected_target_sha: str
    report_present: bool
    report_passed: bool
    contract_clear: bool
    truth_boundary_clear: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FinalUpgradeRegressionReport:
    schema_version: str
    decision: str
    scope: str
    flow3_clear: bool
    contract_clear: bool
    governance_boundary_clear: bool
    evidence_complete: bool
    release_audit_present: bool
    release_audit_passed: bool
    project_results: tuple[ProjectFinalResult, ...]
    project_pass_count: int
    required_project_count: int
    final_owner_review_allowed: bool
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
        payload["project_results"] = [item.to_dict() for item in self.project_results]
        return payload


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FinalUpgradeRegressionError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise FinalUpgradeRegressionError(f"expected JSON object at {path}")
    return payload


def _validate_contract(contract: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    required_keys = {
        "schema_version",
        "gate_id",
        "version",
        "phase",
        "checked_on",
        "scope",
        "flow3_contract",
        "release_audit_report",
        "projects",
        "required_flow3_state",
        "required_generic_truth_boundary",
        "decision_policy",
        "governance",
    }
    if set(contract) != required_keys:
        raise FinalUpgradeRegressionError("Flow 4 root keys do not match v1 contract")
    if contract["schema_version"] != 1:
        raise FinalUpgradeRegressionError("Flow 4 schema_version must be 1")
    if contract["scope"] != "final_regression_and_cross_project_dogfood_no_release_authority":
        raise FinalUpgradeRegressionError("Flow 4 scope drifted")

    raw_projects = contract.get("projects")
    if not isinstance(raw_projects, list) or len(raw_projects) != len(EXPECTED_PROJECT_IDS):
        raise FinalUpgradeRegressionError("Flow 4 requires exactly four representative projects")
    if tuple(str(item.get("project_id", "")) for item in raw_projects) != EXPECTED_PROJECT_IDS:
        raise FinalUpgradeRegressionError("Flow 4 project order/set drifted")

    seen_reports: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for item in raw_projects:
        if set(item) != {"project_id", "repo", "expected_target_sha", "report"}:
            raise FinalUpgradeRegressionError("Flow 4 project contract keys drifted")
        project_id = str(item["project_id"])
        profile = project_profile(project_id)
        repo = str(item["repo"])
        sha = str(item["expected_target_sha"])
        report = str(item["report"])
        if repo != profile.repo:
            raise FinalUpgradeRegressionError(f"Flow 4 repo drift for {project_id}")
        if not SHA_RE.fullmatch(sha):
            raise FinalUpgradeRegressionError(f"Flow 4 SHA must be a full lowercase git SHA for {project_id}")
        if not report.endswith("-generic.json") or "/" in report or "\\" in report:
            raise FinalUpgradeRegressionError(f"unsafe/invalid Flow 4 report filename for {project_id}")
        if report in seen_reports:
            raise FinalUpgradeRegressionError("Flow 4 report filenames must be unique")
        seen_reports.add(report)
        normalized.append(dict(item))

    required_flow3 = contract.get("required_flow3_state")
    if required_flow3 != {
        "decision": "ARCHITECTURE_DEBT_LEDGER_CLOSED_FOR_UPGRADE",
        "closed_count": 4,
        "intentional_hold_count": 5,
        "actionable_debt_count": 0,
        "flow4_allowed": True,
    }:
        raise FinalUpgradeRegressionError("Flow 4 required Flow 3 state drifted")

    required_truth = contract.get("required_generic_truth_boundary")
    if required_truth != {
        "browser_status": "NOT_RUN",
        "provider_reasoning_status": "NOT_RUN",
        "human_review_status": "pending",
        "human_review_verdict": None,
        "release_status": "NOT_ATTEMPTED",
    }:
        raise FinalUpgradeRegressionError("Flow 4 generic truth boundary drifted")

    expected_policy = {
        "missing_or_incomplete_evidence": "HOLD_FINAL_REGRESSION_EVIDENCE_REQUIRED",
        "failed_or_boundary_regression": "FINAL_REGRESSION_FAILED",
        "all_required_evidence_passed": "WORKSPACE_UPGRADE_FINAL_REGRESSION_PASS",
    }
    if contract.get("decision_policy") != expected_policy:
        raise FinalUpgradeRegressionError("Flow 4 decision policy drifted")
    return tuple(normalized)


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
    ) and governance.get("final_owner_review_status") == "PENDING_AFTER_FLOW4_PASS"


def _release_audit_clear(payload: dict[str, Any]) -> bool:
    checks = payload.get("checks")
    return all(
        (
            payload.get("schema_version") == 1,
            payload.get("release_candidate") == "uiux-factory-v1",
            payload.get("passed") is True,
            isinstance(checks, dict),
            bool(checks),
            all(isinstance(row, dict) and row.get("passed") is True for row in checks.values())
            if isinstance(checks, dict)
            else False,
            "never fabricates provider quality" in str(payload.get("truth_boundary", "")),
        )
    )


def _project_result(
    item: dict[str, Any],
    report_root: Path | None,
    required_truth: dict[str, Any],
) -> ProjectFinalResult:
    project_id = str(item["project_id"])
    expected_sha = str(item["expected_target_sha"])
    if report_root is None:
        return ProjectFinalResult(project_id, expected_sha, False, False, False, False)

    path = report_root / str(item["report"])
    if not path.is_file():
        return ProjectFinalResult(project_id, expected_sha, False, False, False, False)

    payload = _read_json(path)
    profile = project_profile(project_id)
    checks = payload.get("checks")
    flow = payload.get("flow") if isinstance(payload.get("flow"), dict) else {}
    evidence = payload.get("evidence") if isinstance(payload.get("evidence"), dict) else {}
    contract = payload.get("contract") if isinstance(payload.get("contract"), dict) else {}
    dogfood_profile = (
        contract.get("dogfood_profile")
        if isinstance(contract.get("dogfood_profile"), dict)
        else {}
    )

    contract_clear = all(
        (
            payload.get("schema_version") == 2,
            payload.get("phase") == "A14-fix-once-validate-across-projects",
            payload.get("project") == project_id,
            payload.get("target") == profile.repo,
            payload.get("target_sha") == expected_sha,
            payload.get("expected_target_sha") == expected_sha,
            bool(str(payload.get("source_truth", "")).strip()),
            flow.get("id") == profile.expected_flow_id,
            flow.get("expected_id") == profile.expected_flow_id,
            evidence.get("model") == profile.evidence_model,
            list(evidence.get("missing_paths") or []) == [],
            dogfood_profile.get("project_id") == project_id,
            dogfood_profile.get("archetype") == profile.archetype,
            isinstance(checks, dict),
            bool(checks),
            all(value is True for value in checks.values()) if isinstance(checks, dict) else False,
        )
    )

    browser = payload.get("browser") if isinstance(payload.get("browser"), dict) else {}
    provider = (
        payload.get("provider_reasoning")
        if isinstance(payload.get("provider_reasoning"), dict)
        else {}
    )
    human = payload.get("human_review") if isinstance(payload.get("human_review"), dict) else {}
    release = payload.get("release") if isinstance(payload.get("release"), dict) else {}
    truth_boundary_clear = all(
        (
            browser.get("status") == required_truth["browser_status"],
            provider.get("status") == required_truth["provider_reasoning_status"],
            human.get("status") == required_truth["human_review_status"],
            human.get("verdict") is required_truth["human_review_verdict"],
            release.get("status") == required_truth["release_status"],
            "not manufactured" in str(payload.get("truth_boundary", "")),
        )
    )

    return ProjectFinalResult(
        project_id=project_id,
        expected_target_sha=expected_sha,
        report_present=True,
        report_passed=payload.get("passed") is True,
        contract_clear=contract_clear,
        truth_boundary_clear=truth_boundary_clear,
    )


def evaluate_final_upgrade_regression(
    contract_path: Path,
    *,
    report_root: Path | None = None,
) -> FinalUpgradeRegressionReport:
    contract_path = Path(contract_path).resolve()
    contract = _read_json(contract_path)
    projects = _validate_contract(contract)
    repo_root = contract_path.parents[2]

    flow3_path = repo_root / str(contract["flow3_contract"])
    flow3 = evaluate_architecture_debt_closure_audit(flow3_path)
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

    governance = dict(contract["governance"])
    governance_boundary_clear = _governance_clear(contract)
    required_truth = dict(contract["required_generic_truth_boundary"])
    normalized_root = Path(report_root).resolve() if report_root is not None else None

    release_present = bool(
        normalized_root is not None
        and (normalized_root / str(contract["release_audit_report"])).is_file()
    )
    release_passed = False
    if release_present and normalized_root is not None:
        release_passed = _release_audit_clear(
            _read_json(normalized_root / str(contract["release_audit_report"]))
        )

    results = tuple(
        _project_result(item, normalized_root, required_truth)
        for item in projects
    )
    project_pass_count = sum(
        item.report_present
        and item.report_passed
        and item.contract_clear
        and item.truth_boundary_clear
        for item in results
    )
    evidence_complete = release_present and all(item.report_present for item in results)
    contract_clear = flow3_clear and governance_boundary_clear

    policy = dict(contract["decision_policy"])
    if not contract_clear:
        decision = policy["failed_or_boundary_regression"]
    elif not evidence_complete:
        decision = policy["missing_or_incomplete_evidence"]
    elif not release_passed or project_pass_count != len(results):
        decision = policy["failed_or_boundary_regression"]
    else:
        decision = policy["all_required_evidence_passed"]

    final_owner_review_allowed = decision == "WORKSPACE_UPGRADE_FINAL_REGRESSION_PASS"

    return FinalUpgradeRegressionReport(
        schema_version="final-upgrade-regression.v1",
        decision=decision,
        scope=str(contract["scope"]),
        flow3_clear=flow3_clear,
        contract_clear=contract_clear,
        governance_boundary_clear=governance_boundary_clear,
        evidence_complete=evidence_complete,
        release_audit_present=release_present,
        release_audit_passed=release_passed,
        project_results=results,
        project_pass_count=project_pass_count,
        required_project_count=len(results),
        final_owner_review_allowed=final_owner_review_allowed,
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
