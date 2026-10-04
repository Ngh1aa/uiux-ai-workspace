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



FLEET_DEGRADED_STATES = frozenset(
    {
        "HEALTHY_WITH_OPTIONAL_CREDENTIAL_GAPS",
        "DEGRADED_MISSING_OPTIONAL_CREDENTIALS",
    }
)


@dataclass(frozen=True)
class ContinuousProviderTruthFleetMember:
    repository: str
    state: str
    blocking: bool
    canonical_status: str
    credential_gap_providers: tuple[str, ...] = ()
    provider_visibility_failure_providers: tuple[str, ...] = ()
    evidence_gap_providers: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["credential_gap_providers"] = list(self.credential_gap_providers)
        payload["provider_visibility_failure_providers"] = list(
            self.provider_visibility_failure_providers
        )
        payload["evidence_gap_providers"] = list(self.evidence_gap_providers)
        return payload


@dataclass(frozen=True)
class ContinuousProviderTruthFleetAssessment:
    version: str
    state: str
    passed: bool
    expected_registry_valid: bool
    expected_repositories: tuple[str, ...]
    observed_repositories: tuple[str, ...]
    healthy_repositories: tuple[str, ...]
    degraded_repositories: tuple[str, ...]
    blocking_repositories: tuple[str, ...]
    missing_repositories: tuple[str, ...]
    unexpected_repositories: tuple[str, ...]
    duplicate_repositories: tuple[str, ...]
    malformed_reports: tuple[str, ...]
    members: tuple[ContinuousProviderTruthFleetMember, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "state": self.state,
            "passed": self.passed,
            "expected_registry_valid": self.expected_registry_valid,
            "expected_repositories": list(self.expected_repositories),
            "observed_repositories": list(self.observed_repositories),
            "healthy_repositories": list(self.healthy_repositories),
            "degraded_repositories": list(self.degraded_repositories),
            "blocking_repositories": list(self.blocking_repositories),
            "missing_repositories": list(self.missing_repositories),
            "unexpected_repositories": list(self.unexpected_repositories),
            "duplicate_repositories": list(self.duplicate_repositories),
            "malformed_reports": list(self.malformed_reports),
            "members": [item.to_dict() for item in self.members],
            "reason": self.reason,
        }


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError("provider list fields must be arrays")
    values: list[str] = []
    for item in value:
        text = str(item or "").strip()
        if not text:
            raise ValueError("provider list fields cannot contain blank values")
        if text not in values:
            values.append(text)
    return tuple(sorted(values))


def _fleet_member_from_report(report: Mapping[str, Any]) -> ContinuousProviderTruthFleetMember:
    repository = str(report.get("repository") or "").strip()
    monitoring = report.get("monitoring")
    if not repository or not isinstance(monitoring, Mapping):
        raise ValueError("continuous provider truth report requires repository and monitoring object")

    state = str(monitoring.get("state") or "").strip()
    canonical_status = str(monitoring.get("canonical_status") or "").strip()
    blocking = monitoring.get("blocking")
    if not state or not canonical_status or not isinstance(blocking, bool):
        raise ValueError("continuous provider truth monitoring requires state, boolean blocking, and canonical_status")

    if report.get("credential_values_persisted") is True:
        raise ValueError("continuous provider truth report claims credential persistence")

    return ContinuousProviderTruthFleetMember(
        repository=repository,
        state=state,
        blocking=blocking,
        canonical_status=canonical_status,
        credential_gap_providers=_string_tuple(monitoring.get("credential_gap_providers")),
        provider_visibility_failure_providers=_string_tuple(
            monitoring.get("provider_visibility_failure_providers")
        ),
        evidence_gap_providers=_string_tuple(monitoring.get("evidence_gap_providers")),
    )


def aggregate_continuous_provider_truth_reports(
    reports: Iterable[Mapping[str, Any]],
    *,
    expected_repositories: Iterable[str],
    malformed_reports: Iterable[str] = (),
) -> ContinuousProviderTruthFleetAssessment:
    """Aggregate one scheduled P1.7.10 report per registered repository.

    Missing/extra/duplicate/malformed reports fail closed. Credential-only degraded
    states remain visible but do not block the fleet when every expected repository
    produced a valid non-blocking report.
    """

    expected_values = [str(value or "").strip() for value in expected_repositories]
    expected_values = [value for value in expected_values if value]
    expected_by_key: dict[str, str] = {}
    expected_duplicates: list[str] = []
    for value in expected_values:
        key = value.lower()
        if key in expected_by_key:
            expected_duplicates.append(value)
            continue
        expected_by_key[key] = value

    expected_registry_valid = bool(expected_by_key) and not expected_duplicates
    members_by_key: dict[str, ContinuousProviderTruthFleetMember] = {}
    duplicates: list[str] = list(expected_duplicates)
    malformed = [str(value) for value in malformed_reports if str(value).strip()]

    for index, report in enumerate(reports):
        try:
            member = _fleet_member_from_report(report)
        except (TypeError, ValueError) as exc:
            malformed.append(f"report[{index}]: {exc}")
            continue
        key = member.repository.lower()
        if key in members_by_key:
            duplicates.append(member.repository)
            continue
        members_by_key[key] = member

    expected_keys = set(expected_by_key)
    observed_keys = set(members_by_key)
    missing = tuple(sorted(expected_by_key[key] for key in expected_keys - observed_keys))
    unexpected = tuple(sorted(members_by_key[key].repository for key in observed_keys - expected_keys))

    members = tuple(
        sorted(
            (member for key, member in members_by_key.items() if key in expected_keys),
            key=lambda item: item.repository.lower(),
        )
    )
    blocking = tuple(sorted(item.repository for item in members if item.blocking))
    degraded = tuple(
        sorted(
            item.repository
            for item in members
            if not item.blocking and item.state in FLEET_DEGRADED_STATES
        )
    )
    healthy = tuple(
        sorted(
            item.repository
            for item in members
            if not item.blocking and item.state not in FLEET_DEGRADED_STATES
        )
    )

    malformed_tuple = tuple(sorted(set(malformed)))
    duplicate_tuple = tuple(sorted(set(duplicates)))
    passed = (
        expected_registry_valid
        and not blocking
        and not missing
        and not unexpected
        and not duplicate_tuple
        and not malformed_tuple
    )

    if not passed:
        state = "FLEET_ACTION_REQUIRED"
        reasons: list[str] = []
        if not expected_registry_valid:
            reasons.append("expected repository registry is empty or duplicated")
        if blocking:
            reasons.append("blocking=" + ",".join(blocking))
        if missing:
            reasons.append("missing=" + ",".join(missing))
        if unexpected:
            reasons.append("unexpected=" + ",".join(unexpected))
        if duplicate_tuple:
            reasons.append("duplicate=" + ",".join(duplicate_tuple))
        if malformed_tuple:
            reasons.append("malformed=" + ",".join(malformed_tuple))
        reason = "Continuous provider truth fleet requires action: " + "; ".join(reasons) + "."
    elif degraded:
        state = "FLEET_DEGRADED_OPTIONAL_CREDENTIALS"
        reason = (
            "All registered repositories produced non-blocking monitoring truth. Optional credential gaps remain for: "
            + ", ".join(degraded)
            + "."
        )
    else:
        state = "FLEET_HEALTHY_VERIFIED"
        reason = "All registered repositories produced healthy non-blocking continuous provider truth."

    return ContinuousProviderTruthFleetAssessment(
        version=CONTINUOUS_PROVIDER_TRUTH_VERSION,
        state=state,
        passed=passed,
        expected_registry_valid=expected_registry_valid,
        expected_repositories=tuple(sorted(expected_by_key.values())),
        observed_repositories=tuple(sorted(item.repository for item in members_by_key.values())),
        healthy_repositories=healthy,
        degraded_repositories=degraded,
        blocking_repositories=blocking,
        missing_repositories=missing,
        unexpected_repositories=unexpected,
        duplicate_repositories=duplicate_tuple,
        malformed_reports=malformed_tuple,
        members=members,
        reason=reason,
    )


def render_continuous_provider_truth_fleet_markdown(
    assessment: ContinuousProviderTruthFleetAssessment,
) -> str:
    lines = [
        "# P1.7.11 Continuous Provider Truth Fleet",
        "",
        f"**State:** `{assessment.state}`",
        f"**Passed:** `{str(assessment.passed).lower()}`",
        "",
        assessment.reason,
        "",
        "| Repository | Monitoring state | Canonical status | Blocking | Credential gaps |",
        "| --- | --- | --- | --- | --- |",
    ]
    for member in assessment.members:
        gaps = ", ".join(member.credential_gap_providers) or "—"
        lines.append(
            f"| {member.repository} | `{member.state}` | `{member.canonical_status}` | "
            f"`{str(member.blocking).lower()}` | {gaps} |"
        )

    if assessment.missing_repositories:
        lines.extend(["", "**Missing reports:** " + ", ".join(assessment.missing_repositories)])
    if assessment.unexpected_repositories:
        lines.extend(["", "**Unexpected reports:** " + ", ".join(assessment.unexpected_repositories)])
    if assessment.duplicate_repositories:
        lines.extend(["", "**Duplicate reports:** " + ", ".join(assessment.duplicate_repositories)])
    if assessment.malformed_reports:
        lines.extend(["", "**Malformed reports:** " + "; ".join(assessment.malformed_reports)])

    return "\n".join(lines) + "\n"
