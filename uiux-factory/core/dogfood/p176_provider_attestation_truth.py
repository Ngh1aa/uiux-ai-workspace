from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from core.runtime.flow_os.external_integration_discovery import (
    DEFAULT_EXTERNAL_EVIDENCE_MAX_AGE_DAYS,
    GitHubDeploymentIntegrationObserver,
)
from core.runtime.flow_os.external_side_effects import detect_static_integrations
from core.runtime.flow_os.provider_attestation import (
    VercelProviderAttestor,
    resolve_canonical_integration_truth,
)
from core.runtime.flow_os.repository_policy_registry import (
    REPOSITORY_POLICY_REGISTRY_VERSION,
    registered_repository_policies,
    resolve_repository_policy,
)


P176_REPORT_VERSION = "1.0"


def _slug(repository: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", repository.lower()).strip("-")
    return value or "repository"


def build_provider_attestation_matrix() -> dict[str, list[dict[str, str]]]:
    return {
        "include": [
            {"repository": policy.repository, "slug": _slug(policy.repository)}
            for policy in registered_repository_policies()
        ]
    }


def run_p176_provider_attestation_truth(
    *,
    repository: str,
    repo_root: Path | str,
    output_dir: Path | str,
    github_token: str | None,
    vercel_token: str | None,
    vercel_team_id: str | None = None,
    max_age_days: int = DEFAULT_EXTERNAL_EVIDENCE_MAX_AGE_DAYS,
    github_observer: GitHubDeploymentIntegrationObserver | None = None,
    vercel_attestor: VercelProviderAttestor | None = None,
) -> dict[str, Any]:
    """Resolve canonical integration truth from static, GitHub and provider-native evidence.

    This function is read-only against the target repository and external providers.
    Provider credentials are invocation inputs only and are never serialized.
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

    attestations = {}
    if "vercel" in policy.known_integration_providers:
        attestor = vercel_attestor or VercelProviderAttestor(
            vercel_token,
            team_id=vercel_team_id,
        )
        attestations["vercel"] = attestor.attest_repository(repository)

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
        "version": P176_REPORT_VERSION,
        "registry_version": REPOSITORY_POLICY_REGISTRY_VERSION,
        "repository": truth.repository,
        "passed": truth.passed,
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
    report_path = output_path / f"p176-provider-attestation-{_slug(truth.repository)}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not truth.passed:
        raise RuntimeError(
            "P1.7.6 canonical integration truth is not verified: "
            + json.dumps(report, ensure_ascii=False)
        )
    return report
