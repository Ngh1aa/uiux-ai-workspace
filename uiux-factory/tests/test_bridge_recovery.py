import json
from pathlib import Path

from apps.bridge import server
from apps.bridge.job_runtime import JobStore


def _install_temp_store(monkeypatch, tmp_path: Path) -> JobStore:
    store = JobStore(tmp_path)
    monkeypatch.setattr(server, "RUNS", tmp_path)
    monkeypatch.setattr(server, "STORE", store)
    return store


def test_reconcile_marks_completed_run_completed_after_restart(
    monkeypatch,
    tmp_path: Path,
) -> None:
    store = _install_temp_store(monkeypatch, tmp_path)
    job_id = "abcdef123456"
    store.create(
        {
            "id": job_id,
            "status": "running",
            "prompt": "hello",
            "created_at": 1.0,
        }
    )
    (tmp_path / job_id / "run.json").write_text(
        json.dumps(
            {
                "run_id": job_id,
                "status": "completed",
                "active_stage": None,
                "completed_stages": ["research"],
                "artifacts": {},
                "errors": [],
            }
        ),
        encoding="utf-8",
    )

    server.reconcile_interrupted_jobs()

    recovered = store.snapshot(job_id)
    assert recovered is not None
    assert recovered["status"] == "completed"
    assert recovered["recovered_after_restart"] is True


def test_reconcile_marks_unfinished_job_failed_instead_of_running_forever(
    monkeypatch,
    tmp_path: Path,
) -> None:
    store = _install_temp_store(monkeypatch, tmp_path)
    job_id = "123456abcdef"
    store.create(
        {
            "id": job_id,
            "status": "queued",
            "prompt": "hello",
            "created_at": 1.0,
        }
    )

    server.reconcile_interrupted_jobs()

    recovered = store.snapshot(job_id)
    assert recovered is not None
    assert recovered["status"] == "failed"
    assert recovered["recovered_after_restart"] is True
    assert "Bridge restarted" in recovered["error"]


def test_artifact_allowlist_rejects_path_traversal() -> None:
    assert server.is_allowed_artifact_name("design-system.json") is True
    assert (
        server.is_allowed_artifact_name(
            "references/reference-abcdef123456-desktop.png"
        )
        is True
    )
    assert server.is_allowed_artifact_name("../../.env.local") is False
    assert server.is_allowed_artifact_name("references/../run.json") is False
