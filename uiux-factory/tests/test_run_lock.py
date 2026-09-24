import json
import os
import time
from pathlib import Path

import pytest

from core.runtime.run_lock import RunLock, RunLockTimeout


def test_run_lock_blocks_second_owner_until_release(tmp_path: Path) -> None:
    first = RunLock(tmp_path, timeout_seconds=0.1, poll_seconds=0.01)
    first.acquire()

    second = RunLock(tmp_path, timeout_seconds=0.03, poll_seconds=0.01)
    with pytest.raises(RunLockTimeout):
        second.acquire()

    first.release()
    second.acquire()
    assert second.acquired is True
    second.release()


def test_run_lock_persists_owner_metadata(tmp_path: Path) -> None:
    lock = RunLock(tmp_path, timeout_seconds=0.1)
    lock.acquire()

    owner = json.loads(lock.owner_path.read_text(encoding="utf-8"))
    assert owner["token"] == lock.token
    assert owner["pid"] == os.getpid()

    lock.release()
    assert not lock.lock_dir.exists()


def test_run_lock_reclaims_stale_directory(tmp_path: Path) -> None:
    stale = tmp_path / ".runtime" / "active-run.lock"
    stale.mkdir(parents=True)
    (stale / "owner.json").write_text('{"pid": 123}', encoding="utf-8")

    old = time.time() - 30
    os.utime(stale, (old, old))

    lock = RunLock(
        tmp_path,
        timeout_seconds=0.1,
        stale_seconds=1,
        poll_seconds=0.01,
    )
    lock.acquire()
    assert lock.acquired is True
    assert json.loads(lock.owner_path.read_text(encoding="utf-8"))["token"] == lock.token
    lock.release()
