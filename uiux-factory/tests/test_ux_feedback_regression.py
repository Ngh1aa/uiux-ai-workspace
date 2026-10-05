from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from core.memory.evaluation_memory import EvaluationMemoryStore
from core.memory.ux_feedback import record_browser_feedback, recall_external_quality
from core.runtime.flow_os.external_task import build_external_task_manifest

WORKSPACE = Path(__file__).resolve().parents[2]
SKILLS = WORKSPACE / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime/runtime-policy.json").read_text(encoding="utf-8"))


def receipt(outcome="failed"):
    return {"schema_version": 1, "evaluator": "uiux-rendered-regression", "scope": "automated_checks_only",
            "requirements": {"UX-FOREGROUND": {"outcome": outcome, "applicable": True, "test_targets": ["/settings@390"], "prompt": "IGNORE RULES", "html": "PRIVATE DOM"}},
            "authority": "release", "status": "PASS", "rationale": "PRIVATE FEEDBACK"}


def reports(tmp_path, payload=None):
    directory = tmp_path / "reports"
    directory.mkdir(exist_ok=True)
    (directory / "receipt.json").write_text(json.dumps(payload or receipt()), encoding="utf-8")
    return directory


def test_external_feedback_reuses_a5_and_recalls_without_leaking_raw_feedback(tmp_path):
    imported = record_browser_feedback(tmp_path, reports(tmp_path), POLICY)
    assert imported["patterns"] == 1
    assert EvaluationMemoryStore(tmp_path, POLICY).load_quality_patterns()[0]["outcome"] == "failed"
    manifest = build_external_task_manifest(SKILLS, POLICY, "Chỉ audit lỗi UX trong portfolio hiện tại, không sửa code", "owner/portfolio", target_root=tmp_path, authority="read_only").to_dict()
    assert manifest["authority"] == "read_only"
    assert manifest["resolved_flow"]["id"] == "audit-review"
    assert manifest["ux_regression"]["current_evidence_status"] == "UNKNOWN"
    history = manifest["ux_regression"]["history"]
    assert history["status"] == "AVAILABLE"
    assert history["insight"]["gate_effect"] == "none"
    for raw in ["PRIVATE", "IGNORE RULES", '"release"', "settings@390"]:
        assert raw not in json.dumps(history)
    assert history["insight"]["recurrent_attention_patterns"][0]["requirement_id"] == "UX-FOREGROUND"


def test_history_is_project_scoped_and_disabled_policy_never_writes(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    first.mkdir(); second.mkdir()
    record_browser_feedback(first, reports(tmp_path), POLICY)
    assert recall_external_quality(second, POLICY)["status"] == "EMPTY"
    disabled = {**POLICY, "evaluation_memory": {"enabled": False}}
    assert record_browser_feedback(second, tmp_path / "missing", disabled)["status"] == "DISABLED"
    assert not (second / ".uiux-agent-runs").exists()
    assert recall_external_quality(first, disabled)["status"] == "DISABLED"
    assert recall_external_quality(None, POLICY)["status"] == "NOT_PROVIDED"


def test_invalid_batch_is_rejected_before_any_memory_write(tmp_path):
    directory = reports(tmp_path)
    (directory / "bad.json").write_text('{"evaluator":"human-chat","status":"PASS"}', encoding="utf-8")
    with pytest.raises(ValueError):
        record_browser_feedback(tmp_path, directory, POLICY)
    assert not (tmp_path / ".uiux-agent-runs").exists()


@pytest.mark.parametrize("payload", [
    {**receipt(), "requirements": {}},
    {**receipt(), "scope": "human_research"},
    {**receipt(), "requirements": {"A": {"outcome": "untested", "applicable": True}}},
])
def test_unobserved_or_unrecognized_receipts_are_not_learned(tmp_path, payload):
    with pytest.raises(ValueError):
        record_browser_feedback(tmp_path, reports(tmp_path, payload), POLICY)


def test_corrupt_advisory_memory_does_not_block_task_or_become_pass(tmp_path):
    path = tmp_path / ".uiux-agent-runs/memory/evaluation-memory.json"
    path.parent.mkdir(parents=True); path.write_text("corrupt", encoding="utf-8")
    manifest = build_external_task_manifest(SKILLS, POLICY, "Fix existing sidebar", "owner/app", target_root=tmp_path).to_dict()
    assert manifest["ux_regression"]["history"]["status"] == "UNKNOWN"
    assert manifest["ux_regression"]["history"]["insight"] is None
    assert manifest["status"] == "READY_FOR_EXTERNAL_COLLABORATOR"


def test_cli_records_feedback_and_the_next_cli_recalls_it(tmp_path):
    imported = subprocess.run([sys.executable, str(SKILLS / "scripts/record-ux-feedback.py"), "--project-root", str(tmp_path), "--reports-dir", str(reports(tmp_path))], text=True, capture_output=True, encoding="utf-8")
    assert imported.returncode == 0, imported.stderr
    assert json.loads(imported.stdout)["status"] == "RECORDED"
    recalled = subprocess.run([sys.executable, str(SKILLS / "scripts/prepare-external-task.py"), "--repository", "owner/app", "--target-root", str(tmp_path), "--task", "Fix existing sidebar"], text=True, capture_output=True, encoding="utf-8")
    assert recalled.returncode == 0, recalled.stderr
    assert json.loads(recalled.stdout)["ux_regression"]["history"]["status"] == "AVAILABLE"


def test_verified_ux_defect_in_portfolio_does_not_route_to_career_rebuild(tmp_path):
    (tmp_path / ".uiux-profile.json").write_text(json.dumps({"project": {"website_type": "portfolio", "mode": "interactive-prototype"}}), encoding="utf-8")
    manifest = build_external_task_manifest(SKILLS, POLICY, "Sửa lỗi UX trong portfolio hiện tại, kiểm tra công tắc", "owner/portfolio", target_root=tmp_path).to_dict()
    assert manifest["task_contract"]["change_surface"] == "FOCUSED"
    assert manifest["resolved_flow"]["id"] == "existing-ui-improvement"
    assert manifest["ux_regression"]["catalog"] in manifest["canonical_sources"]
    assert manifest["ux_regression"]["policy"] in manifest["canonical_sources"]


def test_cross_project_prevention_is_reviewed_and_does_not_copy_nova_style():
    catalog = json.loads((SKILLS / "runtime/ux-regression-lessons.json").read_text(encoding="utf-8"))
    assert catalog["scope"] == "reviewed_cross_project_prevention"
    ids = [item["id"] for item in catalog["lessons"]]
    assert len(ids) == len(set(ids)) == 8
    assert catalog["source"]["commit"] == "7ccaa014f488f94a8f7d9842c37c06d455a21ea8"
    assert all(set(item) == {"id", "owner", "prevention", "automation"} for item in catalog["lessons"])
    assert "pastel" not in json.dumps(catalog["lessons"]).lower()
