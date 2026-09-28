from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from core.runtime.flow_os.agent import LocalCheckpointStore
from core.runtime.flow_os.workspace import WorkspaceMetadata, WorktreeManager


_LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")


class RecoveryError(RuntimeError):
    """Raised when an explicit recovery/rollback invariant is not satisfied."""


@dataclass(frozen=True)
class RecoverySnapshot:
    run_id: str
    label: str
    path: str
    checkpoint_sha256: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class WorkspaceRollbackResult:
    run_id: str
    workspace_root: str
    branch: str
    source_head_before: str
    source_head_after: str
    workspace_removed: bool
    branch_removed: bool
    source_unchanged: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CheckpointRecoveryManager:
    """Explicit, hash-verified recovery snapshots for local Flow checkpoints.

    Snapshots are local recovery points, not distributed durability. Restoring is
    always explicit so FAILED/BLOCKED stages are never silently retried.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        if not self.project_root.is_dir():
            raise RecoveryError(f"project root does not exist: {self.project_root}")
        self.store = LocalCheckpointStore(self.project_root / ".uiux-agent-runs")

    @staticmethod
    def _label(value: str) -> str:
        label = str(value).strip()
        if not _LABEL_RE.fullmatch(label):
            raise RecoveryError(
                "recovery label must match [A-Za-z0-9][A-Za-z0-9._-]{0,95}"
            )
        return label

    def _snapshot_path(self, run_id: str, label: str) -> Path:
        safe_label = self._label(label)
        checkpoints_root = (self.project_root / ".uiux-agent-runs").resolve()
        root = (checkpoints_root / str(run_id) / "recovery").resolve()
        if not root.is_relative_to(checkpoints_root):
            raise RecoveryError("recovery path escaped checkpoint root")
        root.mkdir(parents=True, exist_ok=True)
        return root / f"{safe_label}.json"

    @staticmethod
    def _hash_checkpoint(checkpoint: dict[str, Any]) -> str:
        encoded = json.dumps(
            checkpoint,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        os.replace(tmp, path)

    def snapshot(self, run_id: str, label: str) -> RecoverySnapshot:
        checkpoint = self.store.load(str(run_id))
        if str(checkpoint.get("run_id", "")) != str(run_id):
            raise RecoveryError("checkpoint run_id mismatch")
        digest = self._hash_checkpoint(checkpoint)
        path = self._snapshot_path(str(run_id), label)
        document = {
            "schema_version": 1,
            "run_id": str(run_id),
            "label": self._label(label),
            "checkpoint_sha256": digest,
            "checkpoint": checkpoint,
            "truth_boundary": (
                "Local explicit recovery snapshot only; not distributed durability and "
                "not permission to retry, merge, deploy or release."
            ),
        }
        self._atomic_write(path, document)
        return RecoverySnapshot(str(run_id), self._label(label), str(path), digest)

    def restore(self, run_id: str, label: str) -> RecoverySnapshot:
        path = self._snapshot_path(str(run_id), label)
        if not path.is_file():
            raise RecoveryError(f"recovery snapshot not found: {label}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RecoveryError("recovery snapshot must be a JSON object")
        if payload.get("schema_version") != 1:
            raise RecoveryError("unsupported recovery snapshot schema")
        if str(payload.get("run_id", "")) != str(run_id):
            raise RecoveryError("recovery snapshot run_id mismatch")
        checkpoint = payload.get("checkpoint")
        if not isinstance(checkpoint, dict):
            raise RecoveryError("recovery snapshot missing checkpoint object")
        if str(checkpoint.get("run_id", "")) != str(run_id):
            raise RecoveryError("snapshot checkpoint run_id mismatch")
        digest = self._hash_checkpoint(checkpoint)
        if digest != str(payload.get("checkpoint_sha256", "")):
            raise RecoveryError("recovery snapshot hash mismatch")
        self.store.save(str(run_id), checkpoint)
        return RecoverySnapshot(str(run_id), self._label(label), str(path), digest)


class WorkspaceRollbackManager:
    """Discard one validated isolated worktree without mutating the source checkout."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.worktrees = WorktreeManager(self.project_root)

    def rollback(
        self,
        raw_metadata: dict[str, Any],
        *,
        expected_run_id: str,
    ) -> WorkspaceRollbackResult:
        metadata: WorkspaceMetadata = self.worktrees.validate_metadata(
            raw_metadata,
            expected_run_id=str(expected_run_id),
        )
        before = self.worktrees._git(["rev-parse", "HEAD"])
        workspace = Path(metadata.workspace_root)

        if workspace.exists():
            self.worktrees._git(
                ["worktree", "remove", "--force", str(workspace)],
                timeout=120,
            )

        if self.worktrees._git(["branch", "--list", metadata.branch]).strip():
            self.worktrees._git(["branch", "-D", metadata.branch])
        self.worktrees._git(["worktree", "prune"])

        after = self.worktrees._git(["rev-parse", "HEAD"])
        if before != after:
            raise RecoveryError("source checkout HEAD changed during isolated rollback")
        return WorkspaceRollbackResult(
            run_id=metadata.run_id,
            workspace_root=metadata.workspace_root,
            branch=metadata.branch,
            source_head_before=before,
            source_head_after=after,
            workspace_removed=not workspace.exists(),
            branch_removed=not bool(
                self.worktrees._git(["branch", "--list", metadata.branch]).strip()
            ),
            source_unchanged=True,
        )


class RunRecoveryController:
    """Explicit fail-safe recovery: rollback isolated writes, then restore a checkpoint."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.checkpoints = CheckpointRecoveryManager(self.project_root)
        self.workspaces = WorkspaceRollbackManager(self.project_root)

    def recover(
        self,
        run_id: str,
        label: str,
        *,
        rollback_workspace: bool = True,
    ) -> dict[str, Any]:
        current = self.checkpoints.store.load(str(run_id))
        raw_context = current.get("context", {})
        raw_workspace = raw_context.get("workspace") if isinstance(raw_context, dict) else None
        rollback: dict[str, Any] | None = None
        if rollback_workspace and isinstance(raw_workspace, dict):
            rollback = self.workspaces.rollback(
                raw_workspace,
                expected_run_id=str(run_id),
            ).to_dict()
        snapshot = self.checkpoints.restore(str(run_id), label)
        return {
            "run_id": str(run_id),
            "restored_snapshot": snapshot.to_dict(),
            "workspace_rollback": rollback,
            "truth_boundary": (
                "Recovery is explicit and local. It discards only a validated isolated "
                "workspace and restores a hash-verified checkpoint; it never performs "
                "merge, deploy or release."
            ),
        }
