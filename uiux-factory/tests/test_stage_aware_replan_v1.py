from __future__ import annotations

import json
from types import SimpleNamespace

from core.manager.intelligent_manager import IntelligentDevelopmentManager


def test_stage_aware_replan_registry_covers_every_rerunnable_stage() -> None:
    manager = IntelligentDevelopmentManager
    assert set(manager.REPLAN_STAGE_ORDER) == set(manager.STAGE_ARTIFACT_KEYS)
    assert manager._canonical_replan_stage("reference_analysis") == "research"
    assert manager._canonical_replan_stage("browser_qa") == "implementation"
    assert manager._canonical_replan_stage("visual_qa") == "implementation"
    assert manager._canonical_replan_stage("repair") == "implementation"
    assert manager._canonical_replan_stage("not-a-stage") is None


def test_stage_aware_replan_reruns_every_downstream_owner() -> None:
    stages = IntelligentDevelopmentManager._stages_from("art_direction")
    assert stages == (
        "art_direction",
        "design_contract",
        "design_system",
        "implementation_plan",
        "visual_composition",
        "implementation",
    )
    assert IntelligentDevelopmentManager._stages_from("design_system") == (
        "design_system",
        "implementation_plan",
        "visual_composition",
        "implementation",
    )
    assert IntelligentDevelopmentManager._stages_from("browser_qa") == ("implementation",)


def test_evidence_remediation_plan_selects_earliest_owner_stage(tmp_path) -> None:
    plan = {
        "schema_version": 1,
        "earliest_owner_stage": "art_direction",
        "blocker_count": 2,
    }
    (tmp_path / "evidence-remediation-plan.json").write_text(
        json.dumps(plan),
        encoding="utf-8",
    )
    result = SimpleNamespace(
        stop_reason="prototype_evidence_contract_requires_root_replan:evidence-remediation-plan.json"
    )
    assert (
        IntelligentDevelopmentManager._evidence_replan_target(result, tmp_path)
        == "art_direction"
    )


def test_non_evidence_quality_failure_does_not_fake_upstream_owner(tmp_path) -> None:
    result = SimpleNamespace(stop_reason="same_issue_fingerprint_without_minimum_score_improvement")
    assert IntelligentDevelopmentManager._evidence_replan_target(result, tmp_path) is None
