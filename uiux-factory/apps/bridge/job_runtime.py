from __future__ import annotations

import json
import os
import queue
import re
import signal
import subprocess
import threading
import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


JOB_ID_RE = re.compile(r"[a-f0-9]{12}")


def validate_job_id(job_id: str) -> str:
    if not JOB_ID_RE.fullmatch(job_id):
        raise ValueError("Invalid job id")
    return job_id


def atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


class JobStore:
    """Small disk-backed job store for the local Workbench bridge."""

    def __init__(self, runs_root: Path, *, output_tail_chars: int = 16000) -> None:
        self.runs_root = Path(runs_root).resolve()
        self.output_tail_chars = max(1000, int(output_tail_chars))
        self._lock = threading.RLock()

    def run_dir(self, job_id: str) -> Path:
        return self.runs_root / validate_job_id(job_id)

    def state_path(self, job_id: str) -> Path:
        return self.run_dir(job_id) / "job.json"

    def log_path(self, job_id: str) -> Path:
        return self.run_dir(job_id) / "job.log"

    def create(self, job: dict) -> dict:
        job_id = validate_job_id(str(job.get("id", "")))
        with self._lock:
            path = self.state_path(job_id)
            if path.exists():
                raise FileExistsError(f"Job already exists: {job_id}")
            payload = dict(job)
            payload.pop("output_tail", None)
            atomic_write_json(path, payload)
        return self.snapshot(job_id)

    def load(self, job_id: str) -> dict | None:
        path = self.state_path(job_id)
        if not path.is_file():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return None
        return payload if isinstance(payload, dict) else None

    def update(self, job_id: str, **values) -> dict | None:
        validate_job_id(job_id)
        with self._lock:
            current = self.load(job_id)
            if current is None:
                return None
            current.update(values)
            current.pop("output_tail", None)
            atomic_write_json(self.state_path(job_id), current)
        return self.snapshot(job_id)

    def append_output(self, job_id: str, text: str) -> None:
        if not text:
            return
        path = self.log_path(job_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            with path.open("a", encoding="utf-8") as stream:
                stream.write(text)

    def output_tail(self, job_id: str) -> str:
        path = self.log_path(job_id)
        if not path.is_file():
            return ""
        try:
            with path.open("rb") as stream:
                stream.seek(0, os.SEEK_END)
                size = stream.tell()
                # UTF-8 can use multiple bytes per character. Reading a bounded
                # multiple keeps payloads small while avoiding whole-log reads.
                read_bytes = min(size, self.output_tail_chars * 4)
                stream.seek(-read_bytes, os.SEEK_END)
                raw = stream.read()
            text = raw.decode("utf-8", errors="replace")
            return text[-self.output_tail_chars :]
        except OSError:
            return ""

    def snapshot(self, job_id: str) -> dict | None:
        payload = self.load(job_id)
        if payload is None:
            return None
        payload["output_tail"] = self.output_tail(job_id)
        return payload

    def iter_jobs(self) -> list[dict]:
        if not self.runs_root.is_dir():
            return []
        jobs: list[dict] = []
        for run_dir in self.runs_root.iterdir():
            if not run_dir.is_dir() or not JOB_ID_RE.fullmatch(run_dir.name):
                continue
            payload = self.load(run_dir.name)
            if payload:
                jobs.append(payload)
        return jobs


class QueueFullError(RuntimeError):
    pass


class BoundedJobExecutor:
    """ThreadPoolExecutor with a hard cap on running + waiting jobs."""

    def __init__(self, *, max_workers: int = 1, max_queue: int = 8) -> None:
        self.max_workers = max(1, int(max_workers))
        self.max_queue = max(0, int(max_queue))
        self.capacity = self.max_workers + self.max_queue
        self._slots = threading.BoundedSemaphore(self.capacity)
        self._executor = ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="uiux-job",
        )

    def submit(self, fn: Callable, /, *args, **kwargs) -> Future:
        if not self._slots.acquire(blocking=False):
            raise QueueFullError(
                f"Bridge job queue is full ({self.capacity} running/waiting jobs)."
            )

        try:
            future = self._executor.submit(fn, *args, **kwargs)
        except Exception:
            self._slots.release()
            raise

        future.add_done_callback(lambda _future: self._slots.release())
        return future

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)


@dataclass(frozen=True)
class ProcessResult:
    return_code: int
    timed_out: bool


def _terminate_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return

    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
    except (OSError, ProcessLookupError):
        pass

    try:
        process.wait(timeout=5)
        return
    except subprocess.TimeoutExpired:
        pass

    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except (OSError, ProcessLookupError):
        pass


def run_process_streaming(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout_seconds: float,
    on_output: Callable[[str], None],
) -> ProcessResult:
    """Run a child process with live output and a hard wall-clock timeout."""

    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        env=env,
        start_new_session=(os.name == "posix"),
    )
    assert process.stdout is not None

    output_queue: queue.Queue[str | None] = queue.Queue()

    def reader() -> None:
        try:
            for line in process.stdout:
                output_queue.put(line)
        finally:
            output_queue.put(None)

    reader_thread = threading.Thread(
        target=reader,
        name=f"uiux-output-{process.pid}",
        daemon=True,
    )
    reader_thread.start()

    deadline = time.monotonic() + max(0.1, float(timeout_seconds))
    timed_out = False
    reader_finished = False

    while not reader_finished:
        remaining = deadline - time.monotonic()
        if remaining <= 0 and process.poll() is None:
            timed_out = True
            on_output("\n[TIMEOUT] Factory process exceeded its configured limit.\n")
            _terminate_process(process)

        try:
            item = output_queue.get(timeout=min(0.25, max(0.01, remaining)))
        except queue.Empty:
            if process.poll() is not None and not reader_thread.is_alive():
                break
            continue

        if item is None:
            reader_finished = True
        else:
            on_output(item)

    if timed_out:
        _terminate_process(process)

    try:
        return_code = process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        _terminate_process(process)
        return_code = process.wait(timeout=5)

    return ProcessResult(return_code=return_code, timed_out=timed_out)
