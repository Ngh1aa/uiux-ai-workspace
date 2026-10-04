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


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Preflight an external task and recommend a model capability/reasoning profile "
            "before opening a ChatGPT/Codex execution run."
        )
    )
    parser.add_argument("--repository", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--target-root")
    parser.add_argument(
        "--authority",
        choices=["read_only", "branch_write", "external_write", "release"],
        default="branch_write",
    )
    parser.add_argument(
        "--full-manifest",
        action="store_true",
        help="Emit the whole task manifest instead of only the execution advice.",
    )
    args = parser.parse_args()

    policy_doc = json.loads(
        (SKILLS_ROOT / "runtime" / "runtime-policy.json").read_text(encoding="utf-8")
    )
    manifest = build_external_task_manifest(
        SKILLS_ROOT,
        policy_doc,
        args.task,
        args.repository,
        authority=args.authority,
        target_root=Path(args.target_root).resolve() if args.target_root else None,
    ).to_dict()

    payload = manifest if args.full_manifest else {
        "target_repository": manifest["target_repository"],
        "task": manifest["task"],
        "resolved_flow": manifest["resolved_flow"]["id"],
        "execution_advice": manifest["execution_advice"],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
