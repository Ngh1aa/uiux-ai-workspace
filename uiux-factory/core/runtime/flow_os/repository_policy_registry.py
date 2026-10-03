from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any, Iterable

from core.runtime.flow_os.external_side_effects import (
    ExternalSideEffectBlocked,
    ExternalSideEffectEvidence,
    PreviewPolicy,
    assess_external_side_effects,
)


REPOSITORY_POLICY_REGISTRY_VERSION = "1.2"
POLICY_SOURCE = "repository-policy-registry"


class RepositoryPolicyError(RuntimeError):
    """Raised when repository governance cannot authorize an operation."""


class RepositoryPolicyBroadeningError(ValueError):
    """Raised when a runtime override attempts to broaden canonical repository authority."""


@dataclass(frozen=True)
class ReleaseBoundary:
    allow_merge: bool = False
    allow_production_deploy: bool = False
    allow_release: bool = False

    def to_dict(self) -> dict[str, bool]:
        return asdict(self)

    def allows(self, action: str) -> bool:
        mapping = {
            "merge": self.allow_merge,
            "production-deploy": self.allow_production_deploy,
            "release": self.allow_release,
        }
        if action not in mapping:
            raise ValueError(f"unknown release action: {action}")
        return mapping[action]


@dataclass(frozen=True)
class IntegrationFreshnessRule:
    provider: str
    evidence_channels: tuple[str, ...] = ("repository-static",)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "evidence_channels": list(self.evidence_channels),
        }


@dataclass(frozen=True)
class RepositoryPolicy:
    repository: str
    preview_policy: str
    allowed_preview_providers: tuple[str, ...]
    known_integration_providers: tuple[str, ...]
    mutation_scope: tuple[str, ...]
    release_boundary: ReleaseBoundary
    registered: bool = True
    source: str = POLICY_SOURCE
    rationale: str = ""
    integration_freshness: tuple[IntegrationFreshnessRule, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["release_boundary"] = self.release_boundary.to_dict()
        payload["allowed_preview_providers"] = list(self.allowed_preview_providers)
        payload["known_integration_providers"] = list(self.known_integration_providers)
        payload["mutation_scope"] = list(self.mutation_scope)
        payload["integration_freshness"] = [rule.to_dict() for rule in self.integration_freshness]
        return payload


@dataclass(frozen=True)
class RepositoryPolicyOverride:
    preview_policy: str | None = None
    allowed_preview_providers: tuple[str, ...] | None = None
    mutation_scope: tuple[str, ...] | None = None
    release_boundary: ReleaseBoundary | None = None


@dataclass(frozen=True)
class RepositoryGovernanceAssessment:
    version: str
    registry_version: str
    repository: str
    registered: bool
    policy: RepositoryPolicy
    status: str
    mutation_allowed: bool
    required_mutations: tuple[str, ...]
    external_side_effect: dict[str, Any]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "registry_version": self.registry_version,
            "repository": self.repository,
            "registered": self.registered,
            "policy": self.policy.to_dict(),
            "status": self.status,
            "mutation_allowed": self.mutation_allowed,
            "required_mutations": list(self.required_mutations),
            "external_side_effect": self.external_side_effect,
            "reason": self.reason,
        }

    def require_mutation_allowed(self) -> None:
        if not self.mutation_allowed:
            raise ExternalSideEffectBlocked(self.reason)


_PR_MUTATION_SCOPE = ("branch-create", "branch-push", "pr-create", "pr-update")
_NO_RELEASE = ReleaseBoundary()
_STATIC = ("repository-static",)
_STATIC_OR_EXTERNAL = ("repository-static", "external-observed")\n_STATIC_OR_EXTERNAL = ("repository-static", "external-observed")


REPOSITORY_POLICIES: dict[str, RepositoryPolicy] = {
    "ngh1aa/nova": RepositoryPolicy(
        repository="Ngh1aa/Nova",
        preview_policy=PreviewPolicy.PR_PREVIEW_ALLOWED.value,
        allowed_preview_providers=("vercel",),
        known_integration_providers=("vercel",),
        mutation_scope=_PR_MUTATION_SCOPE,
        release_boundary=_NO_RELEASE,
        rationale="Nova uses Vercel PR previews as review evidence; merge and production release remain owner-controlled.",
        integration_freshness=(IntegrationFreshnessRule("vercel", _STATIC_OR_EXTERNAL),),
    ),
    "ngh1aa/lumen": RepositoryPolicy(
        repository="Ngh1aa/Lumen",
        preview_policy=PreviewPolicy.ZERO_DEPLOY_STRICT.value,
        allowed_preview_providers=(),
        known_integration_providers=("vercel", "github-pages"),
        mutation_scope=(),
        release_boundary=_NO_RELEASE,
        rationale="Lumen has Vercel configuration and deploys GitHub Pages from main; Factory read-only review must not create remote mutations that could cross either external deployment boundary.",
        integration_freshness=(
            IntegrationFreshnessRule("vercel", _STATIC_OR_EXTERNAL),
            IntegrationFreshnessRule("github-pages", _STATIC_OR_EXTERNAL),
        ),
    ),
    "ngh1aa/cennext-b2b-prototype": RepositoryPolicy(
        repository="Ngh1aa/cennext-b2b-prototype",
        preview_policy=PreviewPolicy.PR_PREVIEW_ALLOWED.value,
        allowed_preview_providers=("vercel",),
        known_integration_providers=("vercel",),
        mutation_scope=_PR_MUTATION_SCOPE,
        release_boundary=_NO_RELEASE,
        rationale="CENNEXT has Vercel review previews; PR mutation is allowed while merge and production release remain owner-controlled.",
        integration_freshness=(IntegrationFreshnessRule("vercel", _STATIC_OR_EXTERNAL),),
    ),
    "ngh1aa/luxroom": RepositoryPolicy(
        repository="Ngh1aa/LuxRoom",
        preview_policy=PreviewPolicy.PR_PREVIEW_ALLOWED.value,
        allowed_preview_providers=("vercel",),
        known_integration_providers=("vercel",),
        mutation_scope=_PR_MUTATION_SCOPE,
        release_boundary=_NO_RELEASE,
        rationale="LuxRoom P1.7.2 dogfood proved Vercel PR preview side effects; those previews are allowed and evidence-backed only.",
        integration_freshness=(IntegrationFreshnessRule("vercel", _STATIC_OR_EXTERNAL),),
    ),
}


def _normalize_repository(repository: str) -> str:
    normalized = repository.strip().strip("/").lower()
    if normalized.startswith("https://github.com/"):
        normalized = normalized.removeprefix("https://github.com/")
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    return normalized


def _canonical_tuple(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(value).strip().lower() for value in values if str(value).strip()))


def registered_repository_policies() -> tuple[RepositoryPolicy, ...]:
    """Return the canonical registered policy set in stable registry order."""
    return tuple(policy for policy in REPOSITORY_POLICIES.values() if policy.registered)


def _apply_override(policy: RepositoryPolicy, override: RepositoryPolicyOverride) -> RepositoryPolicy:
    preview_policy = policy.preview_policy
    if override.preview_policy is not None:
        requested = PreviewPolicy(override.preview_policy).value
        if policy.preview_policy == PreviewPolicy.ZERO_DEPLOY_STRICT.value and requested != policy.preview_policy:
            raise RepositoryPolicyBroadeningError("repository override cannot broaden zero-deploy-strict to PR-preview-allowed")
        preview_policy = requested

    allowed_providers = policy.allowed_preview_providers
    if override.allowed_preview_providers is not None:
        requested_providers = _canonical_tuple(override.allowed_preview_providers)
        if not set(requested_providers).issubset(set(policy.allowed_preview_providers)):
            raise RepositoryPolicyBroadeningError("repository override may only narrow allowed preview providers")
        allowed_providers = requested_providers

    mutation_scope = policy.mutation_scope
    if override.mutation_scope is not None:
        requested_scope = _canonical_tuple(override.mutation_scope)
        if not set(requested_scope).issubset(set(policy.mutation_scope)):
            raise RepositoryPolicyBroadeningError("repository override may only narrow mutation scope")
        mutation_scope = requested_scope

    release_boundary = policy.release_boundary
    if override.release_boundary is not None:
        requested_release = override.release_boundary
        if (
            (requested_release.allow_merge and not policy.release_boundary.allow_merge)
            or (requested_release.allow_production_deploy and not policy.release_boundary.allow_production_deploy)
            or (requested_release.allow_release and not policy.release_boundary.allow_release)
        ):
            raise RepositoryPolicyBroadeningError("repository override cannot broaden the release boundary")
        release_boundary = requested_release

    return replace(
        policy,
        preview_policy=preview_policy,
        allowed_preview_providers=allowed_providers,
        mutation_scope=mutation_scope,
        release_boundary=release_boundary,
        source=f"{policy.source}+runtime-narrowing",
    )


def resolve_repository_policy(
    repository: str,
    *,
    override: RepositoryPolicyOverride | None = None,
) -> RepositoryPolicy:
    key = _normalize_repository(repository)
    policy = REPOSITORY_POLICIES.get(key)
    if policy is None:
        canonical = repository.strip().removesuffix(".git") or "unknown"
        policy = RepositoryPolicy(
            repository=canonical,
            preview_policy=PreviewPolicy.ZERO_DEPLOY_STRICT.value,
            allowed_preview_providers=(),
            known_integration_providers=(),
            mutation_scope=(),
            release_boundary=_NO_RELEASE,
            registered=False,
            source="repository-policy-registry:unregistered-fail-closed",
            rationale="Unregistered repositories receive no remote mutation or release authority.",
            integration_freshness=(),
        )
    return _apply_override(policy, override) if override is not None else policy


def repository_policy_integration_evidence(policy: RepositoryPolicy) -> tuple[ExternalSideEffectEvidence, ...]:
    evidence: list[ExternalSideEffectEvidence] = []
    for provider in policy.known_integration_providers:
        effect = "deployment" if provider == "github-pages" else "pr-preview"
        evidence.append(
            ExternalSideEffectEvidence(
                provider=provider,
                effect=effect,
                source=POLICY_SOURCE,
                state="configured",
                detail=f"{provider} is registered as a known repository integration; registration is evidence, not permission.",
            )
        )
    return tuple(evidence)


def assess_repository_governance(
    repository: str,
    evidence: Iterable[ExternalSideEffectEvidence],
    *,
    inspection_complete: bool,
    required_mutations: Iterable[str] = (),
    override: RepositoryPolicyOverride | None = None,
) -> RepositoryGovernanceAssessment:
    policy = resolve_repository_policy(repository, override=override)
    required = _canonical_tuple(required_mutations)
    combined_evidence = (*repository_policy_integration_evidence(policy), *tuple(evidence))
    external = assess_external_side_effects(
        policy.repository,
        policy.preview_policy,
        combined_evidence,
        inspection_complete=inspection_complete,
    )

    if not policy.registered:
        status = "BLOCKED_UNREGISTERED_REPOSITORY"
        allowed = False
        reason = "Repository is not registered; Factory fails closed before any remote mutation."
    elif not external.mutation_allowed:
        status = external.status
        allowed = False
        reason = external.reason
    else:
        observed_providers = {item.provider for item in combined_evidence}
        unexpected = sorted(observed_providers - set(policy.allowed_preview_providers))
        if unexpected:
            status = "BLOCKED_PROVIDER_NOT_ALLOWED"
            allowed = False
            reason = f"Repository policy does not allow external provider(s): {', '.join(unexpected)}"
        else:
            missing_mutations = sorted(set(required) - set(policy.mutation_scope))
            if missing_mutations:
                status = "BLOCKED_MUTATION_SCOPE"
                allowed = False
                reason = f"Repository policy does not authorize mutation(s): {', '.join(missing_mutations)}"
            else:
                status = external.status
                allowed = True
                reason = external.reason

    return RepositoryGovernanceAssessment(
        version="1.0",
        registry_version=REPOSITORY_POLICY_REGISTRY_VERSION,
        repository=policy.repository,
        registered=policy.registered,
        policy=policy,
        status=status,
        mutation_allowed=allowed,
        required_mutations=required,
        external_side_effect=external.to_dict(),
        reason=reason,
    )
