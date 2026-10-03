from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from core.runtime.flow_os.external_side_effects import ExternalSideEffectEvidence, detect_static_integrations
from core.runtime.flow_os.repository_policy_registry import (
    REPOSITORY_POLICY_REGISTRY_VERSION,
    IntegrationFreshnessRule,
    resolve_repository_policy,
)


POLICY_DRIFT_VERSION = "1.1"
REPOSITORY_STATIC_CHANNEL = "repository-static"
GITHUB_DEPLOYMENT_CHANNEL = "github-deployment"
GITHUB_PR_COMMENT_CHANNEL = "github-pr-comment"
GENERIC_EXTERNAL_CHANNEL = "external-observed"


class RepositoryPolicyDriftError(RuntimeError):
    """Raised when the repository integration footprint no longer matches its canonical policy."""


@dataclass(frozen=True)
class RepositoryPolicyDriftAssessment:
    version: str
    registry_version: str
    repository: str
    registered: bool
    status: str
    in_sync: bool
    inspection_complete: bool
    inspected_channels: tuple[str, ...]
    detected_providers: tuple[str, ...]
    registered_providers: tuple[str, ...]
    added_providers: tuple[str, ...]
    removed_providers: tuple[str, ...]
    unverifiable_providers: tuple[str, ...]
    evidence_channels: dict[str, tuple[str, ...]]
    evidence: tuple[ExternalSideEffectEvidence, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "registry_version": self.registry_version,
            "repository": self.repository,
            "registered": self.registered,
            "status": self.status,
            "in_sync": self.in_sync,
            "inspection_complete": self.inspection_complete,
            "inspected_channels": list(self.inspected_channels),
            "detected_providers": list(self.detected_providers),
            "registered_providers": list(self.registered_providers),
            "added_providers": list(self.added_providers),
            "removed_providers": list(self.removed_providers),
            "unverifiable_providers": list(self.unverifiable_providers),
            "evidence_channels": {key: list(value) for key, value in self.evidence_channels.items()},
            "evidence": [item.to_dict() for item in self.evidence],
            "reason": self.reason,
        }

    def require_in_sync(self) -> None:
        if not self.in_sync:
            raise RepositoryPolicyDriftError(self.reason)


def _evidence_channel(item: ExternalSideEffectEvidence) -> str:
    if item.source == "repository-static-config" or item.source.startswith("workflow:"):
        return REPOSITORY_STATIC_CHANNEL
    if item.source.startswith("github-deployment"):
        return GITHUB_DEPLOYMENT_CHANNEL
    if item.source == "github-pr-comment":
        return GITHUB_PR_COMMENT_CHANNEL
    if item.state == "observed":
        return GENERIC_EXTERNAL_CHANNEL
    return item.source


def _canonical_channels(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(value).strip().lower() for value in values if str(value).strip()))


def _rules_by_provider(rules: Iterable[IntegrationFreshnessRule]) -> dict[str, IntegrationFreshnessRule]:
    result: dict[str, IntegrationFreshnessRule] = {}
    for rule in rules:
        provider = rule.provider.strip().lower()
        if provider:
            result[provider] = rule
    return result


def assess_repository_policy_drift(
    repository: str,
    evidence: Iterable[ExternalSideEffectEvidence],
    *,
    inspection_complete: bool,
    inspected_channels: Iterable[str] | None = None,
) -> RepositoryPolicyDriftAssessment:
    policy = resolve_repository_policy(repository)
    items = tuple(evidence)
    registered = tuple(sorted(set(policy.known_integration_providers)))
    active_items = tuple(item for item in items if item.state in {"configured", "observed"})
    detected = tuple(sorted({item.provider for item in active_items}))
    added = tuple(sorted(set(detected) - set(registered)))

    channels: dict[str, set[str]] = {}
    for item in active_items:
        channels.setdefault(item.provider, set()).add(_evidence_channel(item))
    normalized_channels = {provider: tuple(sorted(values)) for provider, values in sorted(channels.items())}

    rules = _rules_by_provider(policy.integration_freshness)
    unverifiable = tuple(sorted(set(registered) - set(rules)))
    if inspected_channels is None:
        inspected = tuple(
            sorted(
                {
                    channel
                    for rule in rules.values()
                    for channel in rule.evidence_channels
                }
            )
        )
    else:
        inspected = tuple(sorted(set(_canonical_channels(inspected_channels))))

    removed: list[str] = []
    inspected_set = set(inspected)
    for provider in registered:
        rule = rules.get(provider)
        if rule is None:
            continue
        accepted_channels = set(rule.evidence_channels)
        observable_channels = accepted_channels.intersection(inspected_set)
        if not observable_channels:
            # This scan did not inspect any channel capable of proving/removing this provider.
            continue
        observed_channels = set(channels.get(provider, set()))
        if not observed_channels.intersection(observable_channels):
            removed.append(provider)
    removed_tuple = tuple(sorted(removed))

    if not policy.registered:
        status = "BLOCKED_UNREGISTERED_REPOSITORY"
        in_sync = False
        reason = "Repository is not registered; policy freshness cannot be established."
    elif not inspection_complete:
        status = "UNKNOWN_POLICY_DRIFT"
        in_sync = False
        reason = "Repository integration inspection is incomplete; registry freshness is unknown."
    elif unverifiable:
        status = "UNKNOWN_UNVERIFIABLE_PROVIDER"
        in_sync = False
        reason = f"Registry provider(s) have no freshness rule: {', '.join(unverifiable)}"
    elif added and removed_tuple:
        status = "DRIFT_ADDED_AND_REMOVED_PROVIDER"
        in_sync = False
        reason = (
            f"Repository integration footprint changed: added {', '.join(added)}; "
            f"removed {', '.join(removed_tuple)}."
        )
    elif added:
        status = "DRIFT_ADDED_PROVIDER"
        in_sync = False
        reason = f"Repository has unregistered integration provider(s): {', '.join(added)}"
    elif removed_tuple:
        status = "DRIFT_REMOVED_PROVIDER"
        in_sync = False
        reason = f"Registry still declares provider(s) no longer evidenced by inspected channels: {', '.join(removed_tuple)}"
    else:
        status = "IN_SYNC"
        in_sync = True
        reason = "Current integration evidence matches the canonical registry for the inspected evidence channels."

    return RepositoryPolicyDriftAssessment(
        version=POLICY_DRIFT_VERSION,
        registry_version=REPOSITORY_POLICY_REGISTRY_VERSION,
        repository=policy.repository,
        registered=policy.registered,
        status=status,
        in_sync=in_sync,
        inspection_complete=inspection_complete,
        inspected_channels=inspected,
        detected_providers=detected,
        registered_providers=registered,
        added_providers=added,
        removed_providers=removed_tuple,
        unverifiable_providers=unverifiable,
        evidence_channels=normalized_channels,
        evidence=items,
        reason=reason,
    )


def inspect_repository_policy_drift(repository: str, repo_root: Path | str) -> RepositoryPolicyDriftAssessment:
    root = Path(repo_root)
    if not root.is_dir():
        return assess_repository_policy_drift(
            repository,
            (),
            inspection_complete=False,
            inspected_channels=(REPOSITORY_STATIC_CHANNEL,),
        )
    evidence = detect_static_integrations(root)
    return assess_repository_policy_drift(
        repository,
        evidence,
        inspection_complete=True,
        inspected_channels=(REPOSITORY_STATIC_CHANNEL,),
    )
