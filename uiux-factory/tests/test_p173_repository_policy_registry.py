from __future__ import annotations

import inspect

import pytest

from core.dogfood.p171_authenticated_real_runner import DOGFOOD_PROFILES, run_authenticated_dogfood
from core.dogfood.p173_repository_policy_registry import DOGFOOD_TARGETS
from core.runtime.flow_os.external_side_effects import ExternalSideEffectEvidence, PreviewPolicy
from core.runtime.flow_os.repository_policy_registry import (
    REPOSITORY_POLICIES,
    ReleaseBoundary,
    RepositoryPolicyBroadeningError,
    RepositoryPolicyOverride,
    assess_repository_governance,
    repository_policy_integration_evidence,
    resolve_repository_policy,
)


CANONICAL_REPOSITORIES = {
    "Ngh1aa/Nova",
    "Ngh1aa/Lumen",
    "Ngh1aa/cennext-b2b-prototype",
    "Ngh1aa/LuxRoom",
}


def _evidence(provider: str) -> ExternalSideEffectEvidence:
    return ExternalSideEffectEvidence(
        provider=provider,
        effect="pr-preview",
        source="github-pr-comment",
        state="observed",
        url=f"https://github.com/example/repo/pull/1#{provider}",
        detail=f"{provider} observed",
    )


def test_registry_has_exactly_the_four_canonical_dogfood_repositories() -> None:
    assert {policy.repository for policy in REPOSITORY_POLICIES.values()} == CANONICAL_REPOSITORIES
    assert len(REPOSITORY_POLICIES) == 4


def test_repository_lookup_is_case_insensitive_and_preserves_canonical_name() -> None:
    policy = resolve_repository_policy("https://github.com/ngh1AA/lUxRoOm.git")
    assert policy.repository == "Ngh1aa/LuxRoom"
    assert policy.registered is True


def test_preview_policy_matrix_is_repository_owned() -> None:
    for repository in ("Ngh1aa/Nova", "Ngh1aa/cennext-b2b-prototype", "Ngh1aa/LuxRoom"):
        policy = resolve_repository_policy(repository)
        assert policy.preview_policy == PreviewPolicy.PR_PREVIEW_ALLOWED.value
        assert policy.allowed_preview_providers == ("vercel",)
        assert policy.known_integration_providers == ("vercel",)
        assert set(policy.mutation_scope) == {"branch-create", "branch-push", "pr-create", "pr-update"}

    lumen = resolve_repository_policy("Ngh1aa/Lumen")
    assert lumen.preview_policy == PreviewPolicy.ZERO_DEPLOY_STRICT.value
    assert lumen.allowed_preview_providers == ()
    assert lumen.known_integration_providers == ("vercel", "github-pages")
    assert lumen.mutation_scope == ()


def test_known_integrations_are_evidence_not_permission() -> None:
    lumen = resolve_repository_policy("Ngh1aa/Lumen")
    evidence = repository_policy_integration_evidence(lumen)
    assert {item.provider for item in evidence} == {"vercel", "github-pages"}
    assert all(item.state == "configured" for item in evidence)
    assessment = assess_repository_governance(
        "Ngh1aa/Lumen",
        (),
        inspection_complete=True,
        required_mutations=("branch-create",),
    )
    assert assessment.status == "BLOCKED_EXTERNAL_SIDE_EFFECT"
    assert assessment.mutation_allowed is False


def test_live_dogfood_expected_provider_footprint_matches_registry_exactly() -> None:
    expected = {
        "Ngh1aa/Nova": {"vercel"},
        "Ngh1aa/Lumen": {"vercel", "github-pages"},
        "Ngh1aa/cennext-b2b-prototype": {"vercel"},
        "Ngh1aa/LuxRoom": {"vercel"},
    }
    assert {target.repository: set(target.expected_providers) for target in DOGFOOD_TARGETS} == expected
    for repository, providers in expected.items():
        assert set(resolve_repository_policy(repository).known_integration_providers) == providers


def test_vercel_is_allowed_for_registered_preview_repositories() -> None:
    for repository in ("Ngh1aa/Nova", "Ngh1aa/cennext-b2b-prototype", "Ngh1aa/LuxRoom"):
        assessment = assess_repository_governance(
            repository,
            (_evidence("vercel"),),
            inspection_complete=True,
            required_mutations=("branch-create", "branch-push", "pr-create"),
        )
        assert assessment.status == "PREVIEW_OBSERVED"
        assert assessment.mutation_allowed is True


def test_unlisted_provider_blocks_even_when_pr_preview_is_generally_allowed() -> None:
    assessment = assess_repository_governance(
        "Ngh1aa/Nova",
        (_evidence("netlify"),),
        inspection_complete=True,
        required_mutations=("branch-create",),
    )
    assert assessment.status == "BLOCKED_PROVIDER_NOT_ALLOWED"
    assert assessment.mutation_allowed is False
    assert "netlify" in assessment.reason


def test_unknown_repository_fails_closed_even_after_clean_inspection() -> None:
    policy = resolve_repository_policy("Ngh1aa/not-registered")
    assert policy.registered is False
    assert policy.preview_policy == PreviewPolicy.ZERO_DEPLOY_STRICT.value
    assert policy.mutation_scope == ()
    assessment = assess_repository_governance(
        "Ngh1aa/not-registered",
        (),
        inspection_complete=True,
        required_mutations=("branch-create",),
    )
    assert assessment.status == "BLOCKED_UNREGISTERED_REPOSITORY"
    assert assessment.mutation_allowed is False


def test_mutation_scope_is_enforced_after_side_effect_policy() -> None:
    assessment = assess_repository_governance(
        "Ngh1aa/Nova",
        (_evidence("vercel"),),
        inspection_complete=True,
        required_mutations=("merge",),
    )
    assert assessment.status == "BLOCKED_MUTATION_SCOPE"
    assert assessment.mutation_allowed is False


def test_release_boundary_denies_merge_production_deploy_and_release_for_all_registered_repos() -> None:
    for repository in CANONICAL_REPOSITORIES:
        boundary = resolve_repository_policy(repository).release_boundary
        assert boundary.allows("merge") is False
        assert boundary.allows("production-deploy") is False
        assert boundary.allows("release") is False


def test_runtime_override_may_narrow_preview_policy_but_never_broaden_it() -> None:
    narrowed = resolve_repository_policy(
        "Ngh1aa/Nova",
        override=RepositoryPolicyOverride(preview_policy=PreviewPolicy.ZERO_DEPLOY_STRICT.value),
    )
    assert narrowed.preview_policy == PreviewPolicy.ZERO_DEPLOY_STRICT.value
    with pytest.raises(RepositoryPolicyBroadeningError):
        resolve_repository_policy(
            "Ngh1aa/Lumen",
            override=RepositoryPolicyOverride(preview_policy=PreviewPolicy.PR_PREVIEW_ALLOWED.value),
        )


def test_runtime_override_provider_and_mutation_scope_may_only_shrink() -> None:
    narrowed = resolve_repository_policy(
        "Ngh1aa/Nova",
        override=RepositoryPolicyOverride(allowed_preview_providers=(), mutation_scope=("branch-create",)),
    )
    assert narrowed.allowed_preview_providers == ()
    assert narrowed.mutation_scope == ("branch-create",)
    with pytest.raises(RepositoryPolicyBroadeningError):
        resolve_repository_policy(
            "Ngh1aa/Nova",
            override=RepositoryPolicyOverride(allowed_preview_providers=("vercel", "netlify")),
        )
    with pytest.raises(RepositoryPolicyBroadeningError):
        resolve_repository_policy(
            "Ngh1aa/Nova",
            override=RepositoryPolicyOverride(mutation_scope=("branch-create", "merge")),
        )


def test_runtime_override_release_boundary_cannot_widen_authority() -> None:
    with pytest.raises(RepositoryPolicyBroadeningError):
        resolve_repository_policy(
            "Ngh1aa/LuxRoom",
            override=RepositoryPolicyOverride(release_boundary=ReleaseBoundary(allow_merge=True)),
        )


def test_policy_serialization_is_stable_and_explicit() -> None:
    first = resolve_repository_policy("Ngh1aa/LuxRoom").to_dict()
    second = resolve_repository_policy("ngh1aa/luxroom").to_dict()
    assert first == second
    assert first["preview_policy"] == "pr-preview-allowed"
    assert first["release_boundary"] == {
        "allow_merge": False,
        "allow_production_deploy": False,
        "allow_release": False,
    }


def test_p171_profile_no_longer_owns_preview_policy() -> None:
    profile = DOGFOOD_PROFILES["luxroom-cart-total-live-region"]
    assert not hasattr(profile, "preview_policy")
    policy = resolve_repository_policy(profile.repository)
    assert policy.preview_policy == PreviewPolicy.PR_PREVIEW_ALLOWED.value
    assert "external PR preview side effects are allowed" in profile.pr_body
    assert "no production deploy/release" in profile.pr_body


def test_p171_repository_policy_preflight_stays_before_transaction_construction() -> None:
    source = inspect.getsource(run_authenticated_dogfood)
    governance_index = source.index("assess_repository_governance(")
    transaction_index = source.index("GitHubTransactionConfig(")
    assert governance_index < transaction_index