from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from core.runtime.flow_os.external_integration_discovery import (
    DEFAULT_EXTERNAL_EVIDENCE_MAX_AGE_DAYS,
    GitHubDeploymentIntegrationObserver,
)
from core.runtime.flow_os.external_side_effects import detect_static_integrations
from core.runtime.flow_os.provider_attestation import (
    CloudflarePagesProviderAttestor,
    NetlifyProviderAttestor,
    RenderProviderAttestor,
    RailwayProviderAttestor,
    SUPPORTED_PROVIDER_ATTESTORS,
    VercelProviderAttestor,
    assess_provider_attestation_coverage,
    resolve_canonical_integration_truth,
)
from core.runtime.flow_os.repository_policy_registry import (
    REPOSITORY_POLICY_REGISTRY_VERSION,
    registered_repository_policies,
    resolve_repository_policy,
)


P177_REPORT_VERSION = "1.0"


def _slug(repository: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", repository.lower()).strip("-")
    return value or "repository"


def build_multi_provider_attestation_matrix() -> dict[str, list[dict[str, str]]]:
    return {
        "include": [
            {"repository": policy.repository, "slug": _slug(policy.repository)}
            for policy in registered_repository_policies()
        ]
    }


def _default_attestor(
    provider: str,
    *,
    vercel_token: str | None,
    vercel_team_id: str | None,
    netlify_token: str | None,
    render_token: str | None,
    cloudflare_token: str | None,
    cloudflare_account_id: str | None,
    railway_token: str | None,
    railway_workspace_id: str | None,
):
    if provider == "vercel":
        return VercelProviderAttestor(vercel_token, team_id=vercel_team_id)
    if provider == "netlify":
        return NetlifyProviderAttestor(netlify_token)
    if provider == "render":
        return RenderProviderAttestor(render_token)
    if provider == "cloudflare":
        return CloudflarePagesProviderAttestor(
            cloudflare_token,
            account_id=cloudflare_account_id,
        )
    if provider == "railway":
        return RailwayProviderAttestor(
            railway_token,
            workspace_id=railway_workspace_id,
        )
    return None


def run_p177_multi_provider_attestation_truth(
    *,
    repository: str,
    repo_root: Path | str,
    output_dir: Path | str,
    github_token: str | None,
    vercel_token: str | None = None,
    vercel_team_id: str | None = None,
    netlify_token: str | None = None,
    render_token: str | None = None,
    cloudflare_token: str | None = None,
    cloudflare_account_id: str | None = None,
    railway_token: str | None = None,
    railway_workspace_id: str | None = None,
    max_age_days: int = DEFAULT_EXTERNAL_EVIDENCE_MAX_AGE_DAYS,
    github_observer: GitHubDeploymentIntegrationObserver | None = None,
    provider_attestors: Mapping[str, Any] | None = None,
    enforce_passed: bool = True,
) -> dict[str, Any]:
    """Resolve canonical integration truth with bounded multi-provider attestation.

    Only providers already registered for the target repository are queried.
    GitHub Pages remains covered by GitHub-native/static evidence and does not need
    a separate external credential. Missing provider credentials produce UNKNOWN
    attestation, never an invented configured/not-configured verdict.
    """

    policy = resolve_repository_policy(repository)
    root = Path(repo_root)
    static_complete = root.is_dir()
    static_evidence = detect_static_integrations(root) if static_complete else ()

    observer = github_observer or GitHubDeploymentIntegrationObserver(
        github_token,
        max_age_days=max_age_days,
    )
    external = observer.discover_repository(repository)

    coverage = assess_provider_attestation_coverage(policy.known_integration_providers)

    injected = {str(key).strip().lower(): value for key, value in dict(provider_attestors or {}).items()}
    attestations = {}
    for provider in policy.known_integration_providers:
        if provider not in SUPPORTED_PROVIDER_ATTESTORS:
            continue
        attestor = injected.get(provider) or _default_attestor(
            provider,
            vercel_token=vercel_token,
            vercel_team_id=vercel_team_id,
            netlify_token=netlify_token,
            render_token=render_token,
            cloudflare_token=cloudflare_token,
            cloudflare_account_id=cloudflare_account_id,
            railway_token=railway_token,
            railway_workspace_id=railway_workspace_id,
        )
        if attestor is not None:
            attestations[provider] = attestor.attest_repository(repository)

    all_evidence = [*static_evidence, *external.evidence]
    for attestation in attestations.values():
        all_evidence.extend(attestation.evidence)

    truth = resolve_canonical_integration_truth(
        repository,
        all_evidence,
        attestations=attestations,
        inspection_complete=static_complete and external.inspection_complete,
        inspection_channels=(
            "repository-static",
            "github-provider-native",
            *(("provider-attestation",) if attestations else ()),
        ),
    )

    report = {
        "version": P177_REPORT_VERSION,
        "registry_version": REPOSITORY_POLICY_REGISTRY_VERSION,
        "repository": truth.repository,
        "passed": truth.passed,
        "supported_provider_attestors": sorted(SUPPORTED_PROVIDER_ATTESTORS),
        "registered_integration_providers": list(policy.known_integration_providers),
        "provider_attestation_coverage": coverage.to_dict(),
        "static_inspection_complete": static_complete,
        "github_discovery": external.to_dict(),
        "provider_attestations": {
            provider: result.to_dict()
            for provider, result in sorted(attestations.items())
        },
        "canonical_integration_truth": truth.to_dict(),
        "credential_values_persisted": False,
        "target_mutation": "NOT_PERFORMED",
        "target_branch_create_or_push": "NOT_PERFORMED",
        "target_pr_create_or_update": "NOT_PERFORMED",
        "provider_mutation": "NOT_PERFORMED",
        "merge": "NOT_PERFORMED",
        "production_deployment": "NOT_PERFORMED",
        "release": "NOT_PERFORMED",
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report_path = output_path / f"p177-multi-provider-attestation-{_slug(truth.repository)}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if enforce_passed and not truth.passed:
        raise RuntimeError(
            "P1.7.7 canonical integration truth is not verified: "
            + json.dumps(report, ensure_ascii=False)
        )
    return report
