from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Callable

from core.runtime.flow_os.provider import ModelProvider, ProviderStageRequest, ProviderStageResponse


@dataclass(frozen=True)
class StageProviderBudget:
    stage_id: str
    agent: str
    enabled: bool
    source: str
    max_calls: int
    max_estimated_total_tokens: int | None = None
    output_reserve_tokens_per_call: int = 0
    timeout_seconds: int | None = None
    max_cost_usd: float | None = None
    input_usd_per_million: float | None = None
    output_usd_per_million: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProviderUsageTelemetry:
    stage_id: str
    agent: str
    provider: str
    model: str
    calls: int = 0
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    estimated_total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    elapsed_ms: int = 0
    exhausted: bool = False
    exhaustion_reason: str | None = None
    measurement: str = "runtime_utf8_byte_estimate"

    @classmethod
    def from_dict(
        cls,
        payload: dict[str, Any] | None,
        *,
        stage_id: str,
        agent: str,
        provider: str,
        model: str,
    ) -> "ProviderUsageTelemetry":
        raw = payload if isinstance(payload, dict) else {}
        return cls(
            stage_id=stage_id,
            agent=agent,
            provider=provider,
            model=model,
            calls=max(0, int(raw.get("calls", 0) or 0)),
            estimated_input_tokens=max(0, int(raw.get("estimated_input_tokens", 0) or 0)),
            estimated_output_tokens=max(0, int(raw.get("estimated_output_tokens", 0) or 0)),
            estimated_total_tokens=max(0, int(raw.get("estimated_total_tokens", 0) or 0)),
            estimated_cost_usd=max(0.0, float(raw.get("estimated_cost_usd", 0.0) or 0.0)),
            elapsed_ms=max(0, int(raw.get("elapsed_ms", 0) or 0)),
            exhausted=bool(raw.get("exhausted", False)),
            exhaustion_reason=str(raw.get("exhaustion_reason")) if raw.get("exhaustion_reason") else None,
            measurement="runtime_utf8_byte_estimate",
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["estimated_cost_usd"] = round(self.estimated_cost_usd, 8)
        return payload


class StageProviderBudgetResolver:
    """Resolve operator-owned provider budgets for one stage.

    The budget source is runtime policy only. Task text, provider/model output, recalled
    memory and tool observations are intentionally not inputs, so a provider cannot
    grant itself more calls/tokens/cost/time.
    """

    def __init__(self, policy_doc: dict[str, Any]) -> None:
        raw = policy_doc.get("provider_budget", {})
        if raw is None:
            raw = {}
        if not isinstance(raw, dict):
            raise ValueError("runtime provider_budget policy must be an object")
        self.policy = dict(raw)

    @staticmethod
    def _positive_int(value: Any, *, field: str, maximum: int) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"{field} must be a positive integer") from exc
        if parsed < 1 or parsed > maximum:
            raise ValueError(f"{field} must be between 1 and {maximum}")
        return parsed

    @staticmethod
    def _optional_positive_int(value: Any, *, field: str, maximum: int) -> int | None:
        if value is None:
            return None
        return StageProviderBudgetResolver._positive_int(value, field=field, maximum=maximum)

    @staticmethod
    def _optional_non_negative_float(value: Any, *, field: str, maximum: float) -> float | None:
        if value is None:
            return None
        try:
            parsed = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"{field} must be a non-negative number") from exc
        if parsed < 0 or parsed > maximum:
            raise ValueError(f"{field} must be between 0 and {maximum}")
        return parsed

    @staticmethod
    def _mapping(value: Any, *, field: str) -> dict[str, Any]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError(f"{field} must be an object")
        return dict(value)

    def _merged_entry(self, stage_id: str, agent: str) -> tuple[dict[str, Any], str]:
        merged = self._mapping(self.policy.get("default"), field="provider_budget.default")
        sources = ["default"]

        by_agent = self._mapping(self.policy.get("by_agent"), field="provider_budget.by_agent")
        if agent in by_agent:
            entry = by_agent[agent]
            if not isinstance(entry, dict):
                raise ValueError(f"provider_budget.by_agent.{agent} must be an object")
            merged.update(entry)
            sources.append(f"by_agent:{agent}")

        by_stage = self._mapping(self.policy.get("by_stage"), field="provider_budget.by_stage")
        if stage_id in by_stage:
            entry = by_stage[stage_id]
            if not isinstance(entry, dict):
                raise ValueError(f"provider_budget.by_stage.{stage_id} must be an object")
            merged.update(entry)
            sources.append(f"by_stage:{stage_id}")

        return merged, "+".join(sources)

    def resolve(
        self,
        *,
        stage_id: str,
        agent: str,
        requested_max_calls: int,
    ) -> StageProviderBudget:
        caller_calls = self._positive_int(requested_max_calls, field="requested_max_calls", maximum=64)
        if not bool(self.policy.get("enabled", False)):
            return StageProviderBudget(
                stage_id=stage_id,
                agent=agent,
                enabled=False,
                source="disabled",
                max_calls=caller_calls,
            )

        entry, source = self._merged_entry(stage_id, agent)
        configured_calls = self._positive_int(
            entry.get("max_calls", caller_calls),
            field=f"provider_budget.{source}.max_calls",
            maximum=64,
        )
        max_total_tokens = self._optional_positive_int(
            entry.get("max_estimated_total_tokens"),
            field=f"provider_budget.{source}.max_estimated_total_tokens",
            maximum=20_000_000,
        )
        output_reserve = self._positive_int(
            entry.get("output_reserve_tokens_per_call", 8192),
            field=f"provider_budget.{source}.output_reserve_tokens_per_call",
            maximum=262_144,
        )
        timeout_seconds = self._optional_positive_int(
            entry.get("timeout_seconds"),
            field=f"provider_budget.{source}.timeout_seconds",
            maximum=3600,
        )
        max_cost_usd = self._optional_non_negative_float(
            entry.get("max_cost_usd"),
            field=f"provider_budget.{source}.max_cost_usd",
            maximum=10_000.0,
        )

        pricing = self._mapping(entry.get("pricing"), field=f"provider_budget.{source}.pricing")
        input_rate = self._optional_non_negative_float(
            pricing.get("input_usd_per_million"),
            field=f"provider_budget.{source}.pricing.input_usd_per_million",
            maximum=100_000.0,
        )
        output_rate = self._optional_non_negative_float(
            pricing.get("output_usd_per_million"),
            field=f"provider_budget.{source}.pricing.output_usd_per_million",
            maximum=100_000.0,
        )
        if max_cost_usd is not None and (input_rate is None or output_rate is None):
            raise ValueError(
                "provider_budget.max_cost_usd requires explicit input/output pricing; "
                "the runtime will not invent model pricing"
            )

        return StageProviderBudget(
            stage_id=stage_id,
            agent=agent,
            enabled=True,
            source=source,
            max_calls=min(caller_calls, configured_calls),
            max_estimated_total_tokens=max_total_tokens,
            output_reserve_tokens_per_call=output_reserve,
            timeout_seconds=timeout_seconds,
            max_cost_usd=max_cost_usd,
            input_usd_per_million=input_rate,
            output_usd_per_million=output_rate,
        )


def _json_byte_estimate(value: Any, *, overhead: int = 0) -> int:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    # Byte length is deliberately used as a provider-neutral conservative token proxy.
    # It is telemetry/reservation data, not a claim of provider-reported billing tokens.
    return len(payload) + max(0, overhead)


def _estimate_cost(budget: StageProviderBudget, input_tokens: int, output_tokens: int) -> float:
    if budget.input_usd_per_million is None or budget.output_usd_per_million is None:
        return 0.0
    return (
        input_tokens * budget.input_usd_per_million
        + output_tokens * budget.output_usd_per_million
    ) / 1_000_000.0


class BudgetedProvider:
    """Provider wrapper enforcing immutable stage budgets and recording bounded telemetry."""

    def __init__(
        self,
        provider: ModelProvider,
        budget: StageProviderBudget,
        *,
        prior_usage: dict[str, Any] | None = None,
        on_update: Callable[[StageProviderBudget, ProviderUsageTelemetry], None] | None = None,
    ) -> None:
        self.provider = provider
        self.budget = budget
        self.name = provider.name
        self.model = provider.model
        self.usage = ProviderUsageTelemetry.from_dict(
            prior_usage,
            stage_id=budget.stage_id,
            agent=budget.agent,
            provider=self.name,
            model=self.model,
        )
        self.on_update = on_update
        # A previous exhaustion remains authoritative for the same stage budget.
        if self.usage.exhausted:
            self._emit()

    def _emit(self) -> None:
        if self.on_update is not None:
            self.on_update(self.budget, self.usage)

    def _block(self, reason: str) -> ProviderStageResponse:
        self.usage.exhausted = True
        self.usage.exhaustion_reason = reason[:500]
        self._emit()
        return ProviderStageResponse(
            status="BLOCKED",
            actions=[],
            summary=f"Provider stage budget exhausted: {reason}",
            evidence=[],
            replan_signal="BLOCKED",
        )

    def _remaining_seconds(self) -> float | None:
        if self.budget.timeout_seconds is None:
            return None
        return max(0.0, self.budget.timeout_seconds - (self.usage.elapsed_ms / 1000.0))

    def can_start(self) -> tuple[bool, str]:
        if self.usage.exhausted:
            return False, self.usage.exhaustion_reason or "stage budget already exhausted"
        if self.usage.calls >= self.budget.max_calls:
            return False, f"call budget exhausted ({self.usage.calls}/{self.budget.max_calls})"
        remaining = self._remaining_seconds()
        if remaining is not None and remaining <= 0:
            return False, f"stage timeout budget exhausted ({self.budget.timeout_seconds}s)"
        if (
            self.budget.max_estimated_total_tokens is not None
            and self.usage.estimated_total_tokens >= self.budget.max_estimated_total_tokens
        ):
            return False, "estimated token budget exhausted"
        if (
            self.budget.max_cost_usd is not None
            and self.usage.estimated_cost_usd >= self.budget.max_cost_usd
        ):
            return False, "estimated cost budget exhausted"
        return True, "ok"

    def _apply_timeout_ceiling(self) -> None:
        remaining = self._remaining_seconds()
        if remaining is None:
            return
        bounded = max(1, int(remaining))
        current = getattr(self.provider, "timeout", None)
        if current is None:
            try:
                setattr(self.provider, "timeout", bounded)
            except Exception:
                return
            return
        try:
            setattr(self.provider, "timeout", min(int(current), bounded))
        except Exception:
            return

    def run_stage(self, request: ProviderStageRequest) -> ProviderStageResponse:
        allowed, reason = self.can_start()
        if not allowed:
            return self._block(reason)

        input_estimate = _json_byte_estimate(request.to_dict(), overhead=4096)
        reserved_total = (
            self.usage.estimated_total_tokens
            + input_estimate
            + self.budget.output_reserve_tokens_per_call
        )
        if (
            self.budget.max_estimated_total_tokens is not None
            and reserved_total > self.budget.max_estimated_total_tokens
        ):
            return self._block(
                "next call reservation would exceed estimated token budget "
                f"({reserved_total}>{self.budget.max_estimated_total_tokens})"
            )

        reserved_cost = self.usage.estimated_cost_usd + _estimate_cost(
            self.budget,
            input_estimate,
            self.budget.output_reserve_tokens_per_call,
        )
        if self.budget.max_cost_usd is not None and reserved_cost > self.budget.max_cost_usd:
            return self._block(
                "next call reservation would exceed estimated cost budget "
                f"({reserved_cost:.6f}>{self.budget.max_cost_usd:.6f} USD)"
            )

        self._apply_timeout_ceiling()
        self.usage.calls += 1
        self.usage.estimated_input_tokens += input_estimate
        started = time.monotonic()
        try:
            response = self.provider.run_stage(request)
        except Exception:
            self.usage.elapsed_ms += max(0, int((time.monotonic() - started) * 1000))
            self.usage.estimated_total_tokens = (
                self.usage.estimated_input_tokens + self.usage.estimated_output_tokens
            )
            self.usage.estimated_cost_usd += _estimate_cost(self.budget, input_estimate, 0)
            self._emit()
            raise

        elapsed_ms = max(0, int((time.monotonic() - started) * 1000))
        output_estimate = _json_byte_estimate(response.to_dict())
        self.usage.elapsed_ms += elapsed_ms
        self.usage.estimated_output_tokens += output_estimate
        self.usage.estimated_total_tokens = (
            self.usage.estimated_input_tokens + self.usage.estimated_output_tokens
        )
        self.usage.estimated_cost_usd += _estimate_cost(
            self.budget,
            input_estimate,
            output_estimate,
        )

        over_reason: str | None = None
        if (
            self.budget.max_estimated_total_tokens is not None
            and self.usage.estimated_total_tokens > self.budget.max_estimated_total_tokens
        ):
            over_reason = "provider response exceeded estimated token budget"
        elif (
            self.budget.max_cost_usd is not None
            and self.usage.estimated_cost_usd > self.budget.max_cost_usd
        ):
            over_reason = "provider response exceeded estimated cost budget"
        elif (
            self.budget.timeout_seconds is not None
            and self.usage.elapsed_ms > self.budget.timeout_seconds * 1000
        ):
            over_reason = "provider call exceeded stage timeout budget"

        if over_reason is not None:
            return self._block(over_reason)
        self._emit()
        return response


def load_prior_provider_usage(harness: Any, managed: Any, stage_id: str) -> dict[str, Any] | None:
    manager_state = harness.resume(managed.manager_run_id)
    by_stage = manager_state.context.get("provider_usage_by_stage", {})
    if not isinstance(by_stage, dict):
        return None
    payload = by_stage.get(stage_id)
    return dict(payload) if isinstance(payload, dict) else None


def persist_provider_usage(
    harness: Any,
    managed: Any,
    budget: StageProviderBudget,
    usage: ProviderUsageTelemetry,
) -> None:
    """Persist bounded budget/usage snapshots without prompts, outputs or secrets."""

    manager_state = harness.resume(managed.manager_run_id)
    budget_by_stage = dict(manager_state.context.get("provider_budget_by_stage", {}))
    usage_by_stage = dict(manager_state.context.get("provider_usage_by_stage", {}))
    budget_by_stage[budget.stage_id] = budget.to_dict()
    usage_by_stage[budget.stage_id] = usage.to_dict()
    manager_state.context["provider_budget_by_stage"] = budget_by_stage
    manager_state.context["provider_usage_by_stage"] = usage_by_stage

    totals = {
        "calls": 0,
        "estimated_input_tokens": 0,
        "estimated_output_tokens": 0,
        "estimated_total_tokens": 0,
        "estimated_cost_usd": 0.0,
        "elapsed_ms": 0,
    }
    for item in usage_by_stage.values():
        if not isinstance(item, dict):
            continue
        totals["calls"] += max(0, int(item.get("calls", 0) or 0))
        totals["estimated_input_tokens"] += max(0, int(item.get("estimated_input_tokens", 0) or 0))
        totals["estimated_output_tokens"] += max(0, int(item.get("estimated_output_tokens", 0) or 0))
        totals["estimated_total_tokens"] += max(0, int(item.get("estimated_total_tokens", 0) or 0))
        totals["estimated_cost_usd"] += max(0.0, float(item.get("estimated_cost_usd", 0.0) or 0.0))
        totals["elapsed_ms"] += max(0, int(item.get("elapsed_ms", 0) or 0))
    totals["estimated_cost_usd"] = round(float(totals["estimated_cost_usd"]), 8)
    manager_state.context["provider_usage_totals"] = totals

    history = list(manager_state.context.get("provider_usage_history", []))
    history.append({"budget": budget.to_dict(), "usage": usage.to_dict()})
    manager_state.context["provider_usage_history"] = history[-128:]
    harness.checkpoints.save(manager_state.run_id, manager_state.to_dict())

    stage_runs = managed.stage_runs.get(budget.stage_id, [])
    if stage_runs:
        stage_state = harness.resume(stage_runs[-1])
        stage_state.context["provider_budget"] = budget.to_dict()
        stage_state.context["provider_usage"] = usage.to_dict()
        harness.checkpoints.save(stage_state.run_id, stage_state.to_dict())
