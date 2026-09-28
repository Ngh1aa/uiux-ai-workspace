from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from core.runtime.flow_os.evidence import EvidenceRecord
from core.runtime.flow_os.managed import ManagedWebsiteRun
from core.runtime.flow_os.workspace import WorktreeManager, WorkspaceFinalizeResult


class ProductionReleaseError(RuntimeError):
    """Raised when a production release violates authority or evidence policy."""


@dataclass(frozen=True)
class DeploymentResult:
    adapter: str
    returncode: int
    stdout: str
    stderr: str
    deployed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CommandDeployAdapter:
    """Execute one operator-configured exact argv deployment command.

    The command is never sourced from a model response and never executed through a
    shell. Credentials are provided only through an explicit environment-name allowlist;
    values are neither persisted nor returned in observations.
    """

    def __init__(self, policy: dict[str, Any]) -> None:
        config = dict(policy.get("production_release", {}))
        self.timeout_seconds = int(config.get("timeout_seconds", 600))
        self.max_output_chars = int(config.get("max_output_chars", 12000))
        self.env_allowlist = [str(item) for item in config.get("deploy_env_allowlist", [])]
        self.argv_env = str(config.get("command_argv_env", "UIUX_PRODUCTION_DEPLOY_ARGV_JSON"))

    def _argv(self) -> list[str]:
        raw = os.environ.get(self.argv_env, "").strip()
        if not raw:
            raise ProductionReleaseError(
                f"production deploy adapter is not configured; set {self.argv_env} to an exact JSON argv array"
            )
        try:
            argv = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ProductionReleaseError(f"{self.argv_env} must be valid JSON") from exc
        if not isinstance(argv, list) or not argv or len(argv) > 32 or not all(isinstance(item, str) and item for item in argv):
            raise ProductionReleaseError("production deploy argv must be a non-empty string array with at most 32 items")
        return list(argv)

    def deploy(self, project_root: Path) -> DeploymentResult:
        argv = self._argv()
        env = {
            key: value
            for key, value in os.environ.items()
            if key in {"PATH", "SYSTEMROOT", "WINDIR", "HOME", "USERPROFILE", "TMP", "TEMP"}
            or key in self.env_allowlist
        }
        result = subprocess.run(
            argv,
            cwd=Path(project_root).resolve(),
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
            env=env,
            shell=False,
        )
        stdout = (result.stdout or "")[-self.max_output_chars :]
        stderr = (result.stderr or "")[-self.max_output_chars :]
        return DeploymentResult(
            adapter="command",
            returncode=int(result.returncode),
            stdout=stdout,
            stderr=stderr,
            deployed=result.returncode == 0,
        )


class ProductionReleaseController:
    """Human-owned boundary for merge/finalize and production deployment."""

    def __init__(self, harness: Any) -> None:
        self.harness = harness
        self.worktrees = WorktreeManager(harness.project_root)

    def _require_authority(self, authority: str, minimum: str) -> None:
        order = tuple(self.harness.permissions.order)
        if authority not in order or minimum not in order or order.index(authority) < order.index(minimum):
            raise ProductionReleaseError(f"{minimum} authority is required; caller grants {authority}")

    def _manager_state(self, managed: ManagedWebsiteRun) -> Any:
        return self.harness.resume(managed.manager_run_id)

    def _all_evidence(self, managed: ManagedWebsiteRun) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for run_ids in managed.stage_runs.values():
            for run_id in run_ids:
                state = self.harness.resume(run_id)
                records.extend(list(state.context.get("evidence_records", [])))
        manager = self._manager_state(managed)
        records.extend(list(manager.context.get("release_evidence", [])))
        return records

    def attach_release_evidence(self, managed: ManagedWebsiteRun, records: list[EvidenceRecord]) -> None:
        manager = self._manager_state(managed)
        existing = list(manager.context.get("release_evidence", []))
        existing.extend(record.to_dict() for record in records)
        manager.context["release_evidence"] = existing[-128:]
        self.harness.checkpoints.save(manager.run_id, manager.to_dict())

    def finalize_workspace(
        self,
        managed: ManagedWebsiteRun,
        authority: str,
        commit_message: str,
        cleanup: bool = True,
    ) -> WorkspaceFinalizeResult:
        self._require_authority(authority, "external_write")
        if managed.state != "COMPLETED":
            raise ProductionReleaseError(
                f"automatic merge requires managed flow COMPLETED; current state is {managed.state}"
            )
        manager = self._manager_state(managed)
        raw = manager.context.get("workspace")
        if not isinstance(raw, dict):
            result = WorkspaceFinalizeResult(
                run_id=managed.manager_run_id,
                branch="",
                commit=None,
                merged=True,
                cleaned=True,
                changed=False,
            )
        else:
            result = self.worktrees.finalize(raw, commit_message=commit_message, merge=True, cleanup=cleanup)
        manager.context["workspace_finalize"] = result.to_dict()
        self.harness.checkpoints.save(manager.run_id, manager.to_dict())
        return result

    def validate_release_ready(self, managed: ManagedWebsiteRun) -> list[str]:
        errors: list[str] = []
        if managed.state != "COMPLETED":
            errors.append(f"managed flow must be COMPLETED before production release; current state is {managed.state}")
        manager = self._manager_state(managed)
        workspace = manager.context.get("workspace")
        finalized = manager.context.get("workspace_finalize")
        if isinstance(workspace, dict):
            if not isinstance(finalized, dict) or not bool(finalized.get("merged")):
                errors.append("isolated worktree changes must be finalized and merged before production release")
        records = []
        for payload in self._all_evidence(managed):
            try:
                record = EvidenceRecord.from_dict(dict(payload))
            except (KeyError, TypeError, ValueError):
                continue
            if record.trusted and record.origin == "runtime":
                records.append(record)
        if any(record.status == "FAIL" for record in records):
            errors.append("trusted runtime evidence contains a failing result")
        browser = [record for record in records if record.type == "browser_render" and record.status == "PASS"]
        if not browser:
            errors.append("at least one PASS browser_render evidence record is required for production release")
        checks = [
            record for record in records
            if record.type in {"validator_result", "command_result"} and record.status == "PASS"
        ]
        if not checks:
            errors.append("at least one successful validator_result or command_result is required for production release")
        return errors

    def deploy_production(
        self,
        managed: ManagedWebsiteRun,
        authority: str,
        confirmation: str,
        adapter: CommandDeployAdapter | None = None,
    ) -> DeploymentResult:
        self._require_authority(authority, "release")
        if str(confirmation).strip() != "PRODUCTION":
            raise ProductionReleaseError("production deployment requires explicit confirmation value: PRODUCTION")
        errors = self.validate_release_ready(managed)
        if errors:
            raise ProductionReleaseError("; ".join(errors))
        deployer = adapter or CommandDeployAdapter(self.harness.policy_doc)
        result = deployer.deploy(self.harness.project_root)
        manager = self._manager_state(managed)
        manager.context["production_deploy"] = result.to_dict()
        deployment_evidence = EvidenceRecord(
            id=f"deploy_{managed.manager_run_id}",
            type="deployment_result",
            stage_id="release",
            tool=result.adapter,
            status="PASS" if result.deployed else "FAIL",
            summary=f"production deployment via {result.adapter}: {'PASS' if result.deployed else 'FAIL'}",
            data={
                "adapter": result.adapter,
                "returncode": result.returncode,
                "deployed": result.deployed,
            },
        )
        existing = list(manager.context.get("release_evidence", []))
        existing.append(deployment_evidence.to_dict())
        manager.context["release_evidence"] = existing[-128:]
        self.harness.checkpoints.save(manager.run_id, manager.to_dict())
        if not result.deployed:
            raise ProductionReleaseError(f"production deploy command failed with code {result.returncode}")
        return result
