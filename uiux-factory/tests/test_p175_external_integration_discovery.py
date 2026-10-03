from __future__ import annotations

from datetime import datetime, timezone

from core.dogfood.p175_external_integration_discovery import build_external_integration_matrix
from core.runtime.flow_os.external_integration_discovery import (
    GitHubDeploymentIntegrationObserver,
    infer_provider_from_github_deployment,
)
from core.runtime.flow_os.external_side_effects import ExternalSideEffectEvidence
from core.runtime.flow_os.repository_policy_drift import assess_repository_policy_drift
from core.runtime.flow_os.repository_policy_registry import registered_repository_policies, resolve_repository_policy


NOW = datetime(2026, 10, 4, tzinfo=timezone.utc)
FULL_SCOPE = ("repository-static", "external-observed")


def _static(provider: str, effect: str = "pr-preview") -> ExternalSideEffectEvidence:
    return ExternalSideEffectEvidence(
        provider=provider,
        effect=effect,
        source="repository-static-config",
        state="configured",
        detail=f"{provider} static marker",
    )


def test_provider_classifier_covers_supported_external_hosts() -> None:
    assert infer_provider_from_github_deployment("vercel[bot]") == "vercel"
    assert infer_provider_from_github_deployment("https://preview.netlify.app") == "netlify"
    assert infer_provider_from_github_deployment("github-pages") == "github-pages"
    assert infer_provider_from_github_deployment("https://app.onrender.com") == "render"
    assert infer_provider_from_github_deployment("https://service.railway.app") == "railway"
    assert infer_provider_from_github_deployment("https://site.pages.dev") == "cloudflare"
    assert infer_provider_from_github_deployment("https://project.web.app") == "firebase-hosting"


def test_vercel_deployment_is_observed_without_status_lookup() -> None:
    requested: list[str] = []

    def request(path: str):
        requested.append(path)
        return [
            {
                "id": 101,
                "creator": {"login": "vercel[bot]"},
                "environment": "Preview",
                "created_at": "2026-10-03T12:00:00Z",
                "updated_at": "2026-10-03T12:00:00Z",
                "url": "https://api.github.com/repos/Ngh1aa/Nova/deployments/101",
            }
        ]

    observer = GitHubDeploymentIntegrationObserver(None, request_json=request, include_check_runs=False)
    result = observer.discover_repository("Ngh1aa/Nova", now=NOW)

    assert result.inspection_complete is True
    assert result.inspected_deployments == 1
    assert result.evidence[0].provider == "vercel"
    assert result.evidence[0].source == "github-deployment"
    assert len(requested) == 1


def test_status_metadata_can_attribute_provider_when_deployment_is_generic() -> None:
    def request(path: str):
        if path.endswith("/deployments?per_page=20"):
            return [
                {
                    "id": 202,
                    "creator": {"login": "github-actions[bot]"},
                    "environment": "preview",
                    "created_at": "2026-10-03T12:00:00Z",
                }
            ]
        if path.endswith("/deployments/202/statuses?per_page=10"):
            return [
                {
                    "creator": {"login": "netlify[bot]"},
                    "environment_url": "https://example.netlify.app",
                    "created_at": "2026-10-03T12:01:00Z",
                }
            ]
        raise AssertionError(path)

    observer = GitHubDeploymentIntegrationObserver(None, request_json=request, include_check_runs=False)
    result = observer.discover_repository("Ngh1aa/Nova", now=NOW)

    assert result.inspection_complete is True
    assert result.evidence[0].provider == "netlify"
    assert result.evidence[0].source == "github-deployment-status"
    assert result.evidence[0].url == "https://example.netlify.app"


def test_default_branch_check_run_can_supply_provider_native_evidence() -> None:
    def request(path: str):
        if path.endswith("/deployments?per_page=20"):
            return []
        if path == "/repos/Ngh1aa/Nova":
            return {"default_branch": "main"}
        if path.endswith("/commits/main/check-runs?per_page=100"):
            return {
                "check_runs": [
                    {
                        "id": 808,
                        "name": "Vercel",
                        "app": {"slug": "vercel", "name": "Vercel"},
                        "details_url": "https://vercel.com/example/deployment",
                        "completed_at": "2026-10-03T12:00:00Z",
                    }
                ]
            }
        raise AssertionError(path)

    observer = GitHubDeploymentIntegrationObserver(None, request_json=request, include_check_runs=True)
    result = observer.discover_repository("Ngh1aa/Nova", now=NOW)

    assert result.inspection_complete is True
    assert result.inspected_deployments == 0
    assert result.inspected_check_runs == 1
    assert result.evidence[0].provider == "vercel"
    assert result.evidence[0].source == "github-check-run"


def test_stale_deployment_history_is_not_current_freshness_evidence() -> None:
    def request(path: str):
        return [
            {
                "id": 303,
                "creator": {"login": "vercel[bot]"},
                "environment": "Preview",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
            }
        ]

    observer = GitHubDeploymentIntegrationObserver(
        None,
        request_json=request,
        max_age_days=90,
        include_check_runs=False,
    )
    result = observer.discover_repository("Ngh1aa/Nova", now=NOW)

    assert result.inspection_complete is True
    assert result.inspected_deployments == 0
    assert result.ignored_stale_deployments == 1
    assert result.evidence == ()


def test_unclassified_recent_deployment_becomes_explicit_unknown_external_evidence() -> None:
    def request(path: str):
        if path.endswith("/deployments?per_page=20"):
            return [
                {
                    "id": 404,
                    "creator": {"login": "deploy-bot"},
                    "environment": "production",
                    "created_at": "2026-10-03T12:00:00Z",
                }
            ]
        if path.endswith("/deployments/404/statuses?per_page=10"):
            return []
        raise AssertionError(path)

    observer = GitHubDeploymentIntegrationObserver(None, request_json=request, include_check_runs=False)
    result = observer.discover_repository("Ngh1aa/Nova", now=NOW)

    assert result.inspection_complete is True
    assert result.unknown_deployment_ids == (404,)
    assert result.evidence[0].provider == "unknown-external"

    assessment = assess_repository_policy_drift(
        "Ngh1aa/Nova",
        (_static("vercel"), *result.evidence),
        inspection_complete=True,
        inspection_channels=FULL_SCOPE,
    )
    assert assessment.status == "DRIFT_ADDED_AND_REMOVED_PROVIDER"
    assert assessment.added_providers == ("unknown-external",)
    assert assessment.removed_providers == ("github-pages",)


def test_external_visibility_failure_is_unknown_not_safe() -> None:
    def request(path: str):
        raise OSError("network unavailable")

    observer = GitHubDeploymentIntegrationObserver(None, request_json=request, include_check_runs=False)
    result = observer.discover_repository("Ngh1aa/Nova", now=NOW)

    assert result.inspection_complete is False
    assessment = assess_repository_policy_drift(
        "Ngh1aa/Nova",
        (_static("vercel"),),
        inspection_complete=False,
        inspection_channels=FULL_SCOPE,
    )
    assert assessment.status == "UNKNOWN_POLICY_DRIFT"
    assert assessment.in_sync is False


def test_external_vercel_does_not_replace_static_required_vercel_marker() -> None:
    def request(path: str):
        return [
            {
                "id": 505,
                "creator": {"login": "vercel[bot]"},
                "environment": "Preview",
                "created_at": "2026-10-03T12:00:00Z",
            },
            {
                "id": 506,
                "creator": {"login": "github-actions[bot]"},
                "environment": "github-pages",
                "created_at": "2026-10-03T12:00:00Z",
            },
        ]

    observer = GitHubDeploymentIntegrationObserver(None, request_json=request, include_check_runs=False)
    result = observer.discover_repository("Ngh1aa/Nova", now=NOW)
    assessment = assess_repository_policy_drift(
        "Ngh1aa/Nova",
        result.evidence,
        inspection_complete=True,
        inspection_channels=FULL_SCOPE,
    )

    assert assessment.status == "DRIFT_REMOVED_PROVIDER"
    assert assessment.removed_providers == ("vercel",)
    assert assessment.evidence_channels["vercel"] == ("external-observed",)
    assert assessment.evidence_channels["github-pages"] == ("external-observed",)


def test_static_vercel_plus_external_pages_is_full_scope_in_sync() -> None:
    pages = ExternalSideEffectEvidence(
        provider="github-pages",
        effect="deployment",
        source="github-deployment",
        state="observed",
        detail="recent Pages deployment",
    )
    assessment = assess_repository_policy_drift(
        "Ngh1aa/Nova",
        (_static("vercel"), pages),
        inspection_complete=True,
        inspection_channels=FULL_SCOPE,
    )

    assert assessment.status == "IN_SYNC"
    assert assessment.in_sync is True
    assert assessment.coverage_complete is True
    assert assessment.unresolved_providers == ()
    assert assessment.evidence_channels == {
        "github-pages": ("external-observed",),
        "vercel": ("repository-static",),
    }


def test_missing_external_pages_is_removed_in_full_scope() -> None:
    assessment = assess_repository_policy_drift(
        "Ngh1aa/Nova",
        (_static("vercel"),),
        inspection_complete=True,
        inspection_channels=FULL_SCOPE,
    )

    assert assessment.status == "DRIFT_REMOVED_PROVIDER"
    assert assessment.removed_providers == ("github-pages",)
    assert assessment.coverage_complete is True


def test_recent_unregistered_external_provider_is_added_drift() -> None:
    pages = ExternalSideEffectEvidence(
        provider="github-pages",
        effect="deployment",
        source="github-deployment",
        state="observed",
        detail="recent Pages deployment",
    )
    netlify = ExternalSideEffectEvidence(
        provider="netlify",
        effect="pr-preview",
        source="github-deployment",
        state="observed",
        detail="unexpected Netlify deployment",
    )
    assessment = assess_repository_policy_drift(
        "Ngh1aa/Nova",
        (_static("vercel"), pages, netlify),
        inspection_complete=True,
        inspection_channels=FULL_SCOPE,
    )

    assert assessment.status == "DRIFT_ADDED_PROVIDER"
    assert assessment.added_providers == ("netlify",)


def test_registry_separates_static_and_external_freshness_without_broadening_authority() -> None:
    nova = resolve_repository_policy("Ngh1aa/Nova")
    rules = {rule.provider: rule for rule in nova.integration_freshness}

    assert rules["vercel"].evidence_channels == ("repository-static",)
    assert rules["github-pages"].evidence_channels == ("external-observed",)
    assert nova.allowed_preview_providers == ("vercel",)
    assert nova.known_integration_providers == ("vercel", "github-pages")
    assert nova.release_boundary.allow_merge is False
    assert nova.release_boundary.allow_production_deploy is False
    assert nova.release_boundary.allow_release is False


def test_p175_matrix_is_registry_derived() -> None:
    matrix = build_external_integration_matrix()
    assert [item["repository"] for item in matrix["include"]] == [
        policy.repository for policy in registered_repository_policies()
    ]
