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
from core.runtime.flow_os.repository_policy_drift import assess_repository_policy_drift
from core.runtime.flow_os.repository_policy_registry import (
    REPOSITORY_POLICY_REGISTRY_VERSION,
    registered_repository_policies,
)


P175_REPORT_VERSION = "1.0"


def _slug(repository: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", repository.lower()).strip("-")
    return value or "repository"


def build_external_integration_matrix() -> dict[str, list[dict[str, str]]]:
    return {
        "include": [
            {"repository": policy.repository, "slug": _slug(policy.repository)}
            for policy in registered_repository_policies()
        ]
    }


def run_p175_external_integration_discovery(
    *,
    repository: str,
    repo_root: Path | str,
    output_dir: Path | str,
    token: str | None,
    max_age_days: int = DEFAULT_EXTERNAL_EVIDENCE_MAX_AGE_DAYS,
    observer: GitHubDeploymentIntegrationObserver | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    static_complete = root.is_dir()
    static_evidence = detect_static_integrations(root) if static_complete else ()

    deployment_observer = observer or GitHubDeploymentIntegrationObserver(
        token,
        max_age_days=max_age_days,
    )
    external = deployment_observer.discover_repository(repository)
    assessment = assess_repository_policy_drift(
        repository,
        (*static_evidence, *external.evidence),
        inspection_complete=static_complete and external.inspection_complete,
        inspected_channels=("repository-static", "github-provider-native"),
    )

    report = {
        "version": P175_REPORT_VERSION,
        "registry_version": REPOSITORY_POLICY_REGISTRY_VERSION,
        "repository": assessment.repository,
        "passed": assessment.in_sync,
        "static_inspection_complete": static_complete,
        "external_discovery": external.to_dict(),
        "assessment": assessment.to_dict(),
        "target_mutation": "NOT_PERFORMED",
        "target_branch_create_or_push": "NOT_PERFORMED",
        "target_pr_create_or_update": "NOT_PERFORMED",
        "merge": "NOT_PERFORMED",
        "production_deployment": "NOT_PERFORMED",
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report_path = output_path / f"p175-external-integration-{_slug(assessment.repository)}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not assessment.in_sync:
        raise RuntimeError(f"P1.7.5 external integration drift detected: {json.dumps(report, ensure_ascii=False)}")
    return report
