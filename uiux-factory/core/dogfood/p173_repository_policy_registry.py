from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.runtime.flow_os.external_side_effects import (
    GitHubExternalSideEffectObserver,
    detect_static_integrations,
)
from core.runtime.flow_os.repository_policy_registry import (
    REPOSITORY_POLICY_REGISTRY_VERSION,
    assess_repository_governance,
    resolve_repository_policy,
)


P173_REPORT_VERSION = "1.1"


@dataclass(frozen=True)
class RepositoryDogfoodTarget:
    repository: str
    checkout_dir: str
    expected_providers: tuple[str, ...]
    expected_status: str
    evidence_pr_number: int | None = None
    base_branch: str = "main"


DOGFOOD_TARGETS: tuple[RepositoryDogfoodTarget, ...] = (
    RepositoryDogfoodTarget(
        repository="Ngh1aa/Nova",
        checkout_dir="nova",
        expected_providers=("vercel",),
        expected_status="PREVIEW_OBSERVED",
        evidence_pr_number=73,
    ),
    RepositoryDogfoodTarget(
        repository="Ngh1aa/Lumen",
        checkout_dir="lumen",
        expected_providers=("github-pages", "vercel"),
        expected_status="BLOCKED_EXTERNAL_SIDE_EFFECT",
    ),
    RepositoryDogfoodTarget(
        repository="Ngh1aa/cennext-b2b-prototype",
        checkout_dir="cennext",
        expected_providers=("vercel",),
        expected_status="PREVIEW_OBSERVED",
        evidence_pr_number=8,
    ),
    RepositoryDogfoodTarget(
        repository="Ngh1aa/LuxRoom",
        checkout_dir="luxroom",
        expected_providers=("vercel",),
        expected_status="PREVIEW_OBSERVED",
        evidence_pr_number=24,
    ),
)


def _branch_sha(observer: GitHubExternalSideEffectObserver, repository: str, branch: str) -> str:
    payload = observer._request(f"/repos/{repository}/branches/{branch}")
    if not isinstance(payload, dict):
        raise RuntimeError(f"branch inspection returned a non-object payload for {repository}")
    sha = str(((payload.get("commit") or {}).get("sha")) or "")
    if not sha:
        raise RuntimeError(f"branch inspection returned no SHA for {repository}:{branch}")
    return sha


def run_p173_live_dogfood(
    *,
    github_token: str,
    target_root: Path | str,
    output_dir: Path | str,
) -> dict[str, Any]:
    if not github_token.strip():
        raise ValueError("P1.7.3 live repository-policy dogfood requires a GitHub token")

    target_root = Path(target_root)
    observer = GitHubExternalSideEffectObserver(github_token)
    repo_reports: list[dict[str, Any]] = []

    for target in DOGFOOD_TARGETS:
        checkout = target_root / target.checkout_dir
        if not checkout.is_dir():
            raise FileNotFoundError(f"P1.7.3 target checkout missing: {checkout}")

        policy = resolve_repository_policy(target.repository)
        base_sha_before = _branch_sha(observer, target.repository, target.base_branch)
        static_evidence = detect_static_integrations(checkout)
        pr_evidence = ()
        pr_inspection_complete = True
        if target.evidence_pr_number is not None:
            pr_evidence, pr_inspection_complete = observer.observe_pull_request(
                target.repository,
                target.evidence_pr_number,
            )
        combined_evidence = (*static_evidence, *pr_evidence)
        governance = assess_repository_governance(
            target.repository,
            combined_evidence,
            inspection_complete=pr_inspection_complete,
            required_mutations=("branch-create", "branch-push", "pr-create"),
        )
        base_sha_after = _branch_sha(observer, target.repository, target.base_branch)

        providers = tuple(sorted({item.provider for item in combined_evidence} | set(policy.known_integration_providers)))
        expected_providers = tuple(sorted(target.expected_providers))
        registered_providers = tuple(sorted(policy.known_integration_providers))
        preview_expected = policy.preview_policy == "pr-preview-allowed"
        target_passed = all(
            [
                policy.registered,
                pr_inspection_complete,
                providers == expected_providers,
                registered_providers == expected_providers,
                governance.status == target.expected_status,
                governance.mutation_allowed is preview_expected,
                base_sha_before == base_sha_after,
            ]
        )
        repo_reports.append(
            {
                "repository": target.repository,
                "base_branch": target.base_branch,
                "base_sha_before": base_sha_before,
                "base_sha_after": base_sha_after,
                "main_unchanged": base_sha_before == base_sha_after,
                "evidence_pr_number": target.evidence_pr_number,
                "inspection_complete": pr_inspection_complete,
                "providers": list(providers),
                "expected_providers": list(expected_providers),
                "registered_providers": list(registered_providers),
                "provider_footprint_matches_registry": providers == expected_providers == registered_providers,
                "static_evidence": [item.to_dict() for item in static_evidence],
                "pr_evidence": [item.to_dict() for item in pr_evidence],
                "policy": policy.to_dict(),
                "governance": governance.to_dict(),
                "expected_status": target.expected_status,
                "passed": target_passed,
            }
        )

    passed = len(repo_reports) == len(DOGFOOD_TARGETS) and all(item["passed"] for item in repo_reports)
    report = {
        "version": P173_REPORT_VERSION,
        "registry_version": REPOSITORY_POLICY_REGISTRY_VERSION,
        "passed": passed,
        "repositories": repo_reports,
        "target_mutation": "NOT_PERFORMED",
        "target_branch_create_or_push": "NOT_PERFORMED",
        "target_pr_create_or_update": "NOT_PERFORMED",
        "merge": "NOT_PERFORMED",
        "production_deployment": "NOT_PERFORMED_BY_DOGFOOD",
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    (output_path / "p173-repository-policy-registry-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if not passed:
        raise RuntimeError(f"P1.7.3 repository-policy dogfood failed: {json.dumps(report, ensure_ascii=False)}")
    return report