from __future__ import annotations

import json
from pathlib import Path

import pytest

import core.dogfood.p1710_continuous_provider_truth as dogfood_module
from core.dogfood.p1710_continuous_provider_truth import run_p1710_continuous_provider_truth
from core.runtime.flow_os.continuous_provider_truth import (
    assess_continuous_provider_truth,
    assess_continuous_provider_truth_payload,
)
from core.runtime.flow_os.provider_attestation import (
    CanonicalIntegrationTruthResult,
    ProviderAttestationResult,
    ProviderIntegrationTruth,
)


def _attestation(
    *,
    provider: str = "vercel",
    credential_configured: bool,
    inspection_complete: bool,
    state: str,
) -> ProviderAttestationResult:
    return ProviderAttestationResult(
        version="1.0",
        provider=provider,
        repository="Ngh1aa/Test",
        inspection_complete=inspection_complete,
        credential_configured=credential_configured,
        state=state,
        reason=state,
    )


def _truth(
    *,
    status: str,
    passed: bool,
    provider_state: str,
    attestation: ProviderAttestationResult | None,
    provider: str = "vercel",
) -> CanonicalIntegrationTruthResult:
    return CanonicalIntegrationTruthResult(
        version="1.0",
        repository="Ngh1aa/Test",
        status=status,
        passed=passed,
        inspection_complete=True,
        inspection_channels=("repository-static", "github-provider-native", "provider-attestation"),
        providers=(
            ProviderIntegrationTruth(
                provider=provider,
                state=provider_state,
                configured=True if provider_state.startswith("CONFIGURED") else None,
                evidence_channels=(),
                reason=provider_state,
                attestation=attestation,
            ),
        ),
        added_providers=(),
        conflicting_providers=(),
        evidence=(),
        reason=status,
    )


def test_p1710_missing_optional_secret_is_degraded_not_blocking() -> None:
    truth = _truth(
        status="UNKNOWN_IDLE_INTEGRATION_TRUTH",
        passed=False,
        provider_state="UNKNOWN_IDLE_TRUTH",
        attestation=_attestation(
            credential_configured=False,
            inspection_complete=False,
            state="unknown",
        ),
    )

    assessment = assess_continuous_provider_truth(truth)

    assert assessment.state == "DEGRADED_MISSING_OPTIONAL_CREDENTIALS"
    assert assessment.blocking is False
    assert assessment.credential_gap_providers == ("vercel",)
    assert assessment.provider_visibility_failure_providers == ()
    assert assessment.evidence_gap_providers == ()


def test_p1710_verified_static_truth_can_stay_green_without_optional_secret() -> None:
    truth = _truth(
        status="IN_SYNC",
        passed=True,
        provider_state="CONFIGURED_EVIDENCED",
        attestation=_attestation(
            credential_configured=False,
            inspection_complete=False,
            state="unknown",
        ),
    )

    assessment = assess_continuous_provider_truth(truth)

    assert assessment.state == "HEALTHY_WITH_OPTIONAL_CREDENTIAL_GAPS"
    assert assessment.blocking is False
    assert assessment.credential_gap_providers == ("vercel",)


def test_p1710_configured_credential_visibility_failure_is_blocking() -> None:
    truth = _truth(
        status="IN_SYNC",
        passed=True,
        provider_state="CONFIGURED_EVIDENCED",
        attestation=_attestation(
            credential_configured=True,
            inspection_complete=False,
            state="unknown",
        ),
    )

    assessment = assess_continuous_provider_truth(truth)

    assert assessment.state == "ACTION_REQUIRED_PROVIDER_VISIBILITY"
    assert assessment.blocking is True
    assert assessment.provider_visibility_failure_providers == ("vercel",)


def test_p1710_noncredential_idle_evidence_gap_remains_blocking() -> None:
    truth = _truth(
        status="UNKNOWN_IDLE_INTEGRATION_TRUTH",
        passed=False,
        provider_state="UNKNOWN_IDLE_TRUTH",
        attestation=None,
        provider="github-pages",
    )

    assessment = assess_continuous_provider_truth(truth)

    assert assessment.state == "ACTION_REQUIRED_CANONICAL_TRUTH"
    assert assessment.blocking is True
    assert assessment.credential_gap_providers == ()
    assert assessment.evidence_gap_providers == ("github-pages",)


def test_p1710_drift_remains_blocking_even_if_optional_secret_is_missing() -> None:
    truth = _truth(
        status="DRIFT_ADDED_PROVIDER",
        passed=False,
        provider_state="CONFIGURED_EVIDENCED",
        attestation=_attestation(
            credential_configured=False,
            inspection_complete=False,
            state="unknown",
        ),
    )

    assessment = assess_continuous_provider_truth(truth)

    assert assessment.state == "ACTION_REQUIRED_CANONICAL_TRUTH"
    assert assessment.blocking is True


def test_p1710_payload_classifier_matches_object_semantics() -> None:
    truth = _truth(
        status="UNKNOWN_IDLE_INTEGRATION_TRUTH",
        passed=False,
        provider_state="UNKNOWN_IDLE_TRUTH",
        attestation=_attestation(
            credential_configured=False,
            inspection_complete=False,
            state="unknown",
        ),
    )

    from_object = assess_continuous_provider_truth(truth)
    from_payload = assess_continuous_provider_truth_payload(truth.to_dict())

    assert from_payload == from_object


def test_p1710_runner_does_not_fail_for_missing_optional_credentials(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    truth = _truth(
        status="UNKNOWN_IDLE_INTEGRATION_TRUTH",
        passed=False,
        provider_state="UNKNOWN_IDLE_TRUTH",
        attestation=_attestation(
            credential_configured=False,
            inspection_complete=False,
            state="unknown",
        ),
    )

    def fake_p177(**kwargs):
        assert kwargs["enforce_passed"] is False
        return {
            "passed": False,
            "canonical_integration_truth": truth.to_dict(),
            "provider_attestation_coverage": {"classification_complete": True},
            "provider_attestations": {"vercel": truth.providers[0].attestation.to_dict()},
        }

    monkeypatch.setattr(dogfood_module, "run_p177_multi_provider_attestation_truth", fake_p177)

    report = run_p1710_continuous_provider_truth(
        repository="Ngh1aa/Test",
        repo_root=tmp_path,
        output_dir=tmp_path / "out",
        github_token="github-token",
    )

    assert report["monitoring"]["state"] == "DEGRADED_MISSING_OPTIONAL_CREDENTIALS"
    assert report["monitoring"]["blocking"] is False
    assert report["missing_optional_credentials_are_blocking"] is False
    serialized = json.dumps(report, ensure_ascii=False)
    assert "github-token" not in serialized
    assert (tmp_path / "out" / "p1710-continuous-provider-truth-ngh1aa-test.json").is_file()


def test_p1710_runner_fails_for_real_canonical_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    truth = _truth(
        status="DRIFT_ADDED_PROVIDER",
        passed=False,
        provider_state="CONFIGURED_EVIDENCED",
        attestation=None,
    )

    monkeypatch.setattr(
        dogfood_module,
        "run_p177_multi_provider_attestation_truth",
        lambda **kwargs: {
            "passed": False,
            "canonical_integration_truth": truth.to_dict(),
            "provider_attestation_coverage": {"classification_complete": True},
            "provider_attestations": {},
        },
    )

    with pytest.raises(RuntimeError, match="requires action"):
        run_p1710_continuous_provider_truth(
            repository="Ngh1aa/Test",
            repo_root=tmp_path,
            output_dir=tmp_path / "out",
            github_token=None,
        )

    report_path = tmp_path / "out" / "p1710-continuous-provider-truth-ngh1aa-test.json"
    assert report_path.is_file()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["monitoring"]["blocking"] is True
