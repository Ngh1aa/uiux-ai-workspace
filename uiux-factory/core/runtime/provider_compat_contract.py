from __future__ import annotations


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
