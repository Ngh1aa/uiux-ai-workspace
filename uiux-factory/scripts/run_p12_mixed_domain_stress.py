from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from core.dogfood.mixed_domain_matrix import CASES, validate_matrix
from core.runtime.flow_os.flow import FlowPlanner
from core.runtime.flow_os.task_context import GoalInterpreter


FACTORY_ROOT = Path(__file__).resolve().parents[1]
SKILLS = FACTORY_ROOT.parent / "skills_UIUX"
POLICY = json.loads((SKILLS / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))


def _stage_map(flow):
    return {stage.id: stage for stage in flow.stages}


def evaluate() -> dict[str, object]:
    validate_matrix()
    planner = FlowPlanner(SKILLS, POLICY)
    reports: list[dict[str, object]] = []
    for case in CASES:
        profile = GoalInterpreter().interpret(case.goal)
        flow = planner.plan(profile.to_context())
        stages = _stage_map(flow)
        skill_checks = []
        skills_ok = True
        for stage_id, required in case.required_stage_skills:
            present = set(stages.get(stage_id).skills if stage_id in stages else [])
            missing = sorted(set(required).difference(present))
            skills_ok = skills_ok and not missing
            skill_checks.append({"stage": stage_id, "required": list(required), "missing": missing})

        secondary = sorted(item.split(":", 1)[1] for item in profile.evidence if item.startswith("secondary_domain:"))
        expected_secondary = sorted(case.expected_secondary_domains)
        domain_evidence = [item for item in profile.evidence if item.startswith("domain:")]
        checks = {
            "domain_expected": profile.domain == case.expected_domain,
            "archetype_expected": profile.product_archetype == case.expected_archetype,
            "surface_expected": profile.change_surface == case.expected_change_surface,
            "flow_expected": flow.id == case.expected_flow_id,
            "explicit_primary_provenance": f"domain_precedence:explicit-primary->{case.expected_domain}" in profile.evidence,
            "secondary_domains_preserved": secondary == expected_secondary,
            "domain_evidence_clean": domain_evidence == [f"domain:{case.expected_domain}"],
            "specialist_stage_skills_present": skills_ok,
        }
        reports.append(
            {
                "case": asdict(case),
                "contract": profile.to_context(),
                "flow_id": flow.id,
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
        evidence = contract.get("inference", {}).get("evidence", [])
        signature = (
            contract.get("domain"),
            contract.get("product_archetype"),
            contract.get("change_surface"),
            report.get("flow_id"),
            tuple(sorted(item for item in evidence if str(item).startswith("secondary_domain:"))),
        )
        order_pairs.setdefault(str(case["order_pair"]), []).append(signature)

    order_invariance = {
        pair: len(values) == 2 and values[0] == values[1]
        for pair, values in order_pairs.items()
    }
    passed = all(bool(report["passed"]) for report in reports) and all(order_invariance.values())
    return {
        "schema_version": 1,
        "phase": "P1.2-mixed-domain-stress",
        "case_count": len(reports),
        "families": sorted({case.family for case in CASES}),
        "cases": reports,
        "order_invariance": order_invariance,
        "passed": passed,
        "truth_boundary": (
            "PASS proves deterministic canonical primary-domain arbitration, secondary-domain provenance, "
            "FlowPlanner routing and specialist composition for the declared mixed-domain corpus. It does not "
            "claim semantic correctness for arbitrary unstated priorities or replace target-project evidence."
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
