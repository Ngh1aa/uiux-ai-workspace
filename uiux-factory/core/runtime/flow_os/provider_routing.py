from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


ROUTABLE_PROVIDERS = frozenset({"openai", "anthropic", "command"})


@dataclass(frozen=True)
class StageProviderSelection:
    stage_id: str
    agent: str
    provider: str
    model: str | None
    max_turns: int
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class StageProviderRouter:
    """Resolve an explicit provider/model policy for one canonical Flow stage.

    Routing is deliberately policy-only. Task text, model output and recalled memory
    cannot select a provider. The caller's CLI/provider choice remains the fallback,
    and any provider switch must be explicitly enabled by runtime policy.
    """

    def __init__(self, policy_doc: dict[str, Any]) -> None:
        raw = policy_doc.get("provider_routing", {})
        if raw is None:
            raw = {}
        if not isinstance(raw, dict):
            raise ValueError("runtime provider_routing policy must be an object")
        self.policy = dict(raw)

    @staticmethod
    def _positive_turns(value: Any, *, field: str) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"{field} must be a positive integer") from exc
        if parsed < 1 or parsed > 64:
            raise ValueError(f"{field} must be between 1 and 64")
        return parsed

    @staticmethod
    def _route_map(value: Any, *, field: str) -> dict[str, Any]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError(f"{field} must be an object")
        return dict(value)

    def _entry_for(self, stage_id: str, agent: str) -> tuple[dict[str, Any], str]:
        by_stage = self._route_map(self.policy.get("by_stage"), field="provider_routing.by_stage")
        if stage_id in by_stage:
            entry = by_stage[stage_id]
            if not isinstance(entry, dict):
                raise ValueError(f"provider_routing.by_stage.{stage_id} must be an object")
            return dict(entry), f"by_stage:{stage_id}"

        by_agent = self._route_map(self.policy.get("by_agent"), field="provider_routing.by_agent")
        if agent in by_agent:
            entry = by_agent[agent]
            if not isinstance(entry, dict):
                raise ValueError(f"provider_routing.by_agent.{agent} must be an object")
            return dict(entry), f"by_agent:{agent}"

        default = self.policy.get("default", {})
        if default is None:
            default = {}
        if not isinstance(default, dict):
            raise ValueError("provider_routing.default must be an object")
        return dict(default), "policy_default"

    def resolve(
        self,
        *,
        stage_id: str,
        agent: str,
        default_provider: str,
        default_model: str | None,
        requested_max_turns: int,
    ) -> StageProviderSelection:
        caller_turns = self._positive_turns(requested_max_turns, field="requested_max_turns")
        if not bool(self.policy.get("enabled", False)):
            return StageProviderSelection(
                stage_id=stage_id,
                agent=agent,
                provider=default_provider,
                model=default_model,
                max_turns=caller_turns,
                source="caller_default",
            )

        entry, source = self._entry_for(stage_id, agent)
        provider = str(entry.get("provider") or default_provider).strip().lower()
        if provider == "auto":
            raise ValueError(
                "provider_routing entries may not use provider=auto; choose an explicit provider "
                "so stage routing cannot silently fall back to an unintended paid model"
            )
        if provider not in ROUTABLE_PROVIDERS:
            raise ValueError(f"unsupported routed provider: {provider or '(missing)'}")

        normalized_default = str(default_provider).strip().lower()
        allow_switch = bool(self.policy.get("allow_provider_switch", False))
        if provider != normalized_default and not allow_switch:
            raise ValueError(
                f"provider routing attempted {normalized_default or '(missing)'} -> {provider} "
                "while provider_routing.allow_provider_switch is false"
            )

        raw_model = entry.get("model", default_model)
        model = str(raw_model).strip() if raw_model is not None else None
        if model == "":
            model = None

        configured_turns = entry.get("max_turns", caller_turns)
        route_turns = self._positive_turns(
            configured_turns,
            field=f"provider_routing.{source}.max_turns",
        )

        return StageProviderSelection(
            stage_id=stage_id,
            agent=agent,
            provider=provider,
            model=model,
            max_turns=min(caller_turns, route_turns),
            source=source,
        )
