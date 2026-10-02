from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_p0_prepare_external_task_cli_uses_optional_target_root(tmp_path: Path) -> None:
    workspace = Path(__file__).resolve().parents[2]
    target = tmp_path / "target"
    target.mkdir()
    (target / ".uiux-profile.json").write_text(
        json.dumps(
            {
                "website_type": "portfolio",
                "domain": "ai_software",
                "mode": "interactive_prototype",
            }
        ) + "\n",
        encoding="utf-8",
    )

    output = tmp_path / "manifest.json"
    script = workspace / "skills_UIUX" / "scripts" / "prepare-external-task.py"
    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repository",
            "owner/portfolio",
            "--target-root",
            str(target),
            "--task",
            "Redesign the whole product experience and add user research evidence.",
            "--output",
            str(output),
        ],
        cwd=workspace,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload == json.loads(output.read_text(encoding="utf-8"))
    assert payload["task_contract"]["target_truth"]["status"] == "PROBED"
    assert payload["task_contract"]["website_type"] == "portfolio"
    assert payload["resolved_flow"]["id"] == "portfolio-career-system"
    assert payload["evidence_boundary"]["target_truth_probed_before_flow_resolution"] is True
