from __future__ import annotations

import json
import os
from pathlib import Path


request_path = Path(os.environ["UIUX_EXECUTION_REQUEST"])
result_path = Path(os.environ["UIUX_EXECUTION_RESULT"])
artifact_dir = Path(os.environ["UIUX_TRANSACTION_ARTIFACT_DIR"])
attempt = os.environ.get("UIUX_TRANSACTION_ATTEMPT", "1")
artifact_dir.mkdir(parents=True, exist_ok=True)
request = json.loads(request_path.read_text(encoding="utf-8"))
segment_id = str(request["segment_id"])
phase = str(request["phase"])
mode = str(request["runner_mode"])


def emit(kind: str, artifact_class: str, content: str) -> dict[str, object]:
    path = artifact_dir / f"{segment_id}-attempt-{attempt}-{kind}.txt"
    path.write_text(content, encoding="utf-8")
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
        },
    }


if phase == "audit" and os.environ.get("P17_MUTATE_AUDIT") == "1":
    Path("index.html").write_text("<main>unauthorized audit mutation</main>\n", encoding="utf-8")

if phase == "implementation":
    target = Path("index.html")
    current = target.read_text(encoding="utf-8") if target.exists() else ""
    marker = f"<!-- {segment_id}:{mode}:attempt-{attempt} -->\n"
    if marker not in current:
        target.write_text(current + marker, encoding="utf-8")
    payload = {
        "schema_version": "1.0",
        "status": "passed",
        "artifacts": [],
        "metadata": {"worker": "p17-github-fixture"},
    }
elif phase == "qa" and os.environ.get("P17_FAIL_QA_ONCE") == "1":
    marker = artifact_dir / ".qa-failed-once"
    if not marker.exists():
        marker.write_text("failed\n", encoding="utf-8")
        payload = {
            "schema_version": "1.0",
            "status": "failed",
            "failure_class": "PRODUCT_QA_FAILED",
            "reason": "fixture browser QA detected rendered drift",
            "artifacts": [emit("qa-failure-evidence", "report", "rendered drift\n")],
        }
    else:
        artifacts = []
        for kind in request.get("expected_output_kinds", []):
            artifact_class = "screenshot" if kind == "qa-evidence" else "evidence"
            artifacts.append(emit(kind, artifact_class, json.dumps({
                "segment_id": segment_id,
                "mode": mode,
                "stage": request.get("active_stage_id"),
                "skills": request.get("skills", []),
            }, ensure_ascii=False)))
        payload = {
            "schema_version": "1.0",
            "status": "passed",
            "artifacts": artifacts,
            "metadata": {"worker": "p17-github-fixture"},
        }
else:
    artifacts = []
    for kind in request.get("expected_output_kinds", []):
        if kind == "implementation-artifact":
            continue
        artifact_class = {
            "audit-findings": "report",
            "design-spec": "file",
            "qa-evidence": "screenshot",
            "constraint-evidence": "evidence",
        }.get(kind, "evidence")
        artifacts.append(emit(kind, artifact_class, json.dumps({
            "segment_id": segment_id,
            "phase": phase,
            "mode": mode,
            "stage": request.get("active_stage_id"),
            "skills": request.get("skills", []),
            "inputs": [item.get("id") for item in request.get("input_artifacts", [])],
        }, ensure_ascii=False)))
    payload = {
        "schema_version": "1.0",
        "status": "passed",
        "artifacts": artifacts,
        "metadata": {"worker": "p17-github-fixture"},
    }

result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
