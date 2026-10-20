"""Regression coverage for UX-first visual routing, not automated taste grading."""
import json
from pathlib import Path

import pytest

from core.runtime.flow_os.external_task import build_external_task_manifest
from core.skills.design_knowledge import retrieve_design_knowledge

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime/runtime-policy.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("output,flow", [
    ("design", "mobile-app-design"),
    ("browser-prototype", "mobile-web-preview"),
])
def test_mobile_visual_contract_is_routed_after_ux_without_granting_release(output, flow):
    result = build_external_task_manifest(
        SKILLS, POLICY, "Redesign mobile app iOS", "example/app",
        authority="branch_write",
        overrides={"requested_output": output},
    ).to_dict()
    assert result["resolved_flow"]["id"] == flow
    stages = {stage["id"]: stage for stage in result["stages"]}
    assert "ux-before-visual" in {gate["id"] for gate in stages["research"]["gates"]}
    design = stages["design"]["design_workflow"]
    assert design["active"] and design["decision_contract_required"]
    assert design["ux_contract_required"]
    assert design["required_check_phases"] == ["design"]
    assert "wireframes" in design["sequence"][2]
    assert design["sequence"][2].endswith("before visual styling")
    assert stages["qa"]["design_workflow"]["required_check_phases"] == ["rendered"]
    assert "ui-craft-and-visual-qa" in stages["qa"]["skills"]
    assert design["aesthetic_quality"] == "UNKNOWN"
    assert design["authority_effect"] == "none"
    assert result["authority"] == "branch_write"
    assert not result["evidence_boundary"]["native_runtime_qa_available"]


@pytest.mark.parametrize("role", ["app-overview", "app-selection", "app-task"])
def test_healthcare_returns_task_specific_synthetic_reference_not_approved_preset(role):
    result = retrieve_design_knowledge(SKILLS, {
        "website_type": "healthcare", "domain": "healthcare",
        "product_archetype": "service-workflow",
    }, role)
    assert result["domain_status"] == "CONTEXT_MATCHED_CANDIDATE"
    assert result["role_card"]["compositions"]
    assert result["reference_anatomy"]["status"] == "CONTEXT_MATCHED_CANDIDATES"
    source = result["reference_anatomy"]["sources"]["mobile-care-specimen"]
    assert (ROOT / source["url"]).is_file()
    assert source["observation_method"] == "local-authored-specimen"
    assert source["human_usability"] == "UNKNOWN"
    assert result["adopted"] is False
    assert result["aesthetic_quality"] == "UNKNOWN"


def test_missing_and_conflicting_identity_never_get_healthcare_by_role_alone():
    unknown = retrieve_design_knowledge(SKILLS, {"domain": "unknown"}, "app-task")
    assert unknown["domain_status"] == "NO_CURATED_DOMAIN_PROFILE"
    assert unknown["reference_anatomy"]["status"] == "NO_CURATED_REFERENCE_ANATOMY"
    conflict = retrieve_design_knowledge(SKILLS, {
        "domain": "retail", "website_type": "ecommerce",
        "product_archetype": "patient-journey",
    }, "app-task")
    assert not conflict["domain_profiles"]
    assert not conflict["reference_anatomy"]["cards"]


def test_mobile_specimen_review_hashes_match_portable_checkout():
    from hashlib import sha256

    specimen = SKILLS / "visual-design-direction/examples/mobile-care"
    manifest = json.loads((specimen / "review/manifest.json").read_text(encoding="utf-8"))
    for relative, expected in manifest["source_and_capture_sha256"].items():
        assert sha256((specimen / relative).read_bytes()).hexdigest() == expected, relative


def test_ux_blockers_cannot_be_bought_off_by_visual_eval_points():
    task = json.loads((SKILLS / "evals/tasks/mobile-design-001-ios-android.json").read_text(encoding="utf-8"))
    assert sum(task["rubric"].values()) == 100
    assert task["rubric"]["task_clarity_and_recovery"] > task["rubric"]["visual_hierarchy_and_composition"]
    assert "Accept broken task navigation because the screen looks polished" in task["must_not"]


def ux_fixture():
    return {
        "entry_state": "Selected appointment", "user_goal": "Review before submitting",
        "information_priority": ["patient", "date", "status"],
        "primary_action": "Continue", "destination": "Review request",
        "feedback": "Show retained patient and date", "recovery": "Back preserves inputs",
        "walkthrough_observation": "Synthetic fixture: back retained the selected patient",
        "evidence_ref": "Synthetic test fixture, not a real walkthrough",
        "review_source": "agent-heuristic", "findings": [],
    }


def test_ux_gate_rejects_missing_or_forged_records_but_accepts_bound_task_record(tmp_path):
    from core.skills.design_decisions import check_design_file
    from core.runtime.flow_os.evidence import evidence_from_tool, gate_evidence_errors
    from test_design_decision_integrity import contract_fixture

    payload = contract_fixture()
    target = tmp_path / "design.json"
    gates = [{"id": "ux-design", "evidence_types": ["design_contract_check"],
              "ux_contract_required": True}]

    def receipt():
        target.write_text(json.dumps(payload), encoding="utf-8")
        return evidence_from_tool("design", "check_design_decisions",
                                  check_design_file(tmp_path, target.name)).to_dict()

    record = receipt()
    assert gate_evidence_errors(gates, "design", [record], "implementation")
    record["data"]["ux_integrity"] = "RECORDED"
    assert gate_evidence_errors(gates, "design", [record], "implementation")
    payload["pages"][0]["ux"] = ux_fixture()
    record = receipt()
    assert gate_evidence_errors(gates, "design", [record], "implementation") == []
    assert record["data"]["aesthetic_quality"] == "UNKNOWN"
    assert record["data"]["human_preference"] == "UNKNOWN"


@pytest.mark.parametrize("defect", ["open_blocker", "no_retest", "blank_recovery"])
def test_ux_contract_rejects_blocking_or_empty_walkthrough_claims(defect):
    from core.skills.design_decisions import check_design_decisions
    from test_design_decision_integrity import contract_fixture

    payload = contract_fixture()
    ux = payload["pages"][0]["ux"] = ux_fixture()
    if defect == "blank_recovery":
        ux["recovery"] = " "
    else:
        ux["findings"] = [{"observation": "Back loses input", "severity": "blocker",
                           "status": "open" if defect == "open_blocker" else "resolved"}]
    assert check_design_decisions(payload)["status"] == "FAIL"


def test_47_screen_mobile_rollout_fits_one_bounded_decision_contract():
    from copy import deepcopy
    from core.skills.design_decisions import check_design_decisions
    from test_design_decision_integrity import contract_fixture

    payload = contract_fixture()
    owner = payload["pages"][0]
    owner["ux"] = ux_fixture()
    for index in range(1, 47):
        page = deepcopy(owner)
        page.update(route=f"/screen-{index}", comparison_required=False, inherited_from="/")
        page["compositions"] = page["compositions"][:1]
        payload["pages"].append(page)
    result = check_design_decisions(payload)
    assert result["status"] == "PASS", result["errors"]
    assert result["page_count"] == 47
    assert result["ux_integrity"] == "RECORDED"
    assert result["aesthetic_quality"] == "UNKNOWN"

    for index in range(47, 101):
        page = deepcopy(payload["pages"][-1])
        page["route"] = f"/screen-{index}"
        payload["pages"].append(page)
    assert check_design_decisions(payload)["status"] == "FAIL"
