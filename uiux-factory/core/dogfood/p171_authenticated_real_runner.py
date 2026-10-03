from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.runtime.flow_os.github_transaction import GitHubTransactionConfig


P171_REPORT_VERSION = "1.0"
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
SKILLS_ROOT = WORKSPACE_ROOT / "skills_UIUX"
WORKER_SCRIPT = SKILLS_ROOT / "scripts" / "p171-authenticated-real-runner-worker.py"


@dataclass(frozen=True)
class AuthenticatedDogfoodProfile:
    id: str
    repository: str
    base_branch: str
    goal: str
    pr_title: str
    pr_body: str
    expected_changed_files: tuple[str, ...]
    target_truth: dict[str, str]


DOGFOOD_PROFILES: dict[str, AuthenticatedDogfoodProfile] = {
    "luxroom-cart-total-live-region": AuthenticatedDogfoodProfile(
        id="luxroom-cart-total-live-region",
        repository="Ngh1aa/LuxRoom",
        base_branch="main",
        goal=(
            "Audit the LuxRoom cart accessibility, redesign the dynamic cart total feedback while preserving "
            "the existing visual styling and motion, implement it, and QA it."
        ),
        pr_title="P1.7.1 dogfood: announce cart total updates",
        pr_body=(
            "## P1.7.1 authenticated real-runner dogfood\n\n"
            "This PR was created by `GitHubProductionRunner` through the authenticated Actions boundary. "
            "It is intentionally **PR-only**: do not merge or deploy it as part of this dogfood.\n\n"
            "### Payload\n"
            "Add polite, atomic live-region semantics to the dynamic cart total so assistive technology can "
            "announce total changes without changing LuxRoom visual styling, motion, checkout behavior, or release state.\n\n"
            "### Boundary\n"
            "- transaction branch only\n"
            "- target-owned `npm run qa` before PR finalization\n"
            "- no merge\n"
            "- no deploy/release\n"
        ),
        expected_changed_files=("cart.html",),
        target_truth={"domain": "commerce-retail", "product_archetype": "checkout-commerce"},
    ),
}


def _run(command: list[str], *, cwd: Path | None = None) -> str:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stderr.strip()[:1000]}"
        )
    return completed.stdout.strip()


def _remote_sha(remote_url: str, branch: str) -> str:
    output = _run(["git", "ls-remote", "--heads", remote_url, f"refs/heads/{branch}"])
    if not output:
        raise RuntimeError(f"remote branch is missing: {branch}")
    return output.split()[0]


def _changed_files(repo_root: Path, base_sha: str, head_sha: str) -> list[str]:
    output = _run(["git", "diff", "--name-only", f"{base_sha}..{head_sha}"], cwd=repo_root)
    return [line.strip() for line in output.splitlines() if line.strip()]


def _copy_evidence(runner, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for source, destination in (
        (runner.state_path, output_dir / "transaction-state.json"),
        (runner.transaction_root / "execution-checkpoint.json", output_dir / "execution-checkpoint.json"),
    ):
        if source.is_file():
            shutil.copy2(source, destination)
    for source_dir, name in ((runner.evidence_dir, "evidence"), (runner.exchange_dir, "exchange")):
        if source_dir.is_dir():
            shutil.copytree(source_dir, output_dir / name, dirs_exist_ok=True)


def run_authenticated_dogfood(
    *,
    profile_id: str,
    transaction_id: str,
    github_token: str,
    workspace_root: Path | str,
    output_dir: Path | str,
) -> dict[str, Any]:
    if profile_id not in DOGFOOD_PROFILES:
        raise ValueError(f"unknown or non-opted-in P1.7.1 profile: {profile_id}")
    if not github_token.strip():
        raise ValueError("authenticated P1.7.1 dogfood requires a GitHub token")
    if not WORKER_SCRIPT.is_file():
        raise FileNotFoundError(f"P1.7.1 worker missing: {WORKER_SCRIPT}")

    profile = DOGFOOD_PROFILES[profile_id]
    remote_url = f"https://github.com/{profile.repository}.git"
    config = GitHubTransactionConfig(
        repository=profile.repository,
        remote_url=remote_url,
        workspace_root=Path(workspace_root),
        transaction_id=transaction_id,
        worker_command=["python", str(WORKER_SCRIPT)],
        base_branch=profile.base_branch,
        github_token=github_token,
        pr_title=profile.pr_title,
        pr_body=profile.pr_body,
        lease_owner=f"p171:{transaction_id}",
        preview_command=["npm", "run", "qa"],
        push_enabled=True,
        pr_enabled=True,
        extra_env={"UIUX_P171_PROFILE": profile_id},
    )

    factory = ProfessionalWebsiteFlow(SKILLS_ROOT)
    routing_profile, driver, runner = factory.resolve_github_execution_driver(
        profile.goal,
        config,
        target_truth=profile.target_truth,
        max_repair_attempts=1,
    )
    completion_status = driver.run_until_blocked(max_steps=10)

    base_sha_after = _remote_sha(remote_url, profile.base_branch)
    changed_files: list[str] = []
    if runner.state.base_sha and runner.state.last_commit_sha:
        changed_files = _changed_files(runner.repo_root, runner.state.base_sha, runner.state.last_commit_sha)

    pr = None
    if runner.state.pr_number is not None:
        pr = runner.api.find_pull_request(
            profile.repository,
            head_branch=config.transaction_branch,
            base_branch=profile.base_branch,
        )
    pr_state = str(pr.get("state")) if isinstance(pr, dict) and pr.get("state") else None

    expected_files = list(profile.expected_changed_files)
    passed = all(
        [
            routing_profile.routing_status == "resolved",
            completion_status == "completed",
            runner.state.status == "completed",
            bool(runner.state.last_commit_sha),
            bool(runner.state.pr_number),
            bool(runner.state.pr_url),
            pr_state == "open",
            runner.state.base_sha == base_sha_after,
            changed_files == expected_files,
            config.transaction_branch != profile.base_branch,
        ]
    )

    report: dict[str, Any] = {
        "version": P171_REPORT_VERSION,
        "passed": passed,
        "profile": asdict(profile),
        "routing_status": routing_profile.routing_status,
        "completion_status": completion_status,
        "transaction": runner.state.to_dict(),
        "transaction_branch": config.transaction_branch,
        "base_sha_after": base_sha_after,
        "main_unchanged": runner.state.base_sha == base_sha_after,
        "changed_files": changed_files,
        "expected_changed_files": expected_files,
        "pr_state": pr_state,
        "pr_url": runner.state.pr_url,
        "runner_history": driver.history,
        "visual_qa": "NOT_RUN",
        "deployment": "OUT_OF_SCOPE",
        "merge": "OUT_OF_SCOPE",
    }

    output_path = Path(output_dir)
    _copy_evidence(runner, output_path)
    (output_path / "p171-authenticated-real-runner-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if not passed:
        raise RuntimeError(f"P1.7.1 authenticated dogfood did not satisfy acceptance: {json.dumps(report, ensure_ascii=False)}")
    return report
