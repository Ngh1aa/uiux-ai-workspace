#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SKILLS = WORKSPACE / "skills_UIUX"
TEST_WORKER = ROOT / "tests" / "fixtures" / "p17_github_worker.py"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.runtime.flow_os.github_transaction import GitHubTransactionConfig


GOAL = "Audit the landing page, redesign checkout, implement it, and QA it."


def run(command: list[str], *, cwd: Path | None = None) -> str:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stdout}\n{completed.stderr}"
        )
    return completed.stdout.strip()


def remote_sha(remote: Path, branch: str) -> str | None:
    completed = subprocess.run(
        ["git", "--git-dir", str(remote), "rev-parse", f"refs/heads/{branch}"],
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Produce P1.7 GitHub transaction evidence using real git + PR REST boundary.")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)

    state: dict[str, object] = {"prs": [], "create_count": 0}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, _format: str, *_args) -> None:
            return

        def respond(self, status: int, payload: object) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path != "/repos/example/product/pulls":
                self.respond(404, {"message": "not found"})
                return
            query = parse_qs(parsed.query)
            head = query.get("head", [""])[0]
            base = query.get("base", [""])[0]
            rows = [
                pr for pr in state["prs"]
                if pr["head"]["label"] == head and pr["base"]["ref"] == base
            ]
            self.respond(200, rows)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(size).decode("utf-8")) if size else {}
            if parsed.path != "/repos/example/product/pulls":
                self.respond(404, {"message": "not found"})
                return
            state["create_count"] = int(state["create_count"]) + 1
            number = len(state["prs"]) + 1
            pr = {
                "number": number,
                "html_url": f"https://github.test/example/product/pull/{number}",
                "head": {"label": f"example:{payload['head']}", "ref": payload["head"]},
                "base": {"ref": payload["base"]},
                "title": payload["title"],
            }
            state["prs"].append(pr)
            self.respond(201, pr)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        with tempfile.TemporaryDirectory(prefix="uiux-p17-") as temp:
            temp_root = Path(temp)
            seed = temp_root / "seed"
            seed.mkdir()
            run(["git", "init", "-b", "main"], cwd=seed)
            run(["git", "config", "user.email", "fixture@example.com"], cwd=seed)
            run(["git", "config", "user.name", "P17 Evidence"], cwd=seed)
            (seed / "index.html").write_text("<main><h1>P1.7</h1></main>\n", encoding="utf-8")
            run(["git", "add", "index.html"], cwd=seed)
            run(["git", "commit", "-m", "fixture base"], cwd=seed)
            base_sha = run(["git", "rev-parse", "HEAD"], cwd=seed)

            remote = temp_root / "origin.git"
            run(["git", "init", "--bare", str(remote)])
            run(["git", "remote", "add", "origin", str(remote)], cwd=seed)
            run(["git", "push", "-u", "origin", "main"], cwd=seed)
            run(["git", "--git-dir", str(remote), "symbolic-ref", "HEAD", "refs/heads/main"])

            config = GitHubTransactionConfig(
                repository="example/product",
                remote_url=str(remote),
                workspace_root=temp_root / "transactions",
                transaction_id="p17-evidence",
                worker_command=[sys.executable, str(TEST_WORKER)],
                github_api_base=f"http://127.0.0.1:{server.server_port}",
                github_token="fixture-token",
                lease_owner="evidence-run",
                preview_command=[sys.executable, "-c", "print('preview-ready')"],
                extra_env={"P17_FAIL_QA_ONCE": "1"},
                pr_title="P1.7 evidence transaction",
            )
            factory = ProfessionalWebsiteFlow(SKILLS)
            profile, driver, runner = factory.resolve_github_execution_driver(GOAL, config)
            completion = driver.run_until_blocked(max_steps=12)
            branch_sha = remote_sha(remote, runner.config.transaction_branch)
            main_sha = remote_sha(remote, "main")
            commit_message = run([
                "git", "--git-dir", str(remote), "show", "-s", "--format=%B", str(branch_sha),
            ]) if branch_sha else ""
            pr_records = [record for record in driver.registry.records.values() if record.kind == "pull-request"]
            commit_records = [
                record for record in driver.registry.records.values() if record.kind == "implementation-artifact"
            ]
            report = {
                "version": GITHUB_TRANSACTION_VERSION,
                "passed": completion == "completed" and main_sha == base_sha and int(state["create_count"]) == 1,
                "completion_status": completion,
                "routing_status": profile.routing_status,
                "transaction_status": runner.state.status,
                "transaction_id": runner.config.transaction_id,
                "transaction_branch": runner.config.transaction_branch,
                "base_sha": base_sha,
                "main_sha_after": main_sha,
                "main_unchanged": main_sha == base_sha,
                "branch_sha": branch_sha,
                "last_commit_sha": runner.state.last_commit_sha,
                "runner_invocations": runner.state.runner_invocations,
                "pr_number": runner.state.pr_number,
                "pr_url": runner.state.pr_url,
                "pr_create_count": state["create_count"],
                "pr_artifacts": [record.to_dict() for record in pr_records],
                "commit_artifacts": [record.to_dict() for record in commit_records],
                "commit_provenance": {
                    "has_transaction": "UIUX-Transaction: p17-evidence" in commit_message,
                    "has_repair_segment": "UIUX-Segment: work-3" in commit_message,
                    "has_repair_mode": "UIUX-Runner-Mode: repair" in commit_message,
                    "has_lease_owner": "UIUX-Lease-Owner: evidence-run" in commit_message,
                },
                "history": driver.history,
            }
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["passed"] else 1
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


if __name__ == "__main__":
    from core.runtime.flow_os.github_transaction import GITHUB_TRANSACTION_VERSION

    raise SystemExit(main())
