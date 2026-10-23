"""UX structure record: structural integrity and honest labels, never usability."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from designlib.design_decisions import UXTask
from designlib.ux_structure import check_ux_structure, check_ux_structure_file, export_page_ux

REPO = Path(__file__).resolve().parents[2]
EXAMPLE_ROOT = REPO / "skills_UIUX/ux-structure-and-flow-design/examples/edtech-class-booking"
EXAMPLE = json.loads((EXAMPLE_ROOT / "docs/ux/ux-structure.json").read_text(encoding="utf-8"))


def fresh() -> dict:
    return copy.deepcopy(EXAMPLE)


def test_example_passes_with_honest_limits():
    result = check_ux_structure_file(EXAMPLE_ROOT, "docs/ux/ux-structure.json")
    assert result["status"] == "PASS"
    assert result["verdict"] == "READY_WITH_RISKS"
    assert result["usability"] == "UNKNOWN"
    assert any("agent-heuristic" in w for w in result["warnings"])


def test_open_blocker_forces_not_ready():
    data = fresh()
    data["walkthrough"]["findings"][1]["status"] = "open"
    data["walkthrough"]["findings"][1].pop("retest")
    result = check_ux_structure(data)
    assert result["status"] == "FAIL"
    assert any("contradicts open blockers" in e for e in result["errors"])


def test_not_ready_verdict_blocks_gate():
    data = fresh()
    data["verdict"]["status"] = "NOT_READY"
    result = check_ux_structure(data)
    assert result["status"] == "FAIL" and result["returncode"] == 1


def test_happy_path_only_flow_is_rejected():
    data = fresh()
    data["flows"][1]["failure_paths"] = []
    assert check_ux_structure(data)["status"] == "FAIL"


def test_top_task_without_flow_is_rejected():
    data = fresh()
    data["flows"] = [f for f in data["flows"] if f["task_id"] != "T3"]
    data["screens"] = [s for s in data["screens"] if "F3" not in s["flows"]]
    result = check_ux_structure(data)
    assert any("T3 has no flow" in e for e in result["errors"])


def test_fewer_than_five_scenarios_is_rejected():
    data = fresh()
    data["walkthrough"]["scenarios"] = data["walkthrough"]["scenarios"][:4]
    data["walkthrough"]["findings"] = [f for f in data["walkthrough"]["findings"] if "S5" not in f["scenario_ids"]]
    assert any("at least 5" in e for e in check_ux_structure(data)["errors"])


def test_ready_requires_evidence_not_hypothesis():
    data = fresh()
    data["verdict"]["status"] = "READY"
    assert any("READY_WITH_RISKS" in e for e in check_ux_structure(data)["errors"])


def test_evidenced_label_requires_reference():
    data = fresh()
    data["audiences"][0]["label"] = "EVIDENCED"
    assert check_ux_structure(data)["status"] == "FAIL"


def test_resolved_finding_requires_retest():
    data = fresh()
    data["walkthrough"]["findings"][0].pop("retest")
    assert check_ux_structure(data)["status"] == "FAIL"


def test_whitespace_screen_fields_are_rejected():
    data = fresh()
    data["screens"][0]["recovery"] = "   "
    assert check_ux_structure(data)["status"] == "FAIL"


def test_over_budget_flow_needs_reason():
    data = fresh()
    data["flows"][0]["happy_path"] = [f"step-{i}" for i in range(9)]
    assert any("over_budget_reason" in e for e in check_ux_structure(data)["errors"])
    data["flows"][0]["over_budget_reason"] = "Legal consent steps required by regulator"
    assert not any("over_budget_reason" in e for e in check_ux_structure(data)["errors"])


def test_hidden_top_task_is_rejected():
    data = fresh()
    data["navigation"]["hidden"] = ["Move a class"]
    assert any("hidden" in e for e in check_ux_structure(data)["errors"])


def test_unlisted_open_major_under_risks_is_rejected():
    data = fresh()
    data["walkthrough"]["findings"][0]["status"] = "open"
    data["walkthrough"]["findings"][0].pop("retest")
    assert any("open majors" in e for e in check_ux_structure(data)["errors"])
    data["verdict"]["open_majors"] = ["W1"]
    assert check_ux_structure(data)["status"] == "PASS"


def test_export_matches_visual_contract_ux_model():
    blocks = export_page_ux(fresh(), "docs/ux/ux-structure.json")
    assert len(blocks) == len(EXAMPLE["screens"])
    for block in blocks:
        UXTask.model_validate(block["ux"])


def test_export_refuses_when_gate_fails():
    data = fresh()
    data["verdict"]["status"] = "NOT_READY"
    with pytest.raises(ValueError):
        export_page_ux(data, "docs/ux/ux-structure.json")
