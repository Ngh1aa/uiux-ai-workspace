from __future__ import annotations

import json
import os
import shutil
import time
import uuid
from pathlib import Path


class RunLockTimeout(TimeoutError):
    """Raised when the local Factory run slot cannot be acquired in time."""


class RunLock:
    """Cross-process local run lock based on atomic directory creation.

    UIUX Factory is currently a local-first application whose pipeline can spawn
    Playwright, MetaGPT and model-provider work at the same time. Serializing the
    expensive pipeline keeps repeated Workbench submissions from exhausting a
    developer laptop while the bridge queue is still intentionally lightweight.

    A lock directory is created atomically. If a process crashes, an old lock can
    be reclaimed after ``stale_seconds``. Ownership is tokenized so one process
    never removes a lock that has already been replaced by another process.
    """

    def __init__(
        self,
        root: Path,
        *,
        timeout_seconds: float = 7200.0,
        stale_seconds: float = 14400.0,
        poll_seconds: float = 0.25,
    ) -> None:
        self.root = Path(root).resolve()
        self.timeout_seconds = max(0.0, float(timeout_seconds))
        self.stale_seconds = max(1.0, float(stale_seconds))
        self.poll_seconds = max(0.01, float(poll_seconds))
        self.lock_dir = self.root / ".runtime" / "active-run.lock"
        self.owner_path = self.lock_dir / "owner.json"
        self.token = uuid.uuid4().hex
        self.acquired = False

    def _owner_payload(self) -> dict[str, object]:
        return {
            "token": self.token,
            "pid": os.getpid(),
            "created_at": time.time(),
        }

    def _write_owner(self) -> None:
        self.owner_path.write_text(
            json.dumps(self._owner_payload(), indent=2),
            encoding="utf-8",
        )

    def _read_owner(self) -> dict[str, object]:
        try:
            data = json.loads(self.owner_path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError, TypeError):
            return {}

    def _is_stale(self) -> bool:
        try:
            age = time.time() - self.lock_dir.stat().st_mtime
        except FileNotFoundError:
            return False
        return age >= self.stale_seconds

    def _reclaim_stale_lock(self) -> None:
        if not self._is_stale():
            return

        stale_dir = self.lock_dir.with_name(
            f"active-run.stale-{uuid.uuid4().hex[:10]}"
        )
        try:
            self.lock_dir.rename(stale_dir)
        except FileNotFoundError:
            return
        except OSError:
            return
        shutil.rmtree(stale_dir, ignore_errors=True)

    def acquire(self) -> None:
        deadline = time.monotonic() + self.timeout_seconds
        self.lock_dir.parent.mkdir(parents=True, exist_ok=True)

        while True:
            try:
                self.lock_dir.mkdir()
                try:
                    self._write_owner()
                except Exception:
                    shutil.rmtree(self.lock_dir, ignore_errors=True)
                    raise
                self.acquired = True
                return
            except FileExistsError:
                self._reclaim_stale_lock()

            if time.monotonic() >= deadline:
                owner = self._read_owner()
                pid = owner.get("pid", "unknown")
                raise RunLockTimeout(
                    f"Timed out waiting for the local UIUX Factory run slot; "
                    f"current owner pid={pid}."
                )

            time.sleep(self.poll_seconds)

    def release(self) -> None:
        if not self.acquired:
            return

        owner = self._read_owner()
        if owner.get("token") == self.token:
            shutil.rmtree(self.lock_dir, ignore_errors=True)
        self.acquired = False

    def __enter__(self) -> "RunLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()
