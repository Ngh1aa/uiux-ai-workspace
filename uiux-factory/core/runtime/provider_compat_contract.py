from __future__ import annotations

from typing import Any, Mapping


class ProviderError(RuntimeError):
    """Shared provider-boundary error without importing any network transport."""


PROVIDER_CONTEXT_CHAR_LIMIT = 80_000
PROVIDER_MAX_CALLS_PER_RUN = 20

PROVIDER_STAGE_MAX_TOKENS: dict[str, int] = {
    "implementation": 12_000,
    "repair": 12_000,
    "visual_composition": 8_000,
    "art_direction": 8_000,
}

PROVIDER_STAGE_TIMEOUT: dict[str, int] = {
    "implementation": 180,
    "repair": 180,
    "visual_composition": 120,
}

FACTORY_PROVIDER_LANE_ENV = "UIUX_FACTORY_PROVIDER_LANE"
FACTORY_PROVIDER_LANES = frozenset({"legacy", "managed_compat"})


def resolve_factory_provider_lane(env: Mapping[str, str]) -> tuple[str, str]:
    """Resolve the controlled Factory provider lane without importing transports.

    Missing configuration intentionally preserves the legacy lane. Unknown values
    fail closed; there is no implicit/automatic migration mode.
    """

    raw = str(env.get(FACTORY_PROVIDER_LANE_ENV, "")).strip().lower()
    if not raw:
        return "legacy", "default"
    if raw not in FACTORY_PROVIDER_LANES:
        allowed = ", ".join(sorted(FACTORY_PROVIDER_LANES))
        raise ValueError(
            f"Unknown {FACTORY_PROVIDER_LANE_ENV}={raw!r}; expected one of: {allowed}."
        )
    return raw, "explicit"


def provider_descriptors(provider: Any) -> list[dict[str, str]]:
    """Return bounded non-secret provider/model identifiers for run provenance."""

    descriptors: list[dict[str, str]] = []
    raw_items = getattr(provider, "configs", None)
    if raw_items is None:
        raw_items = getattr(provider, "providers", [])
    for item in list(raw_items or [])[:8]:
        name = str(getattr(item, "name", "")).strip()[:128]
        model = str(getattr(item, "model", "")).strip()[:256]
        if name or model:
            descriptors.append({"name": name, "model": model})
    return descriptors


def build_provider_lane_provenance(
    *,
    provider: Any,
    lane: str,
    selection_source: str,
) -> dict[str, Any]:
    """Build secret-free, non-authoritative provider-lane execution metadata."""

    if lane not in FACTORY_PROVIDER_LANES:
        raise ValueError(f"Cannot persist unknown provider lane: {lane!r}")
    if selection_source not in {"default", "explicit"}:
        raise ValueError(f"Unknown provider lane selection source: {selection_source!r}")

    provider_class = f"{provider.__class__.__module__}.{provider.__class__.__name__}"
    return {
        "schema_version": "provider-lane.v1",
        "engine": "ai",
        "lane": lane,
        "selection_source": selection_source,
        "feature_flag": FACTORY_PROVIDER_LANE_ENV,
        "legacy_default_preserved": lane == "legacy" and selection_source == "default",
        "provider_class": provider_class,
        "providers": provider_descriptors(provider),
        "automatic_cross_lane_fallback": False,
        "rollback": {
            "action": f"unset {FACTORY_PROVIDER_LANE_ENV} or set it to legacy for the next run",
            "changes_current_run": False,
        },
        "authority_effect": "none",
        "gate_effect": "none",
        "evidence_effect": "none",
        "release_effect": "none",
        "rule": (
            "Provider-lane provenance records execution selection only. It is not runtime evidence, "
            "cannot satisfy gates, and cannot authorize merge/deploy/release."
        ),
    }
