from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_github_external_agent_runner_emits_truthful_packet(tmp_path: Path) -> None:
    workspace = Path(__file__).resolve().parents[2]
    target = tmp_path / "target"
    target.mkdir()
    (target / "index.html").write_text("<main><h1>Fixture</h1></main>\n", encoding="utf-8")
    subprocess.run(["git", "init", "-b", "main"], cwd=target, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "qa@example.com"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "QA Fixture"], cwd=target, check=True)
    subprocess.run(["git", "add", "index.html"], cwd=target, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=target, check=True, capture_output=True)

    output = tmp_path / "packet"
    script = workspace / "skills_UIUX" / "scripts" / "github-external-agent-runner.py"
    completed = subprocess.run(
        [
            sys.executable, str(script),
            "--repository", "example/product",
            "--target-ref", "main",
            "--target-root", str(target),
            "--task", "Improve the existing interface and verify lifecycle states",
            "--authority", "branch_write",
            "--qa-routes", "/,/checkout",
            "--state-contract", "uiux-state-coverage.json",
            "--output-dir", str(output),
        ],
        cwd=workspace, check=True, capture_output=True, text=True,
    )

    assert "READY_FOR_EXTERNAL_COLLABORATOR" in completed.stdout
    run_doc = json.loads((output / "github-external-agent-run.json").read_text(encoding="utf-8"))
    manifest = json.loads((output / "external-task-manifest.json").read_text(encoding="utf-8"))
    handoff = (output / "HANDOFF.md").read_text(encoding="utf-8")

    assert run_doc["status"] == "READY_FOR_EXTERNAL_COLLABORATOR"
    assert run_doc["execution_boundary"]["invokes_llm_provider"] is False
    assert run_doc["execution_boundary"]["manifest_is_not_qa_pass"] is True
    assert run_doc["target_snapshot"]["checked_out_sha"]
    assert run_doc["target_snapshot"]["tracked_file_count"] == 1
    assert run_doc["verification_plan"]["state_coverage_contract"] == "uiux-state-coverage.json"
    assert "PRODUCT_QA_FAILED" in run_doc["verification_plan"]["failure_classes"]
    assert manifest["status"] == "READY_FOR_EXTERNAL_COLLABORATOR"
    assert manifest["qa_routes"] == ["/", "/checkout"]
    assert "routing contract, not evidence" in handoff

def test_b16_github_runner_routes_and_verifies_same_monorepo_target_dir(tmp_path: Path) -> None:
    workspace = Path(__file__).resolve().parents[2]
    target = tmp_path / "monorepo"
    app = target / "apps" / "dashboard"
    app.mkdir(parents=True)
    (target / ".uiux-profile.json").write_text(
        json.dumps({"website_type": "portfolio", "domain": "art_culture"}) + "\n",
        encoding="utf-8",
    )
    (app / ".uiux-profile.json").write_text(
        json.dumps(
            {
                "website_type": "saas",
                "domain": "ai_software",
                "product_archetype": "ai_workspace",
                "mode": "interactive_prototype",
            }
        ) + "\n",
        encoding="utf-8",
    )
    (app / "index.html").write_text("<main><h1>Dashboard</h1></main>\n", encoding="utf-8")
    subprocess.run(["git", "init", "-b", "main"], cwd=target, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "qa@example.com"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "QA Fixture"], cwd=target, check=True)
    subprocess.run(["git", "add", "."], cwd=target, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=target, check=True, capture_output=True)

    output = tmp_path / "packet"
    script = workspace / "skills_UIUX" / "scripts" / "github-external-agent-runner.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repository",
            "example/monorepo",
            "--target-ref",
            "main",
            "--target-root",
            str(target),
            "--target-dir",
            "apps/dashboard",
            "--task",
            "Improve the existing product interface and verify it.",
            "--authority",
            "branch_write",
            "--state-contract",
            "uiux-state-coverage.json",
            "--output-dir",
            str(output),
        ],
        cwd=workspace,
        check=True,
        capture_output=True,
        text=True,
    )

    manifest = json.loads((output / "external-task-manifest.json").read_text(encoding="utf-8"))
    run_doc = json.loads((output / "github-external-agent-run.json").read_text(encoding="utf-8"))
    handoff = (output / "HANDOFF.md").read_text(encoding="utf-8")
    stdout = json.loads(completed.stdout)

    assert manifest["task_contract"]["website_type"] == "saas"
    assert manifest["task_contract"]["domain"] == "ai-software"
    assert manifest["task_contract"]["product_archetype"] == "ai-workspace"
    assert manifest["task_contract"]["routing_provenance"]["field_sources"]["website_type"] == "target_project_truth"
    assert run_doc["target_snapshot"]["target_dir"] == "apps/dashboard"
    assert run_doc["verification_plan"]["target_dir"] == "apps/dashboard"
    assert stdout["target_dir"] == "apps/dashboard"
    assert "**Target dir:** `apps/dashboard`" in handoff


def test_b16_github_runner_rejects_target_dir_escape(tmp_path: Path) -> None:
    workspace = Path(__file__).resolve().parents[2]
    target = tmp_path / "target"
    target.mkdir()
    output = tmp_path / "packet"
    script = workspace / "skills_UIUX" / "scripts" / "github-external-agent-runner.py"

    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repository",
            "example/monorepo",
            "--target-root",
            str(target),
            "--target-dir",
            "../outside",
            "--task",
            "Audit the project.",
            "--output-dir",
            str(output),
        ],
        cwd=workspace,
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "target_dir must stay inside the checked-out repository" in completed.stderr
    assert not output.exists()


def test_b16_external_agent_workflow_uses_same_target_dir_for_routing_and_qa() -> None:
    workspace = Path(__file__).resolve().parents[2]
    workflow = (workspace / ".github" / "workflows" / "external-agent-runner.yml").read_text(
        encoding="utf-8"
    )

    assert 'TARGET_DIR: ${{ inputs.target_dir }}' in workflow
    assert '--target-dir "$TARGET_DIR"' in workflow
    assert 'INPUT_TARGET_DIR: ${{ inputs.target_dir }}' in workflow
    assert 'realpath -m "$REPO_ROOT/$TARGET_RELATIVE"' in workflow
    assert 'target_dir resolves outside target repository' in workflow

