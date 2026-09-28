from __future__ import annotations

import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.contracts.creative_review_schema import CreativeDirective
from core.runtime.flow_os.agent import ProviderNeutralAgentHarness, SafeReader
from core.runtime.flow_os.managed import ManagedFlowController


class FactoryControlError(RuntimeError):
    """Raised when authenticated Factory control-plane boundaries are violated."""


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


class FactoryControlPlane:
    """Authenticated allowlisted lifecycle facade for the canonical managed Flow OS.

    This class is transport-neutral. It does not claim TLS by itself; an HTTPS/MCP
    deployment must provide transport security around this authenticated application
    boundary. No arbitrary shell or generic filesystem endpoint is exposed here.
    """

    def __init__(
        self,
        skills_root: Path,
        *,
        token: str,
        allowed_project_roots: list[Path],
        audit_log: Path | None = None,
    ) -> None:
        self.skills_root = Path(skills_root).resolve()
        self.token = str(token)
        if len(self.token) < 24:
            raise FactoryControlError("Factory control token must contain at least 24 characters")
        roots: list[Path] = []
        for raw in allowed_project_roots:
            root = Path(raw).resolve()
            if not root.is_dir():
                raise FactoryControlError(f"allowlisted project root is not a directory: {root}")
            if root not in roots:
                roots.append(root)
        if not roots:
            raise FactoryControlError("at least one allowed project root is required")
        self.allowed_project_roots = roots
        self.audit_log = Path(audit_log or (self.skills_root.parent / ".uiux-control" / "audit.jsonl")).resolve()

    @classmethod
    def from_environment(cls, skills_root: Path) -> "FactoryControlPlane":
        token = os.environ.get("UIUX_FACTORY_CONTROL_TOKEN", "").strip()
        raw_roots = os.environ.get("UIUX_FACTORY_ALLOWED_PROJECT_ROOTS_JSON", "").strip()
        if not token or not raw_roots:
            raise FactoryControlError(
                "remote Factory control requires UIUX_FACTORY_CONTROL_TOKEN and UIUX_FACTORY_ALLOWED_PROJECT_ROOTS_JSON"
            )
        try:
            values = json.loads(raw_roots)
        except json.JSONDecodeError as exc:
            raise FactoryControlError("UIUX_FACTORY_ALLOWED_PROJECT_ROOTS_JSON must be valid JSON") from exc
        if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
            raise FactoryControlError("allowed project roots must be a JSON string array")
        audit = os.environ.get("UIUX_FACTORY_AUDIT_LOG", "").strip()
        return cls(
            skills_root,
            token=token,
            allowed_project_roots=[Path(item) for item in values],
            audit_log=Path(audit) if audit else None,
        )

    def _authenticate(self, supplied: str) -> None:
        if not isinstance(supplied, str) or not hmac.compare_digest(supplied, self.token):
            raise FactoryControlError("Factory control authentication failed")

    def _project(self, raw: str | Path) -> Path:
        project = Path(raw).resolve()
        if not project.is_dir():
            raise FactoryControlError(f"project root is not a directory: {project}")
        for root in self.allowed_project_roots:
            try:
                project.relative_to(root)
                return project
            except ValueError:
                continue
        raise FactoryControlError("project root is outside the configured allowlist")

    def _audit(self, action: str, project: Path | None, **metadata: Any) -> None:
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "project": str(project) if project else "",
            "metadata": {
                key: value
                for key, value in metadata.items()
                if key.lower() not in {"token", "authorization", "secret", "password"}
            },
        }
        with self.audit_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    def _runtime(self, project: Path) -> tuple[ProviderNeutralAgentHarness, ManagedFlowController]:
        harness = ProviderNeutralAgentHarness(self.skills_root, project)
        return harness, ManagedFlowController(harness)

    def health(self, token: str) -> dict[str, Any]:
        self._authenticate(token)
        self._audit("health", None)
        return {
            "status": "ok",
            "control_plane": "authenticated",
            "transport_security": "external_transport_required",
            "arbitrary_shell": False,
            "generic_filesystem": False,
            "allowed_project_roots": len(self.allowed_project_roots),
        }

    def start_managed_run(
        self,
        token: str,
        project_root: str,
        task: str,
        authority: str = "branch_write",
        overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._authenticate(token)
        project = self._project(project_root)
        _harness, manager = self._runtime(project)
        managed = manager.start_from_goal(
            str(task),
            authority=str(authority),
            overrides=dict(overrides or {}),
        )
        self._audit(
            "start_managed_run",
            project,
            manager_run_id=managed.manager_run_id,
            flow_id=managed.flow.id,
            active_stage=managed.active_stage,
            authority=managed.authority,
        )
        return {
            "manager_run_id": managed.manager_run_id,
            "flow_id": managed.flow.id,
            "flow_revision": managed.flow.revision,
            "active_stage": managed.active_stage,
            "state": managed.state,
            "authority": managed.authority,
        }

    def status(self, token: str, project_root: str, manager_run_id: str) -> dict[str, Any]:
        self._authenticate(token)
        project = self._project(project_root)
        _harness, manager = self._runtime(project)
        managed = manager.resume(str(manager_run_id))
        self._audit("status", project, manager_run_id=managed.manager_run_id)
        return {
            "manager_run_id": managed.manager_run_id,
            "flow_id": managed.flow.id,
            "flow_revision": managed.flow.revision,
            "active_stage": managed.active_stage,
            "state": managed.state,
            "completed_stages": list(managed.completed_stages),
            "approved_gates": list(managed.approved_gates),
            "replan_count": managed.replan_count,
            "stage_runs": {key: list(value) for key, value in managed.stage_runs.items()},
        }

    def list_artifacts(self, token: str, project_root: str, manager_run_id: str) -> list[dict[str, Any]]:
        self._authenticate(token)
        project = self._project(project_root)
        harness, manager = self._runtime(project)
        managed = manager.resume(str(manager_run_id))
        artifacts: list[dict[str, Any]] = []
        for stage_id, run_ids in managed.stage_runs.items():
            for run_id in run_ids:
                state = harness.resume(run_id)
                workspace = state.context.get("workspace", {})
                workspace_root = str(workspace.get("workspace_root", project)) if isinstance(workspace, dict) else str(project)
                for relative in state.artifacts:
                    item = {
                        "stage_id": stage_id,
                        "run_id": run_id,
                        "path": str(relative),
                        "workspace_root": workspace_root,
                    }
                    if item not in artifacts:
                        artifacts.append(item)
        self._audit("list_artifacts", project, manager_run_id=managed.manager_run_id, count=len(artifacts))
        return artifacts

    def read_artifact(
        self,
        token: str,
        project_root: str,
        manager_run_id: str,
        stage_run_id: str,
        path: str,
    ) -> dict[str, Any]:
        self._authenticate(token)
        project = self._project(project_root)
        harness, manager = self._runtime(project)
        managed = manager.resume(str(manager_run_id))
        valid_run_ids = {run_id for values in managed.stage_runs.values() for run_id in values}
        if stage_run_id not in valid_run_ids:
            raise FactoryControlError("stage run is not part of the requested managed run")
        state = harness.resume(stage_run_id)
        if path not in state.artifacts:
            raise FactoryControlError("artifact path was not emitted by the requested stage run")
        workspace = state.context.get("workspace", {})
        root = Path(str(workspace.get("workspace_root", project))).resolve() if isinstance(workspace, dict) else project
        loaded = SafeReader(root).read_text(path)
        self._audit(
            "read_artifact",
            project,
            manager_run_id=managed.manager_run_id,
            stage_run_id=stage_run_id,
            path=loaded.relative_path,
        )
        return loaded.observation()

    def submit_creative_directive(
        self,
        token: str,
        project_root: str,
        manager_run_id: str,
        directive_payload: dict[str, Any],
    ) -> dict[str, Any]:
        self._authenticate(token)
        project = self._project(project_root)
        harness, manager = self._runtime(project)
        managed = manager.resume(str(manager_run_id))
        directive = CreativeDirective.model_validate(dict(directive_payload))
        state = harness.resume(managed.manager_run_id)
        state.context["external_creative_directive"] = directive.model_dump(mode="json")
        managed.task_context["external_creative_directive"] = directive.model_dump(mode="json")
        state.context["managed_run"] = managed.to_dict()
        harness.checkpoints.save(state.run_id, state.to_dict())
        directive_path = project / ".uiux-agent-runs" / managed.manager_run_id / "creative-directive.json"
        _atomic_json(directive_path, directive.model_dump(mode="json"))
        self._audit(
            "submit_creative_directive",
            project,
            manager_run_id=managed.manager_run_id,
            source_run_id=directive.source_run_id,
            status=directive.status,
            revision_count=len(directive.revise),
        )
        return {
            "accepted": True,
            "manager_run_id": managed.manager_run_id,
            "source_run_id": directive.source_run_id,
            "status": directive.status,
            "earliest_owner": directive.earliest_owner(),
            "stored": str(directive_path.relative_to(project)),
        }

    def start_revision(
        self,
        token: str,
        project_root: str,
        manager_run_id: str,
        signal: str = "CONTEXT_DRIFT",
    ) -> dict[str, Any]:
        self._authenticate(token)
        project = self._project(project_root)
        _harness, manager = self._runtime(project)
        managed = manager.resume(str(manager_run_id))
        decision = manager.replan(managed, str(signal))
        self._audit(
            "start_revision",
            project,
            manager_run_id=managed.manager_run_id,
            signal=signal,
            accepted=decision.accepted,
            target_stage=decision.target_stage,
        )
        return {
            "accepted": decision.accepted,
            "reason": decision.reason,
            "target_stage": decision.target_stage,
            "flow_revision": managed.flow.revision,
            "active_stage": managed.active_stage,
            "state": managed.state,
        }

    def cancel(self, token: str, project_root: str, manager_run_id: str) -> dict[str, Any]:
        self._authenticate(token)
        project = self._project(project_root)
        _harness, manager = self._runtime(project)
        managed = manager.resume(str(manager_run_id))
        if managed.state in {"COMPLETED", "FAILED", "BLOCKED"}:
            return {"cancelled": False, "state": managed.state, "reason": "run is already terminal"}
        managed.state = "BLOCKED"
        manager._checkpoint_managed(managed)
        self._audit("cancel", project, manager_run_id=managed.manager_run_id, resulting_state=managed.state)
        return {
            "cancelled": True,
            "state": managed.state,
            "note": "cooperative checkpoint cancellation; it does not kill an unrelated external process",
        }
