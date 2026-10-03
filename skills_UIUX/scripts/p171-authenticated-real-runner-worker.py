#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path


PROFILE_ID = "luxroom-cart-total-live-region"
TARGET_FILE = Path("cart.html")
OLD_SNIPPET = '<strong id="cart-total">$0</strong>'
NEW_SNIPPET = '<strong id="cart-total" aria-live="polite" aria-atomic="true">$0</strong>'

request_path = Path(os.environ["UIUX_EXECUTION_REQUEST"])
result_path = Path(os.environ["UIUX_EXECUTION_RESULT"])
artifact_dir = Path(os.environ["UIUX_TRANSACTION_ARTIFACT_DIR"])
attempt = os.environ.get("UIUX_TRANSACTION_ATTEMPT", "1")
profile = os.environ.get("UIUX_P171_PROFILE", "")
artifact_dir.mkdir(parents=True, exist_ok=True)
request = json.loads(request_path.read_text(encoding="utf-8"))
segment_id = str(request["segment_id"])
phase = str(request["phase"])
mode = str(request["runner_mode"])


def emit(kind: str, artifact_class: str, payload: dict[str, object]) -> dict[str, object]:
    path = artifact_dir / f"{segment_id}-attempt-{attempt}-{kind}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "id": f"{segment_id}-attempt-{attempt}-{kind}",
        "kind": kind,
        "artifact_class": artifact_class,
        "path": str(path),
        "metadata": {
            "phase": phase,
            "mode": mode,
            "transaction_id": os.environ.get("UIUX_TRANSACTION_ID", ""),
            "branch": os.environ.get("UIUX_TRANSACTION_BRANCH", ""),
            "profile": profile,
        },
    }


def fail(reason: str, failure_class: str = "RUNNER_CONTRACT_FAILED") -> None:
    payload = {
        "schema_version": "1.0",
        "status": "failed",
        "failure_class": failure_class,
        "reason": reason,
        "artifacts": [],
        "metadata": {"worker": "p171-authenticated-real-runner", "profile": profile},
    }
    result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0)


if profile != PROFILE_ID:
    fail(f"worker refused non-opted-in profile: {profile!r}")
if not TARGET_FILE.is_file():
    fail("LuxRoom cart.html target is missing")
source = TARGET_FILE.read_text(encoding="utf-8")
if "LuxRoom | Your selection" not in source or 'id="cart-total"' not in source:
    fail("target identity does not match the opted-in LuxRoom cart surface")

artifacts: list[dict[str, object]] = []

if phase == "audit":
    findings = {
        "surface": "LuxRoom cart order summary",
        "finding": "#cart-total changes dynamically when quantity or delivery location changes, but the value is not exposed as a polite live region.",
        "risk": "assistive technology may not announce total changes after cart interactions",
        "visual_change_required": False,
    }
    for kind in request.get("expected_output_kinds", []):
        if kind == "audit-findings":
            artifacts.append(emit(kind, "report", findings))

elif phase == "design":
    spec = {
        "surface": "#cart-total",
        "change": "add aria-live=polite and aria-atomic=true to the dynamic total value",
        "preserve": ["visual styling", "layout", "motion", "checkout behavior"],
        "files": ["cart.html"],
    }
    for kind in request.get("expected_output_kinds", []):
        if kind != "implementation-artifact":
            artifacts.append(emit(kind, "file", spec))

elif phase == "implementation":
    if NEW_SNIPPET not in source:
        if OLD_SNIPPET not in source:
            fail("cart total markup drifted; bounded replacement target not found", "TARGET_DRIFTED")
        TARGET_FILE.write_text(source.replace(OLD_SNIPPET, NEW_SNIPPET, 1), encoding="utf-8")

elif phase == "qa":
    current = TARGET_FILE.read_text(encoding="utf-8")
    checks = {
        "target_file": "cart.html",
        "has_polite_live_region": NEW_SNIPPET in current,
        "visual_change": False,
        "motion_change": False,
        "deployment_attempted": False,
        "merge_attempted": False,
    }
    if not checks["has_polite_live_region"]:
        fail("QA could not verify the cart total live-region semantics", "PRODUCT_QA_FAILED")
    for kind in request.get("expected_output_kinds", []):
        artifact_class = "evidence" if kind in {"qa-evidence", "constraint-evidence"} else "report"
        artifacts.append(emit(kind, artifact_class, checks))

else:
    fail(f"unsupported lifecycle phase for P1.7.1 dogfood: {phase}")

payload = {
    "schema_version": "1.0",
    "status": "passed",
    "artifacts": artifacts,
    "metadata": {"worker": "p171-authenticated-real-runner", "profile": profile},
}
result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
