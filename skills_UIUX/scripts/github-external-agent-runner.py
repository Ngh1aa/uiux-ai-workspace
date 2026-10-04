#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath

SKILLS_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = SKILLS_ROOT.parent
FACTORY_ROOT = WORKSPACE_ROOT / "uiux-factory"
if str(FACTORY_ROOT) not in sys.path:
    sys.path.insert(0, str(FACTORY_ROOT))

from core.runtime.flow_os.external_task import build_external_task_manifest

RUNNER_SCHEMA_VERSION = "1.2"
FAILURE_CLASSES = [
    "PRODUCT_QA_FAILED", "PROVIDER_RATE_LIMITED", "AUTH_BLOCKED", "BUILD_FAILED",
    "DEPLOY_FAILED", "READY_BUT_NOT_DEPLOYED", "DEPLOYED_VERIFIED",
    "INFRA_UNAVAILABLE", "UNKNOWN_FAILURE",
]


def _split_values(raw: str) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for part in raw.replace("\r", "\n").replace(",", "\n").split("\n"):
        value = part.strip()
        if value and value not in seen:
            seen.add(value)
            values.append(value)
    return values


def _git(target: Path, *args: str) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(target), *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _resolve_target_project_root(repository_root: Path, target_dir: str) -> tuple[Path, str]:
    repository_root = Path(repository_root).resolve()
    raw = str(target_dir or "").strip().replace("\\", "/")
    if raw in {"", "."}:
        relative = "."
        candidate = repository_root
    else:
        if raw.startswith("/"):
            raise ValueError("target_dir must be repository-relative")
        posix = PurePosixPath(raw)
        if posix.is_absolute() or ".." in posix.parts:
            raise ValueError("target_dir must stay inside the checked-out repository")
        parts = [part for part in posix.parts if part not in {"", "."}]
        if not parts or any(":" in part for part in parts):
            raise ValueError("target_dir must use a repository-relative path")
        relative = "/".join(parts)
        candidate = (repository_root / Path(*parts)).resolve()

    try:
        candidate.relative_to(repository_root)
    except ValueError as exc:
        raise ValueError("target_dir resolves outside the checked-out repository") from exc
    if not candidate.is_dir():
        raise ValueError(f"target_dir does not exist: {relative}")
    return candidate, relative


def _target_snapshot(target: Path, requested_ref: str) -> dict[str, object]:
    tracked = _git(target, "ls-files").splitlines() if target.exists() else []
    return {
        "requested_ref": requested_ref,
        "checked_out_sha": _git(target, "rev-parse", "HEAD"),
        "checked_out_branch": _git(target, "branch", "--show-current"),
        "tracked_file_count": len([item for item in tracked if item]),
        "sample_paths": [item for item in tracked[:80] if item],
        "working_tree_clean": _git(target, "status", "--porcelain") == "",
    }


def _handoff_markdown(run_doc: dict[str, object]) -> str:
    manifest = run_doc["manifest"]
    verification = run_doc["verification_plan"]
    task_contract = manifest.get("task_contract", {})
    target_truth = task_contract.get("target_truth", {})
    provenance = task_contract.get("routing_provenance", {})
    fields = target_truth.get("fields", {}) if isinstance(target_truth, dict) else {}
    lines = [
        "# GitHub-native external-agent handoff", "",
        f"**Target:** `{manifest['target_repository']}`",
        f"**Target dir:** `{run_doc['target_snapshot'].get('target_dir', '.')}`",
        f"**Task:** {manifest['task']}",
        f"**Authority:** `{manifest['authority']}`",
        f"**Status:** `{run_doc['status']}`", "",
        "> This packet is a routing contract, not evidence that implementation or QA passed.", "",
        "## Target-truth routing",
        f"- Probe status: `{target_truth.get('status', 'UNKNOWN') if isinstance(target_truth, dict) else 'UNKNOWN'}`",
        f"- Sources: `{', '.join(target_truth.get('sources', [])) if isinstance(target_truth, dict) and target_truth.get('sources') else 'none'}`",
        f"- Applied routing truth: `{json.dumps(fields, ensure_ascii=False, sort_keys=True)}`",
        f"- Precedence: `{ ' > '.join(provenance.get('precedence', [])) if isinstance(provenance, dict) else 'unknown'}`", "",
        "## Ordered stages",
    ]
    for stage in manifest.get("stages", []):
        skills = ", ".join(stage.get("skills", [])) or "none"
        lines.append(f"- `{stage.get('id')}` — {stage.get('purpose', '')} — skills: {skills}")
    lines.extend([
        "", "## Verification",
        f"- Cloud QA workflow: `{verification['cloud_qa_workflow']}`",
        f"- State coverage contract: `{verification.get('state_coverage_contract') or 'not declared'}`",
        f"- State gate command: `{verification['state_gate_command']}`",
        f"- Deployment truth gate: `{verification['deployment_truth_gate']}`",
        f"- Release evidence registry: `{verification['release_evidence_registry']}`",
        f"- Release evidence manifest: `{verification['release_evidence_manifest']}`",
        f"- Infra classifier: `{verification['infra_failure_classifier']}`", "",
        "## Failure taxonomy", "- " + "\n- ".join(FAILURE_CLASSES), "",
        "## Completion boundary",
        "Target truth influences routing only. It never grants authority or gate evidence. Audit the target source before mutation, execute only within granted authority, and attach target runtime/rendered evidence before claiming PASS. Missing user or deployment evidence remains planned/blocked/unknown rather than fabricated.", "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile a GitHub-native external-agent task packet from checked-out target truth.")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--authority", choices=["read_only", "branch_write", "external_write", "release"], default="branch_write")
    parser.add_argument("--target-root", required=True, help="Checked-out target repository root")
    parser.add_argument("--target-dir", default="", help="Project root inside the target repository; blank means repository root")
    parser.add_argument("--target-ref", default="")
    parser.add_argument("--qa-routes", default="")
    parser.add_argument("--acceptance", default="")
    parser.add_argument("--state-contract", default="")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    repository_root = Path(args.target_root).resolve()
    try:
        target_root, target_dir = _resolve_target_project_root(repository_root, args.target_dir)
    except ValueError as exc:
        parser.error(str(exc))
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    policy_doc = json.loads((SKILLS_ROOT / "runtime" / "runtime-policy.json").read_text(encoding="utf-8"))
    manifest = build_external_task_manifest(
        SKILLS_ROOT,
        policy_doc,
        args.task,
        args.repository,
        authority=args.authority,
        acceptance_criteria=_split_values(args.acceptance),
        qa_routes=_split_values(args.qa_routes),
        target_root=target_root,
    ).to_dict()

    run_doc: dict[str, object] = {
        "schema_version": RUNNER_SCHEMA_VERSION,
        "status": "READY_FOR_EXTERNAL_COLLABORATOR",
        "execution_boundary": {
            "invokes_llm_provider": False,
            "meaning": "GitHub Actions compiles the governed task packet and can run declared verification. The external AI collaborator remains responsible for target implementation within authority.",
            "manifest_is_not_qa_pass": True,
            "target_truth_is_routing_only": True,
        },
        "manifest": manifest,
        "target_snapshot": {
            **_target_snapshot(target_root, args.target_ref),
            "target_dir": target_dir,
        },
        "verification_plan": {
            "target_dir": target_dir,
            "cloud_qa_workflow": ".github/workflows/cloud-qa-toolchain.yml",
            "state_coverage_contract": args.state_contract or None,
            "state_gate_command": "npm run test:state -- --contract <target-state-contract>",
            "matrix_artifact": "uiux-factory/qa/artifacts/state-coverage/state-matrix-2x2.png",
            "deployment_truth_gate": "uiux-factory/qa/scripts/deployment-truth.mjs",
            "release_evidence_registry": "skills_UIUX/scripts/build-release-evidence.py",
            "release_evidence_manifest": "uiux-evidence-manifest.json",
            "infra_failure_classifier": "uiux-factory/qa/scripts/infra-failure-classifier.mjs",
            "failure_classes": FAILURE_CLASSES,
        },
    }

    (output_dir / "external-task-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "github-external-agent-run.json").write_text(json.dumps(run_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "HANDOFF.md").write_text(_handoff_markdown(run_doc), encoding="utf-8")
    print(json.dumps({
        "status": run_doc["status"],
        "target_repository": manifest["target_repository"],
        "target_sha": run_doc["target_snapshot"]["checked_out_sha"],
        "target_dir": target_dir,
        "target_truth_status": manifest["task_contract"]["target_truth"]["status"],
        "resolved_flow": manifest["resolved_flow"]["id"],
        "state_contract": args.state_contract or None,
        "output_dir": str(output_dir),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
