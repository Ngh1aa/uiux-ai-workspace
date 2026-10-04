from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

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


@dataclass(frozen=True)
class _ProviderObservation:
    provider: str
    state: str
    credential_configured: bool | None
    inspection_complete: bool | None
    attestation_state: str | None


def _classify(
    *,
    repository: str,
    canonical_status: str,
    passed: bool,
    observations: Iterable[_ProviderObservation],
) -> ContinuousProviderTruthAssessment:
    credential_gaps: list[str] = []
    visibility_failures: list[str] = []
    evidence_gaps: list[str] = []

    for item in observations:
        if item.credential_configured is False:
            credential_gaps.append(item.provider)

        if (
            item.credential_configured is True
            and item.inspection_complete is False
            and item.attestation_state == "unknown"
        ):
            visibility_failures.append(item.provider)

        if item.state == "UNKNOWN_IDLE_TRUTH":
            if item.credential_configured is False:
                continue
            if item.credential_configured is True and item.inspection_complete is False:
                continue
            evidence_gaps.append(item.provider)

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
    elif passed:
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
        canonical_status == "UNKNOWN_IDLE_INTEGRATION_TRUTH"
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
        details: list[str] = [f"canonical_status={canonical_status}"]
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
        repository=repository,
        state=state,
        blocking=blocking,
        canonical_status=canonical_status,
        credential_gap_providers=credential_gap_providers,
        provider_visibility_failure_providers=provider_visibility_failure_providers,
        evidence_gap_providers=evidence_gap_providers,
        reason=reason,
    )


def assess_continuous_provider_truth(
    truth: CanonicalIntegrationTruthResult,
) -> ContinuousProviderTruthAssessment:
    """Classify scheduled provider truth without treating optional secrets as failures."""

    observations = []
    for provider_truth in truth.providers:
        attestation = provider_truth.attestation
        observations.append(
            _ProviderObservation(
                provider=provider_truth.provider,
                state=provider_truth.state,
                credential_configured=(
                    attestation.credential_configured if attestation is not None else None
                ),
                inspection_complete=(
                    attestation.inspection_complete if attestation is not None else None
                ),
                attestation_state=attestation.state if attestation is not None else None,
            )
        )

    return _classify(
        repository=truth.repository,
        canonical_status=truth.status,
        passed=truth.passed,
        observations=observations,
    )


def assess_continuous_provider_truth_payload(
    payload: Mapping[str, Any],
) -> ContinuousProviderTruthAssessment:
    """Classify a serialized CanonicalIntegrationTruthResult artifact."""

    providers = payload.get("providers")
    if not isinstance(providers, list):
        raise ValueError("canonical provider truth payload requires providers[]")

    observations: list[_ProviderObservation] = []
    for raw in providers:
        if not isinstance(raw, Mapping):
            raise ValueError("canonical provider truth provider entries must be objects")
        attestation = raw.get("attestation")
        attestation_mapping = attestation if isinstance(attestation, Mapping) else None
        observations.append(
            _ProviderObservation(
                provider=str(raw.get("provider") or "").strip(),
                state=str(raw.get("state") or "").strip(),
                credential_configured=(
                    bool(attestation_mapping.get("credential_configured"))
                    if attestation_mapping is not None
                    and isinstance(attestation_mapping.get("credential_configured"), bool)
                    else None
                ),
                inspection_complete=(
                    bool(attestation_mapping.get("inspection_complete"))
                    if attestation_mapping is not None
                    and isinstance(attestation_mapping.get("inspection_complete"), bool)
                    else None
                ),
                attestation_state=(
                    str(attestation_mapping.get("state") or "").strip() or None
                    if attestation_mapping is not None
                    else None
                ),
            )
        )

    repository = str(payload.get("repository") or "").strip()
    canonical_status = str(payload.get("status") or "").strip()
    passed = bool(payload.get("passed"))
    if not repository or not canonical_status:
        raise ValueError("canonical provider truth payload requires repository and status")

    return _classify(
        repository=repository,
        canonical_status=canonical_status,
        passed=passed,
        observations=observations,
    )
