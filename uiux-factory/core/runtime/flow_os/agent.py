from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


AUTHORITY_ORDER = ("read_only", "branch_write", "external_write", "release")
RISK_LEVELS = ("READ", "LOW_WRITE", "HIGH_WRITE", "CRITICAL")
SENSITIVE_FRAGMENTS = ("token", "secret", "password", "authorization", "cookie", "api_key", "apikey")


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    risk: str
    required_authority: str
    side_effect: bool

    def validate(self) -> None:
        if self.risk not in RISK_LEVELS:
            raise ValueError(f"unknown risk: {self.risk}")
        if self.required_authority not in AUTHORITY_ORDER:
            raise ValueError(f"unknown authority: {self.required_authority}")


@dataclass
class RunState:
    run_id: str
    task: str
    project_root: str
    agent: str
    authority: str
    state: str = "READY"
    active_role: str = ""
    completed_actions: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _redact(value: Any, key: str = "") -> Any:
    if any(fragment in key.lower() for fragment in SENSITIVE_FRAGMENTS):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {k: _redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


class TraceRecorder:
    def __init__(self, path: Path, run_id: str) -> None:
        self.path = path
        self.run_id = run_id
        path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: str, status: str = "INFO", **attributes: Any) -> None:
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "event": event,
            "status": status,
            "attributes": _redact(attributes),
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class LocalCheckpointStore:
    """Atomic local resume only; not distributed workflow durability."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def path_for(self, run_id: str) -> Path:
        return self.base_dir / run_id / "checkpoint.json"

    def save(self, run_id: str, payload: dict[str, Any]) -> Path:
        path = self.path_for(run_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)
        return path

    def load(self, run_id: str) -> dict[str, Any]:
        path = self.path_for(run_id)
        if not path.exists():
            raise FileNotFoundError(f"checkpoint not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))


def _context_item(kind: str, path: Path, trust: str) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    chars = len(text)
    return {
        "kind": kind,
        "path": str(path),
        "trust": trust,
        "chars": chars,
        "estimated_tokens": math.ceil(chars / 4),
    }


def build_context_manifest(
    project_root: Path,
    library_root: Path,
    selected_skills: list[str] | None = None,
    explicit_sources: list[str] | None = None,
) -> dict[str, Any]:
    selected_skills = selected_skills or []
    explicit_sources = explicit_sources or []
    items: list[dict[str, Any]] = []

    config_path = project_root / ".uiux-profile.json"
    config: dict[str, Any] = {}
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        items.append(_context_item("project_config", config_path, "project_authoritative"))

    manifest_path = project_root / ".claude" / "skills" / ".skills-uiux-manifest.json"
    installed_skills: list[str] = []
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        installed_skills = list(manifest.get("skills", []))
        items.append(_context_item("installed_manifest", manifest_path, "verify_before_acting"))

    for skill in selected_skills:
        if installed_skills and skill not in installed_skills:
            raise ValueError(f"selected skill is not installed in project manifest: {skill}")
        skill_path = library_root / skill / "SKILL.md"
        if not skill_path.exists():
            skill_path = project_root / ".claude" / "skills" / skill / "SKILL.md"
        if not skill_path.exists():
            raise ValueError(f"selected skill not found: {skill}")
        items.append(_context_item("skill", skill_path, "routed_knowledge"))

    declared_sources = list(config.get("source_of_truth", [])) if config else []
    for raw in explicit_sources:
        path = (project_root / raw).resolve()
        try:
            path.relative_to(project_root.resolve())
        except ValueError as exc:
            raise ValueError(f"source escapes project root: {raw}") from exc
        if not path.exists() or not path.is_file():
            raise ValueError(f"explicit source not found: {raw}")
        items.append(_context_item("source_of_truth", path, "project_authoritative"))

    return {
        "project_root": str(project_root),
        "selected_skills": selected_skills,
        "declared_sources": declared_sources,
        "loaded_sources": explicit_sources,
        "items": items,
        "totals": {
            "items": len(items),
            "chars": sum(item["chars"] for item in items),
            "estimated_tokens": sum(item["estimated_tokens"] for item in items),
        },
        "rule": "declared source_of_truth is discoverable but loaded only when explicitly selected for the active decision",
    }


class PermissionGate:
    def __init__(self, policy_path: Path) -> None:
        self.policy = json.loads(policy_path.read_text(encoding="utf-8"))
        self.order = tuple(self.policy.get("authority_order", AUTHORITY_ORDER))

    def authorize(self, tool: ToolSpec, granted_authority: str) -> tuple[bool, str]:
        if granted_authority not in self.order or tool.required_authority not in self.order:
            return False, "unknown authority"
        if self.order.index(granted_authority) < self.order.index(tool.required_authority):
            return False, f"{tool.name} requires {tool.required_authority}; run grants {granted_authority}"
        if tool.risk == "CRITICAL" and granted_authority != "release":
            return False, "critical action requires explicit release authority"
        return True, f"authority {granted_authority} satisfies {tool.required_authority}"


Handler = Callable[..., Any]


class ToolRegistry:
    def __init__(self, repo_root: Path, project_root: Path) -> None:
        self.repo_root = repo_root
        self.project_root = project_root
        self.specs: dict[str, ToolSpec] = {}
        self.handlers: dict[str, Handler] = {}
        self._register("read_text", "Read a UTF-8 project file", "READ", "read_only", False, self._read_text)
        self._register("list_files", "List files below a project-relative directory", "READ", "read_only", False, self._list_files)
        self._register("write_artifact", "Write a project-local UI/UX artifact", "LOW_WRITE", "branch_write", True, self._write_artifact)
        self._register("run_validator", "Run an allowlisted skills_UIUX validator", "READ", "read_only", False, self._run_validator)
        self._register("release_action", "Contract-only release boundary", "CRITICAL", "release", True, self._release_action)

    def _register(self, name: str, description: str, risk: str, authority: str, side_effect: bool, handler: Handler) -> None:
        spec = ToolSpec(name, description, risk, authority, side_effect)
        spec.validate()
        self.specs[name] = spec
        self.handlers[name] = handler

    def _resolve_project_path(self, raw: str) -> Path:
        path = (self.project_root / raw).resolve()
        try:
            path.relative_to(self.project_root.resolve())
        except ValueError as exc:
            raise ValueError(f"path escapes project root: {raw}") from exc
        return path

    def _read_text(self, path: str) -> dict[str, Any]:
        resolved = self._resolve_project_path(path)
        return {"path": path, "content": resolved.read_text(encoding="utf-8", errors="replace")}

    def _list_files(self, path: str = ".") -> dict[str, Any]:
        resolved = self._resolve_project_path(path)
        if not resolved.exists() or not resolved.is_dir():
            raise ValueError(f"directory not found: {path}")
        return {
            "path": path,
            "items": sorted(str(item.relative_to(self.project_root)) for item in resolved.iterdir()),
        }

    def _write_artifact(self, path: str, content: str) -> dict[str, Any]:
        resolved = self._resolve_project_path(path)
        allowed = self.project_root / "docs" / "uiux"
        allowed.mkdir(parents=True, exist_ok=True)
        try:
            resolved.relative_to(allowed.resolve())
        except ValueError as exc:
            raise ValueError("write_artifact is restricted to docs/uiux/") from exc
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
        return {"path": str(resolved.relative_to(self.project_root)), "bytes": len(content.encode("utf-8"))}

    def _run_validator(self, name: str) -> dict[str, Any]:
        allowlist = {
            "validate-skills": self.repo_root / "scripts" / "validate-skills.py",
            "validate-v2": self.repo_root / "scripts" / "validate-v2.py",
            "validate-runtime": self.repo_root / "scripts" / "validate-runtime-foundation.py",
            "validate-flows": self.repo_root / "scripts" / "validate-flows.py",
        }
        script = allowlist.get(name)
        if not script:
            raise ValueError(f"validator not allowlisted: {name}")
        result = subprocess.run(
            [sys.executable, "-B", str(script)],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "name": name,
            "returncode": result.returncode,
            "stdout": result.stdout[-8000:],
            "stderr": result.stderr[-8000:],
        }

    def _release_action(self, action: str) -> dict[str, Any]:
        return {
            "action": action,
            "executed": False,
            "system_reality": "CONTRACT_ONLY",
            "message": "No external release adapter is bundled.",
        }

    def execute(self, name: str, args: dict[str, Any]) -> Any:
        if name not in self.handlers:
            raise ValueError(f"unknown tool: {name}")
        return self.handlers[name](**args)


class ProviderNeutralAgentHarness:
    """Executes a provider-produced action plan under skills_UIUX guardrails."""

    def __init__(self, repo_root: Path, project_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.project_root = project_root.resolve()
        self.policy_path = self.repo_root / "runtime" / "runtime-policy.json"
        self.policy_doc = json.loads(self.policy_path.read_text(encoding="utf-8"))
        self.permissions = PermissionGate(self.policy_path)
        self.registry = ToolRegistry(self.repo_root, self.project_root)
        self.checkpoints = LocalCheckpointStore(self.project_root / ".uiux-agent-runs")

    def _role(self, name: str) -> dict[str, Any]:
        roles = self.policy_doc.get("roles", {})
        if name not in roles:
            raise ValueError(f"unknown agent role: {name}")
        return roles[name]

    def create_run(
        self,
        task: str,
        agent: str,
        authority: str,
        selected_skills: list[str] | None = None,
        explicit_sources: list[str] | None = None,
        run_id: str | None = None,
    ) -> RunState:
        role = self._role(agent)
        order = tuple(self.permissions.order)
        if order.index(authority) > order.index(role["max_authority"]):
            raise ValueError(f"role {agent} caps authority at {role['max_authority']}")

        effective_skills = _unique(list(role.get("default_skills", [])) + list(selected_skills or []))
        state = RunState(
            run_id=run_id or uuid.uuid4().hex[:16],
            task=task,
            project_root=str(self.project_root),
            agent=agent,
            authority=authority,
            active_role=agent,
            context=build_context_manifest(
                self.project_root,
                self.repo_root,
                selected_skills=effective_skills,
                explicit_sources=explicit_sources,
            ),
            limitations=[
                "model/provider reasoning is not bundled",
                "external MCP/Figma/Playwright integrations are optional adapters",
                "local checkpoints are not distributed durable execution",
            ],
        )
        self.checkpoints.save(state.run_id, state.to_dict())
        return state

    def execute_plan(self, state: RunState, actions: list[dict[str, Any]], dry_run: bool = False) -> RunState:
        trace = TraceRecorder(
            self.project_root / ".uiux-agent-runs" / state.run_id / "trace.jsonl",
            state.run_id,
        )
        state.state = "RUNNING"
        trace.emit("run.start", "START", agent=state.agent, authority=state.authority, context=state.context.get("totals", {}))
        self.checkpoints.save(state.run_id, state.to_dict())

        try:
            for index, action in enumerate(actions):
                if "handoff" in action:
                    target = str(action["handoff"])
                    source_role = state.active_role
                    source = self._role(source_role)
                    allowed_targets = set(source.get("handoff_targets", []))
                    if target not in allowed_targets:
                        raise ValueError(
                            f"handoff {source_role} -> {target} is not allowed; "
                            f"allowed targets: {', '.join(sorted(allowed_targets)) or '(none)'}"
                        )
                    target_role = self._role(target)
                    order = tuple(self.permissions.order)
                    if order.index(state.authority) > order.index(target_role["max_authority"]):
                        state.authority = target_role["max_authority"]
                    state.active_role = target
                    target_defaults = list(target_role.get("default_skills", []))
                    loaded_sources = list(state.context.get("loaded_sources", []))
                    state.context = build_context_manifest(
                        self.project_root,
                        self.repo_root,
                        selected_skills=target_defaults,
                        explicit_sources=loaded_sources,
                    )
                    state.completed_actions.append(f"handoff:{target}")
                    trace.emit(
                        "agent.handoff",
                        "OK",
                        source=source_role,
                        target=target,
                        effective_authority=state.authority,
                        active_skills=target_defaults,
                    )
                    self.checkpoints.save(state.run_id, state.to_dict())
                    continue

                name = str(action["tool"])
                args = dict(action.get("args", {}))
                spec = self.registry.specs.get(name)
                if not spec:
                    raise ValueError(f"unknown tool: {name}")
                allowed, reason = self.permissions.authorize(spec, state.authority)
                trace.emit(
                    "tool.permission",
                    "OK" if allowed else "BLOCKED",
                    tool=name,
                    risk=spec.risk,
                    required_authority=spec.required_authority,
                    reason=reason,
                )
                if not allowed:
                    state.state = "BLOCKED"
                    self.checkpoints.save(state.run_id, state.to_dict())
                    return state

                if dry_run:
                    result = {"dry_run": True, "tool": name}
                else:
                    trace.emit("tool.call", "START", tool=name, args=args)
                    result = self.registry.execute(name, args)
                    trace.emit("tool.call", "OK", tool=name, result=result)

                state.completed_actions.append(f"{index}:{name}")
                self.checkpoints.save(state.run_id, state.to_dict())

            state.state = "COMPLETED"
            trace.emit("run.complete", "OK", completed_actions=state.completed_actions)
            self.checkpoints.save(state.run_id, state.to_dict())
            return state
        except Exception as exc:
            state.state = "FAILED"
            trace.emit("run.error", "ERROR", error_type=type(exc).__name__, message=str(exc))
            self.checkpoints.save(state.run_id, state.to_dict())
            raise

    def resume(self, run_id: str) -> RunState:
        return RunState(**self.checkpoints.load(run_id))
