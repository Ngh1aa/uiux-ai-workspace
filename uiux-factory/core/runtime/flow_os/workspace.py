from __future__ import annotations

import os
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


class WorkspaceIsolationError(RuntimeError):
    """Raised when a writable run cannot be isolated in a trusted git worktree."""


@dataclass(frozen=True)
class WorkspaceMetadata:
    source_root: str
    workspace_root: str
    branch: str
    base_commit: str
    run_id: str
    isolation: str = "git_worktree"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class WorktreeManager:
    """Create branch-scoped writable worktrees without mutating the source checkout.

    The manager is intentionally fail-closed: writable isolation requires a real,
    clean git repository whose top-level directory is exactly ``source_root``.
    Existing branch names or ambiguous worktree paths are never silently reused.
    Canonical runtime checkpoint state under `.uiux-agent-runs/` is ignored by the
    cleanliness check because the harness creates it before the first writable action.
    """

    def __init__(self, source_root: Path, worktrees_root: Path | None = None) -> None:
        self.source_root = Path(source_root).resolve()
        self.worktrees_root = (
            Path(worktrees_root).resolve()
            if worktrees_root is not None
            else (self.source_root.parent / ".uiux-worktrees" / self.source_root.name).resolve()
        )

    @staticmethod
    def _safe_run_id(run_id: str) -> str:
        value = str(run_id).strip()
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", value):
            raise WorkspaceIsolationError("run_id is not safe for a worktree/branch name")
        return value

    def _git(self, args: list[str], cwd: Path | None = None, timeout: int = 60) -> str:
        env = {
            key: value
            for key, value in os.environ.items()
            if key in {"PATH", "SYSTEMROOT", "WINDIR", "HOME", "USERPROFILE", "TMP", "TEMP", "LANG", "LC_ALL"}
        }
        result = subprocess.run(
            ["git", *args],
            cwd=cwd or self.source_root,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            shell=False,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()[-4000:]
            raise WorkspaceIsolationError(f"git {' '.join(args)} failed ({result.returncode}): {detail}")
        return result.stdout.strip()

    @staticmethod
    def _meaningful_status_lines(status: str) -> list[str]:
        meaningful: list[str] = []
        for line in status.splitlines():
            if not line.strip():
                continue
            path = line[3:] if len(line) > 3 else ""
            if path == ".uiux-agent-runs" or path.startswith(".uiux-agent-runs/"):
                continue
            meaningful.append(line)
        return meaningful

    def validate_source(self) -> str:
        if not self.source_root.is_dir():
            raise WorkspaceIsolationError(f"source root is not a directory: {self.source_root}")
        top = Path(self._git(["rev-parse", "--show-toplevel"])).resolve()
        if top != self.source_root:
            raise WorkspaceIsolationError(
                f"writable isolation requires the git top-level directory as project root: {top} != {self.source_root}"
            )
        status = self._git(["status", "--porcelain", "--untracked-files=normal"])
        meaningful = self._meaningful_status_lines(status)
        if meaningful:
            preview = "; ".join(meaningful[:8])
            raise WorkspaceIsolationError(
                "source checkout has uncommitted or untracked project changes; commit/stash them before isolated writes "
                f"so the worktree cannot silently omit local project truth ({preview})"
            )
        return self._git(["rev-parse", "HEAD"])

    def _workspace_path(self, run_id: str) -> Path:
        return (self.worktrees_root / self._safe_run_id(run_id)).resolve()

    def _branch_name(self, run_id: str) -> str:
        return f"uiux-agent/{self._safe_run_id(run_id)}"

    def ensure(self, run_id: str) -> WorkspaceMetadata:
        base_commit = self.validate_source()
        safe_id = self._safe_run_id(run_id)
        branch = self._branch_name(safe_id)
        workspace = self._workspace_path(safe_id)
        self.worktrees_root.mkdir(parents=True, exist_ok=True)

        if workspace.exists():
            if not workspace.is_dir():
                raise WorkspaceIsolationError(f"worktree path is not a directory: {workspace}")
            top = Path(self._git(["rev-parse", "--show-toplevel"], cwd=workspace)).resolve()
            if top != workspace:
                raise WorkspaceIsolationError(f"existing workspace is not the expected git worktree: {workspace}")
            current_branch = self._git(["branch", "--show-current"], cwd=workspace)
            if current_branch != branch:
                raise WorkspaceIsolationError(
                    f"existing worktree branch mismatch: expected {branch}, found {current_branch or '(detached)'}"
                )
            return WorkspaceMetadata(
                source_root=str(self.source_root),
                workspace_root=str(workspace),
                branch=branch,
                base_commit=base_commit,
                run_id=safe_id,
            )

        branch_probe = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
            cwd=self.source_root,
            capture_output=True,
            text=True,
            timeout=30,
            shell=False,
        )
        if branch_probe.returncode == 0:
            raise WorkspaceIsolationError(
                f"isolated branch already exists without its expected worktree: {branch}; manual cleanup is required"
            )
        if branch_probe.returncode not in {0, 1}:
            raise WorkspaceIsolationError("failed to determine isolated branch state")

        self._git(["worktree", "add", "-b", branch, str(workspace), base_commit], timeout=120)
        top = Path(self._git(["rev-parse", "--show-toplevel"], cwd=workspace)).resolve()
        if top != workspace:
            raise WorkspaceIsolationError("created worktree did not resolve to its own top-level directory")
        return WorkspaceMetadata(
            source_root=str(self.source_root),
            workspace_root=str(workspace),
            branch=branch,
            base_commit=base_commit,
            run_id=safe_id,
        )

    def validate_metadata(self, payload: dict[str, Any], expected_run_id: str | None = None) -> WorkspaceMetadata:
        metadata = WorkspaceMetadata(**dict(payload))
        if Path(metadata.source_root).resolve() != self.source_root:
            raise WorkspaceIsolationError("workspace metadata source_root does not match the active harness")
        if expected_run_id is not None and metadata.run_id != self._safe_run_id(expected_run_id):
            raise WorkspaceIsolationError("workspace metadata run_id does not match the active managed run")
        expected = self._workspace_path(metadata.run_id)
        if Path(metadata.workspace_root).resolve() != expected:
            raise WorkspaceIsolationError("workspace metadata path is outside the canonical worktree root")
        if metadata.branch != self._branch_name(metadata.run_id):
            raise WorkspaceIsolationError("workspace metadata branch is not canonical")
        if not expected.is_dir():
            raise WorkspaceIsolationError("recorded worktree no longer exists")
        top = Path(self._git(["rev-parse", "--show-toplevel"], cwd=expected)).resolve()
        if top != expected:
            raise WorkspaceIsolationError("recorded workspace is no longer an isolated git worktree")
        current_branch = self._git(["branch", "--show-current"], cwd=expected)
        if current_branch != metadata.branch:
            raise WorkspaceIsolationError("recorded workspace branch no longer matches checkpoint metadata")
        return metadata
