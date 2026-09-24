from __future__ import annotations

import json
from types import SimpleNamespace

from core.orchestration.stage_replan_v1 import (
    REPLAN_STAGE_ORDER,
    STAGE_ARTIFACT_KEYS,
    canonical_replan_stage,
    evidence_replan_target,
    stages_from,
)


def test_stage_aware_replan_registry_covers_every_rerunnable_stage() -> None:
    assert set(REPLAN_STAGE_ORDER) == set(STAGE_ARTIFACT_KEYS)
    assert canonical_replan_stage("reference_analysis") == "research"
    assert canonical_replan_stage("browser_qa") == "implementation"
    assert canonical_replan_stage("visual_qa") == "implementation"
    assert canonical_replan_stage("repair") == "implementation"
    assert canonical_replan_stage("not-a-stage") is None


def test_stage_aware_replan_reruns_every_downstream_owner() -> None:
    assert stages_from("art_direction") == (
        "art_direction",
        "design_contract",
        "design_system",
        "implementation_plan",
        "visual_composition",
        "implementation",
    )
    assert stages_from("design_system") == (
        "design_system",
        "implementation_plan",
        "visual_composition",
        "implementation",
    )
    assert stages_from("browser_qa") == ("implementation",)


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
    assert evidence_replan_target(result, tmp_path) == "art_direction"


def test_non_evidence_quality_failure_does_not_fake_upstream_owner(tmp_path) -> None:
    result = SimpleNamespace(stop_reason="same_issue_fingerprint_without_minimum_score_improvement")
    assert evidence_replan_target(result, tmp_path) is None
