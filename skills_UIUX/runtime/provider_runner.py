from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runtime.agent import ToolSpec, TraceRecorder
from runtime.manager import DevelopmentManagerAgent, ManagedWebsiteRun
from runtime.provider import ModelProvider, ProviderStageRequest, load_context_documents


@dataclass(frozen=True)
class ProviderRunResult:
    state: str
    active_stage: str
    cycles: int
    provider: str
    model: str
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "active_stage": self.active_stage,
            "cycles": self.cycles,
            "provider": self.provider,
            "model": self.model,
            "message": self.message,
        }


class ProviderManagedRunner:
    """Runs specialist stages as model -> tool -> observation loops under Manager control."""

    def __init__(self, manager: DevelopmentManagerAgent, provider: ModelProvider) -> None:
        self.manager = manager
        self.harness = manager.harness
        self.provider = provider
        self.project_root = self.harness.project_root
        self.write_spec = ToolSpec(
            "write_project_file",
            "Write a UTF-8 project source/config file inside the project root",
            "LOW_WRITE",
            "branch_write",
            True,
        )
        self.write_spec.validate()

    def _set_managed_terminal(self, managed: ManagedWebsiteRun, state: str) -> None:
        managed.state = state
        self.manager._checkpoint_managed(managed)

    def _safe_project_path(self, raw: str) -> Path:
        path = (self.project_root / raw).resolve()
        try:
            path.relative_to(self.project_root.resolve())
        except ValueError as exc:
            raise ValueError(f"path escapes project root: {raw}") from exc
        relative = path.relative_to(self.project_root.resolve())
        forbidden_parts = {".git", ".uiux-agent-runs", "node_modules", ".next", "dist", "build"}
        if any(part in forbidden_parts for part in relative.parts):
            raise ValueError(f"write_project_file refuses generated/internal path: {raw}")
        name = path.name.lower()
        if name == ".env" or name.startswith(".env.") or name in {".npmrc", ".pypirc", ".netrc", "id_rsa", "id_ed25519"}:
            raise ValueError(f"write_project_file refuses credential-bearing path: {raw}")
        return path

    def _write_project_file(self, path: str, content: str) -> dict[str, Any]:
        resolved = self._safe_project_path(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding="utf-8")
        return {
            "path": str(resolved.relative_to(self.project_root)),
            "bytes": len(content.encode("utf-8")),
        }

    def _tools(self, authority: str) -> list[dict[str, Any]]:
        arg_contracts = {
            "read_text": {"path": "project-relative UTF-8 file path"},
            "list_files": {"path": "project-relative directory path; defaults to ."},
            "write_artifact": {"path": "must be below docs/uiux/", "content": "UTF-8 content"},
            "run_validator": {"name": "validate-skills | validate-v2 | validate-runtime | validate-flows"},
            "release_action": {"action": "release intent; contract-only unless an external release adapter exists"},
            "write_project_file": {"path": "project-relative source/config path", "content": "complete UTF-8 file content"},
        }
        specs = list(self.harness.registry.specs.values()) + [self.write_spec]
        result: list[dict[str, Any]] = []
        for spec in specs:
            allowed, reason = self.harness.permissions.authorize(spec, authority)
            if allowed:
                result.append(
                    {
                        "name": spec.name,
                        "description": spec.description,
                        "risk": spec.risk,
                        "arguments": arg_contracts.get(spec.name, {}),
                        "permission": reason,
                    }
                )
        return result

    def _request(
        self,
        managed: ManagedWebsiteRun,
        stage_state: Any,
        observations: list[dict[str, Any]],
    ) -> ProviderStageRequest:
        stage = next(item for item in managed.flow.stages if item.id == managed.active_stage)
        items = list(stage_state.context.get("items", []))
        skills = load_context_documents(items, {"skill"})
        sources = load_context_documents(items, {"source_of_truth", "project_config"})
        manager_state = self.harness.resume(managed.manager_run_id)
        return ProviderStageRequest(
            goal=manager_state.task,
            project_root=str(self.project_root),
            flow_id=managed.flow.id,
            flow_revision=managed.flow.revision,
            stage_id=stage.id,
            agent=stage.agent,
            purpose=stage.purpose,
            gates=list(stage.gates),
            task_context=dict(managed.task_context),
            authority=stage_state.authority,
            tools=self._tools(stage_state.authority),
            skill_context=skills,
            source_context=sources,
            observations=list(observations[-24:]),
        )

    def _execute_actions(
        self,
        stage_state: Any,
        actions: list[dict[str, Any]],
        trace: TraceRecorder,
        dry_run: bool,
    ) -> list[dict[str, Any]]:
        observations: list[dict[str, Any]] = []
        for index, action in enumerate(actions):
            name = str(action["tool"])
            args = dict(action.get("args", {}))
            if name == "write_project_file":
                spec = self.write_spec
                handler = self._write_project_file
            else:
                spec = self.harness.registry.specs.get(name)
                if spec is None:
                    raise ValueError(f"provider requested unknown tool: {name}")
                handler = lambda **kwargs: self.harness.registry.execute(name, kwargs)
            allowed, reason = self.harness.permissions.authorize(spec, stage_state.authority)
            trace.emit(
                "provider.tool.permission",
                "OK" if allowed else "BLOCKED",
                tool=name,
                required_authority=spec.required_authority,
                reason=reason,
            )
            if not allowed:
                raise PermissionError(reason)
            if dry_run:
                result: Any = {"dry_run": True, "tool": name, "args": args}
            else:
                trace.emit("provider.tool.call", "START", tool=name, args=args)
                result = handler(**args)
                trace.emit("provider.tool.call", "OK", tool=name, result=result)
            observation = {"tool": name, "result": result}
            observations.append(observation)
            stage_state.completed_actions.append(f"provider:{index}:{name}")
            if name in {"write_project_file", "write_artifact"} and isinstance(result, dict) and result.get("path"):
                artifact = str(result["path"])
                if artifact not in stage_state.artifacts:
                    stage_state.artifacts.append(artifact)
            stage_state.context["provider_observations"] = list(
                stage_state.context.get("provider_observations", [])[-48:]
            ) + [observation]
            self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())
        return observations

    def run_active_stage(
        self,
        managed: ManagedWebsiteRun,
        max_turns: int = 12,
        auto_replan: bool = True,
        dry_run: bool = False,
    ) -> ProviderRunResult:
        stage_state = self.manager.start_stage(managed)
        stage_state.limitations = [
            item for item in stage_state.limitations if item != "model/provider reasoning is not bundled"
        ]
        stage_state.limitations.append(
            "provider execution is active; browser-rendered visual QA still requires a connected render/observation adapter"
        )
        trace = TraceRecorder(
            self.project_root / ".uiux-agent-runs" / stage_state.run_id / "trace.jsonl",
            stage_state.run_id,
        )
        observations: list[dict[str, Any]] = list(stage_state.context.get("provider_observations", []))
        stage_state.state = "RUNNING"
        self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())

        for turn in range(1, max_turns + 1):
            request = self._request(managed, stage_state, observations)
            trace.emit(
                "provider.call",
                "START",
                provider=self.provider.name,
                model=self.provider.model,
                stage=managed.active_stage,
                turn=turn,
            )
            try:
                response = self.provider.run_stage(request)
            except Exception as exc:
                trace.emit("provider.call", "ERROR", error_type=type(exc).__name__, message=str(exc))
                stage_state.state = "FAILED"
                stage_state.limitations.append(f"provider failure: {type(exc).__name__}: {exc}")
                self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())
                if auto_replan:
                    decision = self.manager.replan(managed, "TOOL_FAILURE")
                    return ProviderRunResult(
                        "REPLANNED" if decision.accepted else "FAILED",
                        managed.active_stage,
                        turn,
                        self.provider.name,
                        self.provider.model,
                        decision.reason,
                    )
                self._set_managed_terminal(managed, "FAILED")
                raise

            trace.emit("provider.call", "OK", response=response.to_dict())
            if response.actions:
                try:
                    new_observations = self._execute_actions(stage_state, response.actions, trace, dry_run)
                    observations.extend(new_observations)
                except Exception as exc:
                    trace.emit("provider.tool.error", "ERROR", error_type=type(exc).__name__, message=str(exc))
                    stage_state.state = "FAILED"
                    self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())
                    if auto_replan:
                        decision = self.manager.replan(managed, "TOOL_FAILURE")
                        return ProviderRunResult(
                            "REPLANNED" if decision.accepted else "FAILED",
                            managed.active_stage,
                            turn,
                            self.provider.name,
                            self.provider.model,
                            decision.reason,
                        )
                    self._set_managed_terminal(managed, "FAILED")
                    raise

            stage_state.context["provider"] = {"name": self.provider.name, "model": self.provider.model}
            stage_state.context["provider_summary"] = response.summary
            stage_state.context["gate_evidence"] = list(response.evidence)
            self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())

            if response.status == "CONTINUE":
                if not response.actions:
                    self._set_managed_terminal(managed, "FAILED")
                    raise ValueError("provider returned CONTINUE without actions")
                continue

            if response.status == "PASS":
                stage_state.state = "COMPLETED"
                self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())
                try:
                    self.manager.complete_stage(managed)
                except ValueError as exc:
                    if managed.state == "AWAITING_APPROVAL":
                        return ProviderRunResult(
                            "AWAITING_APPROVAL",
                            managed.active_stage,
                            turn,
                            self.provider.name,
                            self.provider.model,
                            str(exc),
                        )
                    raise
                return ProviderRunResult(
                    managed.state,
                    managed.active_stage,
                    turn,
                    self.provider.name,
                    self.provider.model,
                    response.summary,
                )

            signal = response.replan_signal or ("GATE_FAIL" if response.status == "FAIL" else "BLOCKED")
            stage_state.state = response.status
            self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())
            if auto_replan:
                decision = self.manager.replan(managed, signal)
                return ProviderRunResult(
                    "REPLANNED" if decision.accepted else response.status,
                    managed.active_stage,
                    turn,
                    self.provider.name,
                    self.provider.model,
                    decision.reason,
                )
            self._set_managed_terminal(managed, response.status)
            return ProviderRunResult(
                response.status,
                managed.active_stage,
                turn,
                self.provider.name,
                self.provider.model,
                response.summary,
            )

        decision = self.manager.replan(managed, "TOOL_FAILURE") if auto_replan else None
        if decision is None or not decision.accepted:
            self._set_managed_terminal(managed, "FAILED")
        return ProviderRunResult(
            "REPLANNED" if decision and decision.accepted else "FAILED",
            managed.active_stage,
            max_turns,
            self.provider.name,
            self.provider.model,
            "provider turn budget exhausted" if decision is None else decision.reason,
        )

    def run_to_boundary(
        self,
        managed: ManagedWebsiteRun,
        max_cycles: int = 16,
        max_turns_per_stage: int = 12,
        auto_replan: bool = True,
        dry_run: bool = False,
    ) -> ProviderRunResult:
        last = ProviderRunResult(
            managed.state,
            managed.active_stage,
            0,
            self.provider.name,
            self.provider.model,
        )
        for cycle in range(1, max_cycles + 1):
            if managed.state in {"COMPLETED", "AWAITING_APPROVAL", "BLOCKED", "FAILED"}:
                return ProviderRunResult(
                    managed.state,
                    managed.active_stage,
                    cycle - 1,
                    self.provider.name,
                    self.provider.model,
                    last.message,
                )
            last = self.run_active_stage(
                managed,
                max_turns=max_turns_per_stage,
                auto_replan=auto_replan,
                dry_run=dry_run,
            )
            if last.state in {"AWAITING_APPROVAL", "BLOCKED", "FAILED"} or managed.state == "COMPLETED":
                return ProviderRunResult(
                    managed.state if managed.state == "COMPLETED" else last.state,
                    managed.active_stage,
                    cycle,
                    self.provider.name,
                    self.provider.model,
                    last.message,
                )
        self._set_managed_terminal(managed, "FAILED")
        return ProviderRunResult(
            "FAILED",
            managed.active_stage,
            max_cycles,
            self.provider.name,
            self.provider.model,
            "managed provider cycle budget exhausted",
        )
