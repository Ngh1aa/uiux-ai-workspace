from __future__ import annotations

import json
from pathlib import Path


def test_a37_cennext_config_is_pinned_and_truthful() -> None:
    root = Path(__file__).resolve().parents[2]
    config = json.loads((root / "uiux-factory/core/dogfood/a37-cennext.json").read_text(encoding="utf-8"))
    contract = json.loads((root / "uiux-factory/qa/dogfood/cennext-state-coverage.json").read_text(encoding="utf-8"))

    assert config["target_repository"] == "Ngh1aa/cennext-b2b-prototype"
    assert config["target_sha"] == "273403accf8979608fbb16dbe2741cedb0430fb6"
    assert config["authority"] == "read_only"
    assert config["expected_deployment_classification_without_provider_sha"] == "READY_BUT_NOT_DEPLOYED"
    assert contract["entry_route"] == "/component-states.html"
    ids = [state["id"] for state in contract["states"]]
    assert ids == ["normal", "disabled", "error", "success", "edge"]
    assert "loading" not in ids  # target has no async-loading specimen; A37 must not invent one.
    for state in contract["states"][1:]:
        assert state["assertions"]
        assert state["focus"]


def test_a37_workflow_requires_honest_unverified_deployment_boundary() -> None:
    root = Path(__file__).resolve().parents[2]
    workflow = (root / ".github/workflows/a37-external-agent-e2e-dogfood.yml").read_text(encoding="utf-8")
    assert "READY_BUT_NOT_DEPLOYED" in workflow
    assert "DEPLOYED_VERIFIED" not in workflow
    assert "build-release-evidence.py" in workflow
    assert "run_cross_project_dogfood.py" in workflow
    assert "state-coverage-report.json" in workflow


def test_external_agent_packet_points_to_release_evidence_surfaces() -> None:
    root = Path(__file__).resolve().parents[2]
    runner = (root / "skills_UIUX/scripts/github-external-agent-runner.py").read_text(encoding="utf-8")
    assert "deployment_truth_gate" in runner
    assert "release_evidence_registry" in runner
    assert "release_evidence_manifest" in runner
