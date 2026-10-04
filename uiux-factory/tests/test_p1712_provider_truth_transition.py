from __future__ import annotations

import json
from pathlib import Path

from core.runtime.flow_os.provider_truth_transition import (
    build_provider_truth_transition_report,
    write_provider_truth_transition_report,
)


def _repo(
    repository: str,
    *,
    state: str = "HEALTHY_VERIFIED",
    blocking: bool = False,
    gaps: tuple[str, ...] = (),
) -> dict:
    return {
        "repository": repository,
        "state": state,
        "blocking": blocking,
        "canonical_status": "DRIFT_ADDED_PROVIDER" if blocking else "IN_SYNC",
        "credential_gap_providers": list(gaps),
        "source": "/tmp/source.json",
    }


def _fleet(*rows: dict, status: str = "FLEET_HEALTHY_VERIFIED", passed: bool = True) -> dict:
    repositories = list(rows)
    return {
        "version": "1.0",
        "status": status,
        "passed": passed,
        "expected_repositories": [row["repository"] for row in repositories],
        "observed_repositories": [row["repository"] for row in repositories],
        "missing_repositories": [],
        "duplicate_repositories": [],
        "blocking_repositories": [
            row["repository"] for row in repositories if row["blocking"]
        ],
        "degraded_repositories": [
            row["repository"]
            for row in repositories
            if not row["blocking"] and row["credential_gap_providers"]
        ],
        "healthy_repositories": [
            row["repository"]
            for row in repositories
            if not row["blocking"] and not row["credential_gap_providers"]
        ],
        "repositories": repositories,
        "reason": "fixture",
    }


def test_p1712_first_run_has_nonblocking_baseline_not_available() -> None:
    current = _fleet(_repo("Ngh1aa/Nova"), _repo("Ngh1aa/Lumen"))

    report = build_provider_truth_transition_report(current, None)

    assert report.baseline_available is False
    assert report.fleet_transition == "BASELINE_NOT_AVAILABLE"
    assert report.workflow_blocking is False
    assert {item.transition for item in report.repository_transitions} == {
        "BASELINE_NOT_AVAILABLE"
    }


def test_p1712_detects_new_blocker() -> None:
    baseline = _fleet(_repo("Ngh1aa/Nova"))
    current = _fleet(
        _repo(
            "Ngh1aa/Nova",
            state="ACTION_REQUIRED_CANONICAL_TRUTH",
            blocking=True,
        ),
        status="ACTION_REQUIRED_FLEET_PROVIDER_TRUTH",
        passed=False,
    )

    report = build_provider_truth_transition_report(current, baseline)

    assert report.fleet_transition == "NEW_BLOCKER"
    assert report.repository_transitions[0].transition == "NEW_BLOCKER"
    assert report.changed_repositories == ("Ngh1aa/Nova",)
    assert report.workflow_blocking is False


def test_p1712_detects_recovery() -> None:
    baseline = _fleet(
        _repo(
            "Ngh1aa/Nova",
            state="ACTION_REQUIRED_CANONICAL_TRUTH",
            blocking=True,
        ),
        status="ACTION_REQUIRED_FLEET_PROVIDER_TRUTH",
        passed=False,
    )
    current = _fleet(_repo("Ngh1aa/Nova"))

    report = build_provider_truth_transition_report(current, baseline)

    assert report.fleet_transition == "RECOVERED"
    assert report.repository_transitions[0].transition == "RECOVERED"


def test_p1712_detects_new_optional_credential_gap() -> None:
    baseline = _fleet(_repo("Ngh1aa/Nova"))
    current = _fleet(
        _repo(
            "Ngh1aa/Nova",
            state="DEGRADED_MISSING_OPTIONAL_CREDENTIALS",
            gaps=("vercel",),
        ),
        status="FLEET_HEALTHY_WITH_OPTIONAL_CREDENTIAL_GAPS",
        passed=True,
    )

    report = build_provider_truth_transition_report(current, baseline)
    item = report.repository_transitions[0]

    assert report.fleet_transition == "NEW_CREDENTIAL_GAP"
    assert item.transition == "NEW_CREDENTIAL_GAP"
    assert item.new_credential_gaps == ("vercel",)
    assert item.resolved_credential_gaps == ()


def test_p1712_detects_resolved_optional_credential_gap() -> None:
    baseline = _fleet(
        _repo(
            "Ngh1aa/Nova",
            state="DEGRADED_MISSING_OPTIONAL_CREDENTIALS",
            gaps=("vercel", "render"),
        ),
        status="FLEET_HEALTHY_WITH_OPTIONAL_CREDENTIAL_GAPS",
        passed=True,
    )
    current = _fleet(
        _repo(
            "Ngh1aa/Nova",
            state="HEALTHY_WITH_OPTIONAL_CREDENTIAL_GAPS",
            gaps=("render",),
        ),
        status="FLEET_HEALTHY_WITH_OPTIONAL_CREDENTIAL_GAPS",
        passed=True,
    )

    report = build_provider_truth_transition_report(current, baseline)
    item = report.repository_transitions[0]

    assert report.fleet_transition == "CREDENTIAL_GAP_RESOLVED"
    assert item.transition == "CREDENTIAL_GAP_RESOLVED"
    assert item.resolved_credential_gaps == ("vercel",)


def test_p1712_detects_unchanged_healthy() -> None:
    baseline = _fleet(_repo("Ngh1aa/Nova"))
    current = _fleet(_repo("Ngh1aa/Nova"))

    report = build_provider_truth_transition_report(current, baseline)

    assert report.fleet_transition == "UNCHANGED_HEALTHY"
    assert report.repository_transitions[0].transition == "UNCHANGED_HEALTHY"
    assert report.changed_repositories == ()


def test_p1712_detects_unchanged_blocking() -> None:
    baseline = _fleet(
        _repo("Ngh1aa/Nova", state="ACTION_REQUIRED_CANONICAL_TRUTH", blocking=True),
        status="ACTION_REQUIRED_FLEET_PROVIDER_TRUTH",
        passed=False,
    )
    current = _fleet(
        _repo("Ngh1aa/Nova", state="ACTION_REQUIRED_CANONICAL_TRUTH", blocking=True),
        status="ACTION_REQUIRED_FLEET_PROVIDER_TRUTH",
        passed=False,
    )

    report = build_provider_truth_transition_report(current, baseline)

    assert report.fleet_transition == "UNCHANGED_BLOCKING"
    assert report.repository_transitions[0].transition == "UNCHANGED_BLOCKING"


def test_p1712_new_registry_member_gets_repository_baseline_not_available() -> None:
    baseline = _fleet(_repo("Ngh1aa/Nova"))
    current = _fleet(_repo("Ngh1aa/Nova"), _repo("Ngh1aa/NewProject"))

    report = build_provider_truth_transition_report(current, baseline)

    by_repo = {item.repository: item for item in report.repository_transitions}
    assert by_repo["Ngh1aa/Nova"].transition == "UNCHANGED_HEALTHY"
    assert by_repo["Ngh1aa/NewProject"].transition == "BASELINE_NOT_AVAILABLE"
    assert report.current_only_repositories == ("Ngh1aa/NewProject",)


def test_p1712_writer_includes_baseline_provenance_and_never_blocks(
    tmp_path: Path,
) -> None:
    current = _fleet(_repo("Ngh1aa/Nova"))
    baseline = _fleet(_repo("Ngh1aa/Nova"))
    selection = {
        "baseline_available": True,
        "baseline_run_id": 123,
        "baseline_artifact_id": 456,
    }

    current_path = tmp_path / "current.json"
    baseline_path = tmp_path / "baseline.json"
    selection_path = tmp_path / "selection.json"
    output_path = tmp_path / "transition.json"
    for path, payload in (
        (current_path, current),
        (baseline_path, baseline),
        (selection_path, selection),
    ):
        path.write_text(json.dumps(payload), encoding="utf-8")

    report = write_provider_truth_transition_report(
        current_summary_path=current_path,
        baseline_summary_path=baseline_path,
        baseline_source_path=selection_path,
        output_path=output_path,
    )

    assert report.workflow_blocking is False
    stored = json.loads(output_path.read_text(encoding="utf-8"))
    assert stored["baseline_source"]["baseline_run_id"] == 123
    assert stored["fleet_transition"] == "UNCHANGED_HEALTHY"
