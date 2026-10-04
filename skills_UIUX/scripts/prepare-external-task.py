#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SKILLS_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = SKILLS_ROOT.parent
FACTORY_ROOT = WORKSPACE_ROOT / "uiux-factory"
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from core.runtime.flow_os.external_task import build_external_task_manifest
from core.runtime.flow_os.agent import configure_cli_utf8


def _overrides(args: argparse.Namespace) -> dict[str, object]:
    values: dict[str, object] = {}
    for key in (
        "intent",
        "change_surface",
        "website_type",
        "domain",
        "product_archetype",
        "validation_lane",
        "mode",
        "risk",
    ):
        value = getattr(args, key)
        if value not in {None, ""}:
            values[key] = value
    if args.feature:
        values["features"] = list(args.feature)
    return values


def main() -> int:
    configure_cli_utf8()
    parser = argparse.ArgumentParser(
        description="Compile one external AI/UIUX task into a bounded Factory routing manifest."
    )
    parser.add_argument("--repository", required=True, help="Target repository, normally owner/name or its GitHub URL")
    parser.add_argument("--task", required=True, help="Natural-language goal for the external collaborator")
    parser.add_argument(
        "--target-root",
        help=(
            "Optional checked-out target-project root. When supplied, bounded project truth is "
            "probed before Flow resolution. Without it, routing truthfully falls back to goal inference."
        ),
    )
    parser.add_argument(
        "--authority",
        choices=["read_only", "branch_write", "external_write", "release"],
        default="branch_write",
        help="Maximum caller-granted authority recorded in the manifest",
    )
    parser.add_argument("--intent", choices=["build", "redesign", "rebuild", "improve", "fix", "polish", "audit", "review", "research", "validate", "qa"])
    parser.add_argument("--change-surface", dest="change_surface", choices=["MICRO", "FOCUSED", "PAGE", "REDESIGN", "PRODUCT"])
    parser.add_argument("--website-type", dest="website_type")
    parser.add_argument("--domain")
    parser.add_argument("--product-archetype", dest="product_archetype")
    parser.add_argument("--validation-lane", dest="validation_lane", choices=["prototype", "evidence-led", "production-learning"])
    parser.add_argument("--mode", choices=["visual-prototype", "interactive-prototype", "production-candidate", "production"])
    parser.add_argument("--risk")
    parser.add_argument("--feature", action="append", default=[], help="Explicit feature override; repeat as needed")
    parser.add_argument("--acceptance", action="append", default=[], help="Additional acceptance criterion; repeat as needed")
    parser.add_argument("--qa-route", action="append", default=[], help="Target route expected in rendered QA; repeat as needed")
    parser.add_argument("--output", help="Optional JSON output path; parent directories are created")
    args = parser.parse_args()

    policy_path = SKILLS_ROOT / "runtime" / "runtime-policy.json"
    policy_doc = json.loads(policy_path.read_text(encoding="utf-8"))
    target_root = Path(args.target_root).resolve() if args.target_root else None
    manifest = build_external_task_manifest(
        SKILLS_ROOT,
        policy_doc,
        args.task,
        args.repository,
        authority=args.authority,
        overrides=_overrides(args),
        acceptance_criteria=list(args.acceptance),
        qa_routes=list(args.qa_route),
        target_root=target_root,
    )
    payload = json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n"

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload, encoding="utf-8")

    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
