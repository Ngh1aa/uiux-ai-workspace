"""Managed completion integration: real tools/CLI; synthetic records are explicit."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.evidence import evidence_from_tool
from core.runtime.flow_os.managed import ManagedFlowController
from test_factory_render_gates import _png, rendered

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills_UIUX"


def _fresh(tmp_path, approval="auto"):
    (tmp_path / "index.html").write_text("Industrial solutions", encoding="utf-8")
    harness = ProviderNeutralAgentHarness(SKILLS, tmp_path)
    manager = ManagedFlowController(harness)
    managed = manager.start_from_goal("Build a corporate industrial automation website", authority="read_only",
                                      overrides={"approval_mode": approval})
    return harness, manager, managed


@pytest.mark.parametrize("case", ["empty", "wrong_stage", "untrusted", "failed", "malformed", "stale_revision", "wrong_manager", "wrong_gates"])
def test_common_completion_rejects_invalid_or_missing_evidence(tmp_path, case):
    harness, manager, managed = _fresh(tmp_path)
    state = manager.start_stage(managed)
    record = evidence_from_tool("research", "read_text", {"path": "index.html", "content": "synthetic fixture"}).to_dict()
    if case == "empty":
        records = []
    elif case == "malformed":
        records = [{}]
    else:
        records = [record]
    if case == "wrong_stage": record["stage_id"] = "design"
    if case == "untrusted": record.update(trusted=False, origin="provider")
    if case == "failed": record["status"] = "FAIL"
    if case == "stale_revision": state.context["flow_revision"] = managed.flow.revision + 1
    if case == "wrong_manager": state.context["manager_run_id"] = "other-run"
    if case == "wrong_gates": state.context["stage_gates"] = []
    state.context["evidence_records"] = records
    state.state = "COMPLETED"
    harness.checkpoints.save(state.run_id, state.to_dict())
    with pytest.raises(ValueError, match="cannot complete stage research"):
        manager.complete_stage(managed)
    assert managed.active_stage == "research"
    assert managed.state != "COMPLETED"
    assert not managed.completed_stages


def test_real_manual_read_records_evidence_and_advances(tmp_path):
    harness, manager, managed = _fresh(tmp_path)
    state = harness.execute_plan(manager.start_stage(managed), [{"tool": "read_text", "args": {"path": "index.html"}}])
    assert [item["type"] for item in state.context["evidence_records"]] == ["file_read"]
    assert manager.complete_stage(managed) == "design"
    assessment = harness.resume(managed.manager_run_id).context["managed_run"]["task_context"]["completion_assessments"]["research"]
    assert assessment["machine_gate_status"] == "PASS"
    assert assessment["human_approval_status"] == "NOT_REQUIRED"


def test_manual_approval_does_not_replace_machine_evidence(tmp_path):
    harness, manager, managed = _fresh(tmp_path, approval="manual")
    harness.execute_plan(manager.start_stage(managed), [{"tool": "read_text", "args": {"path": "index.html"}}])
    manager.complete_stage(managed)
    design = harness.execute_plan(manager.start_stage(managed), [])
    with pytest.raises(ValueError, match="human approval required"):
        manager.complete_stage(managed)
    assert managed.state == "AWAITING_APPROVAL"
    manager.approve_gate(managed, "design-contract")
    with pytest.raises(ValueError, match="evidence"):
        manager.complete_stage(managed)
    assert managed.active_stage == "design"
    # Explicit validator fixture, not a real design review.
    design.state = "COMPLETED"
    design.context["evidence_records"] = [evidence_from_tool("design", "run_validator", {"name": "fixture", "returncode": 0}).to_dict()]
    harness.checkpoints.save(design.run_id, design.to_dict())
    assert manager.complete_stage(managed) == "implementation"


def test_auto_approval_is_explicitly_human_unreviewed(tmp_path):
    harness, manager, managed = _fresh(tmp_path)
    harness.execute_plan(manager.start_stage(managed), [{"tool": "read_text", "args": {"path": "index.html"}}])
    manager.complete_stage(managed)
    design = manager.start_stage(managed)
    design.state = "COMPLETED"
    design.context["evidence_records"] = [evidence_from_tool("design", "run_validator", {"name": "fixture", "returncode": 0}).to_dict()]
    harness.checkpoints.save(design.run_id, design.to_dict())
    manager.complete_stage(managed)
    assessment = managed.task_context["completion_assessments"]["design"]
    assert assessment == {"machine_gate_status": "PASS", "human_approval_status": "UNREVIEWED"}


@pytest.mark.parametrize("stale", [False, True])
def test_qa_completion_rechecks_current_capture_bytes(tmp_path, rendered, stale):
    harness, manager, managed = _fresh(tmp_path)
    # Isolated QA boundary fixture, not claimed as an end-to-end design run.
    managed.active_stage = "qa"
    state = manager.start_stage(managed)
    record, image = rendered
    state.context["evidence_records"] = [record]
    state.state = "COMPLETED"
    harness.checkpoints.save(state.run_id, state.to_dict())
    if stale:
        image.write_bytes(_png(width=321))
        with pytest.raises(ValueError, match="stale evidence"):
            manager.complete_stage(managed)
        assert managed.state != "COMPLETED"
    else:
        assert manager.complete_stage(managed) is None
        assert managed.state == "COMPLETED"
        assert "qa" in managed.task_context["completion_assessments"]
        assert manager.replan(managed, "GATE_FAIL").accepted
        assert "qa" not in managed.task_context["completion_assessments"]


def test_manual_browser_attachment_can_satisfy_qa_completion(tmp_path, rendered):
    from core.runtime.flow_os.evidence import EvidenceRecord
    from core.runtime.flow_os.release import ProductionReleaseController
    harness, manager, managed = _fresh(tmp_path)
    managed.active_stage = "qa"  # Isolated QA acceptance boundary.
    harness.execute_plan(manager.start_stage(managed), [])
    record, _image = rendered
    ProductionReleaseController(harness).attach_release_evidence(managed, [EvidenceRecord.from_dict(record)])
    assert manager.complete_stage(managed) is None
    assert managed.state == "COMPLETED"


def test_dry_run_cannot_create_completion_evidence(tmp_path):
    harness, manager, managed = _fresh(tmp_path)
    state = harness.execute_plan(manager.start_stage(managed), [{"tool": "read_text", "args": {"path": "index.html"}}], dry_run=True)
    assert not state.context.get("evidence_records")
    with pytest.raises(ValueError, match="evidence"):
        manager.complete_stage(managed)


def test_handoff_preserves_existing_runtime_evidence(tmp_path):
    harness, manager, managed = _fresh(tmp_path)
    read = {"tool": "read_text", "args": {"path": "index.html"}}
    state = harness.execute_plan(manager.start_stage(managed), [read, {"handoff": "qa"}, read])
    assert state.active_role == "qa" and state.authority == "read_only"
    assert [item["type"] for item in state.context["evidence_records"]] == ["file_read", "file_read"]
    assert all(item["stage_id"] == "research" and item["origin"] == "runtime" for item in state.context["evidence_records"])


@pytest.mark.parametrize("mode", ["advance-on-success", "complete-stage"])
def test_actual_cli_empty_completion_cannot_advance(tmp_path, mode):
    harness, manager, managed = _fresh(tmp_path)
    if mode == "complete-stage":
        harness.execute_plan(manager.start_stage(managed), [])
    command = [sys.executable, "-B", str(SKILLS / "scripts/uiux-agent.py"), "--project", str(tmp_path),
               "--managed-run-id", managed.manager_run_id, "--stage", "research", "--" + mode]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                            env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"})
    assert result.returncode != 0, result.stdout
    assert "evidence" in result.stdout + result.stderr
    restored = manager.resume(managed.manager_run_id)
    assert restored.active_stage == "research" and not restored.completed_stages
    assert restored.state != "COMPLETED"
