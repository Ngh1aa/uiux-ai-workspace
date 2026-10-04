from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from core.dogfood.p176_provider_attestation_truth import run_p176_provider_attestation_truth
from core.runtime.flow_os.external_integration_discovery import ExternalIntegrationDiscoveryResult
from core.runtime.flow_os.external_side_effects import ExternalSideEffectEvidence
from core.runtime.flow_os.provider_attestation import (
    ProviderAttestationResult,
    VercelProviderAttestor,
    resolve_canonical_integration_truth,
)


def _pages() -> ExternalSideEffectEvidence:
    return ExternalSideEffectEvidence(
        provider="github-pages",
        effect="deployment",
        source="github-deployment",
        state="observed",
        detail="recent GitHub Pages deployment",
    )


def _vercel_attestation(state: str, *, complete: bool = True) -> ProviderAttestationResult:
    evidence = ()
    if state == "configured":
        evidence = (
            ExternalSideEffectEvidence(
                provider="vercel",
                effect="pr-preview",
                source="provider-attestation:vercel",
                state="configured",
                detail="Vercel project is linked to Ngh1aa/Nova",
            ),
        )
    return ProviderAttestationResult(
        version="1.0",
        provider="vercel",
        repository="Ngh1aa/Nova",
        inspection_complete=complete,
        credential_configured=True,
        state=state,
        project_id="prj_123" if state == "configured" else None,
        linked_repository="ngh1aa/nova" if state == "configured" else None,
        evidence=evidence,
        reason=state,
    )


def test_vercel_attestation_proves_idle_integration_without_recent_deployment() -> None:
    requested: list[str] = []

    def request(path: str):
        requested.append(path)
        if path == "/v9/projects?limit=100":
            return {
                "projects": [
                    {
                        "id": "prj_idle",
                        "name": "nova",
                        "link": {
                            "type": "github",
                            "org": "Ngh1aa",
                            "repo": "Nova",
                            "productionBranch": "main",
                        },
                        "latestDeployments": [
                            {"createdAt": 1735689600000},
                        ],
                    }
                ],
                "pagination": {"next": None},
            }
        if path == "/v9/projects/prj_idle":
            return {
                "id": "prj_idle",
                "name": "nova",
                "link": {
                    "type": "github",
                    "org": "Ngh1aa",
                    "repo": "Nova",
                    "productionBranch": "main",
                },
                "customEnvironments": [{"id": "env_preview"}],
                "latestDeployments": [{"createdAt": 1735689600000}],
            }
        raise AssertionError(path)

    result = VercelProviderAttestor("token", request_json=request).attest_repository("Ngh1aa/Nova")

    assert result.inspection_complete is True
    assert result.state == "configured"
    assert result.project_id == "prj_idle"
    assert result.linked_repository == "ngh1aa/nova"
    assert result.production_branch == "main"
    assert result.connection_active is True
    assert result.environment_ids == ("env_preview",)
    assert result.last_deployment_at is not None
    assert result.evidence[0].source == "provider-attestation:vercel"
    assert all(path.startswith("/v9/projects") for path in requested)


def test_vercel_attestation_missing_credential_is_unknown_not_absent() -> None:
    result = VercelProviderAttestor(None).attest_repository("Ngh1aa/Nova")

    assert result.credential_configured is False
    assert result.inspection_complete is False
    assert result.state == "unknown"
    assert result.evidence == ()


def test_vercel_attestation_complete_project_scan_can_prove_absence() -> None:
    def request(path: str):
        assert path == "/v9/projects?limit=100"
        return {
            "projects": [
                {
                    "id": "prj_other",
                    "name": "other",
                    "link": {"org": "Ngh1aa", "repo": "Other"},
                }
            ],
            "pagination": {"next": None},
        }

    result = VercelProviderAttestor("token", request_json=request).attest_repository("Ngh1aa/Nova")

    assert result.inspection_complete is True
    assert result.state == "not_configured"
    assert result.connection_active is False
    assert result.evidence == ()


def test_vercel_attestation_bounded_incomplete_pagination_fails_closed() -> None:
    def request(path: str):
        if path == "/v9/projects?limit=100":
            return {"projects": [], "pagination": {"next": 123}}
        raise AssertionError(path)

    result = VercelProviderAttestor(
        "token",
        request_json=request,
        max_pages=1,
    ).attest_repository("Ngh1aa/Nova")

    assert result.inspection_complete is False
    assert result.state == "unknown"


def test_p176_report_combines_idle_attestation_without_persisting_credentials(tmp_path: Path) -> None:
    repo_root = tmp_path / "target"
    workflow_dir = repo_root / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "pages.yml").write_text(
        "jobs:\n  deploy:\n    steps:\n      - uses: actions/deploy-pages@v4\n",
        encoding="utf-8",
    )

    external = ExternalIntegrationDiscoveryResult(
        version="1.1",
        repository="Ngh1aa/Nova",
        inspection_complete=True,
        inspected_deployments=0,
        ignored_stale_deployments=4,
        inspected_check_runs=0,
        ignored_stale_check_runs=2,
        evidence=(),
        unknown_deployment_ids=(),
        reason="only stale provider activity",
    )
    observer = SimpleNamespace(discover_repository=lambda repository: external)
    attestation = _vercel_attestation("configured")
    attestor = SimpleNamespace(attest_repository=lambda repository: attestation)

    report = run_p176_provider_attestation_truth(
        repository="Ngh1aa/Nova",
        repo_root=repo_root,
        output_dir=tmp_path / "out",
        github_token="github-secret",
        vercel_token="vercel-super-secret",
        github_observer=observer,
        vercel_attestor=attestor,
    )

    assert report["passed"] is True
    assert report["canonical_integration_truth"]["status"] == "IN_SYNC"
    assert report["credential_values_persisted"] is False
    serialized = json.dumps(report, ensure_ascii=False)
    assert "github-secret" not in serialized
    assert "vercel-super-secret" not in serialized


def test_canonical_truth_accepts_provider_attestation_for_idle_vercel() -> None:
    truth = resolve_canonical_integration_truth(
        "Ngh1aa/Nova",
        (_pages(),),
        attestations={"vercel": _vercel_attestation("configured")},
        inspection_complete=True,
    )

    assert truth.passed is True
    assert truth.status == "IN_SYNC"
    states = {item.provider: item.state for item in truth.providers}
    assert states == {
        "github-pages": "CONFIGURED_EVIDENCED",
        "vercel": "CONFIGURED_ATTESTED",
    }


def test_canonical_truth_does_not_equate_no_recent_evidence_with_removal() -> None:
    truth = resolve_canonical_integration_truth(
        "Ngh1aa/Nova",
        (_pages(),),
        attestations={},
        inspection_complete=True,
    )

    assert truth.passed is False
    assert truth.status == "UNKNOWN_IDLE_INTEGRATION_TRUTH"
    vercel = next(item for item in truth.providers if item.provider == "vercel")
    assert vercel.configured is None
    assert vercel.state == "UNKNOWN_IDLE_TRUTH"


def test_canonical_truth_requires_explicit_complete_attestation_to_claim_removal() -> None:
    truth = resolve_canonical_integration_truth(
        "Ngh1aa/Nova",
        (_pages(),),
        attestations={"vercel": _vercel_attestation("not_configured")},
        inspection_complete=True,
    )

    assert truth.passed is False
    assert truth.status == "DRIFT_REMOVED_PROVIDER"
    vercel = next(item for item in truth.providers if item.provider == "vercel")
    assert vercel.configured is False
    assert vercel.state == "NOT_CONFIGURED_ATTESTED"


def test_canonical_truth_fails_closed_when_external_visibility_is_incomplete() -> None:
    vercel = ExternalSideEffectEvidence(
        provider="vercel",
        effect="pr-preview",
        source="repository-static-config",
        state="configured",
        detail="vercel.json",
    )
    truth = resolve_canonical_integration_truth(
        "Ngh1aa/Nova",
        (vercel, _pages()),
        inspection_complete=False,
    )

    assert truth.passed is False
    assert truth.status == "UNKNOWN_EXTERNAL_VISIBILITY"


def test_canonical_truth_fails_closed_on_attestation_evidence_conflict() -> None:
    vercel = ExternalSideEffectEvidence(
        provider="vercel",
        effect="pr-preview",
        source="repository-static-config",
        state="configured",
        detail="vercel.json",
    )
    truth = resolve_canonical_integration_truth(
        "Ngh1aa/Nova",
        (vercel, _pages()),
        attestations={"vercel": _vercel_attestation("not_configured")},
        inspection_complete=True,
    )

    assert truth.passed is False
    assert truth.status == "CONFLICT_PROVIDER_TRUTH"
    assert truth.conflicting_providers == ("vercel",)
    vercel_truth = next(item for item in truth.providers if item.provider == "vercel")
    assert vercel_truth.state == "CONFLICTING_PROVIDER_TRUTH"
    assert vercel_truth.configured is None


def test_canonical_truth_preserves_added_provider_drift() -> None:
    netlify = ExternalSideEffectEvidence(
        provider="netlify",
        effect="pr-preview",
        source="github-deployment",
        state="observed",
        detail="unexpected provider",
    )
    truth = resolve_canonical_integration_truth(
        "Ngh1aa/Nova",
        (_pages(), netlify),
        attestations={"vercel": _vercel_attestation("configured")},
        inspection_complete=True,
    )

    assert truth.passed is False
    assert truth.status == "DRIFT_ADDED_PROVIDER"
    assert truth.added_providers == ("netlify",)
