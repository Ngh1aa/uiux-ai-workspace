from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

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
        capture_output=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    persisted = json.loads(output.read_text(encoding="utf-8"))
    assert payload == persisted
    assert payload["resolved_flow"]["id"] == "portfolio-career-system"
    assert payload["status"] == "READY_FOR_EXTERNAL_COLLABORATOR"


def test_a21_entrypoint_and_contract_map_are_present() -> None:
    assert (WORKSPACE_ROOT / "START-HERE.md").is_file()
    assert (WORKSPACE_ROOT / "docs" / "CONTRACT-OWNERSHIP.md").is_file()
    routing = json.loads((SKILLS / "runtime" / "context-routing.json").read_text(encoding="utf-8"))
    assert routing["principle"] == "progressive_disclosure"
    assert "external_collaborator" in routing["profiles"]


def test_a21_historical_manager_backups_are_not_active_source() -> None:
    manager_dir = FACTORY_ROOT / "core" / "manager"
    assert not list(manager_dir.glob("development_manager.py.before-*"))
