from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
import pytest

from core.runtime.flow_os.external_task import build_external_task_manifest
from core.runtime.flow_os.flow import FlowResolver
from core.runtime.flow_os.task_context import GoalInterpreter


FACTORY_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = FACTORY_ROOT.parent
SKILLS = WORKSPACE_ROOT / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


def _portfolio_goal() -> str:
    return (
        "Nâng cấp portfolio Product Designer cho recruiter, làm rõ cách dùng AI trong công việc, "
        "thêm user research và usability testing có evidence thật, sửa code và mở pull request."
    )


def test_a21_broad_portfolio_upgrade_routes_to_career_system() -> None:
    context = GoalInterpreter().interpret(_portfolio_goal()).to_context()
    assert context["website_type"] == "portfolio"
    assert context["change_surface"] == "PRODUCT"
    assert context["validation_lane"] == "evidence-led"

    _path, document, _score = FlowResolver(SKILLS / "flows").resolve(context)
    assert document["id"] == "portfolio-career-system"


def test_a21_narrow_portfolio_fix_stays_focused() -> None:
    context = GoalInterpreter().interpret("Sửa hero portfolio hiện tại, giữ nguyên animation").to_context()
    assert context["website_type"] == "portfolio"
    assert context["change_surface"] == "FOCUSED"

    _path, document, _score = FlowResolver(SKILLS / "flows").resolve(context)
    assert document["id"] != "portfolio-career-system"


def test_a21_external_manifest_is_bounded_and_research_ready() -> None:
    manifest = build_external_task_manifest(
        SKILLS,
        POLICY,
        _portfolio_goal(),
        "Haign12/DoAnhNghia_BAPortfolio",
        authority="branch_write",
        qa_routes=["/", "/case-study-uiux-factory.html"],
    ).to_dict()

    assert manifest["status"] == "READY_FOR_EXTERNAL_COLLABORATOR"
    assert manifest["authority"] == "branch_write"
    assert manifest["resolved_flow"]["id"] == "portfolio-career-system"
    assert manifest["research_packet"]["required"] is True
    assert manifest["research_packet"]["state"] == "PLANNED_VALIDATION_UNTIL_REAL_EVIDENCE_EXISTS"
    assert manifest["evidence_boundary"]["manifest_is_not_qa_pass"] is True
    assert manifest["evidence_boundary"]["target_runtime_evidence_required_for_runtime_claims"] is True
    assert manifest["qa_routes"] == ["/", "/case-study-uiux-factory.html"]

    research = manifest["stages"][0]
    assert research["id"] == "research"
    assert "portfolio-career-positioning" in research["skills"]
    assert "research-evidence-pipeline" in research["skills"]

    for stage in manifest["stages"]:
        for skill_path in stage["skill_paths"]:
            assert (WORKSPACE_ROOT / skill_path).is_file(), skill_path

    for template_path in manifest["research_packet"]["templates"]:
        assert (WORKSPACE_ROOT / template_path).is_file(), template_path


def test_a21_external_manifest_never_escalates_task_language_authority() -> None:
    manifest = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Chỉ audit portfolio Product Designer, không sửa code",
        "owner/portfolio",
        authority="branch_write",
        overrides={"change_surface": "PRODUCT"},
    ).to_dict()

    assert manifest["authority"] == "read_only"
    assert manifest["task_contract"]["requested_authority"] == "read_only"
    assert manifest["task_contract"]["effective_authority"] == "read_only"


def test_a21_feature_list_override_is_supported() -> None:
    manifest = build_external_task_manifest(
        SKILLS,
        POLICY,
        "Redesign portfolio",
        "owner/portfolio",
        overrides={"features": ["user-validation", "outcome-measurement"]},
    ).to_dict()
    assert manifest["task_contract"]["features"] == ["user-validation", "outcome-measurement"]


def test_a21_prepare_external_task_cli_emits_manifest(tmp_path: Path) -> None:
    output = tmp_path / "external-task-manifest.json"
    script = SKILLS / "scripts" / "prepare-external-task.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repository",
            "owner/portfolio",
            "--task",
            _portfolio_goal(),
            "--authority",
            "branch_write",
            "--qa-route",
            "/",
            "--output",
            str(output),
        ],
        cwd=WORKSPACE_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    persisted = json.loads(output.read_text(encoding="utf-8"))
    assert payload == persisted
    assert payload["resolved_flow"]["id"] == "portfolio-career-system"
    assert payload["status"] == "READY_FOR_EXTERNAL_COLLABORATOR"


@pytest.mark.parametrize("intent", ["audit", "review", "research", "validate", "qa"])
def test_batch1_cli_non_mutating_intent_override_reduces_authority(intent: str, tmp_path: Path) -> None:
    output = tmp_path / "manifest.json"
    result = subprocess.run(
        [sys.executable, str(SKILLS / "scripts/prepare-external-task.py"),
         "--repository", "owner/repo", "--task", "Fix button spacing only",
         "--intent", intent, "--authority", "release", "--output", str(output)],
        cwd=WORKSPACE_ROOT, text=True, encoding="utf-8", capture_output=True, check=True,
    )
    manifest = json.loads(result.stdout)
    assert manifest["task_contract"]["intent"] == intent
    assert manifest["authority"] == "read_only"
    assert all(stage["agent"] != "implementation" for stage in manifest["stages"])


def test_batch1_cli_mutating_override_cannot_remove_read_only_constraint(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SKILLS / "scripts/prepare-external-task.py"),
         "--repository", "owner/repo", "--task", "Chỉ đọc repo, không sửa code",
         "--intent", "fix", "--authority", "release", "--output", str(tmp_path / "manifest.json")],
        cwd=WORKSPACE_ROOT, text=True, encoding="utf-8", capture_output=True, check=True,
    )
    manifest = json.loads(result.stdout)
    assert manifest["authority"] == "read_only"
    assert manifest["task_contract"]["intent"] == "audit"


@pytest.mark.parametrize("script,args", [
    ("prepare-external-task.py", ["--repository", "owner/repo", "--task", "Chỉ đọc repo và lập danh sách lỗi"]),
    ("uiux-agent.py", ["--help"]),
])
def test_windows_completion_cli_uses_utf8_without_preconfigured_environment(script: str, args: list[str]) -> None:
    env = dict(os.environ)
    env.pop("PYTHONUTF8", None)
    env["PYTHONIOENCODING"] = "cp1252"
    result = subprocess.run(
        [sys.executable, "-X", "utf8=0", str(SKILLS / "scripts" / script), *args],
        cwd=WORKSPACE_ROOT, env=env, capture_output=True,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    decoded = result.stdout.decode("utf-8")
    if script == "prepare-external-task.py":
        assert json.loads(decoded)["task"] == args[-1]
    else:
        assert "model→tool→observation" in decoded


def test_windows_completion_cli_propagates_utf8_to_python_children() -> None:
    code = (
        "import json, subprocess, sys; "
        "from core.runtime.flow_os.agent import configure_cli_utf8; configure_cli_utf8(); "
        "child = subprocess.run([sys.executable, '-c', "
        "\"import json, sys; print(json.dumps({'utf8': sys.flags.utf8_mode, 'encoding': sys.stdout.encoding, 'value': 'Tiếng Việt'}, ensure_ascii=False))\"], "
        "capture_output=True, encoding='utf-8', check=True); "
        "print(child.stdout, end='')"
    )
    env = {**os.environ, "PYTHONUTF8": "0", "PYTHONIOENCODING": "cp1252"}
    result = subprocess.run([sys.executable, "-X", "utf8=0", "-c", code], cwd=FACTORY_ROOT, env=env, capture_output=True)
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    child = json.loads(result.stdout.decode("utf-8"))
    assert child == {"utf8": 1, "encoding": "utf-8", "value": "Tiếng Việt"}


def test_windows_completion_command_provider_preserves_unicode_json(tmp_path: Path) -> None:
    stub = tmp_path / "provider.py"
    stub.write_text(
        "import json, sys\n"
        "payload = json.load(sys.stdin)\n"
        "print(json.dumps({'status': 'BLOCKED', 'summary': payload['request']['goal']}, ensure_ascii=False))\n",
        encoding="utf-8",
    )
    goal = "Kiểm tra tiếng Việt và quyền chỉ đọc"
    code = (
        "import shlex, sys; "
        "from core.runtime.flow_os.provider import CommandProvider, ProviderStageRequest; "
        f"request = ProviderStageRequest(goal={goal!r}, project_root='.', flow_id='audit-review', "
        "flow_revision=1, stage_id='research', agent='research', purpose='Encoding test', "
        "gates=[], task_context={}, authority='read_only', tools=[], skill_context=[], source_context=[]); "
        f"provider = CommandProvider(shlex.join([sys.executable, {str(stub)!r}])); "
        "response = provider.run_stage(request); sys.stdout.buffer.write(response.summary.encode('utf-8'))"
    )
    env = {**os.environ, "PYTHONUTF8": "0", "PYTHONIOENCODING": "cp1252"}
    result = subprocess.run([sys.executable, "-X", "utf8=0", "-c", code], cwd=FACTORY_ROOT, env=env, capture_output=True)
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert result.stdout.decode("utf-8") == goal


def test_a21_entrypoint_and_contract_map_are_present() -> None:
    assert (WORKSPACE_ROOT / "START-HERE.md").is_file()
    assert (WORKSPACE_ROOT / "docs" / "CONTRACT-OWNERSHIP.md").is_file()
    routing = json.loads((SKILLS / "runtime" / "context-routing.json").read_text(encoding="utf-8"))
    assert routing["principle"] == "progressive_disclosure"
    assert "external_collaborator" in routing["profiles"]


def test_a21_historical_manager_backups_are_not_active_source() -> None:
    manager_dir = FACTORY_ROOT / "core" / "manager"
    assert not list(manager_dir.glob("development_manager.py.before-*"))
