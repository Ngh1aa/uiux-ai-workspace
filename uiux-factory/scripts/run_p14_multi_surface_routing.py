from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.dogfood.multi_surface_matrix import CASES, validate_matrix
from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT.parent / "skills_UIUX"


def evaluate() -> dict[str, object]:
    validate_matrix()
    factory = ProfessionalWebsiteFlow(SKILLS)
    case_results: list[dict[str, object]] = []

    for case in CASES:
        contract = factory.resolve_contract(case.goal)
        checks: dict[str, bool] = {
            "routing_mode_expected": contract.routing_mode == case.expected_mode,
        }
        result: dict[str, object] = {
            "case_id": case.case_id,
            "family": case.family,
            "goal": case.goal,
            "routing_mode": contract.routing_mode,
            "work_segments": [segment.to_dict() for segment in contract.segments],
        }

        if case.expected_mode == "single":
            checks["no_fake_segments"] = contract.segments == []
            if contract.routing_mode == "single":
                profile, flow = factory.resolve(case.goal)
                result["flow_id"] = flow.id
                result["change_surface"] = profile.change_surface
                checks["single_flow_planned"] = bool(flow.id)
        else:
            checks["segment_count_expected"] = len(contract.segments) == len(case.expected_segments)
            profile, work_plan = factory.resolve_work_plan(case.goal)
            result["profile_domain"] = profile.domain
            result["resolved_segments"] = [segment.to_dict() for segment in work_plan.segments]

            segment_checks: list[dict[str, object]] = []
            for actual, expected in zip(work_plan.segments, case.expected_segments, strict=False):
                current = {
                    "phase": actual.phase == expected.phase,
                    "intent": actual.intent == expected.intent,
                    "scope": tuple(actual.scope) == expected.scope,
                    "surface": actual.change_surface == expected.surface,
                    "flow": actual.flow.id == expected.flow_id,
                    "active_stage": expected.active_stage in actual.active_stage_ids,
                }
                segment_checks.append(current)
            result["segment_checks"] = segment_checks
            checks["segments_expected"] = (
                len(segment_checks) == len(case.expected_segments)
                and all(all(values.values()) for values in segment_checks)
            )

            if case.preserve_contains:
                checks["preserve_inherited"] = all(
                    all(any(token in value for value in (segment.preserve or [])) for token in case.preserve_contains)
                    for segment in contract.segments
                )
            if case.forbidden_contains:
                checks["forbidden_inherited"] = all(
                    all(any(token in value for value in (segment.forbidden or [])) for token in case.forbidden_contains)
                    for segment in contract.segments
                )

        passed = all(checks.values())
        result["checks"] = checks
        result["passed"] = passed
        case_results.append(result)

    passed = all(bool(item["passed"]) for item in case_results)
    return {
        "schema_version": 1,
        "phase": "P1.4-multi-intent-multi-surface-routing",
        "case_count": len(CASES),
        "sequence_case_count": sum(case.expected_mode == "sequence" for case in CASES),
        "single_control_count": sum(case.expected_mode == "single" for case in CASES),
        "families": sorted({case.family for case in CASES}),
        "cases": case_results,
        "passed": passed,
        "truth_boundary": (
            "PASS proves that the declared explicit multi-intent/multi-surface corpus is decomposed into ordered "
            "work owners and each owner uses the smallest canonical flow. It does not infer hidden task boundaries "
            "when the prompt supplies no actionable lifecycle or surface cues."
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
