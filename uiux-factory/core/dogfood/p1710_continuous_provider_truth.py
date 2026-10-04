from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from core.dogfood.p177_multi_provider_attestation_truth import (
    build_multi_provider_attestation_matrix,
    run_p177_multi_provider_attestation_truth,
)
from core.runtime.flow_os.continuous_provider_truth import (
    assess_continuous_provider_truth_payload,
)


P1710_REPORT_VERSION = "1.0"


def _slug(repository: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", repository.lower()).strip("-")
    return value or "repository"


def build_continuous_provider_truth_matrix() -> dict[str, list[dict[str, str]]]:
    return build_multi_provider_attestation_matrix()


def run_p1710_continuous_provider_truth(
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
    max_age_days: int = 90,
    github_observer: Any | None = None,
    provider_attestors: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run scheduled provider truth with credential-aware monitoring semantics.

    Canonical truth is still computed fail-closed by P1.7.7. This wrapper changes
    only workflow severity: missing opt-in credentials are recorded as degraded
    monitoring coverage instead of making a scheduled workflow red. All drift,
    conflicts, non-credential evidence gaps and configured-credential visibility
    failures remain blocking.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    p177_report = run_p177_multi_provider_attestation_truth(
        repository=repository,
        repo_root=repo_root,
        output_dir=output_path,
        github_token=github_token,
        vercel_token=vercel_token,
        vercel_team_id=vercel_team_id,
        netlify_token=netlify_token,
        render_token=render_token,
        cloudflare_token=cloudflare_token,
        cloudflare_account_id=cloudflare_account_id,
        railway_token=railway_token,
        railway_workspace_id=railway_workspace_id,
        max_age_days=max_age_days,
        github_observer=github_observer,
        provider_attestors=provider_attestors,
        enforce_passed=False,
    )

    canonical_payload = p177_report.get("canonical_integration_truth")
    if not isinstance(canonical_payload, Mapping):
        raise RuntimeError("P1.7.10 requires a serialized canonical integration truth result")

    assessment = assess_continuous_provider_truth_payload(canonical_payload)
    report = {
        "version": P1710_REPORT_VERSION,
        "repository": assessment.repository,
        "monitoring": assessment.to_dict(),
        "canonical_truth_passed": bool(p177_report.get("passed")),
        "canonical_integration_truth": canonical_payload,
        "provider_attestation_coverage": p177_report.get("provider_attestation_coverage"),
        "provider_attestations": p177_report.get("provider_attestations"),
        "credential_values_persisted": False,
        "missing_optional_credentials_are_blocking": False,
        "configured_credential_visibility_failures_are_blocking": True,
        "target_mutation": "NOT_PERFORMED",
        "provider_mutation": "NOT_PERFORMED",
        "deploy": "NOT_PERFORMED",
        "merge": "NOT_PERFORMED",
        "release": "NOT_PERFORMED",
    }

    report_path = output_path / f"p1710-continuous-provider-truth-{_slug(repository)}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if assessment.blocking:
        raise RuntimeError(
            "P1.7.10 continuous provider truth requires action: "
            + json.dumps(report, ensure_ascii=False)
        )
    return report
