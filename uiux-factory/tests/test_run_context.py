import json
from pathlib import Path
from unittest.mock import patch

import pytest

from core.runtime.run_context import RunContext


def test_run_context_persists_valid_state_atomically(tmp_path: Path) -> None:
    context = RunContext(root=tmp_path, goal="Create a landing page", run_id="test-run")

    with patch("core.runtime.run_context.os.replace", wraps=__import__("os").replace) as replace_mock:
        context.initialize()
        context.start_stage("research")
        artifact = context.run_dir / "research.md"
        artifact.write_text("research", encoding="utf-8")
        context.add_artifact("research", artifact)
        context.complete_stage("research")
        context.complete()

    state = json.loads(context.state_path.read_text(encoding="utf-8"))

    assert state["status"] == "completed"
    assert state["active_stage"] is None
    assert state["completed_stages"] == ["research"]
    assert state["artifacts"]["research"] == str(artifact.resolve())
    assert replace_mock.call_count >= 1
    assert list(context.run_dir.glob(".*.tmp")) == []


def test_initialize_rejects_existing_run_id(tmp_path: Path) -> None:
    first = RunContext(root=tmp_path, goal="first", run_id="same-run")
    first.initialize()

    second = RunContext(root=tmp_path, goal="second", run_id="same-run")

    with pytest.raises(FileExistsError):
        second.initialize()


def test_error_marks_run_failed(tmp_path: Path) -> None:
    context = RunContext(root=tmp_path, goal="test", run_id="failed-run")
    context.initialize()

    context.add_error(ValueError("bad input"))

    state = json.loads(context.state_path.read_text(encoding="utf-8"))
    assert state["status"] == "failed"
    assert state["errors"] == ["ValueError: bad input"]
