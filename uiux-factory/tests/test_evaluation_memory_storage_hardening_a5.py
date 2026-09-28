from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from core.evaluation.run_evaluator import RunEvaluation
from core.memory.evaluation_memory import EvaluationMemoryError, EvaluationMemoryStore


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir(parents=True)
    _git(root, "init")
    _git(root, "config", "user.email", "a5-storage@example.test")
    _git(root, "config", "user.name", "A5 Storage Test")
    (root / "app.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "fixture")
    return root.resolve()


def _record() -> RunEvaluation:
    return RunEvaluation(
        schema_version=1,
        run_id="storage-hardening",
        flow_id="micro-ui-change",
        flow_revision=0,
        managed_state="COMPLETED",
        outcome="passed",
        evaluated_at="2026-09-28T00:00:00+00:00",
        signature={"change_surface": "MICRO"},
        effective_evidence_count=1,
        status_counts={"PASS": 1},
        evidence_type_counts={"validator_result": 1},
        passing_evidence_types=["validator_result"],
        memory_eligible=True,
    )


def test_a5_memory_rejects_malformed_schema_version_as_memory_error(tmp_path: Path) -> None:
    project = _repo(tmp_path)
    memory_dir = project / ".uiux-agent-runs" / "memory"
    memory_dir.mkdir(parents=True)
    (memory_dir / "evaluation-memory.json").write_text(
        json.dumps({"schema_version": "not-a-number", "records": []}),
        encoding="utf-8",
    )
    store = EvaluationMemoryStore(project, {"evaluation_memory": {"enabled": True}})

    with pytest.raises(EvaluationMemoryError, match="schema version is malformed"):
        store.load()


def test_a5_memory_rejects_symlinked_transaction_lock_directory(tmp_path: Path) -> None:
    project = _repo(tmp_path)
    memory_dir = project / ".uiux-agent-runs" / "memory"
    memory_dir.mkdir(parents=True)
    outside = tmp_path / "outside-lock"
    outside.mkdir()
    os.symlink(outside, memory_dir / ".runtime", target_is_directory=True)
    store = EvaluationMemoryStore(project, {"evaluation_memory": {"enabled": True}})

    with pytest.raises(EvaluationMemoryError, match="lock directory must not be a symlink"):
        store.record(_record())
