#!/usr/bin/env python3
"""Routing eval grader for skills_UIUX V5.1.

Evaluates skill routing quality using the required_owners / allowed_skills /
forbidden_without_trigger / activation_budget schema.  Does NOT use exact-match
precision/recall — grades outcome-aware routing instead.

Input:  JSONL results with routing telemetry (see ADAPTER-CONTRACT.md).
Output: per-task + aggregate routing quality report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT / "evals" / "tasks"


def load_routing_tasks() -> dict[str, dict[str, Any]]:
    """Load tasks that have a routing evaluation schema."""
    tasks: dict[str, dict[str, Any]] = {}
    for path in sorted(TASK_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        task_id = data.get("id")
        if not task_id or "routing" not in data:
            continue
        tasks[task_id] = data
    return tasks


def load_results(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise ValueError(f"results file not found: {path}")
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def grade_routing(task: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """Grade a single trial against the routing schema."""
    spec = task["routing"]
    telemetry = result.get("routing", {})
    activated = set(telemetry.get("activated_skills", []))
    reasons = telemetry.get("activation_reasons", {})

    required = set(spec.get("required_owners", []))
    allowed = set(spec.get("allowed_skills", []))
    forbidden = set(spec.get("forbidden_without_trigger", []))
    soft_max = spec.get("activation_budget", {}).get("soft_max")

    # --- Coverage: required_owners ---
    required_hit = required & activated
    required_miss = required - activated
    coverage = len(required_hit) / len(required) if required else 1.0

    # --- Forbidden activation ---
    forbidden_hit = forbidden & activated
    forbidden_justified: list[str] = []
    forbidden_unjustified: list[str] = []
    for skill in forbidden_hit:
        if skill in reasons and reasons[skill]:
            forbidden_justified.append(skill)
        else:
            forbidden_unjustified.append(skill)
    forbidden_rate = len(forbidden_unjustified) / len(forbidden) if forbidden else 0.0

    # --- Context budget ---
    count_overhead = None
    if soft_max and len(activated) > 0:
        count_overhead = round(len(activated) / soft_max, 2)

    context_chars = telemetry.get("skill_context_chars")
    ref_chars = telemetry.get("reference_context_chars")
    total_context = telemetry.get("total_loaded_context")

    # --- Unknown skills (activated but not in any category) ---
    known = required | allowed | forbidden
    unknown_activated = activated - known

    # --- Composite score ---
    coverage_score = coverage * 40  # 40 pts max
    forbidden_penalty = len(forbidden_unjustified) * 15  # 15 pts per violation
    budget_penalty = 0
    if count_overhead is not None and count_overhead > 1.5:
        budget_penalty = min((count_overhead - 1.5) * 20, 30)  # up to 30 pts
    unknown_penalty = len(unknown_activated) * 3  # mild: 3 pts per unknown

    score = max(0, min(100, 100 - (40 - coverage_score) - forbidden_penalty - budget_penalty - unknown_penalty))
    passed = coverage >= 0.8 and len(forbidden_unjustified) == 0

    return {
        "task_id": task.get("id"),
        "trial_id": result.get("trial_id", "unknown"),
        "passed": passed,
        "score": round(score, 1),
        "details": {
            "coverage": round(coverage, 4),
            "required_hit": sorted(required_hit),
            "required_miss": sorted(required_miss),
            "forbidden_unjustified": sorted(forbidden_unjustified),
            "forbidden_justified": sorted(forbidden_justified),
            "forbidden_rate": round(forbidden_rate, 4),
            "activated_count": len(activated),
            "soft_max": soft_max,
            "count_overhead": count_overhead,
            "skill_context_chars": context_chars,
            "reference_context_chars": ref_chars,
            "total_loaded_context": total_context,
            "unknown_activated": sorted(unknown_activated),
        },
    }


def generate_report(tasks: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate aggregate routing quality report."""
    grades: list[dict[str, Any]] = []

    for result in results:
        task_id = result.get("task_id")
        if task_id not in tasks:
            continue
        if "routing" not in result:
            continue
        grade = grade_routing(tasks[task_id], result)
        grades.append(grade)

    if not grades:
        return {"error": "no routing results found", "tasks_available": len(tasks)}

    total = len(grades)
    passes = sum(1 for g in grades if g["passed"])
    scores = [g["score"] for g in grades]
    coverages = [g["details"]["coverage"] for g in grades]
    forbidden_rates = [g["details"]["forbidden_rate"] for g in grades]

    context_chars_list = [
        g["details"]["total_loaded_context"]
        for g in grades
        if g["details"]["total_loaded_context"] is not None
    ]
    count_overheads = [
        g["details"]["count_overhead"]
        for g in grades
        if g["details"]["count_overhead"] is not None
    ]

    aggregate: dict[str, Any] = {
        "trials": total,
        "passed": passes,
        "pass_rate": round(passes / total, 4),
        "mean_score": round(sum(scores) / total, 2),
        "mean_coverage": round(sum(coverages) / total, 4),
        "mean_forbidden_rate": round(sum(forbidden_rates) / total, 4),
    }
    if count_overheads:
        aggregate["mean_count_overhead"] = round(sum(count_overheads) / len(count_overheads), 2)
    if context_chars_list:
        aggregate["mean_total_context_chars"] = round(sum(context_chars_list) / len(context_chars_list))

    return {
        "per_trial": grades,
        "aggregate": aggregate,
    }


def cmd_report(args: argparse.Namespace) -> int:
    tasks = load_routing_tasks()
    if not tasks:
        print("No routing eval tasks found", file=sys.stderr)
        return 1

    results = load_results(Path(args.results))
    report = generate_report(tasks, results)

    if "error" in report:
        print(f"WARNING: {report['error']}", file=sys.stderr)
        print(f"  Available routing tasks: {report.get('tasks_available', 0)}")
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        agg = report["aggregate"]
        print(f"Routing Eval Report")
        print(f"{'=' * 50}")
        print(f"Trials:                {agg['trials']}")
        print(f"Passed:                {agg['passed']} ({agg['pass_rate']:.1%})")
        print(f"Mean Score:            {agg['mean_score']:.1f}")
        print(f"Mean Coverage:         {agg['mean_coverage']:.1%}")
        print(f"Mean Forbidden Rate:   {agg['mean_forbidden_rate']:.1%}")
        if "mean_count_overhead" in agg:
            print(f"Mean Count Overhead:   {agg['mean_count_overhead']:.2f}x")
        if "mean_total_context_chars" in agg:
            print(f"Mean Context Chars:    {agg['mean_total_context_chars']:,}")
        print()

        # Per-trial summary
        for g in report["per_trial"]:
            status = "PASS" if g["passed"] else "FAIL"
            d = g["details"]
            print(
                f"  [{status}] {g['task_id']}: "
                f"score={g['score']:.0f}, "
                f"coverage={d['coverage']:.0%}, "
                f"activated={d['activated_count']}"
                + (f"/{d['soft_max']}" if d["soft_max"] else "")
                + (f", forbidden={len(d['forbidden_unjustified'])}" if d["forbidden_unjustified"] else "")
            )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", required=True, help="Path to JSONL results with routing telemetry")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return cmd_report(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
