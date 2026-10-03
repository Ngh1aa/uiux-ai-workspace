from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from core.dogfood.ambiguous_domain_matrix import CASES, validate_matrix
from core.runtime.flow_os.flow import AmbiguousRoutingError, FlowPlanner
from core.runtime.flow_os.task_context import GoalInterpreter


FACTORY_ROOT = Path(__file__).resolve().parents[1]
SKILLS = FACTORY_ROOT.parent / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


def evaluate() -> dict[str, object]:
    validate_matrix()
    planner = FlowPlanner(SKILLS, POLICY)
    interpreter = GoalInterpreter()
    reports: list[dict[str, object]] = []

    for case in CASES:
        profile = interpreter.interpret(case.goal, target_truth=case.target_truth)
        context = profile.to_context()
        checks: dict[str, bool] = {
            "candidate_domains_expected": profile.candidate_domains == list(case.expected_candidates),
            "status_expected": profile.routing_status == case.expected_status,
            "conflict_provenance_present": f"domain_conflict:{'|'.join(case.expected_candidates)}" in profile.evidence,
        }
        flow_id: str | None = None
        planner_result = "not-run"
        skill_checks: list[dict[str, object]] = []

        if case.expected_status == "ambiguous":
            checks.update(
                {
                    "domain_unresolved": profile.domain == "unresolved",
                    "archetype_unresolved": profile.product_archetype == "unresolved",
                    "confidence_reduced": profile.confidence <= 0.50,
                    "needs_evidence": profile.resolution_source == "needs-evidence",
                    "needs_evidence_provenance": "routing_action:needs-evidence" in profile.evidence,
                }
            )
            try:
                planner.plan(context)
                checks["planner_fail_closed"] = False
                planner_result = "unexpected-plan"
            except AmbiguousRoutingError as exc:
                checks["planner_fail_closed"] = exc.candidate_domains == case.expected_candidates
                planner_result = "blocked-ambiguous"
        else:
            checks.update(
                {
                    "truth_domain_expected": profile.domain == case.target_truth_domain,
                    "truth_archetype_expected": profile.product_archetype == case.target_truth_archetype,
                    "truth_resolution_source": profile.resolution_source == "target-project-truth",
                    "confidence_recovered": profile.confidence >= 0.85,
                    "truth_provenance_present": f"routing_resolution:target-truth->{case.target_truth_domain}" in profile.evidence,
                }
            )
            try:
                flow = planner.plan(context)
                flow_id = flow.id
                planner_result = "planned"
                stage_map = {stage.id: stage for stage in flow.stages}
                for stage_id, required in case.required_stage_skills:
                    present = set(stage_map.get(stage_id).skills if stage_id in stage_map else [])
                    missing = sorted(set(required).difference(present))
                    skill_checks.append({"stage": stage_id, "required": list(required), "missing": missing})
                checks["specialist_stage_skills_present"] = all(not item["missing"] for item in skill_checks)
            except Exception as exc:  # evidence runner must preserve the failure reason
                planner_result = f"error:{type(exc).__name__}:{exc}"
                checks["specialist_stage_skills_present"] = False

        reports.append(
            {
                "case": asdict(case),
                "contract": context,
                "flow_id": flow_id,
                "planner_result": planner_result,
                "skill_checks": skill_checks,
                "checks": checks,
                "passed": all(checks.values()),
            }
        )

    order_pairs: dict[str, list[tuple[object, ...]]] = {}
    for report in reports:
        case = report["case"]
        contract = report["contract"]
        assert isinstance(case, dict) and isinstance(contract, dict)
        pair = str(case.get("order_pair") or "")
        if not pair:
            continue
        inference = contract.get("inference", {})
        assert isinstance(inference, dict)
        signature = (
            inference.get("routing_status"),
            tuple(inference.get("candidate_domains", [])),
            contract.get("domain"),
            contract.get("product_archetype"),
            contract.get("change_surface"),
            tuple(sorted(contract.get("features", []))),
            inference.get("confidence"),
        )
        order_pairs.setdefault(pair, []).append(signature)

    order_invariance = {
        pair: len(values) == 2 and values[0] == values[1]
        for pair, values in order_pairs.items()
    }
    passed = all(bool(report["passed"]) for report in reports) and all(order_invariance.values())
    return {
        "schema_version": 1,
        "phase": "P1.3-ambiguous-routing-evidence",
        "case_count": len(reports),
        "families": sorted({case.family for case in CASES}),
        "ambiguous_case_count": sum(case.expected_status == "ambiguous" for case in CASES),
        "truth_resolved_case_count": sum(case.expected_status == "resolved" for case in CASES),
        "cases": reports,
        "order_invariance": order_invariance,
        "passed": passed,
        "truth_boundary": (
            "PASS proves fail-closed routing for the declared no-owner mixed-domain corpus and deterministic recovery "
            "when target-project truth selects one of the observed candidates. It does not infer unstated human intent "
            "or claim that arbitrary domain language can be resolved without additional evidence."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    report = evaluate()
    path = Path(args.report)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
