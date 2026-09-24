#!/usr/bin/env python3
"""Capture a V5 eval baseline snapshot for later comparison with V5.1.

Records the current state of the skill library and any existing eval results
so that post-V5.1 improvements can be measured against a known starting point.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT / "evals" / "tasks"
BASELINES_DIR = ROOT / "evals" / "baselines"


def get_git_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=ROOT, check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def get_task_set_info() -> dict[str, Any]:
    task_ids: list[str] = []
    for path in sorted(TASK_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            task_id = data.get("id", path.stem)
            task_ids.append(task_id)
        except (json.JSONDecodeError, OSError):
            task_ids.append(f"ERROR:{path.name}")

    id_hash = hashlib.sha256("|".join(sorted(task_ids)).encode()).hexdigest()[:16]
    return {
        "count": len(task_ids),
        "ids": sorted(task_ids),
        "hash": id_hash,
    }


def load_results(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def summarize_results(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"trials": 0, "note": "no results provided"}

    passes = sum(1 for r in rows if r.get("passed"))
    scores = [float(r["score"]) for r in rows if "score" in r]
    task_ids = {r.get("task_id") for r in rows}

    summary: dict[str, Any] = {
        "trials": len(rows),
        "tasks_covered": len(task_ids),
        "successes": passes,
        "pass_rate": round(passes / len(rows), 4) if rows else 0,
    }
    if scores:
        summary["mean_score"] = round(sum(scores) / len(scores), 2)
        summary["min_score"] = round(min(scores), 2)
        summary["max_score"] = round(max(scores), 2)

    # Routing metrics if present
    routing_rows = [r for r in rows if r.get("routing")]
    if routing_rows:
        context_chars = [
            r["routing"]["skill_context_chars"]
            for r in routing_rows
            if "skill_context_chars" in r.get("routing", {})
        ]
        summary["routing"] = {
            "trials_with_telemetry": len(routing_rows),
            "mean_activated_skills": round(
                sum(len(r["routing"].get("activated_skills", [])) for r in routing_rows) / len(routing_rows), 1
            ),
        }
        if context_chars:
            summary["routing"]["mean_context_chars"] = round(sum(context_chars) / len(context_chars))

    return summary


def capture(args: argparse.Namespace) -> int:
    commit_sha = get_git_sha()
    task_set = get_task_set_info()
    timestamp = datetime.now(timezone.utc).isoformat()

    baseline: dict[str, Any] = {
        "version": "v5-baseline",
        "commit_sha": commit_sha,
        "captured_at": timestamp,
        "task_set": task_set,
    }

    if args.results:
        results_path = Path(args.results)
        rows = load_results(results_path)
        baseline["results_file"] = str(results_path)
        baseline["results_summary"] = summarize_results(rows)
    else:
        baseline["results_summary"] = {"note": "no results file provided — structure-only baseline"}

    if args.provider:
        baseline["provider"] = args.provider
    if args.model:
        baseline["model"] = args.model

    BASELINES_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    short_sha = commit_sha[:8] if commit_sha != "unknown" else "unknown"
    out_path = BASELINES_DIR / f"{short_sha}-{date_str}.json"

    out_path.write_text(
        json.dumps(baseline, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Baseline captured: {out_path.relative_to(ROOT)}")
    print(f"  commit:  {commit_sha}")
    print(f"  tasks:   {task_set['count']} (hash {task_set['hash']})")
    if "results_summary" in baseline and baseline["results_summary"].get("trials"):
        s = baseline["results_summary"]
        print(f"  trials:  {s['trials']} ({s['pass_rate']:.1%} pass rate)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", help="Path to JSONL results file (optional)")
    parser.add_argument("--provider", help="Provider/IDE name (optional)")
    parser.add_argument("--model", help="Model identifier (optional)")
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return capture(args)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
