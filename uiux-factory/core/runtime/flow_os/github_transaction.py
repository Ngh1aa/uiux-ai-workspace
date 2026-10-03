from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from core.runtime.flow_os.execution_driver import (
    RUNNER_RESULT_VERSION,
    RunnerArtifact,
    RunnerContractError,
    RunnerResult,
    SegmentExecutionRequest,
)


GITHUB_TRANSACTION_VERSION = "1.0"
TRANSACTION_STATUSES = frozenset({"new", "active", "completed", "cancelled", "failed"})
READ_ONLY_PHASES = frozenset({"audit", "design", "qa"})


class GitHubTransactionError(RuntimeError):
    """Raised when the P1.7 GitHub transaction boundary is violated."""


class TransactionLeaseConflict(GitHubTransactionError):
    """Raised when another execution owns the active transaction lease."""


class BranchIsolationError(GitHubTransactionError):
    """Raised when a runner attempts to mutate outside its transaction branch."""


class TransactionCancelled(GitHubTransactionError):
    """Raised when a cancellation marker is observed before a mutation boundary."""


def _slug(value: str, *, fallback: str = "transaction") -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-._").lower()
    return cleaned[:48] or fallback


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, prefix=path.name + ".tmp."
    ) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        temp_path = Path(handle.name)
    temp_path.replace(path)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class GitHubTransactionConfig:
    repository: str
    remote_url: str
    workspace_root: Path | str
    transaction_id: str
    worker_command: list[str]
    base_branch: str = "main"
    branch_prefix: str = "uiux-factory"
    preview_command: list[str] = field(default_factory=list)
    github_api_base: str = "https://api.github.com"
    github_token: str | None = None
    pr_title: str = "UIUX Factory governed change"
    pr_body: str = "Created by UIUX Factory P1.7 governed GitHub transaction runner."
    lease_owner: str = ""
    lease_ttl_seconds: int = 1800
    author_name: str = "UIUX Factory"
    author_email: str = "uiux-factory@users.noreply.github.com"
    push_enabled: bool = True
    pr_enabled: bool = True
    extra_env: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if "/" not in self.repository.strip():
            raise ValueError("repository must be owner/name")
        if not self.remote_url.strip():
            raise ValueError("remote_url is required")
        if not self.transaction_id.strip():
            raise ValueError("transaction_id is required")
        if not self.worker_command:
            raise ValueError("worker_command is required")
        branch = self.transaction_branch
        if branch == self.base_branch or branch.endswith("/" + self.base_branch):
            raise ValueError("transaction branch must never equal the base branch")

    @property
    def transaction_branch(self) -> str:
        digest = hashlib.sha256(self.transaction_id.encode("utf-8")).hexdigest()[:10]
        return f"{_slug(self.branch_prefix, fallback='uiux-factory')}/{_slug(self.transaction_id)}-{digest}"

    @property
    def effective_lease_owner(self) -> str:
        if self.lease_owner.strip():
            return self.lease_owner.strip()
        run_id = os.environ.get("GITHUB_RUN_ID", "local")
        attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
        return f"{run_id}:{attempt}"


@dataclass
class GitHubTransactionState:
    schema_version: str
    transaction_id: str
    repository: str
    base_branch: str
    branch: str
    lease_owner: str
    status: str = "new"
    base_sha: str | None = None
    branch_claim_sha: str | None = None
    last_remote_sha: str | None = None
    last_commit_sha: str | None = None
    pr_number: int | None = None
    pr_url: str | None = None
    runner_invocations: int = 0
    segment_commits: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in TRANSACTION_STATUSES:
            raise ValueError(f"invalid transaction status: {self.status}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> GitHubTransactionState:
        return cls(
            schema_version=str(payload.get("schema_version") or GITHUB_TRANSACTION_VERSION),
            transaction_id=str(payload["transaction_id"]),
            repository=str(payload["repository"]),
            base_branch=str(payload["base_branch"]),
            branch=str(payload["branch"]),
            lease_owner=str(payload["lease_owner"]),
            status=str(payload.get("status") or "new"),
            base_sha=str(payload["base_sha"]) if payload.get("base_sha") else None,
            branch_claim_sha=str(payload["branch_claim_sha"]) if payload.get("branch_claim_sha") else None,
            last_remote_sha=str(payload["last_remote_sha"]) if payload.get("last_remote_sha") else None,
            last_commit_sha=str(payload["last_commit_sha"]) if payload.get("last_commit_sha") else None,
            pr_number=int(payload["pr_number"]) if payload.get("pr_number") is not None else None,
            pr_url=str(payload["pr_url"]) if payload.get("pr_url") else None,
            runner_invocations=int(payload.get("runner_invocations") or 0),
            segment_commits={str(k): str(v) for k, v in dict(payload.get("segment_commits") or {}).items()},
            metadata={str(k): str(v) for k, v in dict(payload.get("metadata") or {}).items()},
        )


class TransactionLease:
    """Atomic local lease with TTL; remote branch CAS provides the distributed mutation fence."""

    def __init__(self, path: Path, owner: str, ttl_seconds: int) -> None:
        self.path = path
        self.owner = owner
        self.ttl_seconds = max(30, int(ttl_seconds))

    def _payload(self) -> dict[str, Any]:
        now = time.time()
        return {"owner": self.owner, "acquired_at": now, "expires_at": now + self.ttl_seconds}

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(2):
            payload = self._payload()
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                try:
                    current = _read_json(self.path)
                except (OSError, json.JSONDecodeError, TypeError, ValueError):
                    current = {}
                current_owner = str(current.get("owner") or "")
                expires = float(current.get("expires_at") or 0)
                if current_owner == self.owner:
                    _atomic_json(self.path, payload)
                    return
                if expires <= time.time():
                    try:
                        self.path.unlink()
                    except FileNotFoundError:
                        pass
                    continue
                raise TransactionLeaseConflict(
                    f"transaction lease held by {current_owner or 'unknown'} until {expires:.0f}"
                )
            else:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(payload, handle, ensure_ascii=False, sort_keys=True)
                    handle.write("\n")
                return
        raise TransactionLeaseConflict("could not acquire transaction lease after stale-lease retry")

    def renew(self) -> None:
        self.acquire()

    def release(self) -> None:
        try:
            current = _read_json(self.path)
        except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError, ValueError):
            current = {}
        if not current or str(current.get("owner") or "") == self.owner:
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass


class GitHubRestClient:
    """Minimal GitHub REST PR client with idempotent find-or-create semantics."""

    def __init__(self, base_url: str, token: str | None, *, timeout_seconds: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout_seconds = int(timeout_seconds)

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        data = None
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "uiux-factory-p17",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(self.base_url + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:800]
            raise GitHubTransactionError(f"GitHub API {method} {path} failed: {exc.code} {detail}") from exc
        except urllib.error.URLError as exc:
            raise GitHubTransactionError(f"GitHub API {method} {path} unavailable: {exc}") from exc
        return json.loads(body) if body.strip() else None

    def find_pull_request(self, repository: str, *, head_branch: str, base_branch: str) -> dict[str, Any] | None:
        owner, _name = repository.split("/", 1)
        query = urllib.parse.urlencode({
            "head": f"{owner}:{head_branch}",
            "base": base_branch,
            "state": "all",
        })
        rows = self._request("GET", f"/repos/{repository}/pulls?{query}")
        if not isinstance(rows, list):
            raise GitHubTransactionError("GitHub pull request lookup returned a non-list payload")
        return dict(rows[0]) if rows else None

    def ensure_pull_request(
        self,
        repository: str,
        *,
        head_branch: str,
        base_branch: str,
        title: str,
        body: str,
    ) -> tuple[dict[str, Any], bool]:
        existing = self.find_pull_request(
            repository,
            head_branch=head_branch,
            base_branch=base_branch,
        )
        if existing is not None:
            return existing, False
        created = self._request(
            "POST",
            f"/repos/{repository}/pulls",
            {"title": title, "body": body, "head": head_branch, "base": base_branch},
        )
        if not isinstance(created, dict) or created.get("number") is None or not created.get("html_url"):
            raise GitHubTransactionError("GitHub pull request creation returned incomplete provenance")
        return dict(created), True


class GitHubProductionRunner:
    """P1.7 SegmentRunner that fences target mutation inside one GitHub transaction branch."""

    def __init__(self, config: GitHubTransactionConfig) -> None:
        self.config = config
        tx_slug = _slug(config.transaction_id)
        tx_hash = hashlib.sha256(config.transaction_id.encode("utf-8")).hexdigest()[:10]
        self.transaction_root = Path(config.workspace_root).resolve() / f"{tx_slug}-{tx_hash}"
        self.repo_root = self.transaction_root / "repo"
        self.exchange_dir = self.transaction_root / "exchange"
        self.evidence_dir = self.transaction_root / "evidence"
        self.state_path = self.transaction_root / "transaction-state.json"
        self.cancel_path = self.transaction_root / "CANCELLED"
        self.lease = TransactionLease(
            self.transaction_root / "transaction.lease.json",
            config.effective_lease_owner,
            config.lease_ttl_seconds,
        )
        self.api = GitHubRestClient(config.github_api_base, config.github_token)
        self.exchange_dir.mkdir(parents=True, exist_ok=True)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.state = self._load_or_create_state()

    @property
    def artifact_root(self) -> Path:
        return self.transaction_root

    def _load_or_create_state(self) -> GitHubTransactionState:
        if self.state_path.is_file():
            state = GitHubTransactionState.from_dict(_read_json(self.state_path))
            expected = {
                "transaction_id": self.config.transaction_id,
                "repository": self.config.repository,
                "base_branch": self.config.base_branch,
                "branch": self.config.transaction_branch,
            }
            actual = {
                "transaction_id": state.transaction_id,
                "repository": state.repository,
                "base_branch": state.base_branch,
                "branch": state.branch,
            }
            if actual != expected:
                raise GitHubTransactionError(f"persisted transaction state mismatch: expected {expected}, got {actual}")
            return state
        state = GitHubTransactionState(
            schema_version=GITHUB_TRANSACTION_VERSION,
            transaction_id=self.config.transaction_id,
            repository=self.config.repository,
            base_branch=self.config.base_branch,
            branch=self.config.transaction_branch,
            lease_owner=self.config.effective_lease_owner,
        )
        self._save_state(state)
        return state

    def _save_state(self, state: GitHubTransactionState | None = None) -> None:
        if state is not None:
            self.state = state
        _atomic_json(self.state_path, self.state.to_dict())

    def request_cancellation(self, reason: str = "requested") -> None:
        self.transaction_root.mkdir(parents=True, exist_ok=True)
        self.cancel_path.write_text(reason.strip() or "requested", encoding="utf-8")

    def _check_cancelled(self) -> None:
        if self.cancel_path.exists():
            self.state.status = "cancelled"
            self._save_state()
            self.lease.release()
            raise TransactionCancelled(self.cancel_path.read_text(encoding="utf-8", errors="replace")[:400])

    def _run(self, command: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            command,
            cwd=cwd or self.repo_root,
            text=True,
            capture_output=True,
            check=False,
        )
        if check and completed.returncode != 0:
            raise GitHubTransactionError(
                f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stderr.strip()[:1200]}"
            )
        return completed

    def _git(self, *args: str, check: bool = True) -> str:
        return self._run(["git", *args], cwd=self.repo_root, check=check).stdout.strip()

    def _remote_branch_sha(self) -> str | None:
        completed = self._run(
            ["git", "ls-remote", "--heads", "origin", f"refs/heads/{self.config.transaction_branch}"],
            cwd=self.repo_root,
            check=False,
        )
        if completed.returncode != 0:
            raise GitHubTransactionError(f"cannot inspect transaction branch: {completed.stderr.strip()[:800]}")
        line = completed.stdout.strip()
        return line.split()[0] if line else None

    def _base_remote_sha(self) -> str:
        completed = self._run(
            ["git", "ls-remote", "--heads", "origin", f"refs/heads/{self.config.base_branch}"],
            cwd=self.repo_root,
            check=False,
        )
        line = completed.stdout.strip()
        if completed.returncode != 0 or not line:
            raise GitHubTransactionError(f"base branch {self.config.base_branch} is not available on origin")
        return line.split()[0]

    def _assert_branch_isolation(self) -> None:
        current = self._git("branch", "--show-current")
        if current != self.config.transaction_branch:
            raise BranchIsolationError(
                f"checked out branch {current!r}; expected transaction branch {self.config.transaction_branch!r}"
            )
        if current == self.config.base_branch:
            raise BranchIsolationError("direct base-branch mutation is forbidden")

    def _configure_identity(self) -> None:
        self._git("config", "user.name", self.config.author_name)
        self._git("config", "user.email", self.config.author_email)

    def _claim_message(self) -> str:
        return (
            f"chore(uiux-factory): claim transaction {self.config.transaction_id}\n\n"
            f"UIUX-Transaction: {self.config.transaction_id}\n"
            f"UIUX-Lease-Owner: {self.config.effective_lease_owner}\n"
            f"UIUX-Base-SHA: {self.state.base_sha}\n"
        )

    def _commit_message(self, request: SegmentExecutionRequest) -> str:
        return (
            f"uiux({request.segment_id}): {request.runner_mode} implementation\n\n"
            f"UIUX-Transaction: {self.config.transaction_id}\n"
            f"UIUX-Segment: {request.segment_id}\n"
            f"UIUX-Runner-Mode: {request.runner_mode}\n"
            f"UIUX-Lease-Owner: {self.config.effective_lease_owner}\n"
            f"UIUX-Base-SHA: {self.state.base_sha}\n"
        )

    def _verify_remote_ownership(self, sha: str) -> None:
        self._git("fetch", "origin", f"refs/heads/{self.config.transaction_branch}:refs/remotes/origin/{self.config.transaction_branch}")
        message = self._git("show", "-s", "--format=%B", sha)
        tx_line = f"UIUX-Transaction: {self.config.transaction_id}"
        owner_line = f"UIUX-Lease-Owner: {self.config.effective_lease_owner}"
        if tx_line not in message:
            raise TransactionLeaseConflict("existing transaction branch belongs to a different transaction")
        if owner_line not in message:
            raise TransactionLeaseConflict("existing transaction branch is owned by a different lease owner")

    def _ensure_checkout_and_claim(self) -> None:
        self._check_cancelled()
        self.lease.acquire()
        if not (self.repo_root / ".git").is_dir():
            self.repo_root.parent.mkdir(parents=True, exist_ok=True)
            self._run(["git", "clone", "--no-tags", self.config.remote_url, str(self.repo_root)], cwd=self.transaction_root)
        self._configure_identity()
        self._git("fetch", "origin", self.config.base_branch)
        base_sha = self._base_remote_sha()
        if self.state.base_sha is None:
            self.state.base_sha = base_sha
        remote_tx_sha = self._remote_branch_sha()
        if remote_tx_sha:
            self._verify_remote_ownership(remote_tx_sha)
            self._git("checkout", "-B", self.config.transaction_branch, f"origin/{self.config.transaction_branch}")
            self.state.branch_claim_sha = self.state.branch_claim_sha or remote_tx_sha
            self.state.last_remote_sha = remote_tx_sha
        else:
            self._git("checkout", "-B", self.config.transaction_branch, f"origin/{self.config.base_branch}")
            self._git("commit", "--allow-empty", "-m", self._claim_message())
            claim_sha = self._git("rev-parse", "HEAD")
            self._check_cancelled()
            if self.config.push_enabled:
                pushed = self._run(
                    ["git", "push", "--porcelain", "origin", f"HEAD:refs/heads/{self.config.transaction_branch}"],
                    cwd=self.repo_root,
                    check=False,
                )
                if pushed.returncode != 0:
                    remote_after = self._remote_branch_sha()
                    if remote_after:
                        self._verify_remote_ownership(remote_after)
                        raise TransactionLeaseConflict("transaction branch was claimed concurrently")
                    raise GitHubTransactionError(f"failed to claim transaction branch: {pushed.stderr.strip()[:1000]}")
            self.state.branch_claim_sha = claim_sha
            self.state.last_remote_sha = claim_sha
        self.state.status = "active"
        self._assert_branch_isolation()
        self._save_state()

    def _reset_read_only_mutation(self) -> None:
        self._git("reset", "--hard", "HEAD")
        self._git("clean", "-fd")

    def _invoke_worker(self, request: SegmentExecutionRequest) -> RunnerResult:
        self.state.runner_invocations += 1
        attempt = self.state.runner_invocations
        self._save_state()
        prefix = f"{request.segment_id}-attempt-{attempt}"
        request_path = self.exchange_dir / f"{prefix}-request.json"
        result_path = self.exchange_dir / f"{prefix}-result.json"
        request_path.write_text(json.dumps(request.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        env = os.environ.copy()
        env.update(self.config.extra_env)
        env.update({
            "UIUX_EXECUTION_REQUEST": str(request_path),
            "UIUX_EXECUTION_RESULT": str(result_path),
            "UIUX_EXECUTION_SEGMENT_ID": request.segment_id,
            "UIUX_EXECUTION_MODE": request.runner_mode,
            "UIUX_TRANSACTION_ID": self.config.transaction_id,
            "UIUX_TRANSACTION_BRANCH": self.config.transaction_branch,
            "UIUX_TRANSACTION_ROOT": str(self.transaction_root),
            "UIUX_TRANSACTION_ARTIFACT_DIR": str(self.evidence_dir),
            "UIUX_TRANSACTION_ATTEMPT": str(attempt),
        })
        completed = subprocess.run(
            self.config.worker_command,
            cwd=self.repo_root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        if not result_path.is_file():
            return RunnerResult(
                schema_version=RUNNER_RESULT_VERSION,
                status="failed",
                artifacts=[],
                failure_class="RUNNER_CONTRACT_FAILED",
                reason=(
                    f"production worker exited {completed.returncode} without result contract; "
                    f"stderr={completed.stderr.strip()[:600]}"
                ),
                metadata={"returncode": str(completed.returncode)},
            )
        try:
            return RunnerResult.from_dict(json.loads(result_path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise RunnerContractError(f"invalid production worker result: {exc}") from exc

    def _preview_evidence(self, request: SegmentExecutionRequest) -> tuple[RunnerArtifact | None, RunnerResult | None]:
        if request.phase != "qa" or not self.config.preview_command:
            return None, None
        attempt = self.state.runner_invocations + 1
        completed = subprocess.run(
            self.config.preview_command,
            cwd=self.repo_root,
            env={**os.environ, **self.config.extra_env, "UIUX_TRANSACTION_BRANCH": self.config.transaction_branch},
            text=True,
            capture_output=True,
            check=False,
        )
        report = self.evidence_dir / f"{request.segment_id}-preview-{attempt}.txt"
        report.write_text(
            f"returncode={completed.returncode}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}\n",
            encoding="utf-8",
        )
        artifact = RunnerArtifact(
            id=f"{request.segment_id}-attempt-{attempt}-preview-evidence",
            kind="preview-evidence",
            artifact_class="report",
            path=str(report),
            metadata={"branch": self.config.transaction_branch, "transaction_id": self.config.transaction_id},
        )
        if completed.returncode != 0:
            return artifact, RunnerResult(
                schema_version=RUNNER_RESULT_VERSION,
                status="failed",
                artifacts=[artifact],
                failure_class="BUILD_FAILED",
                reason="preview command failed before browser QA",
            )
        return artifact, None

    def _push_commit_with_lease(self, commit_sha: str) -> None:
        self._assert_branch_isolation()
        self._check_cancelled()
        self.lease.renew()
        if not self.config.push_enabled:
            self.state.last_remote_sha = commit_sha
            self._save_state()
            return
        expected = self.state.last_remote_sha
        if not expected:
            raise GitHubTransactionError("missing expected remote SHA for branch CAS push")
        completed = self._run(
            [
                "git",
                "push",
                "--porcelain",
                f"--force-with-lease=refs/heads/{self.config.transaction_branch}:{expected}",
                "origin",
                f"HEAD:refs/heads/{self.config.transaction_branch}",
            ],
            cwd=self.repo_root,
            check=False,
        )
        if completed.returncode != 0:
            raise TransactionLeaseConflict(
                "transaction branch moved since last observed SHA; refusing to overwrite concurrent work"
            )
        self.state.last_remote_sha = commit_sha
        self._save_state()

    def _commit_implementation(self, request: SegmentExecutionRequest) -> RunnerArtifact:
        self._assert_branch_isolation()
        if not self._git("status", "--porcelain"):
            existing = self.state.segment_commits.get(f"{request.segment_id}:{request.runner_mode}")
            if existing:
                return RunnerArtifact(
                    id=f"{request.segment_id}-attempt-{self.state.runner_invocations}-implementation-artifact",
                    kind="implementation-artifact",
                    artifact_class="commit",
                    uri=f"https://github.com/{self.config.repository}/commit/{existing}",
                    metadata={
                        "commit_sha": existing,
                        "branch": self.config.transaction_branch,
                        "transaction_id": self.config.transaction_id,
                        "segment_id": request.segment_id,
                        "mode": request.runner_mode,
                        "idempotent_reuse": "true",
                    },
                )
            raise GitHubTransactionError("implementation segment passed without repository changes")
        self._check_cancelled()
        self._git("add", "-A")
        self._git("commit", "-m", self._commit_message(request))
        commit_sha = self._git("rev-parse", "HEAD")
        self._push_commit_with_lease(commit_sha)
        self.state.last_commit_sha = commit_sha
        self.state.segment_commits[f"{request.segment_id}:{request.runner_mode}"] = commit_sha
        self._save_state()
        return RunnerArtifact(
            id=f"{request.segment_id}-attempt-{self.state.runner_invocations}-implementation-artifact",
            kind="implementation-artifact",
            artifact_class="commit",
            uri=f"https://github.com/{self.config.repository}/commit/{commit_sha}",
            metadata={
                "commit_sha": commit_sha,
                "branch": self.config.transaction_branch,
                "transaction_id": self.config.transaction_id,
                "segment_id": request.segment_id,
                "mode": request.runner_mode,
                "base_sha": self.state.base_sha or "",
            },
        )

    def _pr_artifact(self, request: SegmentExecutionRequest) -> RunnerArtifact:
        if not self.config.pr_enabled:
            raise GitHubTransactionError("PR finalization is disabled for a production transaction")
        if not self.config.github_token and self.config.github_api_base.startswith("https://api.github.com"):
            raise GitHubTransactionError("GitHub token is required to create or reuse the production PR")
        pr, created = self.api.ensure_pull_request(
            self.config.repository,
            head_branch=self.config.transaction_branch,
            base_branch=self.config.base_branch,
            title=self.config.pr_title,
            body=self.config.pr_body,
        )
        number = int(pr["number"])
        url = str(pr["html_url"])
        self.state.pr_number = number
        self.state.pr_url = url
        self.state.status = "completed"
        self._save_state()
        return RunnerArtifact(
            id=f"{request.segment_id}-attempt-{self.state.runner_invocations}-pull-request",
            kind="pull-request",
            artifact_class="evidence",
            uri=url,
            metadata={
                "pr_number": str(number),
                "head_branch": self.config.transaction_branch,
                "base_branch": self.config.base_branch,
                "transaction_id": self.config.transaction_id,
                "commit_sha": self.state.last_commit_sha or self.state.last_remote_sha or "",
                "created": "true" if created else "false",
            },
        )

    def run(self, request: SegmentExecutionRequest) -> RunnerResult:
        try:
            self._check_cancelled()
            self._ensure_checkout_and_claim()
            self._assert_branch_isolation()
            before_status = self._git("status", "--porcelain")
            preview_artifact, preview_failure = self._preview_evidence(request)
            if preview_failure is not None:
                return preview_failure
            result = self._invoke_worker(request)
            self._check_cancelled()

            if request.phase in READ_ONLY_PHASES:
                after_status = self._git("status", "--porcelain")
                if after_status != before_status:
                    self._reset_read_only_mutation()
                    return RunnerResult(
                        schema_version=RUNNER_RESULT_VERSION,
                        status="failed",
                        artifacts=list(result.artifacts),
                        failure_class="UNAUTHORIZED_TARGET_MUTATION",
                        reason=f"{request.phase} worker mutated the target repository",
                    )

            artifacts = list(result.artifacts)
            if preview_artifact is not None:
                artifacts.append(preview_artifact)
            if result.status == "failed":
                return RunnerResult(
                    schema_version=result.schema_version,
                    status="failed",
                    artifacts=artifacts,
                    failure_class=result.failure_class,
                    reason=result.reason,
                    metadata={**result.metadata, "transaction_branch": self.config.transaction_branch},
                )

            if request.phase == "implementation":
                commit_artifact = self._commit_implementation(request)
                artifacts = [artifact for artifact in artifacts if artifact.kind != "implementation-artifact"]
                artifacts.append(commit_artifact)
            elif request.phase == "qa":
                if not self.state.last_commit_sha:
                    raise GitHubTransactionError("QA cannot finalize a PR before an implementation commit exists")
                pr_artifact = self._pr_artifact(request)
                artifacts.append(pr_artifact)
                self.lease.release()

            return RunnerResult(
                schema_version=result.schema_version,
                status="passed",
                artifacts=artifacts,
                metadata={
                    **result.metadata,
                    "transaction_id": self.config.transaction_id,
                    "transaction_branch": self.config.transaction_branch,
                    "base_sha": self.state.base_sha or "",
                    "last_commit_sha": self.state.last_commit_sha or "",
                    "pr_url": self.state.pr_url or "",
                },
            )
        except TransactionCancelled as exc:
            return RunnerResult(
                schema_version=RUNNER_RESULT_VERSION,
                status="failed",
                artifacts=[],
                failure_class="TRANSACTION_CANCELLED",
                reason=str(exc) or "transaction cancelled",
            )
        except TransactionLeaseConflict as exc:
            return RunnerResult(
                schema_version=RUNNER_RESULT_VERSION,
                status="failed",
                artifacts=[],
                failure_class="TRANSACTION_LEASE_CONFLICT",
                reason=str(exc),
            )
        except BranchIsolationError as exc:
            self.state.status = "failed"
            self._save_state()
            return RunnerResult(
                schema_version=RUNNER_RESULT_VERSION,
                status="failed",
                artifacts=[],
                failure_class="BRANCH_ISOLATION_FAILED",
                reason=str(exc),
            )
        except (GitHubTransactionError, RunnerContractError, OSError, subprocess.SubprocessError) as exc:
            self.state.status = "failed"
            self._save_state()
            return RunnerResult(
                schema_version=RUNNER_RESULT_VERSION,
                status="failed",
                artifacts=[],
                failure_class="GITHUB_TRANSACTION_FAILED",
                reason=str(exc),
            )
