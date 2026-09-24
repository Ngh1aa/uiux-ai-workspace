from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from runtime.agent import ProviderNeutralAgentHarness, RunState
from runtime.flow import DevelopmentManager, ReplanDecision, ResolvedFlow, ResolvedStage
from runtime.task_context import GoalInterpreter


@dataclass
class ManagedWebsiteRun:
    manager_run_id: str
    flow: ResolvedFlow
    task_context: dict[str, Any]
    authority: str
    active_stage: str
    state: str = "READY"
    replan_count: int = 0
    completed_stages: list[str] = field(default_factory=list)
    stage_runs: dict[str, list[str]] = field(default_factory=dict)
    replan_history: list[dict[str, Any]] = field(default_factory=list)
    approved_gates: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ManagedWebsiteRun":
        flow_payload = dict(payload["flow"])
        stages = [ResolvedStage(**dict(item)) for item in flow_payload.pop("stages", [])]
        flow = ResolvedFlow(stages=stages, **flow_payload)
        return cls(
            manager_run_id=str(payload["manager_run_id"]),
            flow=flow,
            task_context=dict(payload.get("task_context", {})),
            authority=str(payload["authority"]),
            active_stage=str(payload["active_stage"]),
            state=str(payload.get("state", "READY")),
            replan_count=int(payload.get("replan_count", 0)),
            completed_stages=list(payload.get("completed_stages", [])),
            stage_runs={key: list(value) for key, value in dict(payload.get("stage_runs", {})).items()},
            replan_history=list(payload.get("replan_history", [])),
            approved_gates=list(payload.get("approved_gates", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "manager_run_id": self.manager_run_id,
            "flow": self.flow.to_dict(),
            "task_context": self.task_context,
            "authority": self.authority,
            "active_stage": self.active_stage,
            "state": self.state,
            "replan_count": self.replan_count,
            "completed_stages": list(self.completed_stages),
            "stage_runs": {key: list(value) for key, value in self.stage_runs.items()},
            "replan_history": list(self.replan_history),
            "approved_gates": list(self.approved_gates),
        }


class DevelopmentManagerAgent:
    """Owns end-to-end website routing while specialist agents own execution stages.

    The manager does not absorb UI/UX knowledge. It interprets the user's goal,
    resolves a declarative flow, activates specialist runs, records stage progress,
    enforces configured human approval gates, and applies bounded replans when
    explicit evidence signals a failure, new risk or invalid assumption.
    """

    def __init__(self, harness: ProviderNeutralAgentHarness) -> None:
        self.harness = harness
        self.manager = DevelopmentManager(harness.repo_root, harness.policy_doc)
        self.goal_interpreter = GoalInterpreter()

    def interpret_goal(
        self,
        goal: str,
        overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        context = self.goal_interpreter.interpret(goal).to_context()
        for key, value in dict(overrides or {}).items():
            if value is None:
                continue
            if key == "features":
                if value:
                    context[key] = list(value)
                continue
            context[key] = value
        context.setdefault("approval_mode", "auto")
        return context

    def resolve_flow(
        self,
        task_context: dict[str, Any],
        additional_skills: list[str] | None = None,
        exclude_skills: list[str] | None = None,
    ) -> ResolvedFlow:
        return self.manager.plan(
            task_context,
            additional_skills=additional_skills,
            exclude_skills=exclude_skills,
        )

    def _stage(self, managed: ManagedWebsiteRun, stage_id: str) -> ResolvedStage:
        stage = next((item for item in managed.flow.stages if item.id == stage_id), None)
        if stage is None:
            raise ValueError(f"unknown stage for flow {managed.flow.id}: {stage_id}")
        return stage

    def _checkpoint_managed(self, managed: ManagedWebsiteRun) -> None:
        state = self.harness.resume(managed.manager_run_id)
        state.state = managed.state
        state.context["flow_plan"] = managed.flow.to_dict()
        state.context["task_context"] = dict(managed.task_context)
        state.context["managed_run"] = managed.to_dict()
        self.harness.checkpoints.save(state.run_id, state.to_dict())

    def resume(self, manager_run_id: str) -> ManagedWebsiteRun:
        state = self.harness.resume(manager_run_id)
        payload = state.context.get("managed_run")
        if not isinstance(payload, dict):
            raise ValueError(f"checkpoint {manager_run_id} does not contain a managed website run")
        return ManagedWebsiteRun.from_dict(payload)

    def start_from_goal(
        self,
        goal: str,
        authority: str = "branch_write",
        overrides: dict[str, Any] | None = None,
        additional_skills: list[str] | None = None,
        exclude_skills: list[str] | None = None,
    ) -> ManagedWebsiteRun:
        context = self.interpret_goal(goal, overrides)
        return self.start(
            goal,
            context,
            authority=authority,
            additional_skills=additional_skills,
            exclude_skills=exclude_skills,
        )

    def start(
        self,
        task: str,
        task_context: dict[str, Any],
        authority: str = "branch_write",
        additional_skills: list[str] | None = None,
        exclude_skills: list[str] | None = None,
    ) -> ManagedWebsiteRun:
        flow = self.resolve_flow(task_context, additional_skills, exclude_skills)
        manager_state = self.harness.create_run(
            task,
            "development",
            authority,
            selected_skills=[],
            explicit_sources=[],
        )
        managed = ManagedWebsiteRun(
            manager_run_id=manager_state.run_id,
            flow=flow,
            task_context=dict(task_context),
            authority=authority,
            active_stage=flow.stages[0].id,
        )
        self._checkpoint_managed(managed)
        return managed

    def start_stage(
        self,
        managed: ManagedWebsiteRun,
        stage_id: str | None = None,
        explicit_sources: list[str] | None = None,
    ) -> RunState:
        target = stage_id or managed.active_stage
        if target != managed.active_stage:
            raise ValueError(
                f"cannot start stage {target}; active stage is {managed.active_stage}. "
                "Complete the active stage or apply an explicit replan first."
            )
        stage = self._stage(managed, target)

        role = self.harness.policy_doc["roles"][stage.agent]
        order = tuple(self.harness.permissions.order)
        authority = managed.authority
        if order.index(authority) > order.index(role["max_authority"]):
            authority = role["max_authority"]

        state = self.harness.create_run(
            task=f"{managed.flow.id}:{stage.id}",
            agent=stage.agent,
            authority=authority,
            selected_skills=stage.skills,
            explicit_sources=explicit_sources or [],
        )
        state.context["manager_run_id"] = managed.manager_run_id
        state.context["flow_id"] = managed.flow.id
        state.context["flow_revision"] = managed.flow.revision
        state.context["stage_id"] = stage.id
        state.context["stage_gates"] = list(stage.gates)
        self.harness.checkpoints.save(state.run_id, state.to_dict())

        managed.active_stage = stage.id
        managed.state = "RUNNING"
        managed.stage_runs.setdefault(stage.id, []).append(state.run_id)
        self._checkpoint_managed(managed)
        return state

    def required_human_approvals(self, managed: ManagedWebsiteRun, stage_id: str | None = None) -> list[str]:
        if str(managed.task_context.get("approval_mode", "auto")) != "manual":
            return []
        stage = self._stage(managed, stage_id or managed.active_stage)
        required: list[str] = []
        for gate in stage.gates:
            if gate.get("approval") == "human" and str(gate.get("id", "")) not in managed.approved_gates:
                required.append(str(gate["id"]))
        return required

    def approve_gate(self, managed: ManagedWebsiteRun, gate_id: str) -> None:
        stage = self._stage(managed, managed.active_stage)
        gate = next((item for item in stage.gates if str(item.get("id", "")) == gate_id), None)
        if gate is None:
            raise ValueError(f"gate {gate_id} is not part of active stage {stage.id}")
        if gate.get("approval") != "human":
            raise ValueError(f"gate {gate_id} does not require human approval")
        if gate_id not in managed.approved_gates:
            managed.approved_gates.append(gate_id)
        self._checkpoint_managed(managed)

    def complete_stage(self, managed: ManagedWebsiteRun, stage_id: str | None = None) -> str | None:
        target = stage_id or managed.active_stage
        if target != managed.active_stage:
            raise ValueError(
                f"cannot complete stage {target}; active stage is {managed.active_stage}"
            )
        self._stage(managed, target)
        pending = self.required_human_approvals(managed, target)
        if pending:
            managed.state = "AWAITING_APPROVAL"
            self._checkpoint_managed(managed)
            raise ValueError(
                f"cannot complete stage {target}; human approval required for gate(s): {', '.join(pending)}"
            )

        runs = managed.stage_runs.get(target, [])
        if not runs:
            raise ValueError(f"cannot complete stage {target}; no specialist run has been started")
        latest = self.harness.resume(runs[-1])
        if latest.state != "COMPLETED":
            raise ValueError(
                f"cannot complete stage {target}; latest specialist run is {latest.state}"
            )
        if target not in managed.completed_stages:
            managed.completed_stages.append(target)

        stage_ids = [stage.id for stage in managed.flow.stages]
        index = stage_ids.index(target)
        if index == len(stage_ids) - 1:
            managed.state = "COMPLETED"
            managed.active_stage = target
            self._checkpoint_managed(managed)
            return None

        managed.active_stage = stage_ids[index + 1]
        managed.state = "READY"
        self._checkpoint_managed(managed)
        return managed.active_stage

    def replan(
        self,
        managed: ManagedWebsiteRun,
        signal: str,
        current_stage: str | None = None,
        replan_count: int | None = None,
        context_updates: dict[str, Any] | None = None,
        apply: bool = True,
    ) -> ReplanDecision:
        stage_id = current_stage or managed.active_stage
        self._stage(managed, stage_id)
        if apply and stage_id != managed.active_stage:
            raise ValueError(
                f"cannot apply replan from stage {stage_id}; active stage is {managed.active_stage}"
            )

        context = dict(managed.task_context)
        context.update(context_updates or {})
        context["current_stage"] = stage_id
        effective_count = managed.replan_count if replan_count is None else replan_count
        decision = self.manager.replan(
            managed.flow,
            signal=signal,
            context=context,
            replan_count=effective_count,
        )

        if decision.accepted and apply:
            managed.flow = self.manager.apply_replan(managed.flow, decision)
            managed.replan_count += 1
            managed.replan_history.append(decision.to_dict())
            managed.state = "REPLANNED"

            target = decision.target_stage or stage_id
            managed.active_stage = target
            stage_ids = [stage.id for stage in managed.flow.stages]
            target_index = stage_ids.index(target)
            managed.completed_stages = [
                item
                for item in managed.completed_stages
                if stage_ids.index(item) < target_index
            ]
            self._checkpoint_managed(managed)

        return decision
