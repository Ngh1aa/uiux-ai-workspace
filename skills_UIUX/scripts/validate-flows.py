#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.flow import DevelopmentManager, validate_flow_document

WEBSITE_TYPES = ["corporate", "ecommerce", "education", "government", "hospitality", "news", "real-estate", "saas", "startup", "portfolio", "nonprofit", "landing"]


def main() -> int:
    errors: list[str] = []
    flows_dir = ROOT / "flows"
    schema_path = ROOT / "schemas" / "flow.schema.json"
    policy_path = ROOT / "runtime" / "runtime-policy.json"

    for required in (flows_dir, schema_path, policy_path, ROOT / "runtime" / "flow.py", ROOT / "runtime" / "manager.py"):
        if not required.exists():
            errors.append(f"missing flow runtime resource: {required.relative_to(ROOT)}")

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        if schema.get("properties", {}).get("schema_version", {}).get("const") != 1:
            errors.append("flow schema must pin schema_version=1")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid schemas/flow.schema.json: {exc}")

    try:
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        policy = {}
        errors.append(f"invalid runtime policy: {exc}")

    roles = set(policy.get("roles", {}))
    referenced_skills: set[str] = set()
    flow_ids: set[str] = set()

    if flows_dir.exists():
        for path in sorted(flows_dir.glob("*.json")):
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{path.relative_to(ROOT)} invalid JSON: {exc}")
                continue
            errors.extend(f"{path.relative_to(ROOT)}: {item}" for item in validate_flow_document(doc))
            flow_id = str(doc.get("id", ""))
            if flow_id in flow_ids:
                errors.append(f"duplicate flow id: {flow_id}")
            flow_ids.add(flow_id)
            for stage in doc.get("stages", []):
                if stage.get("agent") not in roles:
                    errors.append(f"{path.name}: unknown stage agent {stage.get('agent')}")
                referenced_skills.update(stage.get("required_skills", []))
                referenced_skills.update(stage.get("optional_skills", []))
                for rule in stage.get("conditional_skills", []):
                    referenced_skills.update(rule.get("skills", []))
            for policy_rule in doc.get("replanning", {}).get("policies", []):
                referenced_skills.update(policy_rule.get("add_skills", []))
                referenced_skills.update(policy_rule.get("drop_skills", []))

    for role_name, role in policy.get("roles", {}).items():
        referenced_skills.update(role.get("default_skills", []))
        for target in role.get("handoff_targets", []):
            if target not in roles:
                errors.append(f"runtime role {role_name} has unknown handoff target {target}")

    missing = sorted(skill for skill in referenced_skills if not (ROOT / skill / "SKILL.md").is_file())
    if missing:
        errors.append("flow/runtime references missing skills: " + ", ".join(missing))

    if not errors:
        manager = DevelopmentManager(ROOT, policy)
        for website_type in WEBSITE_TYPES:
            context = {"intent": "redesign", "website_type": website_type, "mode": "interactive-prototype", "risk": "standard", "features": []}
            try:
                resolved = manager.plan(context)
            except Exception as exc:
                errors.append(f"failed to resolve {website_type}: {type(exc).__name__}: {exc}")
                continue
            if resolved.id != "professional-website-redesign":
                errors.append(f"{website_type} resolved unexpected flow {resolved.id}")
            if len(resolved.stages) < 4:
                errors.append(f"{website_type} professional flow must resolve at least four stages")

        try:
            ecommerce = manager.plan({"intent": "redesign", "website_type": "ecommerce", "mode": "interactive-prototype", "risk": "standard", "features": ["search"]})
            research = next(stage for stage in ecommerce.stages if stage.id == "research")
            if "ecommerce-website" not in research.skills or "conversion-and-content" not in research.skills:
                errors.append("ecommerce conditional routing did not activate domain/conversion skills")
            decision = manager.replan(ecommerce, "GATE_FAIL", {"intent": "redesign", "website_type": "ecommerce", "mode": "interactive-prototype", "risk": "standard", "features": ["search"], "current_stage": "qa"}, replan_count=0)
            if not decision.accepted or decision.target_stage != "implementation":
                errors.append("QA GATE_FAIL did not route back to implementation")
            if "ui-improvement" not in decision.add_skills:
                errors.append("QA GATE_FAIL replan did not add ui-improvement")
        except Exception as exc:
            errors.append(f"manager/replan smoke failed: {type(exc).__name__}: {exc}")

    print("Declarative Flow OS validation")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Flow OS passed: {len(flow_ids)} flows, {len(referenced_skills)} referenced skills, {len(roles)} roles, {len(WEBSITE_TYPES)} professional website routing smokes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
