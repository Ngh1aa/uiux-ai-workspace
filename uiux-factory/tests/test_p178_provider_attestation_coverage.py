from __future__ import annotations

from core.runtime.flow_os.provider_attestation import (
    KNOWN_EXTERNAL_INTEGRATION_PROVIDERS,
    PROVIDER_ATTESTATION_CAPABILITIES,
    SUPPORTED_PROVIDER_ATTESTORS,
    assess_provider_attestation_coverage,
)
from core.runtime.flow_os.repository_policy_registry import registered_repository_policies


def test_p178_capability_registry_covers_every_known_external_provider() -> None:
    assert set(PROVIDER_ATTESTATION_CAPABILITIES) == set(KNOWN_EXTERNAL_INTEGRATION_PROVIDERS)


def test_p178_available_attestors_match_capability_registry() -> None:
    available = {
        provider
        for provider, capability in PROVIDER_ATTESTATION_CAPABILITIES.items()
        if capability.attestor_available
    }
    assert available == set(SUPPORTED_PROVIDER_ATTESTORS)


def test_p178_railway_gap_is_closed_by_verified_read_adapter() -> None:
    coverage = assess_provider_attestation_coverage(("railway",))

    assert coverage.classification_complete is True
    assert coverage.provider_native_idle_coverage_complete is True
    assert coverage.adapter_pending_providers == ()
    capability = coverage.providers[0]
    assert capability.mode == "provider-api"
    assert capability.repository_linkage_truth is True
    assert capability.attestor_available is True
    assert capability.idle_truth_provider_native is True


def test_p178_firebase_hosting_does_not_fake_repository_linkage_attestation() -> None:
    coverage = assess_provider_attestation_coverage(("firebase-hosting",))

    assert coverage.classification_complete is True
    assert coverage.adapter_pending_providers == ()
    capability = coverage.providers[0]
    assert capability.mode == "repository-static-or-github-native"
    assert capability.repository_linkage_truth is False
    assert capability.attestor_available is False
    assert capability.idle_truth_provider_native is False


def test_p178_github_pages_remains_github_native() -> None:
    coverage = assess_provider_attestation_coverage(("github-pages",))

    assert coverage.classification_complete is True
    capability = coverage.providers[0]
    assert capability.mode == "github-native"
    assert capability.attestor_available is False


def test_p178_unknown_provider_fails_classification_closed() -> None:
    coverage = assess_provider_attestation_coverage(("mystery-provider",))

    assert coverage.classification_complete is False
    assert coverage.provider_native_idle_coverage_complete is False
    assert coverage.unclassified_providers == ("mystery-provider",)
    assert coverage.providers == ()


def test_p178_current_repository_registry_has_no_silent_provider_classification_gap() -> None:
    providers = {
        provider
        for policy in registered_repository_policies()
        for provider in policy.known_integration_providers
    }
    coverage = assess_provider_attestation_coverage(providers)

    assert coverage.classification_complete is True
    assert coverage.unclassified_providers == ()


def test_p178_supported_provider_set_is_stable_and_explicit() -> None:
    assert SUPPORTED_PROVIDER_ATTESTORS == {"vercel", "netlify", "render", "cloudflare", "railway"}
