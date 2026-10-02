from __future__ import annotations

import json
from pathlib import Path

from core.benchmarks.final_upgrade_regression import evaluate_final_upgrade_regression
from core.dogfood.cross_project import project_profile


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "uiux-factory/benchmarks/final-upgrade-regression-v1.json"


def _contract() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def _write_release_audit(root: Path, *, passed: bool = True) -> None:
    payload = {
        "schema_version": 1,
        "release_candidate": "uiux-factory-v1",
        "benchmark_version": "2.0.0",
        "benchmark_cases": 12,
        "benchmark_domains": 12,
        "checks": {
            "structural": {"passed": passed, "detail": "fixture"},
            "security": {"passed": passed, "detail": "fixture"},
        },
        "passed": passed,
        "truth_boundary": (
            "A20 PASS never fabricates provider quality, human aesthetic approval, "
            "user outcomes or production-release authorization."
        ),
    }
    (root / "release-audit.json").write_text(json.dumps(payload), encoding="utf-8")


def _project_payload(project: dict, *, wrong_sha: bool = False, fabricate_human: bool = False) -> dict:
    project_id = project["project_id"]
    profile = project_profile(project_id)
    expected_sha = project["expected_target_sha"]
    sha = "0" * 40 if wrong_sha else expected_sha
    return {
        "schema_version": 2,
        "phase": "A14-fix-once-validate-across-projects",
        "target": profile.repo,
        "target_sha": sha,
        "expected_target_sha": expected_sha,
        "project": project_id,
        "project_shape": {"kind": "fixture"},
        "source_truth": profile.source_truth_candidates[0],
        "contract": {
            "change_surface": profile.expected_change_surface,
            "change_boundary": profile.expected_change_boundary,
            "dogfood_profile": {
                "project_id": project_id,
                "archetype": profile.archetype,
                "routing_intent": profile.routing_intent,
                "evidence_model": profile.evidence_model,
            },
        },
        "flow": {
            "id": profile.expected_flow_id,
            "expected_id": profile.expected_flow_id,
            "score": 1,
            "source": "fixture",
            "error": None,
        },
        "evidence": {
            "model": profile.evidence_model,
            "required_paths": list(profile.evidence_paths),
            "missing_paths": [],
        },
        "checks": {
            "source_truth_loaded": True,
            "flow_resolved": True,
            "expected_flow_preserved": True,
            "target_sha_bound": not wrong_sha,
            "profile_evidence_grounded": True,
            "cross_profile_isolation": True,
        },
        "passed": not wrong_sha,
        "browser": {"status": "NOT_RUN"},
        "provider_reasoning": {"status": "NOT_RUN"},
        "human_review": {
            "status": "passed" if fabricate_human else "pending",
            "verdict": "PASS" if fabricate_human else None,
        },
        "release": {"status": "NOT_ATTEMPTED"},
        "truth_boundary": "Generic browser/provider/human/release verdicts are not manufactured.",
    }


def _write_project_reports(root: Path) -> None:
    for project in _contract()["projects"]:
        (root / project["report"]).write_text(
            json.dumps(_project_payload(project)),
            encoding="utf-8",
        )


def test_flow4_without_a20_reports_holds_fail_closed() -> None:
    report = evaluate_final_upgrade_regression(CONTRACT)

    assert report.decision == "HOLD_FINAL_REGRESSION_EVIDENCE_REQUIRED"
    assert report.flow3_clear is True
    assert report.contract_clear is True
    assert report.governance_boundary_clear is True
    assert report.evidence_complete is False
    assert report.project_pass_count == 0
    assert report.required_project_count == 4
    assert report.final_owner_review_allowed is False


def test_flow4_passes_only_with_release_audit_and_all_four_project_receipts(tmp_path: Path) -> None:
    _write_release_audit(tmp_path)
    _write_project_reports(tmp_path)

    report = evaluate_final_upgrade_regression(CONTRACT, report_root=tmp_path)

    assert report.decision == "WORKSPACE_UPGRADE_FINAL_REGRESSION_PASS"
    assert report.evidence_complete is True
    assert report.release_audit_passed is True
    assert report.project_pass_count == report.required_project_count == 4
    assert all(item.contract_clear and item.truth_boundary_clear for item in report.project_results)
    assert report.final_owner_review_allowed is True


def test_flow4_missing_one_project_receipt_remains_hold(tmp_path: Path) -> None:
    _write_release_audit(tmp_path)
    projects = _contract()["projects"]
    for project in projects[:-1]:
        (tmp_path / project["report"]).write_text(
            json.dumps(_project_payload(project)),
            encoding="utf-8",
        )

    report = evaluate_final_upgrade_regression(CONTRACT, report_root=tmp_path)

    assert report.decision == "HOLD_FINAL_REGRESSION_EVIDENCE_REQUIRED"
    assert report.evidence_complete is False
    assert report.project_pass_count == 3
    assert report.final_owner_review_allowed is False


def test_flow4_wrong_pinned_sha_fails(tmp_path: Path) -> None:
    _write_release_audit(tmp_path)
    projects = _contract()["projects"]
    for project in projects:
        payload = _project_payload(project, wrong_sha=project["project_id"] == "luxroom")
        (tmp_path / project["report"]).write_text(json.dumps(payload), encoding="utf-8")

    report = evaluate_final_upgrade_regression(CONTRACT, report_root=tmp_path)

    assert report.decision == "FINAL_REGRESSION_FAILED"
    assert report.evidence_complete is True
    assert report.project_pass_count == 3
    assert report.final_owner_review_allowed is False


def test_flow4_rejects_fabricated_human_verdict_from_generic_lane(tmp_path: Path) -> None:
    _write_release_audit(tmp_path)
    projects = _contract()["projects"]
    for project in projects:
        payload = _project_payload(project, fabricate_human=project["project_id"] == "nova")
        (tmp_path / project["report"]).write_text(json.dumps(payload), encoding="utf-8")

    report = evaluate_final_upgrade_regression(CONTRACT, report_root=tmp_path)

    assert report.decision == "FINAL_REGRESSION_FAILED"
    assert report.evidence_complete is True
    assert report.project_pass_count == 3
    assert report.final_owner_review_allowed is False


def test_flow4_never_changes_runtime_or_release_authority(tmp_path: Path) -> None:
    _write_release_audit(tmp_path)
    _write_project_reports(tmp_path)
    report = evaluate_final_upgrade_regression(CONTRACT, report_root=tmp_path)

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
