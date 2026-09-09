import os
import sys
import threading
from pathlib import Path

import pytest

from apps.bridge.job_runtime import (
    BoundedJobExecutor,
    JobStore,
    QueueFullError,
    run_process_streaming,
)


def test_job_store_survives_new_instance(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    created = store.create(
        {
            "id": "abcdef123456",
            "status": "queued",
            "prompt": "hello",
            "created_at": 1.0,
        }
    )
    assert created["status"] == "queued"

    store.update("abcdef123456", status="running", started_at=2.0)
    store.append_output("abcdef123456", "line one\n")
    store.append_output("abcdef123456", "line two\n")

    recovered = JobStore(tmp_path).snapshot("abcdef123456")
    assert recovered is not None
    assert recovered["status"] == "running"
    assert recovered["started_at"] == 2.0
    assert recovered["output_tail"].endswith("line one\nline two\n")


def test_job_store_rejects_invalid_job_id(tmp_path: Path) -> None:
    store = JobStore(tmp_path)
    with pytest.raises(ValueError):
        store.create({"id": "../../escape", "status": "queued"})


def test_bounded_executor_rejects_work_beyond_capacity() -> None:
    executor = BoundedJobExecutor(max_workers=1, max_queue=1)
    release = threading.Event()

    def blocking_job() -> None:
        release.wait(timeout=2)

    first = executor.submit(blocking_job)
    second = executor.submit(blocking_job)

    with pytest.raises(QueueFullError):
        executor.submit(blocking_job)

    release.set()
    first.result(timeout=2)
    second.result(timeout=2)
    executor.shutdown()


def test_streaming_process_timeout_returns_and_captures_output(tmp_path: Path) -> None:
    output: list[str] = []
    result = run_process_streaming(
        [
            sys.executable,
            "-c",
            "import time; print('started', flush=True); time.sleep(5)",
        ],
        cwd=tmp_path,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
        timeout_seconds=0.2,
        on_output=output.append,
    )

    assert result.timed_out is True
    assert result.return_code != 0
    joined = "".join(output)
    assert "started" in joined
    assert "[TIMEOUT]" in joined
