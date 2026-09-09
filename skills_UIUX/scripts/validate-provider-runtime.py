#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.agent import ProviderNeutralAgentHarness
from runtime.manager import DevelopmentManagerAgent
from runtime.provider import ProviderStageResponse, ScriptedProvider
from runtime.provider_runner import ProviderManagedRunner


def main() -> int:
    errors: list[str] = []
    required = [
        ROOT / "runtime" / "provider.py",
        ROOT / "runtime" / "provider_runner.py",
        ROOT / "schemas" / "provider-stage-response.schema.json",
    ]
    for path in required:
        if not path.exists():
            errors.append(f"missing provider runtime resource: {path.relative_to(ROOT)}")

    for path in [ROOT / "runtime" / "provider.py", ROOT / "runtime" / "provider_runner.py", ROOT / "scripts" / "uiux-agent.py"]:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except Exception as exc:
            errors.append(f"python syntax failure {path.relative_to(ROOT)}: {exc}")

    try:
        json.loads((ROOT / "schemas" / "provider-stage-response.schema.json").read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"provider schema invalid JSON: {exc}")

    try:
        ProviderStageResponse.from_dict(
            {
                "status": "CONTINUE",
                "actions": [{"handoff": "qa"}],
                "summary": "bad",
                "evidence": [],
                "replan_signal": None,
            }
        )
        errors.append("provider contract allowed agent handoff")
    except ValueError:
        pass

    try:
        ProviderStageResponse.from_dict(
            {
                "status": "PASS",
                "actions": [],
                "summary": "unsupported",
                "evidence": [],
                "replan_signal": None,
            }
        )
        errors.append("provider contract allowed PASS without evidence")
    except ValueError:
        pass

    if not errors:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                project = Path(tmp)
                (project / "README.md").write_text("# Shoe store\n", encoding="utf-8")
                harness = ProviderNeutralAgentHarness(ROOT, project)
                manager = DevelopmentManagerAgent(harness)
                managed = manager.start_from_goal(
                    "Tạo website bán giày thể thao hiện đại, có giỏ hàng, checkout và tìm kiếm",
                    authority="branch_write",
                    overrides={"approval_mode": "auto"},
                )
                provider = ScriptedProvider(
                    [
                        {
                            "status": "CONTINUE",
                            "actions": [{"tool": "list_files", "args": {"path": "."}}],
                            "summary": "inspect project",
                            "evidence": [],
                            "replan_signal": None,
                        },
                        {
                            "status": "PASS",
                            "actions": [],
                            "summary": "research grounded",
                            "evidence": ["project file inventory inspected; ecommerce flow and routed research skills active"],
                            "replan_signal": None,
                        },
                        {
                            "status": "PASS",
                            "actions": [{"tool": "write_artifact", "args": {"path": "docs/uiux/design-contract.md", "content": "# Design Contract\n"}}],
                            "summary": "design contract created",
                            "evidence": ["docs/uiux/design-contract.md created for the active design gate"],
                            "replan_signal": None,
                        },
                        {
                            "status": "PASS",
                            "actions": [{"tool": "write_project_file", "args": {"path": "src/index.html", "content": "<!doctype html><title>Shoe Store</title><main>Shop</main>"}}],
                            "summary": "implementation created",
                            "evidence": ["src/index.html written through branch_write-scoped project tool"],
                            "replan_signal": None,
                        },
                        {
                            "status": "CONTINUE",
                            "actions": [{"tool": "read_text", "args": {"path": "src/index.html"}}],
                            "summary": "inspect implementation source",
                            "evidence": [],
                            "replan_signal": None,
                        },
                        {
                            "status": "BLOCKED",
                            "actions": [],
                            "summary": "rendered QA cannot be proven from source inspection alone; browser/render observation adapter is required",
                            "evidence": ["source was inspected but no rendered-pixel observation exists"],
                            "replan_signal": "BLOCKED",
                        },
                    ]
                )
                runner = ProviderManagedRunner(manager, provider)
                result = runner.run_to_boundary(
                    managed,
                    max_cycles=8,
                    max_turns_per_stage=4,
                    auto_replan=False,
                )
                if result.state != "BLOCKED" or managed.active_stage != "qa":
                    errors.append(f"provider run did not stop truthfully at rendered QA boundary: {result.state}/{managed.active_stage}")
                if not (project / "src" / "index.html").exists():
                    errors.append("provider implementation did not write project source")
                stages = [request.stage_id for request in provider.requests]
                if stages != ["research", "research", "design", "implementation", "qa", "qa"]:
                    errors.append(f"unexpected provider stage sequence: {stages}")
                if not provider.requests[1].observations or provider.requests[1].observations[-1].get("tool") != "list_files":
                    errors.append("tool observation was not fed back to provider")
                if any("write_project_file" in {tool["name"] for tool in request.tools} for request in provider.requests if request.agent in {"research", "qa"}):
                    errors.append("read-only specialist received write_project_file capability")
        except Exception as exc:
            errors.append(f"provider managed smoke exception: {type(exc).__name__}: {exc}")

    if not errors:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                project = Path(tmp)
                harness = ProviderNeutralAgentHarness(ROOT, project)
                manager = DevelopmentManagerAgent(harness)
                managed = manager.start_from_goal(
                    "Tạo website ecommerce bán giày",
                    authority="branch_write",
                    overrides={"approval_mode": "manual"},
                )
                provider = ScriptedProvider(
                    [
                        {"status": "PASS", "actions": [], "summary": "research", "evidence": ["research gate evidence"], "replan_signal": None},
                        {"status": "PASS", "actions": [], "summary": "design", "evidence": ["design contract evidence"], "replan_signal": None},
                    ]
                )
                runner = ProviderManagedRunner(manager, provider)
                result = runner.run_to_boundary(managed, max_cycles=4)
                if result.state != "AWAITING_APPROVAL" or managed.active_stage != "design":
                    errors.append("manual Design Contract gate did not stop at approval boundary")
                manager.approve_gate(managed, "design-contract")
                manager.complete_stage(managed)
                if managed.active_stage != "implementation":
                    errors.append("approved completed design gate did not advance directly to implementation")
        except Exception as exc:
            errors.append(f"manual approval smoke exception: {type(exc).__name__}: {exc}")

    print("Provider-managed runtime validation")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Provider runtime passed: structured provider contract + model/tool observation loop + manager routing + truthful QA boundary + approval boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
