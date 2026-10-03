from __future__ import annotations

from pathlib import Path

import pytest

from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.runtime.flow_os.flow import AmbiguousRoutingError
from core.runtime.flow_os.work_execution import (
    ArtifactRef,
    ExecutionTransitionError,
    WorkExecutionPlan,
)


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


def _factory() -> ProfessionalWebsiteFlow:
    return ProfessionalWebsiteFlow(SKILLS)


def _artifact(segment_id: str, kind: str, suffix: str = "1") -> ArtifactRef:
    return ArtifactRef(
        id=f"{segment_id}-{kind}-{suffix}",
        kind=kind,
        producer_segment_id=segment_id,
        uri=f"artifact://{segment_id}/{kind}/{suffix}",
    )


def _pass_current(plan: WorkExecutionPlan, segment_id: str) -> None:
    node = plan.start(segment_id)
    plan.pass_segment(
        segment_id,
        [_artifact(segment_id, kind) for kind in node.expected_output_kinds],
    )


def _baseline() -> WorkExecutionPlan:
    _profile, plan = _factory().resolve_execution_plan(
        "Audit the landing page, redesign checkout, implement it, and QA it."
    )
    return plan


def test_p15_initial_state_has_one_runnable_owner_and_ordered_dependencies() -> None:
    plan = _baseline()
    assert [node.segment_id for node in plan.nodes] == ["work-1", "work-2", "work-3", "work-4"]
    assert [node.depends_on for node in plan.nodes] == [[], ["work-1"], ["work-2"], ["work-3"]]
    assert plan.runnable_segment_ids() == ["work-1"]
    assert [node.status for node in plan.nodes] == ["runnable", "pending", "pending", "pending"]
    assert plan.completion_status == "in_progress"


def test_p15_artifact_handoff_unlocks_only_the_next_segment() -> None:
    plan = _baseline()
    _pass_current(plan, "work-1")

    assert plan.runnable_segment_ids() == ["work-2"]
    inputs = plan.input_artifacts("work-2")
    assert [artifact.kind for artifact in inputs] == ["audit-findings"]
    assert inputs[0].producer_segment_id == "work-1"
    assert plan._node("work-3").status == "pending"


def test_p15_each_lifecycle_phase_requires_declared_output_before_pass() -> None:
    plan = _baseline()
    plan.start("work-1")
    with pytest.raises(ExecutionTransitionError, match="audit-findings"):
        plan.pass_segment("work-1", [])


def test_p15_wrong_producer_artifact_cannot_satisfy_completion_gate() -> None:
    plan = _baseline()
    plan.start("work-1")
    with pytest.raises(ExecutionTransitionError, match="belongs to work-9"):
        plan.pass_segment("work-1", [_artifact("work-9", "audit-findings")])


def test_p15_failure_blocks_all_descendants_without_running_them() -> None:
    plan = _baseline()
    plan.start("work-1")
    plan.fail_segment("work-1", "audit evidence incomplete")

    assert plan._node("work-1").status == "failed"
    assert [node.status for node in plan.nodes[1:]] == ["blocked", "blocked", "blocked"]
    assert all("upstream_failed" in (node.blocking_reason or "") for node in plan.nodes[1:])
    assert plan.completion_status == "failed"


def test_p15_reset_from_failed_owner_reopens_only_affected_subgraph() -> None:
    plan = _baseline()
    _pass_current(plan, "work-1")
    plan.start("work-2")
    plan.fail_segment("work-2", "design review failed")

    affected = plan.reset_from("work-2")
    assert affected == ["work-2", "work-3", "work-4"]
    assert plan._node("work-1").status == "passed"
    assert plan.runnable_segment_ids() == ["work-2"]
    assert any(artifact.producer_segment_id == "work-1" for artifact in plan.artifacts.values())


def test_p15_partial_qa_rerun_keeps_upstream_outputs_and_attempt_history() -> None:
    plan = _baseline()
    for segment_id in ("work-1", "work-2", "work-3", "work-4"):
        _pass_current(plan, segment_id)
    assert plan.completion_status == "completed"

    upstream_ids = {
        artifact.id
        for artifact in plan.artifacts.values()
        if artifact.producer_segment_id != "work-4"
    }
    affected = plan.reset_from("work-4")

    assert affected == ["work-4"]
    assert [plan._node(segment).status for segment in ("work-1", "work-2", "work-3")] == [
        "passed",
        "passed",
        "passed",
    ]
    assert plan.runnable_segment_ids() == ["work-4"]
    assert upstream_ids.issubset(set(plan.artifacts))
    assert plan._node("work-4").attempts == 1


def test_p15_serialization_round_trip_preserves_resume_state_and_provenance() -> None:
    plan = _baseline()
    _pass_current(plan, "work-1")
    payload = plan.to_dict()
    restored = WorkExecutionPlan.from_dict(payload)

    assert restored.to_dict() == payload
    assert restored.runnable_segment_ids() == ["work-2"]
    assert restored.input_artifacts("work-2")[0].producer_segment_id == "work-1"


def test_p15_constraints_become_runtime_invariants_and_qa_evidence_gate() -> None:
    _profile, plan = _factory().resolve_execution_plan(
        "Redesign checkout, implement it, and QA it; keep animation unchanged; do not change navigation."
    )
    qa = plan.nodes[-1]
    assert any("animation" in value for value in qa.preserve)
    assert any("navigation" in value for value in qa.forbidden)
    assert qa.expected_output_kinds == ["qa-evidence", "constraint-evidence"]

    _pass_current(plan, "work-1")
    _pass_current(plan, "work-2")
    plan.start("work-3")
    with pytest.raises(ExecutionTransitionError, match="constraint-evidence"):
        plan.pass_segment("work-3", [_artifact("work-3", "qa-evidence")])


def test_p15_complete_lifecycle_reaches_completed_only_after_qa_evidence() -> None:
    plan = _baseline()
    for segment_id in ("work-1", "work-2", "work-3"):
        _pass_current(plan, segment_id)
    assert plan.completion_status == "in_progress"
    assert plan.runnable_segment_ids() == ["work-4"]

    _pass_current(plan, "work-4")
    assert plan.completion_status == "completed"
    assert all(node.status == "passed" for node in plan.nodes)


def test_p15_repair_loop_is_ordered_and_second_qa_depends_on_repair_implementation() -> None:
    _profile, plan = _factory().resolve_execution_plan(
        "Redesign checkout, implement it, QA it, repair checkout, implement it, and QA it."
    )
    assert [node.phase for node in plan.nodes] == [
        "design",
        "implementation",
        "qa",
        "design",
        "implementation",
        "qa",
    ]
    assert plan.nodes[-1].depends_on == ["work-5"]


def test_p15_p13_ambiguity_still_fails_closed_before_execution_state_exists() -> None:
    goal = "Audit an AI workspace for fintech treasury, redesign its dashboard, implement it, and QA it."
    with pytest.raises(AmbiguousRoutingError):
        _factory().resolve_execution_plan(goal)


def test_p15_target_truth_can_resolve_ambiguity_then_create_stateful_plan() -> None:
    goal = "Audit an AI workspace for fintech treasury, redesign its dashboard, implement it, and QA it."
    truth = {
        "domain": "ai-software",
        "product_archetype": "ai-workspace",
        "source": "p1.5-fixture",
    }
    profile, plan = _factory().resolve_execution_plan(goal, target_truth=truth)
    assert profile.routing_status == "resolved"
    assert profile.resolution_source == "target-project-truth"
    assert plan.runnable_segment_ids() == ["work-1"]
