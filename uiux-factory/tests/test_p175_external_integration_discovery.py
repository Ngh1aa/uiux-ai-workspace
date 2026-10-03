from __future__ import annotations

from datetime import datetime, timezone

from core.dogfood.p175_external_integration_discovery import build_external_integration_matrix
from core.runtime.flow_os.external_integration_discovery import (
    GitHubDeploymentIntegrationObserver,
    infer_provider_from_github_deployment,
)
from core.runtime.flow_os.repository_policy_drift import assess_repository_policy_drift
from core.runtime.flow_os.repository_policy_registry import registered_repository_policies, resolve_repository_policy


NOW = datetime(2026, 10, 4, tzinfo=timezone.utc)


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

    observer = GitHubDeploymentIntegrationObserver(None, request_json=request)
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

    observer = GitHubDeploymentIntegrationObserver(None, request_json=request)
    result = observer.discover_repository("Ngh1aa/Nova", now=NOW)

    assert result.inspection_complete is True
    assert result.evidence[0].provider == "netlify"
    assert result.evidence[0].source == "github-deployment-status"
    assert result.evidence[0].url == "https://example.netlify.app"


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

    observer = GitHubDeploymentIntegrationObserver(None, request_json=request, max_age_days=90)
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

    observer = GitHubDeploymentIntegrationObserver(None, request_json=request)
    result = observer.discover_repository("Ngh1aa/Nova", now=NOW)

    assert result.inspection_complete is True
    assert result.unknown_deployment_ids == (404,)
    assert result.evidence[0].provider == "unknown-external"

    assessment = assess_repository_policy_drift(
        "Ngh1aa/Nova",
        result.evidence,
        inspection_complete=True,
    )
    assert assessment.status == "DRIFT_ADDED_AND_REMOVED_PROVIDER"
    assert assessment.added_providers == ("unknown-external",)


def test_external_visibility_failure_is_unknown_not_safe() -> None:
    def request(path: str):
        raise OSError("network unavailable")

    observer = GitHubDeploymentIntegrationObserver(None, request_json=request)
    result = observer.discover_repository("Ngh1aa/Nova", now=NOW)

    assert result.inspection_complete is False
    assessment = assess_repository_policy_drift("Ngh1aa/Nova", (), inspection_complete=False)
    assert assessment.status == "UNKNOWN_POLICY_DRIFT"
    assert assessment.in_sync is False


def test_recent_external_vercel_evidence_can_satisfy_registry_without_static_marker() -> None:
    def request(path: str):
        return [
            {
                "id": 505,
                "creator": {"login": "vercel[bot]"},
                "environment": "Preview",
                "created_at": "2026-10-03T12:00:00Z",
            }
        ]

    observer = GitHubDeploymentIntegrationObserver(None, request_json=request)
    result = observer.discover_repository("Ngh1aa/Nova", now=NOW)
    assessment = assess_repository_policy_drift(
        "Ngh1aa/Nova",
        result.evidence,
        inspection_complete=result.inspection_complete,
    )

    assert assessment.status == "IN_SYNC"
    assert assessment.evidence_channels["vercel"] == ("external-observed",)


def test_recent_unregistered_external_provider_is_added_drift_even_when_vercel_is_present() -> None:
    def request(path: str):
        if path.endswith("/deployments?per_page=20"):
            return [
                {
                    "id": 606,
                    "creator": {"login": "vercel[bot]"},
                    "created_at": "2026-10-03T12:00:00Z",
                },
                {
                    "id": 607,
                    "creator": {"login": "netlify[bot]"},
                    "created_at": "2026-10-03T12:00:00Z",
                },
            ]
        raise AssertionError(path)

    observer = GitHubDeploymentIntegrationObserver(None, request_json=request)
    result = observer.discover_repository("Ngh1aa/Nova", now=NOW)
    assessment = assess_repository_policy_drift(
        "Ngh1aa/Nova",
        result.evidence,
        inspection_complete=True,
    )

    assert assessment.status == "DRIFT_ADDED_PROVIDER"
    assert assessment.added_providers == ("netlify",)


def test_registry_accepts_static_or_external_freshness_without_broadening_authority() -> None:
    nova = resolve_repository_policy("Ngh1aa/Nova")
    rule = nova.integration_freshness[0]
    assert rule.provider == "vercel"
    assert rule.evidence_channels == ("repository-static", "external-observed")
    assert nova.allowed_preview_providers == ("vercel",)
    assert nova.release_boundary.allow_merge is False
    assert nova.release_boundary.allow_production_deploy is False
    assert nova.release_boundary.allow_release is False


def test_p175_matrix_is_registry_derived() -> None:
    matrix = build_external_integration_matrix()
    assert [item["repository"] for item in matrix["include"]] == [
        policy.repository for policy in registered_repository_policies()
    ]
