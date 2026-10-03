from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from core.orchestration.intelligent_flow import ProfessionalWebsiteFlow
from core.runtime.flow_os.execution_driver import CommandRunnerAdapter


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SKILLS = WORKSPACE / "skills_UIUX"
FIXTURE = ROOT / "tests" / "fixtures" / "p16_segment_runner.py"
GOAL = "Audit the landing page, redesign checkout, implement it, and QA it."


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="p16-driver-") as temp:
        temp_root = Path(temp)
        target = temp_root / "target"
        target.mkdir()
        exchange = temp_root / "exchange"
        runner = CommandRunnerAdapter(
            [sys.executable, str(FIXTURE)],
            work_dir=WORKSPACE,
            exchange_dir=exchange,
            extra_env={
                "P16_WORKSPACE": str(target),
                "P16_FAIL_QA_ONCE": "1",
            },
        )
        factory = ProfessionalWebsiteFlow(SKILLS)
        profile, driver = factory.resolve_execution_driver(
            GOAL,
            runner,
            workspace_root=target,
            checkpoint_path=temp_root / "checkpoint.json",
        )
        completion = driver.run_until_blocked(max_steps=10)
        nodes = {node.segment_id: node for node in driver.execution_plan.nodes}
        repair_event = next(
            (event for event in driver.history if event.get("failure_class") == "PRODUCT_QA_FAILED"),
            None,
        )
        report = {
            "version": "1.0",
            "passed": completion == "completed",
            "completion_status": completion,
            "routing_status": profile.routing_status,
            "runner_invocations": runner.invocations,
            "statuses": {key: node.status for key, node in nodes.items()},
            "attempts": {key: node.attempts for key, node in nodes.items()},
            "artifact_classes": sorted({record.artifact_class for record in driver.registry.records.values()}),
            "accepted_artifacts": sorted(
                record.id for record in driver.registry.records.values() if record.accepted_for_handoff
            ),
            "failure_artifacts": sorted(
                record.id for record in driver.registry.records.values() if not record.accepted_for_handoff
            ),
            "repair_owner_segment_id": repair_event.get("repair_owner_segment_id") if repair_event else None,
            "repair_modes": [
                event["segment_id"] for event in driver.history if event.get("runner_mode") == "repair"
            ],
            "checkpoint_exists": (temp_root / "checkpoint.json").is_file(),
            "history": driver.history,
        }
        report["passed"] = bool(
            report["passed"]
            and report["runner_invocations"] == 6
            and report["repair_owner_segment_id"] == "work-3"
            and report["attempts"].get("work-1") == 1
            and report["attempts"].get("work-2") == 1
            and report["attempts"].get("work-3") == 2
            and report["attempts"].get("work-4") == 2
            and {"file", "report", "screenshot", "commit"}.issubset(set(report["artifact_classes"]))
            and report["failure_artifacts"]
            and report["checkpoint_exists"]
        )
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
