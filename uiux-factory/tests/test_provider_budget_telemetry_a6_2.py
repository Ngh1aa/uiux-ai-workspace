from __future__ import annotations

from dataclasses import dataclass

import pytest

from core.runtime.flow_os.provider import ProviderStageRequest, ProviderStageResponse, ScriptedProvider
from core.runtime.flow_os.provider_budget import (
    BudgetedProvider,
    ProviderUsageTelemetry,
    StageProviderBudget,
    StageProviderBudgetResolver,
    persist_provider_usage,
)


def _request(stage_id: str = "implementation", agent: str = "implementation") -> ProviderStageRequest:
    return ProviderStageRequest(
        goal="Polish the checkout UI",
        project_root="/tmp/project",
        flow_id="focused-fix",
        flow_revision=1,
        stage_id=stage_id,
        agent=agent,
        purpose="Implement the bounded change",
        gates=[],
        task_context={"intent": "polish"},
        authority="branch_write",
        tools=[],
        skill_context=[],
        source_context=[],
        observations=[],
    )


def _continue() -> dict:
    return {
        "status": "CONTINUE",
        "actions": [{"tool": "read_text", "args": {"path": "index.html"}}],
        "summary": "Need one runtime observation.",
        "evidence": [],
        "replan_signal": None,
    }


def test_a6_2_stage_budget_merges_specificity_and_clamps_to_caller_ceiling() -> None:
    resolver = StageProviderBudgetResolver(
        {
            "provider_budget": {
                "enabled": True,
                "default": {
                    "max_calls": 10,
                    "max_estimated_total_tokens": 100000,
                    "output_reserve_tokens_per_call": 4096,
                    "timeout_seconds": 180,
                },
                "by_agent": {
                    "implementation": {"max_calls": 8, "timeout_seconds": 120},
                },
                "by_stage": {
                    "implementation": {"max_calls": 7, "timeout_seconds": 90},
                },
            }
        }
    )

    budget = resolver.resolve(
        stage_id="implementation",
        agent="implementation",
        requested_max_calls=5,
    )

    assert budget.enabled is True
    assert budget.max_calls == 5
    assert budget.timeout_seconds == 90
    assert budget.max_estimated_total_tokens == 100000
    assert budget.output_reserve_tokens_per_call == 4096
    assert "by_stage:implementation" in budget.source


def test_a6_2_cost_budget_requires_explicit_pricing() -> None:
    resolver = StageProviderBudgetResolver(
        {
            "provider_budget": {
                "enabled": True,
                "default": {
                    "max_calls": 2,
                    "max_cost_usd": 1.0,
                },
            }
        }
    )

    with pytest.raises(ValueError, match="requires explicit input/output pricing"):
        resolver.resolve(stage_id="qa", agent="qa", requested_max_calls=2)


def test_a6_2_provider_cannot_raise_call_budget_through_its_response() -> None:
    base = ScriptedProvider([_continue(), _continue()])
    budget = StageProviderBudget(
        stage_id="implementation",
        agent="implementation",
        enabled=True,
        source="test",
        max_calls=1,
    )
    wrapped = BudgetedProvider(base, budget)

    first = wrapped.run_stage(_request())
    second = wrapped.run_stage(_request())

    assert first.status == "CONTINUE"
    assert second.status == "BLOCKED"
    assert wrapped.usage.calls == 1
    assert len(base.requests) == 1
    assert wrapped.budget.max_calls == 1


def test_a6_2_token_reservation_blocks_before_provider_call() -> None:
    base = ScriptedProvider([_continue()])
    budget = StageProviderBudget(
        stage_id="implementation",
        agent="implementation",
        enabled=True,
        source="test",
        max_calls=2,
        max_estimated_total_tokens=100,
        output_reserve_tokens_per_call=100,
    )
    wrapped = BudgetedProvider(base, budget)

    response = wrapped.run_stage(_request())

    assert response.status == "BLOCKED"
    assert wrapped.usage.calls == 0
    assert base.requests == []
    assert wrapped.usage.exhausted is True
    assert "token budget" in str(wrapped.usage.exhaustion_reason)


def test_a6_2_prior_usage_prevents_budget_reset_after_replan() -> None:
    base = ScriptedProvider([_continue()])
    budget = StageProviderBudget(
        stage_id="qa",
        agent="qa",
        enabled=True,
        source="test",
        max_calls=2,
    )
    prior = ProviderUsageTelemetry(
        stage_id="qa",
        agent="qa",
        provider="scripted",
        model="scripted-test",
        calls=2,
    ).to_dict()
    wrapped = BudgetedProvider(base, budget, prior_usage=prior)

    response = wrapped.run_stage(_request("qa", "qa"))

    assert response.status == "BLOCKED"
    assert wrapped.usage.calls == 2
    assert base.requests == []


class _TimedProvider:
    name = "timed"
    model = "test-model"

    def __init__(self) -> None:
        self.timeout = 300
        self.requests = 0

    def run_stage(self, request: ProviderStageRequest) -> ProviderStageResponse:
        self.requests += 1
        return ProviderStageResponse(
            status="BLOCKED",
            actions=[],
            summary="fixture",
            evidence=[],
            replan_signal="BLOCKED",
        )


def test_a6_2_timeout_budget_can_only_reduce_provider_timeout() -> None:
    base = _TimedProvider()
    budget = StageProviderBudget(
        stage_id="research",
        agent="research",
        enabled=True,
        source="test",
        max_calls=1,
        timeout_seconds=30,
    )
    wrapped = BudgetedProvider(base, budget)

    wrapped.run_stage(_request("research", "research"))
    assert base.timeout <= 30

    base2 = _TimedProvider()
    base2.timeout = 10
    budget2 = StageProviderBudget(
        stage_id="research",
        agent="research",
        enabled=True,
        source="test",
        max_calls=1,
        timeout_seconds=30,
    )
    BudgetedProvider(base2, budget2).run_stage(_request("research", "research"))
    assert base2.timeout == 10


@dataclass
class _FakeState:
    run_id: str
    context: dict

    def to_dict(self) -> dict:
        return {"run_id": self.run_id, "context": self.context}


class _FakeCheckpoints:
    def __init__(self) -> None:
        self.saved: list[tuple[str, dict]] = []

    def save(self, run_id: str, payload: dict) -> None:
        self.saved.append((run_id, payload))


class _FakeHarness:
    def __init__(self) -> None:
        self.states = {
            "manager": _FakeState("manager", {}),
            "stage-run": _FakeState("stage-run", {}),
        }
        self.checkpoints = _FakeCheckpoints()

    def resume(self, run_id: str) -> _FakeState:
        return self.states[run_id]


class _FakeManaged:
    manager_run_id = "manager"
    stage_runs = {"implementation": ["stage-run"]}


def test_a6_2_persists_budget_and_usage_without_prompt_or_output_content() -> None:
    harness = _FakeHarness()
    budget = StageProviderBudget(
        stage_id="implementation",
        agent="implementation",
        enabled=True,
        source="by_stage:implementation",
        max_calls=3,
        max_estimated_total_tokens=50000,
        output_reserve_tokens_per_call=4096,
        timeout_seconds=90,
    )
    usage = ProviderUsageTelemetry(
        stage_id="implementation",
        agent="implementation",
        provider="openai",
        model="configured-model",
        calls=2,
        estimated_input_tokens=1000,
        estimated_output_tokens=250,
        estimated_total_tokens=1250,
        estimated_cost_usd=0.0125,
        elapsed_ms=3210,
    )

    persist_provider_usage(harness, _FakeManaged(), budget, usage)

    manager_context = harness.states["manager"].context
    stage_context = harness.states["stage-run"].context
    assert manager_context["provider_budget_by_stage"]["implementation"]["max_calls"] == 3
    assert manager_context["provider_usage_by_stage"]["implementation"]["calls"] == 2
    assert manager_context["provider_usage_totals"]["estimated_total_tokens"] == 1250
    assert stage_context["provider_budget"]["timeout_seconds"] == 90
    assert stage_context["provider_usage"]["provider"] == "openai"

    serialized = repr(manager_context) + repr(stage_context)
    assert "prompt" not in serialized.lower()
    assert "api_key" not in serialized.lower()
    assert "Need one runtime observation" not in serialized
