#!/usr/bin/env python3
"""Provider-neutral UI/UX agent eval result harness for skills_UIUX V5.

This script does not call a model provider. Provider/IDE adapters execute tasks and emit
JSONL trial results following evals/ADAPTER-CONTRACT.md. The harness validates and
summarizes those results consistently across providers.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT / "evals" / "tasks"
SMOKE_RESULTS = ROOT / "evals" / "fixtures" / "sample-trials.jsonl"
REQUIRED_RESULT_KEYS = {"task_id", "trial_id", "passed", "score"}


def load_tasks() -> dict[str, dict[str, Any]]:
    tasks: dict[str, dict[str, Any]] = {}
    for path in sorted(TASK_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        task_id = data.get("id")
        if not isinstance(task_id, str) or not task_id:
            raise ValueError(f"{path}: missing valid id")
        if task_id in tasks:
            raise ValueError(f"duplicate task id: {task_id}")
        tasks[task_id] = data
    return tasks


def load_results(path: Path, task_ids: set[str]) -> list[dict[str, Any]]:
    if not path.exists():
        raise ValueError(f"results file not found: {path}")

    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc

        missing = REQUIRED_RESULT_KEYS - row.keys()
        if missing:
            raise ValueError(f"{path}:{line_no}: missing keys {sorted(missing)}")

        task_id = row["task_id"]
        trial_id = row["trial_id"]
        passed = row["passed"]
        score = row["score"]

        if task_id not in task_ids:
            raise ValueError(f"{path}:{line_no}: unknown task_id {task_id}")
        if not isinstance(trial_id, str) or not trial_id:
            raise ValueError(f"{path}:{line_no}: trial_id must be a non-empty string")
        if not isinstance(passed, bool):
            raise ValueError(f"{path}:{line_no}: passed must be boolean")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 100:
            raise ValueError(f"{path}:{line_no}: score must be a number in [0, 100]")
        if "graders" in row and not isinstance(row["graders"], dict):
            raise ValueError(f"{path}:{line_no}: graders must be an object when provided")

        key = (task_id, trial_id)
        if key in seen:
            raise ValueError(f"{path}:{line_no}: duplicate trial {task_id}/{trial_id}")
        seen.add(key)
        rows.append(row)

    if not rows:
        raise ValueError(f"results file is empty: {path}")
    return rows


def summarize(rows: list[dict[str, Any]], k: int) -> dict[str, Any]:
    if k < 1:
        raise ValueError("k must be >= 1")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["task_id"]].append(row)

    task_summaries: dict[str, Any] = {}
    all_passes = 0
    all_trials = 0
    all_scores: list[float] = []

    for task_id, trials in sorted(grouped.items()):
        n = len(trials)
        successes = sum(1 for trial in trials if trial["passed"])
        p = successes / n
        scores = [float(trial["score"]) for trial in trials]
        task_summaries[task_id] = {
            "trials": n,
            "successes": successes,
            "pass_rate": round(p, 4),
            "mean_score": round(statistics.fmean(scores), 2),
            "min_score": round(min(scores), 2),
            "max_score": round(max(scores), 2),
            "estimated_pass_at_k": round(1 - math.pow(1 - p, k), 4),
            "estimated_pass_pow_k": round(math.pow(p, k), 4),
            "k": k,
        }
        all_passes += successes
        all_trials += n
        all_scores.extend(scores)

    overall_p = all_passes / all_trials
    return {
        "tasks": task_summaries,
        "overall": {
            "tasks": len(task_summaries),
            "trials": all_trials,
            "successes": all_passes,
            "pass_rate": round(overall_p, 4),
            "mean_score": round(statistics.fmean(all_scores), 2),
            "estimated_pass_at_k": round(1 - math.pow(1 - overall_p, k), 4),
            "estimated_pass_pow_k": round(math.pow(overall_p, k), 4),
            "k": k,
            "note": "pass@k/pass^k values are estimates from observed trial success rates, not population guarantees",
        },
    }


def print_summary(data: dict[str, Any]) -> None:
    for task_id, item in data["tasks"].items():
        print(
            f"{task_id}: {item['successes']}/{item['trials']} pass "
            f"({item['pass_rate']:.1%}), mean={item['mean_score']:.1f}, "
            f"est pass@{item['k']}={item['estimated_pass_at_k']:.1%}, "
            f"est pass^{item['k']}={item['estimated_pass_pow_k']:.1%}"
        )
    overall = data["overall"]
    print(
        f"OVERALL: {overall['successes']}/{overall['trials']} pass "
        f"({overall['pass_rate']:.1%}), mean={overall['mean_score']:.1f}"
    )
    print(overall["note"])


def cmd_list(args: argparse.Namespace) -> int:
    tasks = load_tasks()
    if args.json:
        print(json.dumps(list(tasks.values()), ensure_ascii=False, indent=2))
    else:
        for task_id, task in tasks.items():
            print(f"{task_id}\t{task.get('category', '?')}\t{task.get('prompt', '')}")
        print(f"{len(tasks)} tasks")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    tasks = load_tasks()
    rows = load_results(Path(args.results), set(tasks))
    print(f"Valid: {len(rows)} trial results across {len({r['task_id'] for r in rows})} tasks")
    return 0


def cmd_summarize(args: argparse.Namespace) -> int:
    tasks = load_tasks()
    rows = load_results(Path(args.results), set(tasks))
    data = summarize(rows, args.k)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_summary(data)
    return 0


def cmd_smoke(_: argparse.Namespace) -> int:
    tasks = load_tasks()
    rows = load_results(SMOKE_RESULTS, set(tasks))
    data = summarize(rows, 3)
    if data["overall"]["trials"] < 3:
        raise ValueError("smoke fixture must include at least 3 trials")
    print("V5 eval harness smoke passed")
    print_summary(data)
    return 0


def cmd_routing(args: argparse.Namespace) -> int:
    """Delegate to routing-eval-report for V5.1 routing quality evaluation."""
    import importlib.util

    script = Path(__file__).parent / "routing-eval-report.py"
    if not script.exists():
        print(f"ERROR: {script} not found", file=sys.stderr)
        return 1
    spec = importlib.util.spec_from_file_location("routing_eval_report", script)
    if spec is None or spec.loader is None:
        print(f"ERROR: cannot load {script}", file=sys.stderr)
        return 1
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    routing_args = mod.build_parser().parse_args(
        ["--results", args.results] + (["--json"] if args.json else [])
    )
    return mod.cmd_report(routing_args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="list eval tasks")
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_validate = sub.add_parser("validate-results", help="validate provider-neutral JSONL trial results")
    p_validate.add_argument("--results", required=True)
    p_validate.set_defaults(func=cmd_validate)

    p_summary = sub.add_parser("summarize", help="summarize multi-trial results")
    p_summary.add_argument("--results", required=True)
    p_summary.add_argument("--k", type=int, default=3)
    p_summary.add_argument("--json", action="store_true")
    p_summary.set_defaults(func=cmd_summarize)

    p_smoke = sub.add_parser("smoke", help="run built-in harness smoke test")
    p_smoke.set_defaults(func=cmd_smoke)

    p_routing = sub.add_parser("routing-report", help="generate routing eval quality report (V5.1)")
    p_routing.add_argument("--results", required=True, help="Path to JSONL results with routing telemetry")
    p_routing.add_argument("--json", action="store_true")
    p_routing.set_defaults(func=cmd_routing)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.func(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
