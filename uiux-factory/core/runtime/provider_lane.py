from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Mapping


PROVIDER_LANE_ENV = "UIUX_FACTORY_PROVIDER_LANE"
LEGACY_PROVIDER_LANE = "legacy"
MANAGED_COMPAT_PROVIDER_LANE = "managed-compat"
ALLOWED_PROVIDER_LANES = frozenset({LEGACY_PROVIDER_LANE, MANAGED_COMPAT_PROVIDER_LANE})


@dataclass(frozen=True)
class ProviderLaneDecision:
    lane: str
    source: str
    explicit_opt_in: bool
    default_lane: str = LEGACY_PROVIDER_LANE
    authority_effect: str = "none"
    gate_effect: str = "none"
    evidence_effect: str = "none"
    release_effect: str = "none"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def resolve_factory_provider_lane(env: Mapping[str, str] | None = None) -> ProviderLaneDecision:
    """Resolve the Factory AI provider lane without constructing any provider.

    The compatibility adapter is opt-in only. Missing/blank configuration keeps the
    proven legacy Factory provider lane. Unknown values fail closed instead of
    silently choosing a different execution path.
    """

    source_env = os.environ if env is None else env
    raw = str(source_env.get(PROVIDER_LANE_ENV, "")).strip().lower()
    if not raw:
        return ProviderLaneDecision(
            lane=LEGACY_PROVIDER_LANE,
            source="default",
            explicit_opt_in=False,
        )
    if raw not in ALLOWED_PROVIDER_LANES:
        allowed = ", ".join(sorted(ALLOWED_PROVIDER_LANES))
        raise ValueError(f"{PROVIDER_LANE_ENV} must be one of: {allowed}")
    return ProviderLaneDecision(
        lane=raw,
        source=PROVIDER_LANE_ENV,
        explicit_opt_in=raw == MANAGED_COMPAT_PROVIDER_LANE,
    )


def provider_lane_provenance(decision: ProviderLaneDecision) -> dict[str, object]:
    """Return secret-free run provenance for the selected lane."""

    return {
        "schema_version": "factory-provider-lane.v1",
        "lane": decision.lane,
        "selection_source": decision.source,
        "explicit_opt_in": decision.explicit_opt_in,
        "default_lane": decision.default_lane,
        "rollback": f"unset {PROVIDER_LANE_ENV} or set it to {LEGACY_PROVIDER_LANE}",
        "contains_credentials": False,
        "authority_effect": decision.authority_effect,
        "gate_effect": decision.gate_effect,
        "evidence_effect": decision.evidence_effect,
        "release_effect": decision.release_effect,
        "rule": (
            "Provider lane selection changes only the AI completion transport/adapter path. "
            "It cannot change Flow routing, evidence trust, gates, merge/deploy or release authority."
        ),
    }
