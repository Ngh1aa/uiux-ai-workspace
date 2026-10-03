from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.runtime.flow_os.work_execution import ArtifactRef, WorkExecutionPlan


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


def artifact(segment_id: str, kind: str, suffix: str = "1") -> ArtifactRef:
    return ArtifactRef(
        id=f"{segment_id}-{kind}-{suffix}",
        kind=kind,
        producer_segment_id=segment_id,
        uri=f"artifact://{segment_id}/{kind}/{suffix}",
    )


def pass_current(plan: WorkExecutionPlan, segment_id: str) -> None:
    node = plan.start(segment_id)
    plan.pass_segment(
        segment_id,
        [artifact(segment_id, kind) for kind in node.expected_output_kinds],
    )


def snapshot(plan: WorkExecutionPlan) -> dict[str, object]:
    return {
        "completion_status": plan.completion_status,
        "runnable": plan.runnable_segment_ids(),
        "statuses": {node.segment_id: node.status for node in plan.nodes},
        "artifact_kinds": [artifact.kind for artifact in plan.artifacts.values()],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    factory = ProfessionalWebsiteFlow(SKILLS)
    goal = "Audit the landing page, redesign checkout, implement it, and QA it."
    _profile, plan = factory.resolve_execution_plan(goal)
    evidence: dict[str, object] = {
        "version": plan.version,
        "goal": goal,
        "initial": snapshot(plan),
    }

    pass_current(plan, "work-1")
    evidence["after_audit"] = {
        **snapshot(plan),
        "design_inputs": [item.to_dict() for item in plan.input_artifacts("work-2")],
    }

    pass_current(plan, "work-2")
    pass_current(plan, "work-3")
    pass_current(plan, "work-4")
    evidence["completed"] = snapshot(plan)

    serialized = plan.to_dict()
    resumed = WorkExecutionPlan.from_dict(serialized)
    evidence["resume_round_trip_equal"] = resumed.to_dict() == serialized

    affected = resumed.reset_from("work-4")
    evidence["qa_partial_rerun"] = {
        "affected": affected,
        **snapshot(resumed),
    }

    _profile, failed = factory.resolve_execution_plan(goal)
    failed.start("work-1")
    failed.fail_segment("work-1", "audit evidence incomplete")
    evidence["failure_cascade"] = snapshot(failed)

    constraint_goal = (
        "Redesign checkout, implement it, and QA it; "
        "keep animation unchanged; do not change navigation."
    )
    _profile, constrained = factory.resolve_execution_plan(constraint_goal)
    evidence["constraint_gate"] = {
        "qa_expected_outputs": constrained.nodes[-1].expected_output_kinds,
        "preserve": constrained.nodes[-1].preserve,
        "forbidden": constrained.nodes[-1].forbidden,
    }

    repair_goal = "Redesign checkout, implement it, QA it, repair checkout, implement it, and QA it."
    _profile, repair = factory.resolve_execution_plan(repair_goal)
    evidence["repair_loop"] = {
        "phases": [node.phase for node in repair.nodes],
        "dependencies": {node.segment_id: node.depends_on for node in repair.nodes},
    }

    evidence["passed"] = (
        evidence["initial"]["runnable"] == ["work-1"]
        and evidence["completed"]["completion_status"] == "completed"
        and evidence["resume_round_trip_equal"] is True
        and evidence["qa_partial_rerun"]["runnable"] == ["work-4"]
        and evidence["failure_cascade"]["statuses"]["work-2"] == "blocked"
        and "constraint-evidence" in evidence["constraint_gate"]["qa_expected_outputs"]
        and evidence["repair_loop"]["dependencies"]["work-6"] == ["work-5"]
    )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0 if evidence["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
