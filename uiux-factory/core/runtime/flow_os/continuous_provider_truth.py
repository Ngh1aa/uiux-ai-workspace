from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from core.runtime.flow_os.provider_attestation import CanonicalIntegrationTruthResult


CONTINUOUS_PROVIDER_TRUTH_VERSION = "1.0"


@dataclass(frozen=True)
class ContinuousProviderTruthAssessment:
    version: str
    repository: str
    state: str
    blocking: bool
    canonical_status: str
    credential_gap_providers: tuple[str, ...]
    provider_visibility_failure_providers: tuple[str, ...]
    evidence_gap_providers: tuple[str, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["credential_gap_providers"] = list(self.credential_gap_providers)
        payload["provider_visibility_failure_providers"] = list(
            self.provider_visibility_failure_providers
        )
        payload["evidence_gap_providers"] = list(self.evidence_gap_providers)
        return payload


def assess_continuous_provider_truth(
    truth: CanonicalIntegrationTruthResult,
) -> ContinuousProviderTruthAssessment:
    """Classify scheduled provider truth without treating optional secrets as failures.

    Canonical truth remains fail-closed. This layer only decides whether a scheduled
    monitoring workflow should fail. Missing opt-in credentials are surfaced as a
    degraded-but-nonblocking monitoring state. Drift, conflicts, provider visibility
    failures with configured credentials, and non-credential evidence gaps remain
    blocking.
    """

    credential_gaps: list[str] = []
    visibility_failures: list[str] = []
    evidence_gaps: list[str] = []

    for provider_truth in truth.providers:
        attestation = provider_truth.attestation

        if attestation is not None and not attestation.credential_configured:
            credential_gaps.append(provider_truth.provider)

        if (
            attestation is not None
            and attestation.credential_configured
            and not attestation.inspection_complete
            and attestation.state == "unknown"
        ):
            visibility_failures.append(provider_truth.provider)

        if provider_truth.state == "UNKNOWN_IDLE_TRUTH":
            if attestation is not None and not attestation.credential_configured:
                continue
            if (
                attestation is not None
                and attestation.credential_configured
                and not attestation.inspection_complete
            ):
                continue
            evidence_gaps.append(provider_truth.provider)

    credential_gap_providers = tuple(sorted(set(credential_gaps)))
    provider_visibility_failure_providers = tuple(sorted(set(visibility_failures)))
    evidence_gap_providers = tuple(sorted(set(evidence_gaps)))

    if provider_visibility_failure_providers:
        state = "ACTION_REQUIRED_PROVIDER_VISIBILITY"
        blocking = True
        reason = (
            "Configured provider credentials could not establish readable provider visibility for: "
            + ", ".join(provider_visibility_failure_providers)
            + ". Scheduled monitoring fails closed because this is not a missing-secret condition."
        )
    elif truth.passed:
        blocking = False
        if credential_gap_providers:
            state = "HEALTHY_WITH_OPTIONAL_CREDENTIAL_GAPS"
            reason = (
                "Canonical integration truth is verified from trusted evidence. Optional provider credentials "
                "are absent for: "
                + ", ".join(credential_gap_providers)
                + ". Scheduled monitoring remains green while surfacing the reduced provider-native coverage."
            )
        else:
            state = "HEALTHY_VERIFIED"
            reason = "Canonical integration truth is verified and no provider visibility gap is active."
    elif (
        truth.status == "UNKNOWN_IDLE_INTEGRATION_TRUTH"
        and credential_gap_providers
        and not evidence_gap_providers
    ):
        state = "DEGRADED_MISSING_OPTIONAL_CREDENTIALS"
        blocking = False
        reason = (
            "Canonical idle truth is incomplete only because opt-in provider credentials are absent for: "
            + ", ".join(credential_gap_providers)
            + ". The scheduled lane records this as degraded coverage without failing the workflow."
        )
    else:
        state = "ACTION_REQUIRED_CANONICAL_TRUTH"
        blocking = True
        details: list[str] = [f"canonical_status={truth.status}"]
        if evidence_gap_providers:
            details.append("evidence_gap=" + ",".join(evidence_gap_providers))
        reason = (
            "Scheduled provider truth found a condition that is not explainable solely by missing optional "
            "credentials: "
            + "; ".join(details)
            + "."
        )

    return ContinuousProviderTruthAssessment(
        version=CONTINUOUS_PROVIDER_TRUTH_VERSION,
        repository=truth.repository,
        state=state,
        blocking=blocking,
        canonical_status=truth.status,
        credential_gap_providers=credential_gap_providers,
        provider_visibility_failure_providers=provider_visibility_failure_providers,
        evidence_gap_providers=evidence_gap_providers,
        reason=reason,
    )
