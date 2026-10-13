from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from executor_evidence import file_proof, render_fixture
from core.runtime.flow_os.execution_driver import ArtifactRegistry


request_path = Path(os.environ["UIUX_EXECUTION_REQUEST"])
result_path = Path(os.environ["UIUX_EXECUTION_RESULT"])
workspace = Path(os.environ["P16_WORKSPACE"]).resolve()
workspace.mkdir(parents=True, exist_ok=True)
request = json.loads(request_path.read_text(encoding="utf-8"))
segment_id = request["segment_id"]
phase = request["phase"]
mode = request["runner_mode"]
attempt_tag = result_path.stem.removesuffix("-result")

fail_qa_once = os.environ.get("P16_FAIL_QA_ONCE") == "1"
qa_marker = workspace / ".qa-failed-once"


def emit_file(kind: str, artifact_class: str, name: str, content: str) -> dict[str, object]:
    path = workspace / name
    path.write_text(content, encoding="utf-8")
    return {
        "id": f"{attempt_tag}-{kind}",
        "kind": kind,
        "artifact_class": artifact_class,
        "path": str(path),
        "metadata": {"phase": phase, "mode": mode, "attempt_tag": attempt_tag},
    }


if phase == "qa" and fail_qa_once and not qa_marker.exists():
    qa_marker.write_text("failed\n", encoding="utf-8")
    artifact = emit_file(
        "qa-failure-evidence",
        "report",
        f"{attempt_tag}-qa-failure.txt",
        "PRODUCT_QA_FAILED: rendered checkout drift\n",
    )
    payload = {
        "schema_version": "2.0",
        "status": "failed",
        "failure_class": "PRODUCT_QA_FAILED",
        "reason": "rendered checkout drift",
        "artifacts": [artifact],
    }
else:
    outputs: list[dict[str, object]] = []
    evidence = []
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
                "id": f"{attempt_tag}-{kind}",
                "kind": kind,
                "artifact_class": "commit",
                "uri": f"git+commit://{attempt_tag}",
                "metadata": {"phase": phase, "mode": mode, "attempt_tag": attempt_tag},
            })
        else:
            outputs.append(emit_file(
                kind,
                artifact_class,
                f"{attempt_tag}-{kind}.txt",
                json.dumps({
                    "segment_id": segment_id,
                    "phase": phase,
                    "mode": mode,
                    "stage": request["active_stage_id"],
                    "skills": request["skills"],
                    "inputs": [item["id"] for item in request["input_artifacts"]],
                }, ensure_ascii=False),
            ))
            evidence.append(file_proof(request['active_stage_id'], 'read_text' if phase == 'audit' else 'write_artifact', outputs[-1]['path']))
    if phase == 'implementation':
        check = subprocess.run([sys.executable, '-c', "print('SYNTHETIC implementation boundary')"], capture_output=True, text=True)
        proof = workspace / f'{attempt_tag}-command.json'
        proof.write_text(json.dumps({'returncode': check.returncode, 'stdout': check.stdout}), encoding='utf-8')
        evidence.append(file_proof(request['active_stage_id'], 'run_target_command', proof, {'returncode': check.returncode}))
    if phase == 'qa':
        if os.environ.get('P16_FILE_ONLY_QA') == '1':
            evidence = []  # Deliberate negative fixture: text labeled screenshot must fail.
        else:
            record, image = render_fixture(workspace, attempt_tag, request['active_stage_id'])
            evidence.append(record)
            for artifact in outputs:
                if artifact['kind'] == 'qa-evidence':
                    artifact['path'] = str(image)
    payload = {
        "schema_version": "2.0",
        "status": "passed",
        "artifacts": outputs,
        "evidence_records": evidence,
        "metadata": {"runner": "p16-subprocess-fixture", "attempt_tag": attempt_tag},
    }

for artifact in payload.get("artifacts", []):
    if artifact["kind"] == "qa-evidence":
        artifact["digest"] = ArtifactRegistry._sha256(Path(artifact["path"]))

result_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
