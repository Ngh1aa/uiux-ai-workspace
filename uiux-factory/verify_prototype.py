from __future__ import annotations

import argparse
import sys
from pathlib import Path

from core.verification.prototype_acceptance import PrototypeAcceptanceEvaluator


def latest_quality_pair(run_dir: Path) -> tuple[Path, Path]:
    quality_root = run_dir / "quality-loop"
    if not quality_root.is_dir():
        raise FileNotFoundError(f"Quality loop directory not found: {quality_root}")

    candidates: list[tuple[Path, Path]] = []
    for iteration in sorted(quality_root.glob("iteration-*")):
        browser = iteration / "browser-report.json"
        critic = iteration / "visual-critic.json"
        if browser.is_file() and critic.is_file():
            candidates.append((browser, critic))

    if not candidates:
        raise FileNotFoundError(
            "No quality-loop iteration contains both browser-report.json and visual-critic.json"
        )
    return candidates[-1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify a Factory run against the 56-rule prototype evidence contract."
    )
    parser.add_argument("--run-dir", required=True, help="Path to runs/<run-id>")
    parser.add_argument(
        "--output",
        default="prototype-acceptance.json",
        help="Output filename inside the run directory (default: prototype-acceptance.json)",
    )
    parser.add_argument(
        "--require-final-approval",
        action="store_true",
        help="Exit non-zero unless final_status=approved. Without this flag, only machine_status blocks.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_dir = Path(args.run_dir).resolve()
    if not run_dir.is_dir():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    browser_path, critic_path = latest_quality_pair(run_dir)
    report = PrototypeAcceptanceEvaluator().evaluate(
        run_id=run_dir.name,
        browser_report_path=browser_path,
        visual_critic_path=critic_path,
    )
    output_path = run_dir / args.output
    output_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    print(f"Prototype acceptance: {output_path}")
    print(
        "summary: "
        f"passed={report.summary.passed} "
        f"failed={report.summary.failed} "
        f"inapplicable={report.summary.inapplicable} "
        f"cantTell={report.summary.cantTell} "
        f"untested={report.summary.untested}"
    )
    print(f"machine_status={report.machine_status}")
    print(f"final_status={report.final_status}")

    if report.machine_status != "passed":
        return 2
    if args.require_final_approval and report.final_status != "approved":
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
