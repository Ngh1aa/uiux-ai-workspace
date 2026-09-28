from __future__ import annotations

import json
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.runtime.flow_os.agent import ProviderNeutralAgentHarness
from core.runtime.flow_os.managed import ManagedFlowController
from core.runtime.flow_os.safe_read import SafeReader


class RemoteControlError(ValueError):
    """Raised when a remote-control request violates the bounded control-plane contract."""


@dataclass(frozen=True)
class RemoteControlPolicy:
    enabled: bool = False
    max_artifact_chars: int = 120000
    allow_cancel: bool = True
    allow_revision: bool = True

    @classmethod
    def from_policy(cls, policy_doc: dict[str, Any]) -> "RemoteControlPolicy":
        raw = policy_doc.get("remote_control", {})
        if not isinstance(raw, dict):
            raise RemoteControlError("runtime-policy remote_control must be an object")
        enabled = raw.get("enabled", False)
        allow_cancel = raw.get("allow_cancel", True)
        allow_revision = raw.get("allow_revision", True)
        for name, value in (
            ("enabled", enabled),
            ("allow_cancel", allow_cancel),
            ("allow_revision", allow_revision),
        ):
            if not isinstance(value, bool):
                raise RemoteControlError(f"remote_control.{name} must be a boolean")
        max_chars = raw.get("max_artifact_chars", 120000)
        if isinstance(max_chars, bool) or not isinstance(max_chars, int):
            raise RemoteControlError("remote_control.max_artifact_chars must be an integer")
        if max_chars < 1024 or max_chars > 1_000_000:
            raise RemoteControlError("remote_control.max_artifact_chars must be between 1024 and 1000000")
        return cls(enabled, max_chars, allow_cancel, allow_revision)


class RemoteFactoryControlPlane:
    """Authenticated allowlisted control surface over the canonical managed Flow runtime.

    This class intentionally exposes no arbitrary command execution, repository mutation,
    provider selection or release operation. Transport TLS is owned by the MCP/API gateway;
    this layer owns authentication, project confinement, lifecycle bounds and audit records.
    """

    def __init__(self, skills_root: Path, policy_doc: dict[str, Any] | None = None) -> None:
        self.skills_root = Path(skills_root).resolve()
        self.policy_doc = policy_doc or json.loads(
            (self.skills_root / "runtime" / "runtime-policy.json").read_text(encoding="utf-8")
        )
        self.policy = RemoteControlPolicy.from_policy(self.policy_doc)

    @staticmethod
    def _configured_roots() -> list[Path]:
        raw = os.environ.get("UIUX_REMOTE_PROJECT_ROOTS_JSON", "").strip()
        if not raw:
            return []
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RemoteControlError("UIUX_REMOTE_PROJECT_ROOTS_JSON must be valid JSON") from exc
        if not isinstance(payload, list) or any(not isinstance(item, str) for item in payload):
            raise RemoteControlError("UIUX_REMOTE_PROJECT_ROOTS_JSON must be an array of paths")
        return [Path(item).expanduser().resolve() for item in payload]

    def health(self) -> dict[str, Any]:
        token = os.environ.get("UIUX_REMOTE_CONTROL_TOKEN", "")
        roots = self._configured_roots()
        return {
            "status": "ready" if self.policy.enabled and token and roots else "disabled",
            "enabled": self.policy.enabled,
            "authentication_configured": bool(token),
            "allowed_project_roots": len(roots),
            "transport_tls_required_for_network_exposure": True,
            "arbitrary_shell": False,
            "release_operations": False,
        }

    def _authorize(self, token: str) -> None:
        if not self.policy.enabled:
            raise RemoteControlError("remote control is disabled by runtime policy")
        expected = os.environ.get("UIUX_REMOTE_CONTROL_TOKEN", "")
        if not expected:
            raise RemoteControlError("remote control token is not configured")
        if not isinstance(token, str) or not secrets.compare_digest(token, expected):
            raise RemoteControlError("remote control authentication failed")

    def _project(self, project_root: str) -> Path:
        project = Path(project_root).expanduser().resolve()
        roots = self._configured_roots()
        if not roots:
            raise RemoteControlError("no remote project roots are allowlisted")
        if not any(project == root or root in project.parents for root in roots):
            raise RemoteControlError("project root is outside the remote-control allowlist")
        if not project.is_dir():
            raise RemoteControlError("project root does not exist")
        return project

    def _manager(self, project: Path) -> ManagedFlowController:
        return ManagedFlowController(ProviderNeutralAgentHarness(self.skills_root, project))

    @staticmethod
    def _audit(project: Path, action: str, outcome: str, **metadata: Any) -> None:
        root = project / ".uiux-agent-runs"
        root.mkdir(parents=True, exist_ok=True)
        path = root / "remote-control-audit.jsonl"
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "outcome": outcome,
            **{key: value for key, value in metadata.items() if key not in {"token", "content"}},
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def start_run(
        self,
        *,
        token: str,
        project_root: str,
        goal: str,
        authority: str = "branch_write",
        overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._authorize(token)
        project = self._project(project_root)
        if authority not in {"read_only", "branch_write"}:
            raise RemoteControlError("remote starts are limited to read_only or branch_write authority")
        goal = str(goal).strip()
        if not goal or len(goal) > 12000:
            raise RemoteControlError("goal must contain 1..12000 characters")
        manager = self._manager(project)
        managed = manager.start_from_goal(goal, authority=authority, overrides=dict(overrides or {}))
        self._audit(project, "start_run", "OK", manager_run_id=managed.manager_run_id)
        return self._status_payload(managed)

    @staticmethod
    def _status_payload(managed: Any) -> dict[str, Any]:
        return {
            "manager_run_id": managed.manager_run_id,
            "flow_id": managed.flow.id,
            "flow_revision": managed.flow.revision,
            "state": managed.state,
            "active_stage": managed.active_stage,
            "completed_stages": list(managed.completed_stages),
            "replan_count": managed.replan_count,
            "authority": managed.authority,
        }

    def status(self, *, token: str, project_root: str, manager_run_id: str) -> dict[str, Any]:
        self._authorize(token)
        project = self._project(project_root)
        managed = self._manager(project).resume(str(manager_run_id))
        self._audit(project, "status", "OK", manager_run_id=managed.manager_run_id)
        return self._status_payload(managed)

    def list_artifacts(self, *, token: str, project_root: str, manager_run_id: str) -> dict[str, Any]:
        self._authorize(token)
        project = self._project(project_root)
        manager = self._manager(project)
        managed = manager.resume(str(manager_run_id))
        rows: list[dict[str, Any]] = []
        seen: set[str] = set()
        for stage_id, run_ids in managed.stage_runs.items():
            for run_id in run_ids:
                stage = manager.harness.resume(run_id)
                for artifact in stage.artifacts:
                    path = str(artifact)
                    if path in seen:
                        continue
                    seen.add(path)
                    rows.append({"stage_id": stage_id, "run_id": run_id, "path": path})
        self._audit(project, "list_artifacts", "OK", manager_run_id=managed.manager_run_id, count=len(rows))
        return {"manager_run_id": managed.manager_run_id, "artifacts": rows}

    def read_artifact(
        self,
        *,
        token: str,
        project_root: str,
        manager_run_id: str,
        path: str,
    ) -> dict[str, Any]:
        self._authorize(token)
        project = self._project(project_root)
        listed = self.list_artifacts(
            token=token,
            project_root=str(project),
            manager_run_id=manager_run_id,
        )["artifacts"]
        allowed = {str(item["path"]) for item in listed}
        requested = str(path)
        if requested not in allowed:
            raise RemoteControlError("artifact is not recorded by this managed run")
        relative = Path(requested)
        if relative.is_absolute():
            try:
                relative = relative.resolve().relative_to(project)
            except ValueError as exc:
                raise RemoteControlError("artifact path escapes project root") from exc
        loaded = SafeReader(project, max_bytes=self.policy.max_artifact_chars * 4).read_text(relative)
        if len(loaded.content) > self.policy.max_artifact_chars:
            raise RemoteControlError("artifact exceeds remote read character limit")
        self._audit(project, "read_artifact", "OK", manager_run_id=manager_run_id, path=str(relative))
        return {
            "manager_run_id": manager_run_id,
            "path": str(relative),
            "content": loaded.content,
            "chars": len(loaded.content),
        }

    def submit_creative_directive(
        self,
        *,
        token: str,
        project_root: str,
        manager_run_id: str,
        directive: dict[str, Any],
    ) -> dict[str, Any]:
        self._authorize(token)
        project = self._project(project_root)
        manager = self._manager(project)
        managed = manager.resume(str(manager_run_id))
        if not isinstance(directive, dict):
            raise RemoteControlError("creative directive must be an object")
        encoded = json.dumps(directive, ensure_ascii=False, sort_keys=True)
        if len(encoded) > self.policy.max_artifact_chars:
            raise RemoteControlError("creative directive exceeds remote artifact limit")
        verdicts = directive.get("directives", directive.get("items", []))
        if not isinstance(verdicts, list):
            raise RemoteControlError("creative directive directives/items must be an array")
        target = project / "docs" / "uiux" / "remote-directives" / f"{managed.manager_run_id}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(directive, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        managed.task_context["remote_creative_directive"] = str(target.relative_to(project))
        manager._checkpoint_managed(managed)
        self._audit(project, "submit_creative_directive", "OK", manager_run_id=managed.manager_run_id)
        return {"manager_run_id": managed.manager_run_id, "path": str(target.relative_to(project))}

    def start_revision(
        self,
        *,
        token: str,
        project_root: str,
        manager_run_id: str,
        goal: str | None = None,
    ) -> dict[str, Any]:
        self._authorize(token)
        if not self.policy.allow_revision:
            raise RemoteControlError("remote revision starts are disabled by runtime policy")
        project = self._project(project_root)
        manager = self._manager(project)
        previous = manager.resume(str(manager_run_id))
        manager_state = manager.harness.resume(previous.manager_run_id)
        next_goal = str(goal or f"Revise prior managed run {previous.manager_run_id}: {manager_state.task}").strip()
        if not next_goal or len(next_goal) > 12000:
            raise RemoteControlError("revision goal must contain 1..12000 characters")
        context = manager.interpret_goal(next_goal)
        context["revision_of"] = previous.manager_run_id
        directive = previous.task_context.get("remote_creative_directive")
        if directive:
            context["remote_creative_directive"] = directive
        revised = manager.start(next_goal, context, authority=previous.authority)
        self._audit(project, "start_revision", "OK", manager_run_id=revised.manager_run_id, revision_of=previous.manager_run_id)
        payload = self._status_payload(revised)
        payload["revision_of"] = previous.manager_run_id
        return payload

    def cancel(self, *, token: str, project_root: str, manager_run_id: str) -> dict[str, Any]:
        self._authorize(token)
        if not self.policy.allow_cancel:
            raise RemoteControlError("remote cancellation is disabled by runtime policy")
        project = self._project(project_root)
        manager = self._manager(project)
        managed = manager.resume(str(manager_run_id))
        if managed.state in {"COMPLETED", "FAILED", "BLOCKED"}:
            raise RemoteControlError(f"managed run is already terminal: {managed.state}")
        managed.task_context["remote_cancelled"] = True
        managed.state = "BLOCKED"
        manager._checkpoint_managed(managed)
        self._audit(project, "cancel", "OK", manager_run_id=managed.manager_run_id)
        return self._status_payload(managed)
