from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from core.runtime.flow_os.agent import LocalCheckpointStore
from core.runtime.flow_os.resilience import (
    CheckpointRecoveryManager,
    RecoveryError,
    WorkspaceRollbackManager,
)
from core.runtime.flow_os.workspace import WorktreeManager


def _git_project(root: Path) -> Path:
    project = root / "project"
    project.mkdir()
    (project / "README.md").write_text("# Fixture\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=project, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "ci@example.com"], cwd=project, check=True)
    subprocess.run(["git", "config", "user.name", "CI"], cwd=project, check=True)
    subprocess.run(["git", "add", "README.md"], cwd=project, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=project, check=True, capture_output=True)
    return project


def test_a17_snapshot_restore_is_explicit_and_hash_verified(tmp_path: Path) -> None:
    project = _git_project(tmp_path)
    store = LocalCheckpointStore(project / ".uiux-agent-runs")
    original = {
        "run_id": "run-1",
        "state": "READY",
        "task": "fixture",
        "context": {"marker": "safe"},
    }
    store.save("run-1", original)
    recovery = CheckpointRecoveryManager(project)
    snapshot = recovery.snapshot("run-1", "before-write")

    mutated = {**original, "state": "FAILED", "context": {"marker": "mutated"}}
    store.save("run-1", mutated)
    restored = recovery.restore("run-1", "before-write")

    assert restored.checkpoint_sha256 == snapshot.checkpoint_sha256
    assert store.load("run-1") == original


def test_a17_tampered_snapshot_fails_closed(tmp_path: Path) -> None:
    project = _git_project(tmp_path)
    store = LocalCheckpointStore(project / ".uiux-agent-runs")
    store.save(
        "run-2",
        {"run_id": "run-2", "state": "READY", "task": "fixture", "context": {}},
    )
    recovery = CheckpointRecoveryManager(project)
    snapshot = recovery.snapshot("run-2", "safe")
    path = Path(snapshot.path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["checkpoint"]["state"] = "COMPLETED"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RecoveryError, match="hash mismatch"):
        recovery.restore("run-2", "safe")


def test_a17_rollback_discards_only_isolated_worktree(tmp_path: Path) -> None:
    project = _git_project(tmp_path)
    manager = WorktreeManager(project)
    metadata = manager.ensure("run-3")
    workspace = Path(metadata.workspace_root)
    (workspace / "changed.txt").write_text("discard me\n", encoding="utf-8")
    source_head_before = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    result = WorkspaceRollbackManager(project).rollback(
        metadata.to_dict(),
        expected_run_id="run-3",
    )
    source_head_after = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    assert result.workspace_removed is True
    assert result.branch_removed is True
    assert result.source_unchanged is True
    assert source_head_before == source_head_after
    assert not (project / "changed.txt").exists()


def test_a17_rollback_rejects_metadata_for_another_run(tmp_path: Path) -> None:
    project = _git_project(tmp_path)
    metadata = WorktreeManager(project).ensure("run-4")
    with pytest.raises(Exception, match="run_id"):
        WorkspaceRollbackManager(project).rollback(
            metadata.to_dict(),
            expected_run_id="other-run",
        )
