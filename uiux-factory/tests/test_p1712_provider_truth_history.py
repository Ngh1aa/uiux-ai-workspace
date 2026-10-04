from __future__ import annotations

from core.runtime.flow_os.provider_truth_history import select_previous_fleet_artifact


def test_p1712_history_selects_newest_previous_produced_fleet_artifact() -> None:
    runs = [
        {"id": 30, "status": "in_progress", "event": "schedule", "created_at": "2026-10-04T01:17:00Z"},
        {"id": 29, "status": "completed", "event": "schedule", "created_at": "2026-10-03T01:17:00Z", "conclusion": "failure"},
        {"id": 28, "status": "completed", "event": "schedule", "created_at": "2026-10-02T01:17:00Z", "conclusion": "success"},
    ]
    artifacts = {
        29: [{"id": 901, "name": "p1711-provider-truth-fleet-summary", "expired": False}],
        28: [{"id": 801, "name": "p1711-provider-truth-fleet-summary", "expired": False}],
    }

    selection = select_previous_fleet_artifact(
        current_run_id=30,
        runs=runs,
        artifacts_by_run=artifacts,
    )

    assert selection.baseline_available is True
    assert selection.baseline_run_id == 29
    assert selection.baseline_artifact_id == 901
    assert selection.baseline_event == "schedule"


def test_p1712_history_accepts_previous_manual_baseline() -> None:
    runs = [
        {"id": 100, "status": "completed", "event": "workflow_dispatch", "created_at": "2026-10-03T12:00:00Z"},
    ]
    artifacts = {
        100: [{"id": 44, "name": "p1711-provider-truth-fleet-summary", "expired": False}],
    }

    selection = select_previous_fleet_artifact(
        current_run_id=101,
        runs=runs,
        artifacts_by_run=artifacts,
    )

    assert selection.baseline_available is True
    assert selection.baseline_run_id == 100
    assert selection.baseline_event == "workflow_dispatch"


def test_p1712_history_skips_current_nonmonitor_and_expired_artifacts() -> None:
    runs = [
        {"id": 50, "status": "completed", "event": "schedule"},
        {"id": 49, "status": "completed", "event": "pull_request"},
        {"id": 48, "status": "completed", "event": "schedule"},
    ]
    artifacts = {
        50: [{"id": 1, "name": "p1711-provider-truth-fleet-summary", "expired": False}],
        49: [{"id": 2, "name": "p1711-provider-truth-fleet-summary", "expired": False}],
        48: [{"id": 3, "name": "p1711-provider-truth-fleet-summary", "expired": True}],
    }

    selection = select_previous_fleet_artifact(
        current_run_id=50,
        runs=runs,
        artifacts_by_run=artifacts,
    )

    assert selection.baseline_available is False
    assert selection.baseline_run_id is None
    assert "first-run" in selection.reason


def test_p1712_history_first_run_is_explicit_nonerror_state() -> None:
    selection = select_previous_fleet_artifact(
        current_run_id=1,
        runs=[],
        artifacts_by_run={},
    )

    assert selection.baseline_available is False
    assert selection.baseline_artifact_id is None
