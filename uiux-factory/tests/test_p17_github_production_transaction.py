from __future__ import annotations

import json
import subprocess
import sys
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.runtime.flow_os.github_transaction import (
    GitHubProductionRunner,
    GitHubRestClient,
    GitHubTransactionConfig,
)


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SKILLS = WORKSPACE / "skills_UIUX"
WORKER = Path(__file__).resolve().parent / "fixtures" / "p17_github_worker.py"
GOAL = "Audit the landing page, redesign checkout, implement it, and QA it."


def _run(command: list[str], *, cwd: Path | None = None) -> str:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise AssertionError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stdout}\n{completed.stderr}"
        )
    return completed.stdout.strip()


def _init_remote(tmp_path: Path) -> tuple[Path, str]:
    seed = tmp_path / "seed"
    seed.mkdir()
    _run(["git", "init", "-b", "main"], cwd=seed)
    _run(["git", "config", "user.email", "fixture@example.com"], cwd=seed)
    _run(["git", "config", "user.name", "P17 Fixture"], cwd=seed)
    (seed / "index.html").write_text("<main><h1>Fixture</h1></main>\n", encoding="utf-8")
    _run(["git", "add", "index.html"], cwd=seed)
    _run(["git", "commit", "-m", "fixture base"], cwd=seed)
    base_sha = _run(["git", "rev-parse", "HEAD"], cwd=seed)

    remote = tmp_path / "origin.git"
    _run(["git", "init", "--bare", str(remote)])
    _run(["git", "remote", "add", "origin", str(remote)], cwd=seed)
    _run(["git", "push", "-u", "origin", "main"], cwd=seed)
    _run(["git", "--git-dir", str(remote), "symbolic-ref", "HEAD", "refs/heads/main"])
    return remote, base_sha


def _remote_sha(remote: Path, branch: str) -> str | None:
    completed = subprocess.run(
        ["git", "--git-dir", str(remote), "rev-parse", f"refs/heads/{branch}"],
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


@contextmanager
def _fake_github_api():
    state: dict[str, object] = {"prs": [], "create_count": 0, "requests": []}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, _format: str, *_args) -> None:  # pragma: no cover - silence fixture server
            return

        def _json(self, status: int, payload: object) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            state["requests"].append({"method": "GET", "path": parsed.path, "query": parsed.query})
            if parsed.path != "/repos/example/product/pulls":
                self._json(404, {"message": "not found"})
                return
            query = parse_qs(parsed.query)
            head = query.get("head", [""])[0]
            base = query.get("base", [""])[0]
            rows = [
                pr for pr in state["prs"]
                if pr["head"]["label"] == head and pr["base"]["ref"] == base
            ]
            self._json(200, rows)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(size).decode("utf-8")) if size else {}
            state["requests"].append({"method": "POST", "path": parsed.path, "payload": payload})
            if parsed.path != "/repos/example/product/pulls":
                self._json(404, {"message": "not found"})
                return
            state["create_count"] = int(state["create_count"]) + 1
            number = len(state["prs"]) + 1
            pr = {
                "number": number,
                "html_url": f"https://github.test/example/product/pull/{number}",
                "state": "open",
                "head": {"label": f"example:{payload['head']}", "ref": payload["head"]},
                "base": {"ref": payload["base"]},
                "title": payload["title"],
                "body": payload.get("body", ""),
            }
            state["prs"].append(pr)
            self._json(201, pr)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", state
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def _config(
    tmp_path: Path,
    remote: Path,
    api_base: str,
    *,
    transaction_id: str = "p17-checkout-repair",
    lease_owner: str = "run-1",
    fail_qa_once: bool = False,
    mutate_audit: bool = False,
    preview_command: list[str] | None = None,
) -> GitHubTransactionConfig:
    return GitHubTransactionConfig(
        repository="example/product",
        remote_url=str(remote),
        workspace_root=tmp_path / "transactions",
        transaction_id=transaction_id,
        worker_command=[sys.executable, str(WORKER)],
        base_branch="main",
        github_api_base=api_base,
        github_token="fixture-token",
        pr_title="P1.7 fixture change",
        pr_body="Governed transaction fixture",
        lease_owner=lease_owner,
        preview_command=preview_command or [sys.executable, "-c", "print('preview-ready')"],
        extra_env={
            "P17_FAIL_QA_ONCE": "1" if fail_qa_once else "0",
            "P17_MUTATE_AUDIT": "1" if mutate_audit else "0",
        },
    )


def _build_driver(tmp_path: Path, remote: Path, api_base: str, **config_kwargs):
    factory = ProfessionalWebsiteFlow(SKILLS)
    config = _config(tmp_path, remote, api_base, **config_kwargs)
    profile, driver, runner = factory.resolve_github_execution_driver(GOAL, config)
    return factory, profile, driver, runner


def test_p17_real_git_transaction_runs_repair_and_opens_pr_without_moving_main(tmp_path: Path) -> None:
    remote, base_sha = _init_remote(tmp_path)
    with _fake_github_api() as (api_base, api_state):
        _factory, profile, driver, runner = _build_driver(
            tmp_path,
            remote,
            api_base,
            fail_qa_once=True,
        )
        assert profile.routing_status == "resolved"
        assert driver.run_until_blocked(max_steps=12) == "completed"

        assert _remote_sha(remote, "main") == base_sha
        transaction_sha = _remote_sha(remote, runner.config.transaction_branch)
        assert transaction_sha
        assert transaction_sha != base_sha
        assert runner.config.transaction_branch != "main"
        assert runner.state.status == "completed"
        assert runner.state.pr_number == 1
        assert runner.state.pr_url == "https://github.test/example/product/pull/1"
        assert api_state["create_count"] == 1

        nodes = {node.segment_id: node for node in driver.execution_plan.nodes}
        assert nodes["work-1"].attempts == 1
        assert nodes["work-2"].attempts == 1
        assert nodes["work-3"].attempts == 2
        assert nodes["work-4"].attempts == 2
        failure = next(event for event in driver.history if event.get("failure_class") == "PRODUCT_QA_FAILED")
        assert failure["repair_owner_segment_id"] == "work-3"

        pr_records = [record for record in driver.registry.records.values() if record.kind == "pull-request"]
        assert len(pr_records) == 1
        assert pr_records[0].accepted_for_handoff is True
        assert pr_records[0].metadata["head_branch"] == runner.config.transaction_branch
        assert pr_records[0].metadata["base_branch"] == "main"
        assert pr_records[0].metadata["commit_sha"] == runner.state.last_commit_sha

        commits = [record for record in driver.registry.records.values() if record.kind == "implementation-artifact"]
        assert len(commits) == 2
        superseded = [record for record in commits if record.metadata.get("superseded") == "true"]
        active = [record for record in commits if record.accepted_for_handoff]
        assert len(superseded) == 1
        assert len(active) == 1
        assert active[0].metadata["mode"] == "repair"

        message = _run([
            "git", "--git-dir", str(remote), "show", "-s", "--format=%B", transaction_sha,
        ])
        assert "UIUX-Transaction: p17-checkout-repair" in message
        assert "UIUX-Segment: work-3" in message
        assert "UIUX-Runner-Mode: repair" in message
        assert "UIUX-Lease-Owner: run-1" in message

        checkpoint = runner.transaction_root / "execution-checkpoint.json"
        assert checkpoint.is_file()
        transaction_state = json.loads(runner.state_path.read_text(encoding="utf-8"))
        assert transaction_state["base_sha"] == base_sha
        assert transaction_state["last_commit_sha"] == active[0].metadata["commit_sha"]


def test_p17_pull_request_find_or_create_is_idempotent(tmp_path: Path) -> None:
    _remote, _base_sha = _init_remote(tmp_path)
    with _fake_github_api() as (api_base, state):
        client = GitHubRestClient(api_base, "fixture-token")
        first, created_first = client.ensure_pull_request(
            "example/product",
            head_branch="uiux-factory/idempotent",
            base_branch="main",
            title="Idempotent PR",
            body="fixture",
        )
        second, created_second = client.ensure_pull_request(
            "example/product",
            head_branch="uiux-factory/idempotent",
            base_branch="main",
            title="Idempotent PR",
            body="fixture",
        )
        assert first["number"] == second["number"] == 1
        assert created_first is True
        assert created_second is False
        assert state["create_count"] == 1


def test_p17_active_lease_blocks_concurrent_owner(tmp_path: Path) -> None:
    remote, _base_sha = _init_remote(tmp_path)
    with _fake_github_api() as (api_base, _state):
        _factory, _profile, first_driver, first_runner = _build_driver(
            tmp_path, remote, api_base, transaction_id="lease-case", lease_owner="run-a"
        )
        assert first_driver.run_next()["status"] == "passed"
        assert first_runner.state.status == "active"

        _factory2, _profile2, second_driver, _second_runner = _build_driver(
            tmp_path, remote, api_base, transaction_id="lease-case", lease_owner="run-b"
        )
        event = second_driver.run_next()
        assert event is not None
        assert event["status"] == "failed"
        assert event["failure_class"] == "TRANSACTION_LEASE_CONFLICT"
        assert _remote_sha(remote, "main") is not None


def test_p17_cancellation_stops_before_branch_claim_or_target_mutation(tmp_path: Path) -> None:
    remote, base_sha = _init_remote(tmp_path)
    with _fake_github_api() as (api_base, state):
        _factory, _profile, driver, runner = _build_driver(
            tmp_path, remote, api_base, transaction_id="cancel-case", lease_owner="run-cancel"
        )
        runner.request_cancellation("user cancelled")
        event = driver.run_next()
        assert event is not None
        assert event["status"] == "failed"
        assert event["failure_class"] == "TRANSACTION_CANCELLED"
        assert runner.state.status == "cancelled"
        assert _remote_sha(remote, "main") == base_sha
        assert _remote_sha(remote, runner.config.transaction_branch) is None
        assert state["create_count"] == 0


def test_p17_read_only_phase_mutation_is_reverted_and_never_pushed(tmp_path: Path) -> None:
    remote, base_sha = _init_remote(tmp_path)
    with _fake_github_api() as (api_base, state):
        _factory, _profile, driver, runner = _build_driver(
            tmp_path,
            remote,
            api_base,
            transaction_id="readonly-guard",
            mutate_audit=True,
        )
        event = driver.run_next()
        assert event is not None
        assert event["status"] == "failed"
        assert event["failure_class"] == "UNAUTHORIZED_TARGET_MUTATION"
        assert _remote_sha(remote, "main") == base_sha
        branch_sha = _remote_sha(remote, runner.config.transaction_branch)
        assert branch_sha == runner.state.branch_claim_sha
        tree_content = _run([
            "git", "--git-dir", str(remote), "show", f"{branch_sha}:index.html",
        ])
        assert "Fixture" in tree_content
        assert "unauthorized" not in tree_content
        assert state["create_count"] == 0


def test_p17_preview_failure_blocks_browser_qa_and_pr(tmp_path: Path) -> None:
    remote, base_sha = _init_remote(tmp_path)
    with _fake_github_api() as (api_base, state):
        _factory, _profile, driver, runner = _build_driver(
            tmp_path,
            remote,
            api_base,
            transaction_id="preview-failure",
            preview_command=[sys.executable, "-c", "raise SystemExit(7)"],
        )
        driver.run_next()
        driver.run_next()
        driver.run_next()
        event = driver.run_next()
        assert event is not None
        assert event["status"] == "failed"
        assert event["failure_class"] == "BUILD_FAILED"
        assert state["create_count"] == 0
        assert runner.state.pr_number is None
        assert _remote_sha(remote, "main") == base_sha
        preview_records = [record for record in driver.registry.records.values() if record.kind == "preview-evidence"]
        assert len(preview_records) == 1
        assert preview_records[0].accepted_for_handoff is False


def test_p17_remote_branch_ownership_fence_rejects_external_takeover(tmp_path: Path) -> None:
    remote, base_sha = _init_remote(tmp_path)
    with _fake_github_api() as (api_base, state):
        _factory, _profile, driver, runner = _build_driver(
            tmp_path, remote, api_base, transaction_id="ownership-fence", lease_owner="run-owner"
        )
        driver.run_next()
        driver.run_next()
        driver.run_next()
        assert runner.state.last_commit_sha

        intruder = tmp_path / "intruder"
        _run(["git", "clone", str(remote), str(intruder)])
        _run(["git", "checkout", runner.config.transaction_branch], cwd=intruder)
        _run(["git", "config", "user.email", "intruder@example.com"], cwd=intruder)
        _run(["git", "config", "user.name", "Intruder"], cwd=intruder)
        with (intruder / "index.html").open("a", encoding="utf-8") as handle:
            handle.write("<!-- external takeover -->\n")
        _run(["git", "add", "index.html"], cwd=intruder)
        _run(["git", "commit", "-m", "external takeover"], cwd=intruder)
        _run(["git", "push", "origin", runner.config.transaction_branch], cwd=intruder)

        event = driver.run_next()
        assert event is not None
        assert event["status"] == "failed"
        assert event["failure_class"] == "TRANSACTION_LEASE_CONFLICT"
        assert state["create_count"] == 0
        assert _remote_sha(remote, "main") == base_sha


def test_p17_config_cannot_resolve_transaction_branch_to_base_branch(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        GitHubTransactionConfig(
            repository="example/product",
            remote_url=str(tmp_path / "origin.git"),
            workspace_root=tmp_path,
            transaction_id="main",
            worker_command=[sys.executable, str(WORKER)],
            base_branch="uiux-factory/main-0d6e4079e3",
            branch_prefix="uiux-factory",
        )
