from __future__ import annotations

from pathlib import Path

import pytest

from core.events.run_session_log import RunSessionLog
from core.runtime.run_context import RunContext


def test_run_session_log_append_projection_and_replay(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"
    log = RunSessionLog(path, "run-a")
    log.append("run.created", data={"runtime_preset": "visual-first"})
    log.append("stage.started", stage="research")
    log.append(
        "artifact.registered",
        data={"name": "research", "path": "/tmp/research.md"},
    )
    log.append("stage.completed", stage="research")
    log.append("run.completed")

    assert log.seq == 5
    assert log.event_at(1).type == "run.created"
    assert [event.seq for event in log.snapshot()] == [1, 2, 3, 4, 5]

    replayed: list[str] = []
    log.replay(lambda event: replayed.append(event.type))
    assert replayed == [
        "run.created",
        "stage.started",
        "artifact.registered",
        "stage.completed",
        "run.completed",
    ]

    state = log.project_run_state()
    assert state["status"] == "completed"
    assert state["runtime_preset"] == "visual-first"
    assert state["completed_stages"] == ["research"]
    assert state["artifacts"]["research"] == "/tmp/research.md"


def test_run_session_log_fork_preserves_lineage(tmp_path: Path) -> None:
    source = RunSessionLog(tmp_path / "source.jsonl", "source")
    source.append("run.created", data={"runtime_preset": "standard"})
    source.append("stage.started", stage="research")
    source.append("stage.completed", stage="research")

    child = source.fork(
        tmp_path / "child.jsonl",
        "child",
        boundary=2,
    )
    events = child.snapshot()
    assert [event.type for event in events] == [
        "run.created",
        "stage.started",
        "session.forked",
    ]
    assert events[0].data["inherited_from"] == {"run_id": "source", "seq": 1}
    assert events[-1].data["inherited_event_count"] == 2


def test_run_session_log_rejects_non_contiguous_existing_file(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text(
        '{"seq":2,"type":"x","run_id":"r","timestamp":"now","stage":null,"agent":null,"data":{}}\n',
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="Non-contiguous"):
        RunSessionLog(path, "r")


def test_run_context_lifecycle_projects_from_events(tmp_path: Path) -> None:
    root = tmp_path / "factory"
    context = RunContext(root=root, goal="Test", runtime_preset="research-heavy")
    context.run_id = "run-context"
    context.initialize()

    artifact = context.run_dir / "artifact.txt"
    artifact.write_text("ok", encoding="utf-8")
    context.start_stage("research")
    context.add_artifact("artifact", artifact)
    context.complete_stage("research")
    context.complete()

    projected = context.projected_state()
    assert projected["status"] == "completed"
    assert projected["runtime_preset"] == "research-heavy"
    assert projected["completed_stages"] == ["research"]
    assert projected["artifacts"]["artifact"] == str(artifact.resolve())
    assert context.to_dict()["runtime_preset"] == "research-heavy"
