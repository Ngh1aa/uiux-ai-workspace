from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from core.runtime.flow_os.repository_policy_drift import inspect_repository_policy_drift
from core.runtime.flow_os.repository_policy_registry import (
    REPOSITORY_POLICY_REGISTRY_VERSION,
    registered_repository_policies,
)


P174_REPORT_VERSION = "1.0"


def _slug(repository: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", repository.lower()).strip("-")
    return value or "repository"


def build_policy_drift_matrix() -> dict[str, list[dict[str, str]]]:
    """Build the monitored repository matrix directly from the canonical registry."""
    return {
        "include": [
            {
                "repository": policy.repository,
                "slug": _slug(policy.repository),
            }
            for policy in registered_repository_policies()
        ]
    }


def run_p174_policy_drift(
    *,
    repository: str,
    repo_root: Path | str,
    output_dir: Path | str,
) -> dict[str, Any]:
    assessment = inspect_repository_policy_drift(repository, repo_root)
    report = {
        "version": P174_REPORT_VERSION,
        "registry_version": REPOSITORY_POLICY_REGISTRY_VERSION,
        "repository": assessment.repository,
        "passed": assessment.in_sync,
        "assessment": assessment.to_dict(),
        "target_mutation": "NOT_PERFORMED",
        "target_branch_create_or_push": "NOT_PERFORMED",
        "target_pr_create_or_update": "NOT_PERFORMED",
        "merge": "NOT_PERFORMED",
        "production_deployment": "NOT_PERFORMED",
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report_path = output_path / f"p174-policy-drift-{_slug(assessment.repository)}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not assessment.in_sync:
        raise RuntimeError(f"P1.7.4 repository policy drift detected: {json.dumps(report, ensure_ascii=False)}")
    return report
