from __future__ import annotations

import json
import os
from pathlib import Path


request_path = Path(os.environ["UIUX_EXECUTION_REQUEST"])
result_path = Path(os.environ["UIUX_EXECUTION_RESULT"])
workspace = Path(os.environ["P16_WORKSPACE"]).resolve()
workspace.mkdir(parents=True, exist_ok=True)
request = json.loads(request_path.read_text(encoding="utf-8"))
segment_id = request["segment_id"]
phase = request["phase"]
mode = request["runner_mode"]

fail_qa_once = os.environ.get("P16_FAIL_QA_ONCE") == "1"
qa_marker = workspace / ".qa-failed-once"


def emit_file(kind: str, artifact_class: str, name: str, content: str) -> dict[str, object]:
    path = workspace / name
    path.write_text(content, encoding="utf-8")
    return {
        "id": f"{segment_id}-{kind}-{name}",
        "kind": kind,
        "artifact_class": artifact_class,
        "path": str(path),
        "metadata": {"phase": phase, "mode": mode},
    }


if phase == "qa" and fail_qa_once and not qa_marker.exists():
    qa_marker.write_text("failed\n", encoding="utf-8")
    artifact = emit_file(
        "qa-failure-evidence",
        "report",
        f"{segment_id}-qa-failure.txt",
        "PRODUCT_QA_FAILED: rendered checkout drift\n",
    )
    payload = {
        "schema_version": "1.0",
        "status": "failed",
        "failure_class": "PRODUCT_QA_FAILED",
        "reason": "rendered checkout drift",
        "artifacts": [artifact],
    }
else:
    outputs: list[dict[str, object]] = []
    for kind in request["expected_output_kinds"]:
        artifact_class = {
            "audit-findings": "report",
            "design-spec": "file",
            "implementation-artifact": "commit",
            "qa-evidence": "screenshot",
            "constraint-evidence": "evidence",
        }.get(kind, "evidence")
        if artifact_class == "commit":
            outputs.append({
                "id": f"{segment_id}-{kind}",
                "kind": kind,
                "artifact_class": "commit",
                "uri": "git+commit://0123456789abcdef0123456789abcdef01234567",
                "metadata": {"phase": phase, "mode": mode},
            })
        else:
            outputs.append(emit_file(
                kind,
                artifact_class,
                f"{segment_id}-{kind}.txt",
                json.dumps({
                    "segment_id": segment_id,
                    "phase": phase,
                    "mode": mode,
                    "stage": request["active_stage_id"],
                    "skills": request["skills"],
                    "inputs": [item["id"] for item in request["input_artifacts"]],
                }, ensure_ascii=False),
            ))
    payload = {
        "schema_version": "1.0",
        "status": "passed",
        "artifacts": outputs,
        "metadata": {"runner": "p16-subprocess-fixture"},
    }

result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
