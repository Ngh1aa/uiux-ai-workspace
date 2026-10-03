from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.runtime.flow_os.external_side_effects import (
    EXTERNAL_SIDE_EFFECT_VERSION,
    GitHubExternalSideEffectObserver,
    PreviewPolicy,
    assess_external_side_effects,
)


P172_REPORT_VERSION = "1.0"


def _branch_sha(observer: GitHubExternalSideEffectObserver, repository: str, branch: str) -> str:
    payload = observer._request(f"/repos/{repository}/branches/{branch}")
    if not isinstance(payload, dict):
        raise RuntimeError("branch inspection returned a non-object payload")
    commit = payload.get("commit") or {}
    sha = str(commit.get("sha") or "")
    if not sha:
        raise RuntimeError(f"branch inspection returned no SHA for {repository}:{branch}")
    return sha


def run_p172_live_dogfood(
    *,
    repository: str,
    pr_number: int,
    github_token: str,
    output_dir: Path | str,
    base_branch: str = "main",
) -> dict[str, Any]:
    if not github_token.strip():
        raise ValueError("P1.7.2 live governance dogfood requires a GitHub token")
    observer = GitHubExternalSideEffectObserver(github_token)
    base_sha_before = _branch_sha(observer, repository, base_branch)
    evidence, inspection_complete = observer.observe_pull_request(repository, pr_number)

    preview_allowed = assess_external_side_effects(
        repository,
        PreviewPolicy.PR_PREVIEW_ALLOWED,
        evidence,
        inspection_complete=inspection_complete,
    )
    zero_deploy_strict = assess_external_side_effects(
        repository,
        PreviewPolicy.ZERO_DEPLOY_STRICT,
        evidence,
        inspection_complete=inspection_complete,
    )
    base_sha_after = _branch_sha(observer, repository, base_branch)

    providers = {item.provider for item in evidence}
    passed = all(
        [
            inspection_complete,
            "vercel" in providers,
            preview_allowed.status == "PREVIEW_OBSERVED",
            preview_allowed.mutation_allowed,
            zero_deploy_strict.status == "BLOCKED_EXTERNAL_SIDE_EFFECT",
            not zero_deploy_strict.mutation_allowed,
            base_sha_before == base_sha_after,
        ]
    )
    report = {
        "version": P172_REPORT_VERSION,
        "governance_version": EXTERNAL_SIDE_EFFECT_VERSION,
        "passed": passed,
        "repository": repository,
        "pr_number": int(pr_number),
        "base_branch": base_branch,
        "base_sha_before": base_sha_before,
        "base_sha_after": base_sha_after,
        "main_unchanged": base_sha_before == base_sha_after,
        "inspection_complete": inspection_complete,
        "providers_observed": sorted(providers),
        "preview_allowed": preview_allowed.to_dict(),
        "zero_deploy_strict": zero_deploy_strict.to_dict(),
        "target_mutation": "NOT_PERFORMED",
        "merge": "NOT_PERFORMED",
        "deployment": "NOT_PERFORMED_BY_DOGFOOD",
    }
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "p172-external-side-effect-governance-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if not passed:
        raise RuntimeError(f"P1.7.2 live governance dogfood failed: {json.dumps(report, ensure_ascii=False)}")
    return report
