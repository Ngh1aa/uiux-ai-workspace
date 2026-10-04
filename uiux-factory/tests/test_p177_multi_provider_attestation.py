from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import core.dogfood.p177_multi_provider_attestation_truth as dogfood_module
import core.runtime.flow_os.provider_attestation as provider_module
from core.dogfood.p177_multi_provider_attestation_truth import run_p177_multi_provider_attestation_truth
from core.runtime.flow_os.external_integration_discovery import ExternalIntegrationDiscoveryResult
from core.runtime.flow_os.external_side_effects import ExternalSideEffectEvidence
from core.runtime.flow_os.provider_attestation import (
    CloudflarePagesProviderAttestor,
    NetlifyProviderAttestor,
    ProviderAttestationResult,
    RenderProviderAttestor,
    SUPPORTED_PROVIDER_ATTESTORS,
    resolve_canonical_integration_truth,
)


def _attestation(provider: str, state: str, *, repository: str = "Ngh1aa/Multi") -> ProviderAttestationResult:
    evidence = ()
    if state == "configured":
        evidence = (
            ExternalSideEffectEvidence(
                provider=provider,
                effect="pr-preview" if provider == "netlify" else "deployment",
                source=f"provider-attestation:{provider}",
                state="configured",
                detail=f"{provider} linked",
            ),
        )
    return ProviderAttestationResult(
        version="1.0",
        provider=provider,
        repository=repository,
        inspection_complete=True,
        credential_configured=True,
        state=state,
        project_id=f"{provider}-project" if state == "configured" else None,
        linked_repository=repository.lower() if state == "configured" else None,
        connection_active=state == "configured",
        evidence=evidence,
        reason=state,
    )


def test_p177_supported_provider_attestors_are_multi_provider() -> None:
    assert SUPPORTED_PROVIDER_ATTESTORS == {"vercel", "netlify", "render", "cloudflare", "railway"}


def test_netlify_attestor_proves_git_linkage() -> None:
    requested: list[str] = []

    def request(path: str):
        requested.append(path)
        if path == "/api/v1/sites?per_page=100&page=1":
            return [
                {
                    "id": "site_1",
                    "name": "nova",
                    "build_settings": {
                        "repo_path": "Ngh1aa/Nova",
                        "repo_branch": "main",
                    },
                    "published_deploy": {"published_at": "2026-01-01T00:00:00Z"},
                }
            ]
        if path == "/api/v1/sites/site_1":
            return {
                "id": "site_1",
                "name": "nova",
                "build_settings": {
                    "repo_url": "https://github.com/Ngh1aa/Nova.git",
                    "repo_branch": "main",
                },
                "published_deploy": {"published_at": "2026-01-01T00:00:00Z"},
            }
        raise AssertionError(path)

    result = NetlifyProviderAttestor("token", request_json=request).attest_repository("Ngh1aa/Nova")

    assert result.state == "configured"
    assert result.inspection_complete is True
    assert result.linked_repository == "ngh1aa/nova"
    assert result.production_branch == "main"
    assert result.connection_active is True
    assert result.last_deployment_at == "2026-01-01T00:00:00Z"
    assert result.evidence[0].source == "provider-attestation:netlify"
    assert requested == ["/api/v1/sites?per_page=100&page=1", "/api/v1/sites/site_1"]


def test_netlify_missing_credential_is_unknown() -> None:
    result = NetlifyProviderAttestor(None).attest_repository("Ngh1aa/Nova")
    assert result.state == "unknown"
    assert result.inspection_complete is False
    assert result.credential_configured is False


def test_render_attestor_proves_git_linkage_and_preview_setting() -> None:
    def request(path: str):
        if path == "/v1/services?limit=100":
            return [
                {
                    "cursor": "next",
                    "service": {
                        "id": "srv_1",
                        "name": "nova-render",
                        "repo": "https://github.com/Ngh1aa/Nova",
                        "branch": "main",
                    },
                }
            ]
        if path == "/v1/services/srv_1":
            return {
                "id": "srv_1",
                "name": "nova-render",
                "repo": "https://github.com/Ngh1aa/Nova",
                "branch": "main",
                "serviceDetails": {"pullRequestPreviewsEnabled": "yes"},
            }
        raise AssertionError(path)

    result = RenderProviderAttestor("token", request_json=request).attest_repository("Ngh1aa/Nova")

    assert result.state == "configured"
    assert result.inspection_complete is True
    assert result.linked_repository == "ngh1aa/nova"
    assert result.production_branch == "main"
    assert result.preview_deployments_enabled is True
    assert result.evidence[0].source == "provider-attestation:render"


def test_render_complete_empty_scan_can_prove_absence() -> None:
    result = RenderProviderAttestor(
        "token",
        request_json=lambda path: [],
    ).attest_repository("Ngh1aa/Nova")

    assert result.state == "not_configured"
    assert result.inspection_complete is True
    assert result.connection_active is False


def test_cloudflare_pages_attestor_proves_git_linkage() -> None:
    def request(path: str):
        assert path == "/accounts/account_1/pages/projects?per_page=100&page=1"
        return {
            "success": True,
            "result": [
                {
                    "id": "pages_1",
                    "name": "nova-pages",
                    "production_branch": "main",
                    "latest_deployment": {"created_on": "2026-02-03T04:05:06Z"},
                    "source": {
                        "type": "github",
                        "config": {
                            "owner": "Ngh1aa",
                            "repo_name": "Nova",
                            "production_branch": "main",
                            "preview_deployment_setting": "all",
                        },
                    },
                }
            ],
            "result_info": {"page": 1, "total_pages": 1},
        }

    result = CloudflarePagesProviderAttestor(
        "token",
        account_id="account_1",
        request_json=request,
    ).attest_repository("Ngh1aa/Nova")

    assert result.state == "configured"
    assert result.inspection_complete is True
    assert result.linked_repository == "ngh1aa/nova"
    assert result.production_branch == "main"
    assert result.preview_deployments_enabled is True
    assert result.last_deployment_at == "2026-02-03T04:05:06Z"
    assert result.evidence[0].source == "provider-attestation:cloudflare"


def test_cloudflare_missing_account_scope_is_unknown() -> None:
    result = CloudflarePagesProviderAttestor(
        "token",
        account_id=None,
    ).attest_repository("Ngh1aa/Nova")

    assert result.state == "unknown"
    assert result.inspection_complete is False
    assert result.credential_configured is False


def test_canonical_truth_accepts_multiple_provider_attestations(monkeypatch) -> None:
    policy = SimpleNamespace(
        repository="Ngh1aa/Multi",
        registered=True,
        known_integration_providers=("netlify", "render", "cloudflare"),
    )
    monkeypatch.setattr(provider_module, "resolve_repository_policy", lambda repository: policy)
    attestations = {
        provider: _attestation(provider, "configured")
        for provider in ("netlify", "render", "cloudflare")
    }
    evidence = tuple(item for result in attestations.values() for item in result.evidence)

    truth = resolve_canonical_integration_truth(
        "Ngh1aa/Multi",
        evidence,
        attestations=attestations,
        inspection_complete=True,
    )

    assert truth.passed is True
    assert truth.status == "IN_SYNC"
    assert {item.provider: item.state for item in truth.providers} == {
        "cloudflare": "CONFIGURED_ATTESTED",
        "netlify": "CONFIGURED_ATTESTED",
        "render": "CONFIGURED_ATTESTED",
    }


def test_canonical_multi_provider_conflict_fails_closed(monkeypatch) -> None:
    policy = SimpleNamespace(
        repository="Ngh1aa/Multi",
        registered=True,
        known_integration_providers=("netlify",),
    )
    monkeypatch.setattr(provider_module, "resolve_repository_policy", lambda repository: policy)
    static = ExternalSideEffectEvidence(
        provider="netlify",
        effect="pr-preview",
        source="repository-static-config",
        state="configured",
        detail="netlify.toml",
    )

    truth = resolve_canonical_integration_truth(
        "Ngh1aa/Multi",
        (static,),
        attestations={"netlify": _attestation("netlify", "not_configured")},
        inspection_complete=True,
    )

    assert truth.passed is False
    assert truth.status == "CONFLICT_PROVIDER_TRUTH"
    assert truth.conflicting_providers == ("netlify",)


def test_p177_report_never_persists_provider_credentials(tmp_path: Path, monkeypatch) -> None:
    policy = SimpleNamespace(
        repository="Ngh1aa/Multi",
        registered=True,
        known_integration_providers=("netlify", "render", "cloudflare"),
    )
    monkeypatch.setattr(dogfood_module, "resolve_repository_policy", lambda repository: policy)
    monkeypatch.setattr(provider_module, "resolve_repository_policy", lambda repository: policy)

    repo_root = tmp_path / "target"
    repo_root.mkdir()
    external = ExternalIntegrationDiscoveryResult(
        version="1.1",
        repository="Ngh1aa/Multi",
        inspection_complete=True,
        inspected_deployments=0,
        ignored_stale_deployments=0,
        inspected_check_runs=0,
        ignored_stale_check_runs=0,
        evidence=(),
        unknown_deployment_ids=(),
        reason="complete",
    )
    observer = SimpleNamespace(discover_repository=lambda repository: external)
    attestors = {
        provider: SimpleNamespace(attest_repository=lambda repository, p=provider: _attestation(p, "configured"))
        for provider in ("netlify", "render", "cloudflare")
    }

    report = run_p177_multi_provider_attestation_truth(
        repository="Ngh1aa/Multi",
        repo_root=repo_root,
        output_dir=tmp_path / "out",
        github_token="github-super-secret",
        netlify_token="netlify-super-secret",
        render_token="render-super-secret",
        cloudflare_token="cloudflare-super-secret",
        cloudflare_account_id="account-super-secret",
        github_observer=observer,
        provider_attestors=attestors,
    )

    assert report["passed"] is True
    assert report["credential_values_persisted"] is False
    serialized = json.dumps(report, ensure_ascii=False)
    for secret in (
        "github-super-secret",
        "netlify-super-secret",
        "render-super-secret",
        "cloudflare-super-secret",
        "account-super-secret",
    ):
        assert secret not in serialized
