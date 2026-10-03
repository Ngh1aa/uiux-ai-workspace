from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from core.dogfood.p171_authenticated_real_runner import DOGFOOD_PROFILES, run_authenticated_dogfood
from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SKILLS = WORKSPACE / "skills_UIUX"
WORKER = SKILLS / "scripts" / "p171-authenticated-real-runner-worker.py"
WORKFLOW = WORKSPACE / ".github" / "workflows" / "p171-authenticated-real-runner-dogfood.yml"
PROFILE_ID = "luxroom-cart-total-live-region"
OLD_SNIPPET = '<strong id="cart-total">$0</strong>'
NEW_SNIPPET = '<strong id="cart-total" aria-live="polite" aria-atomic="true">$0</strong>'


def _cart_source(snippet: str = OLD_SNIPPET) -> str:
    return f"<!doctype html><title>LuxRoom | Your selection</title><aside>{snippet}</aside>\n"


def _run_worker(tmp_path: Path, phase: str, expected: list[str], *, profile: str = PROFILE_ID):
    request = {
        "segment_id": f"work-{phase}",
        "phase": phase,
        "runner_mode": "normal",
        "active_stage_id": "implementation" if phase == "implementation" else phase,
        "expected_output_kinds": expected,
    }
    request_path = tmp_path / "request.json"
    result_path = tmp_path / "result.json"
    artifact_dir = tmp_path / "artifacts"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    env = {
        **os.environ,
        "UIUX_EXECUTION_REQUEST": str(request_path),
        "UIUX_EXECUTION_RESULT": str(result_path),
        "UIUX_TRANSACTION_ARTIFACT_DIR": str(artifact_dir),
        "UIUX_TRANSACTION_ATTEMPT": "1",
        "UIUX_EXECUTION_SEGMENT_ID": request["segment_id"],
        "UIUX_EXECUTION_MODE": "normal",
        "UIUX_TRANSACTION_ID": "p171-test",
        "UIUX_TRANSACTION_BRANCH": "uiux-factory/p171-test",
        "UIUX_P171_PROFILE": profile,
    }
    completed = subprocess.run(
        [sys.executable, str(WORKER)],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(result_path.read_text(encoding="utf-8"))


def test_p171_profile_is_explicitly_opted_in_and_pr_only() -> None:
    assert set(DOGFOOD_PROFILES) == {PROFILE_ID}
    profile = DOGFOOD_PROFILES[PROFILE_ID]
    assert profile.repository == "Ngh1aa/LuxRoom"
    assert profile.base_branch == "main"
    assert profile.expected_changed_files == ("cart.html",)
    assert "PR-only" in profile.pr_body
    assert "do not merge" in profile.pr_body
    assert "no deploy/release" in profile.pr_body


def test_p171_goal_resolves_as_sequence_without_ambiguity() -> None:
    profile = DOGFOOD_PROFILES[PROFILE_ID]
    factory = ProfessionalWebsiteFlow(SKILLS)
    contract = factory.resolve_contract(profile.goal, target_truth=profile.target_truth)
    assert contract.routing_mode == "sequence"
    assert contract.profile.routing_status == "resolved"
    assert [segment.lifecycle_phase for segment in contract.segments] == ["audit", "design", "implementation", "qa"]


def test_p171_worker_changes_only_bounded_cart_total_markup(tmp_path: Path) -> None:
    cart = tmp_path / "cart.html"
    cart.write_text(_cart_source(), encoding="utf-8")
    result = _run_worker(tmp_path, "implementation", ["implementation-artifact"])
    assert result["status"] == "passed"
    assert cart.read_text(encoding="utf-8") == _cart_source(NEW_SNIPPET)
    assert sorted(path.name for path in tmp_path.iterdir() if path.is_file()) == ["cart.html", "request.json", "result.json"]


def test_p171_worker_emits_required_audit_design_and_qa_evidence(tmp_path: Path) -> None:
    cart = tmp_path / "cart.html"
    cart.write_text(_cart_source(), encoding="utf-8")
    audit = _run_worker(tmp_path, "audit", ["audit-findings"])
    assert audit["status"] == "passed"
    assert [item["kind"] for item in audit["artifacts"]] == ["audit-findings"]

    design = _run_worker(tmp_path, "design", ["design-spec"])
    assert design["status"] == "passed"
    assert [item["kind"] for item in design["artifacts"]] == ["design-spec"]

    cart.write_text(_cart_source(NEW_SNIPPET), encoding="utf-8")
    qa = _run_worker(tmp_path, "qa", ["qa-evidence", "constraint-evidence"])
    assert qa["status"] == "passed"
    assert [item["kind"] for item in qa["artifacts"]] == ["qa-evidence", "constraint-evidence"]


def test_p171_worker_fails_closed_on_wrong_profile_or_target_drift(tmp_path: Path) -> None:
    cart = tmp_path / "cart.html"
    cart.write_text(_cart_source(), encoding="utf-8")
    wrong_profile = _run_worker(tmp_path, "implementation", ["implementation-artifact"], profile="other")
    assert wrong_profile["status"] == "failed"
    assert cart.read_text(encoding="utf-8") == _cart_source()

    cart.write_text("<!doctype html><title>Other product</title>\n", encoding="utf-8")
    drift = _run_worker(tmp_path, "implementation", ["implementation-artifact"])
    assert drift["status"] == "failed"
    assert drift["failure_class"] == "RUNNER_CONTRACT_FAILED"


def test_p171_runtime_rejects_missing_auth_before_git_mutation(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="requires a GitHub token"):
        run_authenticated_dogfood(
            profile_id=PROFILE_ID,
            transaction_id="p171-no-auth",
            github_token="",
            workspace_root=tmp_path / "transactions",
            output_dir=tmp_path / "artifacts",
        )
    assert not (tmp_path / "transactions").exists()


def test_p171_workflow_has_authenticated_pr_only_boundary() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "secrets.UIUX_TARGET_REPO_TOKEN" in text
    assert "AUTH_BLOCKED" in text
    assert "gh auth setup-git" in text
    assert "gh api repos/Ngh1aa/LuxRoom" in text
    assert "run-p171-authenticated-real-dogfood.py" in text
    assert "[P1.7.1 DOGFOOD]" in text
    assert "Merge/deploy: **not performed**" in text
    forbidden = ["gh pr merge", "merge_pull_request", "vercel deploy", "npm run deploy", "git push origin main"]
    assert not any(token in text for token in forbidden)
