from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.runtime.flow_os.agent import ToolRegistry, ToolSpec, TraceRecorder
from core.runtime.flow_os.evidence import evidence_from_tool, gate_evidence_errors, provider_claim_records
from core.runtime.flow_os.file_tools import WorkspaceFileTools
from core.runtime.flow_os.managed import ManagedFlowController, ManagedWebsiteRun
from core.runtime.flow_os.provider import ModelProvider, ProviderStageRequest, load_context_documents
from core.runtime.flow_os.sandbox import ContainerSandbox
from core.runtime.flow_os.workspace import WorkspaceMetadata, WorktreeManager


class ProviderContextBudgetError(ValueError):
    """The next provider request would exceed the operator-owned document context ceiling."""


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
    """Run model→tool→observation loops under the canonical managed controller.

    Provider-facing execution is isolated through one Git worktree and target commands
    additionally require the canonical container sandbox. Runtime observations become
    typed evidence while provider prose remains untrusted claims.
    """

    def __init__(self, manager: ManagedFlowController, provider: ModelProvider) -> None:
        self.manager = manager
        self.harness = manager.harness
        self.provider = provider
        self.project_root = self.harness.project_root
        self.worktrees = WorktreeManager(self.project_root)
        self.extra_specs = {
            "write_project_file": ToolSpec(
                "write_project_file",
                "Write one bounded UTF-8 file inside the isolated branch worktree",
                "LOW_WRITE",
                "branch_write",
                True,
            ),
            "replace_text": ToolSpec(
                "replace_text",
                "Replace an exact bounded text occurrence inside the isolated branch worktree",
                "LOW_WRITE",
                "branch_write",
                True,
            ),
            "search_text": ToolSpec(
                "search_text",
                "Bounded recursive plain-text search with Safe Read filtering",
                "READ",
                "read_only",
                False,
            ),
            "list_files_recursive": ToolSpec(
                "list_files_recursive",
                "Bounded recursive file listing with secret/symlink filtering",
                "READ",
                "read_only",
                False,
            ),
            "run_target_command": ToolSpec(
                "run_target_command",
                "Run an exact allowlisted argv command in the required container/network sandbox",
                "LOW_WRITE",
                "branch_write",
                True,
            ),
            "activate_skill_context": ToolSpec(
                "activate_skill_context",
                "Activate one Flow-routed non-mandatory skill for subsequent provider turns",
                "READ",
                "read_only",
                False,
            ),
        }
        for spec in self.extra_specs.values():
            spec.validate()

    def _set_managed_terminal(self, managed: ManagedWebsiteRun, state: str) -> None:
        managed.state = state
        self.manager._checkpoint_managed(managed)

    def _manager_workspace(self, managed: ManagedWebsiteRun) -> WorkspaceMetadata | None:
        manager_state = self.harness.resume(managed.manager_run_id)
        raw = manager_state.context.get("workspace")
        if not isinstance(raw, dict):
            return None
        return self.worktrees.validate_metadata(raw, expected_run_id=managed.manager_run_id)

    def _ensure_workspace(self, managed: ManagedWebsiteRun, stage_state: Any) -> WorkspaceMetadata:
        metadata = self._manager_workspace(managed)
        if metadata is None:
            metadata = self.worktrees.ensure(managed.manager_run_id)
            manager_state = self.harness.resume(managed.manager_run_id)
            manager_state.context["workspace"] = metadata.to_dict()
            self.harness.checkpoints.save(manager_state.run_id, manager_state.to_dict())
        stage_state.context["workspace"] = metadata.to_dict()
        self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())
        return metadata

    def _active_root(self, managed: ManagedWebsiteRun, stage_state: Any) -> Path:
        raw = stage_state.context.get("workspace")
        if isinstance(raw, dict):
            return Path(
                self.worktrees.validate_metadata(raw, expected_run_id=managed.manager_run_id).workspace_root
            ).resolve()
        metadata = self._manager_workspace(managed)
        if metadata is not None:
            stage_state.context["workspace"] = metadata.to_dict()
            self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())
            return Path(metadata.workspace_root).resolve()
        return self.project_root

    def _registry_for(self, managed: ManagedWebsiteRun, stage_state: Any) -> ToolRegistry:
        return ToolRegistry(self.harness.repo_root, self._active_root(managed, stage_state))

    def _file_tools_for(
        self,
        managed: ManagedWebsiteRun,
        stage_state: Any,
        require_workspace: bool = False,
    ) -> WorkspaceFileTools:
        root = (
            Path(self._ensure_workspace(managed, stage_state).workspace_root)
            if require_workspace
            else self._active_root(managed, stage_state)
        )
        return WorkspaceFileTools(root)

    def _jit_config(self) -> tuple[bool, int]:
        raw = self.harness.policy_doc.get("jit_skill_context", {})
        if not isinstance(raw, dict):
            raise ValueError("runtime-policy jit_skill_context must be an object")

        enabled = raw.get("enabled", True)
        if not isinstance(enabled, bool):
            raise ValueError("jit_skill_context.enabled must be a boolean")

        max_active = raw.get("max_active_per_stage", 6)
        if isinstance(max_active, bool) or not isinstance(max_active, int):
            raise ValueError("jit_skill_context.max_active_per_stage must be an integer")
        if max_active < 1 or max_active > 32:
            raise ValueError("jit_skill_context.max_active_per_stage must be between 1 and 32")
        return enabled, max_active

    def _provider_context_budget(self) -> tuple[int, str]:
        raw = self.harness.policy_doc.get("provider_context", {})
        if raw is None:
            raw = {}
        if not isinstance(raw, dict):
            raise ValueError("runtime-policy provider_context must be an object")

        max_chars = raw.get("max_document_chars_per_request", 180000)
        if isinstance(max_chars, bool) or not isinstance(max_chars, int):
            raise ValueError("provider_context.max_document_chars_per_request must be an integer")
        if max_chars < 1 or max_chars > 2_000_000:
            raise ValueError("provider_context.max_document_chars_per_request must be between 1 and 2000000")

        source = "runtime_policy"
        env_raw = os.environ.get("UIUX_PROVIDER_CONTEXT_CHARS", "").strip()
        if env_raw:
            try:
                env_chars = int(env_raw)
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError("UIUX_PROVIDER_CONTEXT_CHARS must be a positive integer") from exc
            if env_chars < 1 or env_chars > 2_000_000:
                raise ValueError("UIUX_PROVIDER_CONTEXT_CHARS must be between 1 and 2000000")
            if env_chars < max_chars:
                source = "runtime_policy+env_ceiling"
            max_chars = min(max_chars, env_chars)
        return max_chars, source

    @staticmethod
    def _skill_name(item: dict[str, Any]) -> str:
        path = Path(str(item.get("path", "")))
        return path.parent.name if path.name == "SKILL.md" else ""

    @staticmethod
    def _document_chars(documents: list[dict[str, str]]) -> int:
        return sum(len(str(item.get("content", ""))) for item in documents)

    def _load_provider_context(
        self,
        stage_state: Any,
        active_skill_names: set[str],
    ) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, Any]]:
        items = list(stage_state.context.get("items", []))
        allowed_roots = (self.project_root, self.harness.repo_root)
        limit, source = self._provider_context_budget()
        skill_items = [
            item
            for item in items
            if str(item.get("kind", "")) == "skill" and self._skill_name(item) in active_skill_names
        ]
        try:
            skills = load_context_documents(
                skill_items,
                {"skill"},
                max_chars=limit,
                allowed_roots=allowed_roots,
            )
            sources = load_context_documents(
                items,
                {"source_of_truth", "project_config"},
                max_chars=limit,
                allowed_roots=allowed_roots,
            )
        except ValueError as exc:
            if "provider context budget exceeded" in str(exc):
                raise ProviderContextBudgetError(str(exc)) from exc
            raise

        skill_chars = self._document_chars(skills)
        source_chars = self._document_chars(sources)
        loaded_chars = skill_chars + source_chars
        if loaded_chars > limit:
            raise ProviderContextBudgetError(
                "shared provider context document budget exceeded "
                f"({loaded_chars}>{limit} chars across skill + source documents); "
                "route/activate fewer skills, load fewer sources, or deliberately raise "
                "provider_context.max_document_chars_per_request"
            )
        return skills, sources, {
            "max_document_chars_per_request": limit,
            "loaded_document_chars": loaded_chars,
            "skill_document_chars": skill_chars,
            "source_document_chars": source_chars,
            "remaining_document_chars": max(0, limit - loaded_chars),
            "source": source,
            "measurement": "unicode_chars",
        }

    def _jit_skill_state(self, managed: ManagedWebsiteRun, stage_state: Any) -> dict[str, Any]:
        stage = next(item for item in managed.flow.stages if item.id == managed.active_stage)
        mandatory = list(stage.mandatory_skills)
        pool = list(stage.jit_skills)
        sources = dict(stage.jit_skill_sources)
        enabled, max_active = self._jit_config()
        if not enabled:
            return {
                "enabled": False,
                "mandatory": mandatory,
                "pool": pool,
                "sources": sources,
                "active": list(pool),
                "available": [],
                "max_active": max_active,
            }

        raw_active = stage_state.context.get("jit_active_skills", [])
        if not isinstance(raw_active, list):
            raise ValueError("jit_active_skills checkpoint state must be a list")
        active: list[str] = []
        for raw_skill in raw_active:
            skill = str(raw_skill).strip()
            if skill and skill not in active:
                active.append(skill)
        invalid = sorted(set(active).difference(pool))
        if invalid:
            raise ValueError("checkpoint contains non-routed JIT skills: " + ", ".join(invalid))
        if len(active) > max_active:
            raise ValueError("checkpoint JIT skill count exceeds runtime-policy max_active_per_stage")
        return {
            "enabled": True,
            "mandatory": mandatory,
            "pool": pool,
            "sources": sources,
            "active": active,
            "available": [skill for skill in pool if skill not in set(active)],
            "max_active": max_active,
        }

    def _activate_skill_context(
        self,
        managed: ManagedWebsiteRun,
        stage_state: Any,
        *,
        skill: str,
    ) -> dict[str, Any]:
        state = self._jit_skill_state(managed, stage_state)
        if not state["enabled"]:
            raise ValueError("JIT skill activation is disabled by runtime policy")
        requested = str(skill).strip()
        if not requested:
            raise ValueError("activate_skill_context requires a non-empty skill name")
        if requested in set(state["mandatory"]):
            raise ValueError(f"skill is mandatory and already active: {requested}")
        if requested not in set(state["pool"]):
            raise ValueError(f"skill is not in the Flow-routed JIT pool for this stage: {requested}")

        active = list(state["active"])
        already_active = requested in active
        if not already_active:
            if len(active) >= int(state["max_active"]):
                raise ValueError("JIT skill activation limit reached for this stage")
            active.append(requested)

        try:
            _skills, _sources, context_budget = self._load_provider_context(
                stage_state,
                set(state["mandatory"]) | set(active),
            )
        except ProviderContextBudgetError as exc:
            return {
                "activated": None,
                "requested": requested,
                "accepted": False,
                "source": state["sources"].get(requested, "legacy_inferred"),
                "already_active": already_active,
                "active_jit_skills": list(state["active"]),
                "remaining_jit_skills": [
                    name for name in state["pool"] if name not in set(state["active"])
                ],
                "available_next_turn": False,
                "reason": str(exc),
                "authority_effect": "none",
                "gate_effect": "none",
                "evidence_effect": "none",
            }

        if not already_active:
            stage_state.context["jit_active_skills"] = active
            self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())

        remaining = [name for name in state["pool"] if name not in set(active)]
        return {
            "activated": requested,
            "requested": requested,
            "accepted": True,
            "source": state["sources"].get(requested, "legacy_inferred"),
            "already_active": already_active,
            "active_jit_skills": active,
            "remaining_jit_skills": remaining,
            "available_next_turn": True,
            "document_chars_after_activation": int(context_budget["loaded_document_chars"]),
            "document_char_limit": int(context_budget["max_document_chars_per_request"]),
            "remaining_document_chars": int(context_budget["remaining_document_chars"]),
            "authority_effect": "none",
            "gate_effect": "none",
            "evidence_effect": "none",
        }

    def _tools(self, authority: str, available_jit_skills: list[str] | None = None) -> list[dict[str, Any]]:
        arg_contracts = {
            "read_text": {"path": "safe project/worktree-relative UTF-8 file path"},
            "list_files": {"path": "safe project/worktree-relative directory path; defaults to ."},
            "write_artifact": {"path": "must be below docs/uiux/ in isolated worktree", "content": "UTF-8 content"},
            "run_validator": {"name": "validate-skills | validate-v2 | validate-runtime | validate-flows"},
            "release_action": {"action": "release intent; production release is human-owned outside provider tools"},
            "write_project_file": {"path": "workspace-relative source/config path", "content": "complete UTF-8 file content"},
            "replace_text": {
                "path": "workspace-relative UTF-8 file",
                "old": "exact text to replace",
                "new": "replacement text",
                "expected_count": "positive exact occurrence count; defaults to 1",
            },
            "search_text": {
                "query": "plain text; max 512 characters",
                "path": "relative directory; defaults to .",
                "regex": "must remain false; regex evaluation is disabled in the bounded runtime",
                "case_sensitive": "boolean; defaults false",
                "max_files": "1..1000",
                "max_matches": "1..1000",
            },
            "list_files_recursive": {"path": "relative directory", "max_files": "1..1000"},
            "run_target_command": {
                "argv": "exact runtime-policy allowlisted argv array",
                "cwd": "workspace-relative directory; defaults to .",
                "timeout_seconds": "positive integer no larger than policy maximum",
                "sandbox": "required Docker/Podman container; network none; no host fallback",
            },
            "activate_skill_context": {
                "skill": "one exact name from task_context.jit_skill_context.available_jit_skills"
            },
        }
        available = set(available_jit_skills or [])
        specs = list(self.harness.registry.specs.values()) + list(self.extra_specs.values())
        result: list[dict[str, Any]] = []
        for spec in specs:
            if spec.name == "activate_skill_context" and not available:
                continue
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
        jit = self._jit_skill_state(managed, stage_state)
        active_names = set(jit["mandatory"]) | set(jit["active"])
        skills, sources, context_budget = self._load_provider_context(stage_state, active_names)
        manager_state = self.harness.resume(managed.manager_run_id)
        task_context = dict(managed.task_context)
        task_context["jit_skill_context"] = {
            "enabled": bool(jit["enabled"]),
            "mandatory_skills": list(jit["mandatory"]),
            "active_jit_skills": list(jit["active"]),
            "available_jit_skills": list(jit["available"]),
            "jit_skill_sources": {
                skill: str(jit["sources"].get(skill, "legacy_inferred"))
                for skill in jit["pool"]
            },
            "max_active_per_stage": int(jit["max_active"]),
            "authority_effect": "none",
            "gate_effect": "none",
            "evidence_effect": "none",
            "rule": (
                "Only Flow-routed non-mandatory skills may be activated. Activation adds knowledge on the next "
                "provider turn; it cannot add authority, satisfy gates or count as runtime evidence."
            ),
        }
        task_context["provider_context_budget"] = {
            **context_budget,
            "authority_effect": "none",
            "gate_effect": "none",
            "evidence_effect": "none",
            "rule": (
                "Skill and source documents share one operator-owned request ceiling. "
                "JIT activation is accepted only when the resulting next-turn document context fits this budget."
            ),
        }
        return ProviderStageRequest(
            goal=manager_state.task,
            project_root=str(self._active_root(managed, stage_state)),
            flow_id=managed.flow.id,
            flow_revision=managed.flow.revision,
            stage_id=stage.id,
            agent=stage.agent,
            purpose=stage.purpose,
            gates=list(stage.gates),
            task_context=task_context,
            authority=stage_state.authority,
            tools=self._tools(stage_state.authority, list(jit["available"])),
            skill_context=skills,
            source_context=sources,
            observations=list(observations[-24:]),
        )

    def _spec_for(self, name: str, registry: ToolRegistry) -> ToolSpec:
        if name in self.extra_specs:
            return self.extra_specs[name]
        spec = registry.specs.get(name)
        if spec is None:
            raise ValueError(f"provider requested unknown tool: {name}")
        return spec

    def _execute_one(
        self,
        managed: ManagedWebsiteRun,
        stage_state: Any,
        name: str,
        args: dict[str, Any],
    ) -> Any:
        if name == "activate_skill_context":
            return self._activate_skill_context(managed, stage_state, **args)
        if name == "write_project_file":
            return self._file_tools_for(managed, stage_state, require_workspace=True).write_text(**args)
        if name == "replace_text":
            return self._file_tools_for(managed, stage_state, require_workspace=True).replace_text(**args)
        if name == "search_text":
            return self._file_tools_for(managed, stage_state).search_text(**args)
        if name == "list_files_recursive":
            return self._file_tools_for(managed, stage_state).list_files_recursive(**args)
        if name == "run_target_command":
            metadata = self._ensure_workspace(managed, stage_state)
            sandbox = ContainerSandbox(Path(metadata.workspace_root), self.harness.policy_doc)
            return sandbox.run(**args).to_dict()
        if name == "write_artifact":
            metadata = self._ensure_workspace(managed, stage_state)
            path = str(args.get("path", ""))
            normalized = Path(path)
            if normalized.is_absolute() or tuple(normalized.parts[:2]) != ("docs", "uiux"):
                raise ValueError("write_artifact is restricted to docs/uiux/ in the isolated worktree")
            return WorkspaceFileTools(Path(metadata.workspace_root)).write_text(path, str(args.get("content", "")))
        registry = self._registry_for(managed, stage_state)
        return registry.execute(name, args)

    def _execute_actions(
        self,
        managed: ManagedWebsiteRun,
        stage_state: Any,
        actions: list[dict[str, Any]],
        trace: TraceRecorder,
        dry_run: bool,
    ) -> list[dict[str, Any]]:
        observations: list[dict[str, Any]] = []
        stage = next(item for item in managed.flow.stages if item.id == managed.active_stage)
        for index, action in enumerate(actions):
            name = str(action["tool"])
            args = dict(action.get("args", {}))
            registry = self._registry_for(managed, stage_state)
            spec = self._spec_for(name, registry)
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
                evidence = None
            else:
                trace.emit("provider.tool.call", "START", tool=name, args=args)
                result = self._execute_one(managed, stage_state, name, args)
                trace.emit("provider.tool.call", "OK", tool=name, result=result)
                evidence = None if name == "activate_skill_context" else evidence_from_tool(stage.id, name, result)
                if evidence is not None:
                    records = list(stage_state.context.get("evidence_records", []))
                    records.append(evidence.to_dict())
                    stage_state.context["evidence_records"] = records[-128:]

            observation = {"tool": name, "result": result}
            if evidence is not None:
                observation["evidence_id"] = evidence.id
                observation["evidence_type"] = evidence.type
            observations.append(observation)
            stage_state.completed_actions.append(f"provider:{index}:{name}")
            if name in {"write_project_file", "write_artifact", "replace_text"} and isinstance(result, dict) and result.get("path"):
                artifact = str(result["path"])
                if artifact not in stage_state.artifacts:
                    stage_state.artifacts.append(artifact)
            stage_state.context["provider_observations"] = list(
                stage_state.context.get("provider_observations", [])[-48:]
            ) + [observation]
            self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())
        return observations

    def _typed_gate_errors(self, managed: ManagedWebsiteRun, stage_state: Any) -> list[str]:
        stage = next(item for item in managed.flow.stages if item.id == managed.active_stage)
        return gate_evidence_errors(
            list(stage.gates),
            stage.id,
            list(stage_state.context.get("evidence_records", [])),
            agent=stage.agent,
        )

    def run_active_stage(
        self,
        managed: ManagedWebsiteRun,
        max_turns: int = 12,
        auto_replan: bool = True,
        dry_run: bool = False,
    ) -> ProviderRunResult:
        stage_state = self.manager.start_stage(managed)
        inherited_workspace = self._manager_workspace(managed)
        if inherited_workspace is not None:
            stage_state.context["workspace"] = inherited_workspace.to_dict()
        stage_state.limitations = [
            item for item in stage_state.limitations if item != "model/provider reasoning is not bundled"
        ]
        stage_state.limitations.extend(
            [
                "provider execution is active; browser-rendered evidence is ingested through the Playwright adapter",
                "target commands require a local pre-provisioned Docker/Podman sandbox image and never fall back to host execution",
            ]
        )
        trace = TraceRecorder(
            self.project_root / ".uiux-agent-runs" / stage_state.run_id / "trace.jsonl",
            stage_state.run_id,
        )
        observations: list[dict[str, Any]] = list(stage_state.context.get("provider_observations", []))
        stage_state.state = "RUNNING"
        self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())

        for turn in range(1, max_turns + 1):
            try:
                request = self._request(managed, stage_state, observations)
            except ProviderContextBudgetError as exc:
                trace.emit("provider.context.budget", "BLOCKED", message=str(exc), turn=turn)
                stage_state.state = "BLOCKED"
                stage_state.limitations.append(str(exc))
                self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())
                self._set_managed_terminal(managed, "BLOCKED")
                return ProviderRunResult(
                    "BLOCKED",
                    managed.active_stage,
                    turn,
                    self.provider.name,
                    self.provider.model,
                    str(exc),
                )
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
                    observations.extend(
                        self._execute_actions(managed, stage_state, response.actions, trace, dry_run)
                    )
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
            stage_state.context["provider_evidence_claims"] = provider_claim_records(
                managed.active_stage, list(response.evidence)
            )
            self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())

            if response.status == "CONTINUE":
                if not response.actions:
                    self._set_managed_terminal(managed, "FAILED")
                    raise ValueError("provider returned CONTINUE without actions")
                continue

            if response.status == "PASS":
                if dry_run:
                    return ProviderRunResult(
                        "DRY_RUN",
                        managed.active_stage,
                        turn,
                        self.provider.name,
                        self.provider.model,
                        "dry-run does not satisfy runtime evidence gates",
                    )
                gate_errors = self._typed_gate_errors(managed, stage_state)
                if gate_errors:
                    trace.emit("provider.gate", "FAIL", errors=gate_errors)
                    stage_state.state = "FAILED"
                    stage_state.limitations.extend(gate_errors)
                    self.harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())
                    if auto_replan:
                        decision = self.manager.replan(managed, "GATE_FAIL")
                        return ProviderRunResult(
                            "REPLANNED" if decision.accepted else "FAIL",
                            managed.active_stage,
                            turn,
                            self.provider.name,
                            self.provider.model,
                            "; ".join(gate_errors),
                        )
                    self._set_managed_terminal(managed, "FAILED")
                    return ProviderRunResult(
                        "FAIL",
                        managed.active_stage,
                        turn,
                        self.provider.name,
                        self.provider.model,
                        "; ".join(gate_errors),
                    )
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
            if last.state in {"AWAITING_APPROVAL", "BLOCKED", "FAILED", "FAIL", "DRY_RUN"} or managed.state == "COMPLETED":
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
