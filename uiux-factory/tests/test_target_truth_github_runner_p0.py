from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_p0_github_runner_uses_checked_out_truth_before_flow_resolution(tmp_path: Path) -> None:
    workspace = Path(__file__).resolve().parents[2]
    target = tmp_path / "target"
    target.mkdir()
    (target / "index.html").write_text("<main><h1>Portfolio</h1></main>\n", encoding="utf-8")
    (target / ".uiux-profile.json").write_text(
        json.dumps(
            {
                "project": "Portfolio",
                "website_type": "portfolio",
                "domain": "ai_software",
                "mode": "interactive_prototype",
                "release_authorization": "merge_and_deploy",
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
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
            "example/portfolio",
            "--target-ref",
            "main",
            "--target-root",
            str(target),
            "--task",
            "Redesign the whole product experience and add user research evidence.",
            "--authority",
            "branch_write",
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

    assert manifest["task_contract"]["target_truth"]["status"] == "PROBED"
    assert manifest["task_contract"]["website_type"] == "portfolio"
    assert manifest["task_contract"]["domain"] == "ai-software"
    assert manifest["resolved_flow"]["id"] == "portfolio-career-system"
    assert manifest["task_contract"]["routing_provenance"]["field_sources"]["website_type"] == "target_project_truth"
    assert manifest["evidence_boundary"]["target_truth_never_grants_authority_or_evidence"] is True
    assert run_doc["execution_boundary"]["target_truth_is_routing_only"] is True
    assert run_doc["target_snapshot"]["tracked_file_count"] == 2
    assert "Target-truth routing" in handoff
    assert "portfolio" in handoff
    assert "PROBED" in completed.stdout
