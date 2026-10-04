from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import pytest

from core.runtime.flow_os.execution_advisor import build_execution_advice
from core.runtime.flow_os.external_task import build_external_task_manifest


FACTORY_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = FACTORY_ROOT.parent
SKILLS_ROOT = WORKSPACE_ROOT / "skills_UIUX"
POLICY = json.loads((SKILLS_ROOT / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("english,vietnamese,capability", [
    ("Fix button spacing only", "Chỉ sửa khoảng cách của nút", "balanced"),
    ("Fix login authorization bypass", "Sửa lỗi vượt quyền đăng nhập", "advanced"),
])
def test_batch1_equivalent_languages_have_equal_scope_and_compute(english: str, vietnamese: str, capability: str) -> None:
    manifests = [build_external_task_manifest(SKILLS_ROOT, POLICY, goal, "owner/repo").to_dict() for goal in (english, vietnamese)]
    first, second = manifests
    for field in ("intent", "scope", "change_surface", "risk", "features", "authority"):
        assert first["task_contract"][field] == second["task_contract"][field], field
    assert first["resolved_flow"]["id"] == second["resolved_flow"]["id"]
    assert [stage["skills"] for stage in first["stages"]] == [stage["skills"] for stage in second["stages"]]
    for manifest in manifests:
        assert manifest["execution_advice"]["overall_profile"]["recommended_capability"] == capability


def _flow(*agents: str):
    stages = [
        SimpleNamespace(
            id=f"stage-{index}",
            agent=agent,
            gates=[{"require": "verified"}],
            skills=["project-context"],
        )
        for index, agent in enumerate(agents or ("development",), start=1)
    ]
    return SimpleNamespace(stages=stages)


def test_advisor_keeps_small_focused_work_bounded() -> None:
    context = {
        "intent": "fix",
        "change_surface": "FOCUSED",
        "website_type": "generic",
        "domain": "generic",
        "product_archetype": "generic",
        "validation_lane": "prototype",
        "mode": "interactive-prototype",
        "risk": "standard",
        "features": [],
        "authority": "branch_write",
    }
    advice = build_execution_advice(
        "Fix card padding and spacing only",
        context,
        _flow("development"),
        POLICY,
    ).to_dict()

    assert advice["manual_model_selection_required"] is True
    assert advice["overall_profile"]["auto_switch_model_in_consumer_ui"] is False
    assert advice["overall_profile"]["recommended_capability"] in {"efficient", "balanced"}
    assert advice["quality_boundary"]["advisor_may_satisfy_gates"] is False


def test_advisor_forces_advanced_floor_for_provider_truth_and_production_risk() -> None:
    context = {
        "intent": "improve",
        "change_surface": "PRODUCT",
        "website_type": "saas",
        "domain": "generic",
        "product_archetype": "generic",
        "validation_lane": "production-learning",
        "mode": "production-candidate",
        "risk": "high",
        "features": [],
        "authority": "read_only",
    }
    advice = build_execution_advice(
        "Review provider truth, read-only permissions, production/preview behavior and regression risk",
        context,
        _flow("implementation", "qa"),
        POLICY,
    ).to_dict()

    profile = advice["overall_profile"]
    assert profile["recommended_capability"] == "advanced"
    assert profile["capability_floor"] == "advanced"
    assert profile["reasoning_effort"] == "high"
    assert profile["downgrade_allowed"] is False


def test_external_manifest_contains_advice_without_granting_authority() -> None:
    manifest = build_external_task_manifest(
        SKILLS_ROOT,
        POLICY,
        "Read-only review of architecture and provider integration; do not change code",
        "owner/repo",
        authority="branch_write",
    ).to_dict()

    assert manifest["authority"] == "read_only"
    assert manifest["execution_advice"]["advisory_only"] is True
    assert manifest["execution_advice"]["quality_boundary"]["advisor_may_change_authority"] is False
    assert manifest["evidence_boundary"]["execution_advice_is_not_gate_evidence"] is True


def test_context_strategy_prefers_progressive_disclosure_and_checkpoint_resume() -> None:
    manifest = build_external_task_manifest(
        SKILLS_ROOT,
        POLICY,
        "Redesign a full product experience with research, implementation and responsive QA",
        "owner/repo",
        authority="branch_write",
        overrides={"change_surface": "PRODUCT"},
    ).to_dict()

    advice = manifest["execution_advice"]
    assert advice["context_strategy"]["mode"] == "progressive_disclosure"
    assert advice["context_strategy"]["avoid_eager_loading"] is True
    assert advice["continuation_strategy"]["resume_source"].startswith("latest verified checkpoint")
    assert advice["measurement_strategy"]["measure_before_default_downgrade"] is True
