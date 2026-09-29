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
