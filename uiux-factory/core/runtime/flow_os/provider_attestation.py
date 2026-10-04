from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Iterable, Mapping

from core.runtime.flow_os.external_side_effects import ExternalSideEffectEvidence
from core.runtime.flow_os.repository_policy_registry import resolve_repository_policy


PROVIDER_ATTESTATION_VERSION = "1.0"
CANONICAL_INTEGRATION_TRUTH_VERSION = "1.0"
PROVIDER_ATTESTATION_COVERAGE_VERSION = "1.0"
SUPPORTED_PROVIDER_ATTESTORS = frozenset({"vercel", "netlify", "render", "cloudflare", "railway"})
KNOWN_EXTERNAL_INTEGRATION_PROVIDERS = frozenset(
    {
        "vercel",
        "netlify",
        "render",
        "railway",
        "cloudflare",
        "firebase-hosting",
        "github-pages",
    }
)


@dataclass(frozen=True)
class ProviderAttestationCapability:
    provider: str
    mode: str
    attestor_available: bool
    repository_linkage_truth: bool
    idle_truth_provider_native: bool
    credential_inputs: tuple[str, ...] = ()
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["credential_inputs"] = list(self.credential_inputs)
        return payload


@dataclass(frozen=True)
class ProviderAttestationCoverageResult:
    version: str
    providers: tuple[ProviderAttestationCapability, ...]
    unclassified_providers: tuple[str, ...]
    adapter_pending_providers: tuple[str, ...]
    non_provider_native_providers: tuple[str, ...]
    classification_complete: bool
    provider_native_idle_coverage_complete: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "providers": [item.to_dict() for item in self.providers],
            "unclassified_providers": list(self.unclassified_providers),
            "adapter_pending_providers": list(self.adapter_pending_providers),
            "non_provider_native_providers": list(self.non_provider_native_providers),
            "classification_complete": self.classification_complete,
            "provider_native_idle_coverage_complete": self.provider_native_idle_coverage_complete,
            "reason": self.reason,
        }


PROVIDER_ATTESTATION_CAPABILITIES: dict[str, ProviderAttestationCapability] = {
    "vercel": ProviderAttestationCapability(
        provider="vercel",
        mode="provider-api",
        attestor_available=True,
        repository_linkage_truth=True,
        idle_truth_provider_native=True,
        credential_inputs=("P177_VERCEL_TOKEN", "P177_VERCEL_TEAM_ID"),
        reason="Vercel project/Git linkage is readable through the existing read-only provider adapter.",
    ),
    "netlify": ProviderAttestationCapability(
        provider="netlify",
        mode="provider-api",
        attestor_available=True,
        repository_linkage_truth=True,
        idle_truth_provider_native=True,
        credential_inputs=("P177_NETLIFY_TOKEN",),
        reason="Netlify site/Git linkage is readable through the existing read-only provider adapter.",
    ),
    "render": ProviderAttestationCapability(
        provider="render",
        mode="provider-api",
        attestor_available=True,
        repository_linkage_truth=True,
        idle_truth_provider_native=True,
        credential_inputs=("P177_RENDER_TOKEN",),
        reason="Render service/Git linkage is readable through the existing read-only provider adapter.",
    ),
    "cloudflare": ProviderAttestationCapability(
        provider="cloudflare",
        mode="provider-api",
        attestor_available=True,
        repository_linkage_truth=True,
        idle_truth_provider_native=True,
        credential_inputs=("P177_CLOUDFLARE_API_TOKEN", "P177_CLOUDFLARE_ACCOUNT_ID"),
        reason="Cloudflare Pages GitHub source linkage is readable through the existing read-only provider adapter.",
    ),
    "railway": ProviderAttestationCapability(
        provider="railway",
        mode="provider-api",
        attestor_available=True,
        repository_linkage_truth=True,
        idle_truth_provider_native=True,
        credential_inputs=("P179_RAILWAY_TOKEN", "P179_RAILWAY_WORKSPACE_ID"),
        reason=(
            "Railway project/service Git linkage is read through the public GraphQL API with schema introspection; "
            "missing scope or incompatible schema fails closed."
        ),
    ),
    "firebase-hosting": ProviderAttestationCapability(
        provider="firebase-hosting",
        mode="repository-static-or-github-native",
        attestor_available=False,
        repository_linkage_truth=False,
        idle_truth_provider_native=False,
        credential_inputs=(),
        reason=(
            "Firebase Hosting provider APIs expose hosting sites/releases but do not provide the repository-linkage "
            "truth required by this contract. Repository/static or GitHub workflow evidence remains authoritative."
        ),
    ),
    "github-pages": ProviderAttestationCapability(
        provider="github-pages",
        mode="github-native",
        attestor_available=False,
        repository_linkage_truth=True,
        idle_truth_provider_native=False,
        credential_inputs=(),
        reason=(
            "GitHub Pages is intentionally proven through repository-static and GitHub-native evidence; "
            "a second external-provider credential path is unnecessary."
        ),
    ),
}


def assess_provider_attestation_coverage(
    providers: Iterable[str],
) -> ProviderAttestationCoverageResult:
    normalized = tuple(sorted({str(provider).strip().lower() for provider in providers if str(provider).strip()}))
    capabilities: list[ProviderAttestationCapability] = []
    unclassified: list[str] = []
    adapter_pending: list[str] = []
    non_provider_native: list[str] = []

    for provider in normalized:
        capability = PROVIDER_ATTESTATION_CAPABILITIES.get(provider)
        if capability is None:
            unclassified.append(provider)
            continue
        capabilities.append(capability)
        if capability.mode == "provider-api-adapter-pending":
            adapter_pending.append(provider)
        if capability.mode in {"repository-static-or-github-native", "github-native"}:
            non_provider_native.append(provider)

    classification_complete = not unclassified
    provider_native_idle_coverage_complete = classification_complete and not adapter_pending
    if unclassified:
        reason = (
            "One or more integration providers have no attestation capability classification: "
            + ", ".join(unclassified)
            + "."
        )
    elif adapter_pending:
        reason = (
            "Provider capability classification is complete, but verified provider-native idle attestation "
            "is still pending for: "
            + ", ".join(adapter_pending)
            + "."
        )
    else:
        reason = (
            "Every requested provider has an explicit attestation capability classification and no provider-api "
            "adapter is silently pending."
        )

    return ProviderAttestationCoverageResult(
        version=PROVIDER_ATTESTATION_COVERAGE_VERSION,
        providers=tuple(capabilities),
        unclassified_providers=tuple(unclassified),
        adapter_pending_providers=tuple(adapter_pending),
        non_provider_native_providers=tuple(non_provider_native),
        classification_complete=classification_complete,
        provider_native_idle_coverage_complete=provider_native_idle_coverage_complete,
        reason=reason,
    )


@dataclass(frozen=True)
class ProviderAttestationResult:
    version: str
    provider: str
    repository: str
    inspection_complete: bool
    credential_configured: bool
    state: str
    project_id: str | None = None
    project_name: str | None = None
    linked_repository: str | None = None
    production_branch: str | None = None
    connection_active: bool | None = None
    preview_deployments_enabled: bool | None = None
    environment_ids: tuple[str, ...] = ()
    last_deployment_at: str | None = None
    evidence: tuple[ExternalSideEffectEvidence, ...] = ()
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["environment_ids"] = list(self.environment_ids)
        payload["evidence"] = [item.to_dict() for item in self.evidence]
        return payload


@dataclass(frozen=True)
class ProviderIntegrationTruth:
    provider: str
    state: str
    configured: bool | None
    evidence_channels: tuple[str, ...]
    reason: str
    attestation: ProviderAttestationResult | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "state": self.state,
            "configured": self.configured,
            "evidence_channels": list(self.evidence_channels),
            "reason": self.reason,
            "attestation": self.attestation.to_dict() if self.attestation else None,
        }


@dataclass(frozen=True)
class CanonicalIntegrationTruthResult:
    version: str
    repository: str
    status: str
    passed: bool
    inspection_complete: bool
    inspection_channels: tuple[str, ...]
    providers: tuple[ProviderIntegrationTruth, ...]
    added_providers: tuple[str, ...]
    conflicting_providers: tuple[str, ...]
    evidence: tuple[ExternalSideEffectEvidence, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "repository": self.repository,
            "status": self.status,
            "passed": self.passed,
            "inspection_complete": self.inspection_complete,
            "inspection_channels": list(self.inspection_channels),
            "providers": [item.to_dict() for item in self.providers],
            "added_providers": list(self.added_providers),
            "conflicting_providers": list(self.conflicting_providers),
            "evidence": [item.to_dict() for item in self.evidence],
            "reason": self.reason,
        }

    def require_passed(self) -> None:
        if not self.passed:
            raise RuntimeError(self.reason)


def _normalize_repository(value: str) -> str:
    text = str(value or "").strip().strip("/")
    if text.startswith("https://github.com/"):
        text = text.removeprefix("https://github.com/")
    if text.endswith(".git"):
        text = text[:-4]
    return text.lower()


def _project_linked_repository(project: Mapping[str, Any]) -> str | None:
    candidates: list[Mapping[str, Any]] = []
    for key in ("link", "gitRepository", "repository"):
        value = project.get(key)
        if isinstance(value, Mapping):
            candidates.append(value)
    for item in candidates:
        repo = str(item.get("repo") or item.get("repository") or "").strip()
        org = str(item.get("org") or item.get("owner") or item.get("organization") or "").strip()
        if "/" in repo:
            normalized = _normalize_repository(repo)
            if normalized:
                return normalized
        if repo and org:
            return _normalize_repository(f"{org}/{repo}")
    return None


def _project_production_branch(project: Mapping[str, Any]) -> str | None:
    link = project.get("link")
    values = [
        project.get("productionBranch"),
        link.get("productionBranch") if isinstance(link, Mapping) else None,
    ]
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return None


def _project_preview_enabled(project: Mapping[str, Any]) -> bool | None:
    link = project.get("link")
    for container in (project, link if isinstance(link, Mapping) else {}):
        for key in ("previewDeploymentsEnabled", "enablePreviewDeployments"):
            if key in container and isinstance(container.get(key), bool):
                return bool(container[key])
    return None


def _project_environment_ids(project: Mapping[str, Any]) -> tuple[str, ...]:
    values: list[str] = []
    raw = project.get("customEnvironments")
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, Mapping):
                value = str(item.get("id") or "").strip()
                if value and value not in values:
                    values.append(value)
    return tuple(values)


def _vercel_time(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value) / 1000.0, tz=timezone.utc).isoformat()
        except (OverflowError, OSError, ValueError):
            return None
    text = str(value).strip()
    return text or None


def _last_deployment_at(project: Mapping[str, Any]) -> str | None:
    deployments = project.get("latestDeployments")
    if not isinstance(deployments, list):
        return None
    values: list[tuple[float, str]] = []
    for item in deployments:
        if not isinstance(item, Mapping):
            continue
        raw = item.get("createdAt") or item.get("created")
        if isinstance(raw, (int, float)):
            values.append((float(raw), _vercel_time(raw) or ""))
        elif raw:
            text = str(raw)
            try:
                parsed = datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()
            except ValueError:
                continue
            values.append((parsed * 1000.0, text))
    if not values:
        return None
    return max(values, key=lambda item: item[0])[1] or None


class VercelProviderAttestor:
    """Read-only Vercel project/Git linkage attestation.

    The adapter uses GET requests only. A credential is opt-in input; it is never
    persisted in reports or evidence. Positive Git linkage can establish configured
    truth even when the latest deployment is old or absent.
    """

    def __init__(
        self,
        token: str | None,
        *,
        team_id: str | None = None,
        api_base: str = "https://api.vercel.com",
        timeout_seconds: int = 30,
        max_pages: int = 10,
        request_json: Callable[[str], Any] | None = None,
    ) -> None:
        self.token = str(token or "").strip()
        self.team_id = str(team_id or "").strip() or None
        self.api_base = api_base.rstrip("/")
        self.timeout_seconds = int(timeout_seconds)
        self.max_pages = max(1, int(max_pages))
        self._request_json_override = request_json

    def _request(self, path: str) -> Any:
        if self._request_json_override is not None:
            return self._request_json_override(path)
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "uiux-factory-p176",
        }
        request = urllib.request.Request(self.api_base + path, headers=headers, method="GET")
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            body = response.read().decode("utf-8")
        return json.loads(body) if body.strip() else None

    def _project_query(self, *, until: str | None = None) -> str:
        params: dict[str, str] = {"limit": "100"}
        if self.team_id:
            params["teamId"] = self.team_id
        if until:
            params["until"] = until
        return "/v9/projects?" + urllib.parse.urlencode(params)

    def _project_detail_path(self, project_id: str) -> str:
        path = f"/v9/projects/{urllib.parse.quote(project_id, safe='')}"
        if self.team_id:
            path += "?" + urllib.parse.urlencode({"teamId": self.team_id})
        return path

    def attest_repository(self, repository: str) -> ProviderAttestationResult:
        canonical_repo = _normalize_repository(repository)
        if not self.token:
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="vercel",
                repository=repository,
                inspection_complete=False,
                credential_configured=False,
                state="unknown",
                reason=(
                    "Vercel attestation was not attempted because the opt-in read-only credential is absent; "
                    "absence of recent deployment evidence must not be treated as integration removal."
                ),
            )

        next_cursor: str | None = None
        pages = 0
        matched: dict[str, Any] | None = None
        list_complete = False
        try:
            while pages < self.max_pages:
                payload = self._request(self._project_query(until=next_cursor))
                pages += 1
                if not isinstance(payload, Mapping) or not isinstance(payload.get("projects"), list):
                    return ProviderAttestationResult(
                        version=PROVIDER_ATTESTATION_VERSION,
                        provider="vercel",
                        repository=repository,
                        inspection_complete=False,
                        credential_configured=True,
                        state="unknown",
                        reason="Vercel project listing returned an unexpected payload; integration truth is unknown.",
                    )
                for raw in payload["projects"]:
                    if not isinstance(raw, Mapping):
                        continue
                    candidate = dict(raw)
                    if _project_linked_repository(candidate) == canonical_repo:
                        matched = candidate
                        break
                if matched is not None:
                    break
                pagination = payload.get("pagination")
                cursor = pagination.get("next") if isinstance(pagination, Mapping) else None
                if cursor in (None, "", 0):
                    list_complete = True
                    break
                next_value = str(cursor)
                if next_value == next_cursor:
                    break
                next_cursor = next_value
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="vercel",
                repository=repository,
                inspection_complete=False,
                credential_configured=True,
                state="unknown",
                reason="Vercel project visibility is unavailable; integration truth is unknown.",
            )

        if matched is None:
            if not list_complete:
                return ProviderAttestationResult(
                    version=PROVIDER_ATTESTATION_VERSION,
                    provider="vercel",
                    repository=repository,
                    inspection_complete=False,
                    credential_configured=True,
                    state="unknown",
                    reason=(
                        "Vercel project enumeration did not complete before the bounded page limit; "
                        "integration absence cannot be asserted."
                    ),
                )
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="vercel",
                repository=repository,
                inspection_complete=True,
                credential_configured=True,
                state="not_configured",
                connection_active=False,
                reason=f"No Vercel project linked to {repository} was found in the readable account/team scope.",
            )

        project_id = str(matched.get("id") or "").strip() or None
        project = matched
        if project_id:
            try:
                detail = self._request(self._project_detail_path(project_id))
                if isinstance(detail, Mapping):
                    project = {**matched, **dict(detail)}
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
                pass

        linked = _project_linked_repository(project) or _project_linked_repository(matched)
        if linked != canonical_repo:
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="vercel",
                repository=repository,
                inspection_complete=False,
                credential_configured=True,
                state="unknown",
                project_id=project_id,
                reason="Vercel project detail did not preserve the expected Git repository linkage; fail closed.",
            )

        project_name = str(project.get("name") or matched.get("name") or "").strip() or None
        production_branch = _project_production_branch(project) or _project_production_branch(matched)
        preview_enabled = _project_preview_enabled(project)
        environment_ids = _project_environment_ids(project)
        last_deployment = _last_deployment_at(project)
        evidence = (
            ExternalSideEffectEvidence(
                provider="vercel",
                effect="pr-preview",
                source="provider-attestation:vercel",
                state="configured",
                detail=(
                    f"Vercel project {project_id or project_name or 'unknown'} is linked to {repository}; "
                    f"production branch={production_branch or 'unknown'}; "
                    f"last deployment={last_deployment or 'not reported'}. "
                    "This configuration attestation is independent of recent deployment activity."
                ),
            ),
        )
        return ProviderAttestationResult(
            version=PROVIDER_ATTESTATION_VERSION,
            provider="vercel",
            repository=repository,
            inspection_complete=True,
            credential_configured=True,
            state="configured",
            project_id=project_id,
            project_name=project_name,
            linked_repository=linked,
            production_branch=production_branch,
            connection_active=True,
            preview_deployments_enabled=preview_enabled,
            environment_ids=environment_ids,
            last_deployment_at=last_deployment,
            evidence=evidence,
            reason=f"Vercel project linkage for {repository} is configured and readable.",
        )



def _github_repository_from_value(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    lowered = text.lower()
    if lowered.startswith("git@github.com:"):
        text = text.split(":", 1)[1]
    elif "github.com/" in lowered:
        offset = lowered.index("github.com/") + len("github.com/")
        text = text[offset:]
    text = text.split("#", 1)[0].split("?", 1)[0].strip().strip("/")
    if text.endswith(".git"):
        text = text[:-4]
    parts = [part for part in text.split("/") if part]
    if len(parts) != 2:
        return None
    return _normalize_repository("/".join(parts))


def _mapping_repository(container: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = container.get(key)
        repo = _github_repository_from_value(value)
        if repo:
            return repo
    return None


def _bool_from_setting(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    if text in {"yes", "true", "on", "all", "custom", "commit", "checkspass"}:
        return True
    if text in {"no", "false", "off", "none"}:
        return False
    return None


class NetlifyProviderAttestor:
    """Read-only Netlify site/Git linkage attestation."""

    def __init__(
        self,
        token: str | None,
        *,
        api_base: str = "https://api.netlify.com",
        timeout_seconds: int = 30,
        max_pages: int = 10,
        request_json: Callable[[str], Any] | None = None,
    ) -> None:
        self.token = str(token or "").strip()
        self.api_base = api_base.rstrip("/")
        self.timeout_seconds = int(timeout_seconds)
        self.max_pages = max(1, int(max_pages))
        self._request_json_override = request_json

    def _request(self, path: str) -> Any:
        if self._request_json_override is not None:
            return self._request_json_override(path)
        request = urllib.request.Request(
            self.api_base + path,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "uiux-factory-p177",
            },
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            body = response.read().decode("utf-8")
        return json.loads(body) if body.strip() else None

    @staticmethod
    def _linked_repository(site: Mapping[str, Any]) -> str | None:
        containers = [site]
        for key in ("build_settings", "repo"):
            value = site.get(key)
            if isinstance(value, Mapping):
                containers.append(value)
        for item in containers:
            repo = _mapping_repository(item, "repo_path", "repo_url")
            if repo:
                return repo
        return None

    @staticmethod
    def _production_branch(site: Mapping[str, Any]) -> str | None:
        for key in ("build_settings", "repo"):
            value = site.get(key)
            if isinstance(value, Mapping):
                branch = str(value.get("repo_branch") or "").strip()
                if branch:
                    return branch
        return None

    @staticmethod
    def _last_deployment_at(site: Mapping[str, Any]) -> str | None:
        deploy = site.get("published_deploy")
        if isinstance(deploy, Mapping):
            for key in ("published_at", "created_at", "updated_at"):
                value = str(deploy.get(key) or "").strip()
                if value:
                    return value
        return None

    def attest_repository(self, repository: str) -> ProviderAttestationResult:
        canonical_repo = _normalize_repository(repository)
        if not self.token:
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="netlify",
                repository=repository,
                inspection_complete=False,
                credential_configured=False,
                state="unknown",
                reason="Netlify attestation credential is absent; integration truth remains unknown.",
            )

        matched: dict[str, Any] | None = None
        list_complete = False
        try:
            for page in range(1, self.max_pages + 1):
                payload = self._request(f"/api/v1/sites?per_page=100&page={page}")
                if not isinstance(payload, list):
                    return ProviderAttestationResult(
                        version=PROVIDER_ATTESTATION_VERSION,
                        provider="netlify",
                        repository=repository,
                        inspection_complete=False,
                        credential_configured=True,
                        state="unknown",
                        reason="Netlify site listing returned an unexpected payload; fail closed.",
                    )
                for raw in payload:
                    if isinstance(raw, Mapping) and self._linked_repository(raw) == canonical_repo:
                        matched = dict(raw)
                        break
                if matched is not None:
                    break
                if len(payload) < 100:
                    list_complete = True
                    break
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="netlify",
                repository=repository,
                inspection_complete=False,
                credential_configured=True,
                state="unknown",
                reason="Netlify site visibility is unavailable; integration truth remains unknown.",
            )

        if matched is None:
            if not list_complete:
                return ProviderAttestationResult(
                    version=PROVIDER_ATTESTATION_VERSION,
                    provider="netlify",
                    repository=repository,
                    inspection_complete=False,
                    credential_configured=True,
                    state="unknown",
                    reason="Netlify enumeration hit the bounded page limit; absence cannot be asserted.",
                )
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="netlify",
                repository=repository,
                inspection_complete=True,
                credential_configured=True,
                state="not_configured",
                connection_active=False,
                reason=f"No Netlify site linked to {repository} was found in the readable account scope.",
            )

        site_id = str(matched.get("id") or "").strip() or None
        site = matched
        if site_id:
            try:
                detail = self._request(f"/api/v1/sites/{urllib.parse.quote(site_id, safe='')}")
                if isinstance(detail, Mapping):
                    site = {**matched, **dict(detail)}
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
                pass

        linked = self._linked_repository(site) or self._linked_repository(matched)
        if linked != canonical_repo:
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="netlify",
                repository=repository,
                inspection_complete=False,
                credential_configured=True,
                state="unknown",
                project_id=site_id,
                reason="Netlify detail visibility did not preserve the expected Git linkage; fail closed.",
            )

        project_name = str(site.get("name") or matched.get("name") or "").strip() or None
        production_branch = self._production_branch(site) or self._production_branch(matched)
        last_deployment = self._last_deployment_at(site) or self._last_deployment_at(matched)
        evidence = (
            ExternalSideEffectEvidence(
                provider="netlify",
                effect="pr-preview",
                source="provider-attestation:netlify",
                state="configured",
                detail=(
                    f"Netlify site {site_id or project_name or 'unknown'} is linked to {repository}; "
                    f"production branch={production_branch or 'unknown'}; "
                    f"last deployment={last_deployment or 'not reported'}."
                ),
            ),
        )
        return ProviderAttestationResult(
            version=PROVIDER_ATTESTATION_VERSION,
            provider="netlify",
            repository=repository,
            inspection_complete=True,
            credential_configured=True,
            state="configured",
            project_id=site_id,
            project_name=project_name,
            linked_repository=linked,
            production_branch=production_branch,
            connection_active=True,
            last_deployment_at=last_deployment,
            evidence=evidence,
            reason=f"Netlify site linkage for {repository} is configured and readable.",
        )


class RenderProviderAttestor:
    """Read-only Render service/Git linkage attestation."""

    def __init__(
        self,
        token: str | None,
        *,
        api_base: str = "https://api.render.com",
        timeout_seconds: int = 30,
        max_pages: int = 10,
        request_json: Callable[[str], Any] | None = None,
    ) -> None:
        self.token = str(token or "").strip()
        self.api_base = api_base.rstrip("/")
        self.timeout_seconds = int(timeout_seconds)
        self.max_pages = max(1, int(max_pages))
        self._request_json_override = request_json

    def _request(self, path: str) -> Any:
        if self._request_json_override is not None:
            return self._request_json_override(path)
        request = urllib.request.Request(
            self.api_base + path,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "uiux-factory-p177",
            },
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            body = response.read().decode("utf-8")
        return json.loads(body) if body.strip() else None

    @staticmethod
    def _service_from_row(row: Mapping[str, Any]) -> Mapping[str, Any]:
        service = row.get("service")
        return service if isinstance(service, Mapping) else row

    def attest_repository(self, repository: str) -> ProviderAttestationResult:
        canonical_repo = _normalize_repository(repository)
        if not self.token:
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="render",
                repository=repository,
                inspection_complete=False,
                credential_configured=False,
                state="unknown",
                reason="Render attestation credential is absent; integration truth remains unknown.",
            )

        cursor: str | None = None
        matched: dict[str, Any] | None = None
        list_complete = False
        try:
            for _ in range(self.max_pages):
                query = "/v1/services?limit=100"
                if cursor:
                    query += "&cursor=" + urllib.parse.quote(cursor, safe="")
                payload = self._request(query)
                if not isinstance(payload, list):
                    return ProviderAttestationResult(
                        version=PROVIDER_ATTESTATION_VERSION,
                        provider="render",
                        repository=repository,
                        inspection_complete=False,
                        credential_configured=True,
                        state="unknown",
                        reason="Render service listing returned an unexpected payload; fail closed.",
                    )
                for raw in payload:
                    if not isinstance(raw, Mapping):
                        continue
                    service = self._service_from_row(raw)
                    if _github_repository_from_value(service.get("repo")) == canonical_repo:
                        matched = dict(service)
                        break
                if matched is not None:
                    break
                if len(payload) < 100:
                    list_complete = True
                    break
                last = payload[-1] if payload else None
                next_cursor = str(last.get("cursor") or "").strip() if isinstance(last, Mapping) else ""
                if not next_cursor or next_cursor == cursor:
                    break
                cursor = next_cursor
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="render",
                repository=repository,
                inspection_complete=False,
                credential_configured=True,
                state="unknown",
                reason="Render service visibility is unavailable; integration truth remains unknown.",
            )

        if matched is None:
            if not list_complete:
                return ProviderAttestationResult(
                    version=PROVIDER_ATTESTATION_VERSION,
                    provider="render",
                    repository=repository,
                    inspection_complete=False,
                    credential_configured=True,
                    state="unknown",
                    reason="Render enumeration did not complete before the bounded page limit; absence cannot be asserted.",
                )
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="render",
                repository=repository,
                inspection_complete=True,
                credential_configured=True,
                state="not_configured",
                connection_active=False,
                reason=f"No Render service linked to {repository} was found in the readable workspace scope.",
            )

        service_id = str(matched.get("id") or "").strip() or None
        service = matched
        if service_id:
            try:
                detail = self._request(f"/v1/services/{urllib.parse.quote(service_id, safe='')}")
                if isinstance(detail, Mapping):
                    service = dict(detail.get("service")) if isinstance(detail.get("service"), Mapping) else dict(detail)
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
                pass

        linked = _github_repository_from_value(service.get("repo")) or _github_repository_from_value(matched.get("repo"))
        if linked != canonical_repo:
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="render",
                repository=repository,
                inspection_complete=False,
                credential_configured=True,
                state="unknown",
                project_id=service_id,
                reason="Render service detail did not preserve the expected Git linkage; fail closed.",
            )

        details = service.get("serviceDetails")
        preview_value = None
        if isinstance(details, Mapping):
            preview_value = details.get("pullRequestPreviewsEnabled")
            if preview_value is None and isinstance(details.get("previews"), Mapping):
                preview_value = details["previews"].get("generation")
        project_name = str(service.get("name") or matched.get("name") or "").strip() or None
        production_branch = str(service.get("branch") or matched.get("branch") or "").strip() or None
        preview_enabled = _bool_from_setting(preview_value)
        evidence = (
            ExternalSideEffectEvidence(
                provider="render",
                effect="deployment",
                source="provider-attestation:render",
                state="configured",
                detail=(
                    f"Render service {service_id or project_name or 'unknown'} is linked to {repository}; "
                    f"production branch={production_branch or 'unknown'}."
                ),
            ),
        )
        return ProviderAttestationResult(
            version=PROVIDER_ATTESTATION_VERSION,
            provider="render",
            repository=repository,
            inspection_complete=True,
            credential_configured=True,
            state="configured",
            project_id=service_id,
            project_name=project_name,
            linked_repository=linked,
            production_branch=production_branch,
            connection_active=True,
            preview_deployments_enabled=preview_enabled,
            evidence=evidence,
            reason=f"Render service linkage for {repository} is configured and readable.",
        )


class CloudflarePagesProviderAttestor:
    """Read-only Cloudflare Pages project/Git linkage attestation."""

    def __init__(
        self,
        token: str | None,
        *,
        account_id: str | None,
        api_base: str = "https://api.cloudflare.com/client/v4",
        timeout_seconds: int = 30,
        max_pages: int = 10,
        request_json: Callable[[str], Any] | None = None,
    ) -> None:
        self.token = str(token or "").strip()
        self.account_id = str(account_id or "").strip()
        self.api_base = api_base.rstrip("/")
        self.timeout_seconds = int(timeout_seconds)
        self.max_pages = max(1, int(max_pages))
        self._request_json_override = request_json

    def _request(self, path: str) -> Any:
        if self._request_json_override is not None:
            return self._request_json_override(path)
        request = urllib.request.Request(
            self.api_base + path,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "uiux-factory-p177",
            },
            method="GET",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            body = response.read().decode("utf-8")
        return json.loads(body) if body.strip() else None

    @staticmethod
    def _source_config(project: Mapping[str, Any]) -> Mapping[str, Any]:
        source = project.get("source")
        if not isinstance(source, Mapping) or str(source.get("type") or "").strip().lower() != "github":
            return {}
        config = source.get("config")
        return config if isinstance(config, Mapping) else {}

    @classmethod
    def _linked_repository(cls, project: Mapping[str, Any]) -> str | None:
        config = cls._source_config(project)
        owner = str(config.get("owner") or "").strip()
        repo_name = str(config.get("repo_name") or "").strip()
        if owner and repo_name:
            return _normalize_repository(f"{owner}/{repo_name}")
        return None

    def attest_repository(self, repository: str) -> ProviderAttestationResult:
        canonical_repo = _normalize_repository(repository)
        if not self.token or not self.account_id:
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="cloudflare",
                repository=repository,
                inspection_complete=False,
                credential_configured=False,
                state="unknown",
                reason=(
                    "Cloudflare Pages attestation requires both an opt-in API token and account ID; "
                    "integration truth remains unknown."
                ),
            )

        matched: dict[str, Any] | None = None
        list_complete = False
        try:
            for page in range(1, self.max_pages + 1):
                path = (
                    f"/accounts/{urllib.parse.quote(self.account_id, safe='')}/pages/projects"
                    f"?per_page=100&page={page}"
                )
                payload = self._request(path)
                if not isinstance(payload, Mapping) or payload.get("success") is not True:
                    return ProviderAttestationResult(
                        version=PROVIDER_ATTESTATION_VERSION,
                        provider="cloudflare",
                        repository=repository,
                        inspection_complete=False,
                        credential_configured=True,
                        state="unknown",
                        reason="Cloudflare Pages listing returned an unsuccessful or unexpected payload; fail closed.",
                    )
                projects = payload.get("result")
                if not isinstance(projects, list):
                    return ProviderAttestationResult(
                        version=PROVIDER_ATTESTATION_VERSION,
                        provider="cloudflare",
                        repository=repository,
                        inspection_complete=False,
                        credential_configured=True,
                        state="unknown",
                        reason="Cloudflare Pages project result is not a list; fail closed.",
                    )
                for raw in projects:
                    if isinstance(raw, Mapping) and self._linked_repository(raw) == canonical_repo:
                        matched = dict(raw)
                        break
                if matched is not None:
                    break
                info = payload.get("result_info")
                total_pages = int(info.get("total_pages") or 0) if isinstance(info, Mapping) else 0
                if (total_pages and page >= total_pages) or (not total_pages and len(projects) < 100):
                    list_complete = True
                    break
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, ValueError):
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="cloudflare",
                repository=repository,
                inspection_complete=False,
                credential_configured=True,
                state="unknown",
                reason="Cloudflare Pages visibility is unavailable; integration truth remains unknown.",
            )

        if matched is None:
            if not list_complete:
                return ProviderAttestationResult(
                    version=PROVIDER_ATTESTATION_VERSION,
                    provider="cloudflare",
                    repository=repository,
                    inspection_complete=False,
                    credential_configured=True,
                    state="unknown",
                    reason="Cloudflare Pages enumeration hit the bounded page limit; absence cannot be asserted.",
                )
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="cloudflare",
                repository=repository,
                inspection_complete=True,
                credential_configured=True,
                state="not_configured",
                connection_active=False,
                reason=f"No Cloudflare Pages project linked to {repository} was found in the readable account scope.",
            )

        linked = self._linked_repository(matched)
        config = self._source_config(matched)
        project_id = str(matched.get("id") or matched.get("name") or "").strip() or None
        project_name = str(matched.get("name") or "").strip() or None
        production_branch = str(
            matched.get("production_branch") or config.get("production_branch") or ""
        ).strip() or None
        preview_enabled = _bool_from_setting(config.get("preview_deployment_setting"))
        if preview_enabled is None:
            preview_enabled = _bool_from_setting(config.get("deployments_enabled"))
        deployment = matched.get("latest_deployment")
        last_deployment = None
        if isinstance(deployment, Mapping):
            last_deployment = str(
                deployment.get("created_on") or deployment.get("modified_on") or ""
            ).strip() or None
        evidence = (
            ExternalSideEffectEvidence(
                provider="cloudflare",
                effect="deployment",
                source="provider-attestation:cloudflare",
                state="configured",
                detail=(
                    f"Cloudflare Pages project {project_id or project_name or 'unknown'} is linked to {repository}; "
                    f"production branch={production_branch or 'unknown'}; "
                    f"last deployment={last_deployment or 'not reported'}."
                ),
            ),
        )
        return ProviderAttestationResult(
            version=PROVIDER_ATTESTATION_VERSION,
            provider="cloudflare",
            repository=repository,
            inspection_complete=True,
            credential_configured=True,
            state="configured",
            project_id=project_id,
            project_name=project_name,
            linked_repository=linked,
            production_branch=production_branch,
            connection_active=True,
            preview_deployments_enabled=preview_enabled,
            last_deployment_at=last_deployment,
            evidence=evidence,
            reason=f"Cloudflare Pages project linkage for {repository} is configured and readable.",
        )


def _graphql_named_type(type_payload: Any) -> str | None:
    current = type_payload
    for _ in range(8):
        if not isinstance(current, Mapping):
            return None
        name = str(current.get("name") or "").strip()
        if name:
            return name
        current = current.get("ofType")
    return None


class RailwayProviderAttestor:
    """Read-only Railway project/service Git linkage attestation.

    Railway's public API is GraphQL. The adapter first introspects the Service
    schema before selecting source.repo/source.branch, so schema drift fails
    closed instead of converting an invalid query into provider absence.
    """

    def __init__(
        self,
        token: str | None,
        *,
        workspace_id: str | None = None,
        api_base: str = "https://backboard.railway.com/graphql/v2",
        timeout_seconds: int = 30,
        max_pages: int = 10,
        request_graphql: Callable[[str, Mapping[str, Any]], Any] | None = None,
    ) -> None:
        self.token = str(token or "").strip()
        self.workspace_id = str(workspace_id or "").strip() or None
        self.api_base = api_base
        self.timeout_seconds = int(timeout_seconds)
        self.max_pages = max(1, int(max_pages))
        self._request_graphql_override = request_graphql

    def _request(self, query: str, variables: Mapping[str, Any] | None = None) -> Any:
        payload_variables = dict(variables or {})
        if self._request_graphql_override is not None:
            return self._request_graphql_override(query, payload_variables)
        body = json.dumps({"query": query, "variables": payload_variables}).encode("utf-8")
        request = urllib.request.Request(
            self.api_base,
            data=body,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "uiux-factory-p179",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            raw = response.read().decode("utf-8")
        return json.loads(raw) if raw.strip() else None

    @staticmethod
    def _graphql_data(payload: Any) -> Mapping[str, Any] | None:
        if not isinstance(payload, Mapping):
            return None
        errors = payload.get("errors")
        if isinstance(errors, list) and errors:
            return None
        data = payload.get("data")
        return data if isinstance(data, Mapping) else None

    def _source_field_ready(self) -> bool:
        service_type_query = """
        query P179ServiceSchema {
          __type(name: "Service") {
            fields(includeDeprecated: true) {
              name
              type {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                  }
                }
              }
            }
          }
        }
        """
        payload = self._request(service_type_query, {})
        data = self._graphql_data(payload)
        type_payload = data.get("__type") if isinstance(data, Mapping) else None
        fields = type_payload.get("fields") if isinstance(type_payload, Mapping) else None
        if not isinstance(fields, list):
            return False
        source_field = next(
            (
                item
                for item in fields
                if isinstance(item, Mapping) and str(item.get("name") or "") == "source"
            ),
            None,
        )
        if not isinstance(source_field, Mapping):
            return False
        source_type = _graphql_named_type(source_field.get("type"))
        if not source_type:
            return False

        source_type_query = """
        query P179SourceSchema($name: String!) {
          __type(name: $name) {
            fields(includeDeprecated: true) {
              name
            }
          }
        }
        """
        payload = self._request(source_type_query, {"name": source_type})
        data = self._graphql_data(payload)
        type_payload = data.get("__type") if isinstance(data, Mapping) else None
        source_fields = type_payload.get("fields") if isinstance(type_payload, Mapping) else None
        if not isinstance(source_fields, list):
            return False
        names = {
            str(item.get("name") or "").strip()
            for item in source_fields
            if isinstance(item, Mapping)
        }
        return "repo" in names and "branch" in names

    def _list_projects_page(self, cursor: str | None) -> tuple[list[Mapping[str, Any]], bool, str | None] | None:
        if self.workspace_id:
            query = """
            query P179Projects($workspaceId: String!, $first: Int!, $after: String) {
              projects(workspaceId: $workspaceId, first: $first, after: $after) {
                edges { node { id name } }
                pageInfo { hasNextPage endCursor }
              }
            }
            """
            variables: dict[str, Any] = {
                "workspaceId": self.workspace_id,
                "first": 100,
                "after": cursor,
            }
        else:
            query = """
            query P179Projects($first: Int!, $after: String) {
              projects(first: $first, after: $after) {
                edges { node { id name } }
                pageInfo { hasNextPage endCursor }
              }
            }
            """
            variables = {"first": 100, "after": cursor}

        payload = self._request(query, variables)
        data = self._graphql_data(payload)
        connection = data.get("projects") if isinstance(data, Mapping) else None
        if not isinstance(connection, Mapping):
            return None
        edges = connection.get("edges")
        page_info = connection.get("pageInfo")
        if not isinstance(edges, list) or not isinstance(page_info, Mapping):
            return None
        projects = [
            item["node"]
            for item in edges
            if isinstance(item, Mapping) and isinstance(item.get("node"), Mapping)
        ]
        has_next = bool(page_info.get("hasNextPage"))
        end_cursor = str(page_info.get("endCursor") or "").strip() or None
        if has_next and not end_cursor:
            return None
        return projects, has_next, end_cursor

    def _list_services_page(
        self,
        project_id: str,
        cursor: str | None,
    ) -> tuple[list[Mapping[str, Any]], bool, str | None, str | None] | None:
        query = """
        query P179ProjectServices($id: String!, $first: Int!, $after: String) {
          project(id: $id) {
            id
            name
            services(first: $first, after: $after) {
              edges {
                node {
                  id
                  name
                  source {
                    repo
                    branch
                  }
                }
              }
              pageInfo { hasNextPage endCursor }
            }
          }
        }
        """
        payload = self._request(
            query,
            {"id": project_id, "first": 100, "after": cursor},
        )
        data = self._graphql_data(payload)
        project = data.get("project") if isinstance(data, Mapping) else None
        if not isinstance(project, Mapping):
            return None
        connection = project.get("services")
        if not isinstance(connection, Mapping):
            return None
        edges = connection.get("edges")
        page_info = connection.get("pageInfo")
        if not isinstance(edges, list) or not isinstance(page_info, Mapping):
            return None
        services = [
            item["node"]
            for item in edges
            if isinstance(item, Mapping) and isinstance(item.get("node"), Mapping)
        ]
        has_next = bool(page_info.get("hasNextPage"))
        end_cursor = str(page_info.get("endCursor") or "").strip() or None
        if has_next and not end_cursor:
            return None
        project_name = str(project.get("name") or "").strip() or None
        return services, has_next, end_cursor, project_name

    def attest_repository(self, repository: str) -> ProviderAttestationResult:
        canonical_repo = _normalize_repository(repository)
        if not self.token:
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="railway",
                repository=repository,
                inspection_complete=False,
                credential_configured=False,
                state="unknown",
                reason="Railway attestation credential is absent; integration truth remains unknown.",
            )

        try:
            if not self._source_field_ready():
                return ProviderAttestationResult(
                    version=PROVIDER_ATTESTATION_VERSION,
                    provider="railway",
                    repository=repository,
                    inspection_complete=False,
                    credential_configured=True,
                    state="unknown",
                    reason=(
                        "Railway GraphQL schema did not expose a readable Service.source repo/branch shape; "
                        "repository linkage cannot be asserted."
                    ),
                )

            projects_complete = False
            project_cursor: str | None = None
            project_pages = 0
            while project_pages < self.max_pages:
                project_page = self._list_projects_page(project_cursor)
                project_pages += 1
                if project_page is None:
                    return ProviderAttestationResult(
                        version=PROVIDER_ATTESTATION_VERSION,
                        provider="railway",
                        repository=repository,
                        inspection_complete=False,
                        credential_configured=True,
                        state="unknown",
                        reason="Railway project enumeration returned incomplete GraphQL visibility; fail closed.",
                    )
                projects, projects_has_next, next_project_cursor = project_page

                for project in projects:
                    project_id = str(project.get("id") or "").strip()
                    project_name = str(project.get("name") or "").strip() or None
                    if not project_id:
                        return ProviderAttestationResult(
                            version=PROVIDER_ATTESTATION_VERSION,
                            provider="railway",
                            repository=repository,
                            inspection_complete=False,
                            credential_configured=True,
                            state="unknown",
                            reason="Railway project enumeration omitted a stable project id; fail closed.",
                        )
                    service_cursor: str | None = None
                    service_pages = 0
                    services_complete = False
                    while service_pages < self.max_pages:
                        service_page = self._list_services_page(project_id, service_cursor)
                        service_pages += 1
                        if service_page is None:
                            return ProviderAttestationResult(
                                version=PROVIDER_ATTESTATION_VERSION,
                                provider="railway",
                                repository=repository,
                                inspection_complete=False,
                                credential_configured=True,
                                state="unknown",
                                project_id=project_id,
                                project_name=project_name,
                                reason="Railway service enumeration returned incomplete GraphQL visibility; fail closed.",
                            )
                        services, services_has_next, next_service_cursor, detail_project_name = service_page
                        project_name = detail_project_name or project_name
                        for service in services:
                            source = service.get("source")
                            if not isinstance(source, Mapping):
                                continue
                            linked = _github_repository_from_value(source.get("repo"))
                            if linked != canonical_repo:
                                continue
                            service_id = str(service.get("id") or "").strip() or None
                            service_name = str(service.get("name") or "").strip() or None
                            branch = str(source.get("branch") or "").strip() or None
                            evidence = (
                                ExternalSideEffectEvidence(
                                    provider="railway",
                                    effect="deployment",
                                    source="provider-attestation:railway",
                                    state="configured",
                                    detail=(
                                        f"Railway service {service_id or service_name or 'unknown'} in project "
                                        f"{project_id} is linked to {repository}; production branch={branch or 'unknown'}."
                                    ),
                                ),
                            )
                            return ProviderAttestationResult(
                                version=PROVIDER_ATTESTATION_VERSION,
                                provider="railway",
                                repository=repository,
                                inspection_complete=True,
                                credential_configured=True,
                                state="configured",
                                project_id=project_id,
                                project_name=project_name,
                                linked_repository=linked,
                                production_branch=branch,
                                connection_active=True,
                                evidence=evidence,
                                reason=f"Railway service linkage for {repository} is configured and readable.",
                            )

                        if not services_has_next:
                            services_complete = True
                            break
                        if next_service_cursor == service_cursor:
                            break
                        service_cursor = next_service_cursor

                    if not services_complete:
                        return ProviderAttestationResult(
                            version=PROVIDER_ATTESTATION_VERSION,
                            provider="railway",
                            repository=repository,
                            inspection_complete=False,
                            credential_configured=True,
                            state="unknown",
                            project_id=project_id,
                            project_name=project_name,
                            reason=(
                                "Railway service enumeration hit the bounded page limit; "
                                "repository-linkage absence cannot be asserted."
                            ),
                        )

                if not projects_has_next:
                    projects_complete = True
                    break
                if next_project_cursor == project_cursor:
                    break
                project_cursor = next_project_cursor

            if not projects_complete:
                return ProviderAttestationResult(
                    version=PROVIDER_ATTESTATION_VERSION,
                    provider="railway",
                    repository=repository,
                    inspection_complete=False,
                    credential_configured=True,
                    state="unknown",
                    reason=(
                        "Railway project enumeration hit the bounded page limit; "
                        "repository-linkage absence cannot be asserted."
                    ),
                )

            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="railway",
                repository=repository,
                inspection_complete=True,
                credential_configured=True,
                state="not_configured",
                connection_active=False,
                reason=(
                    f"No Railway service linked to {repository} was found in the fully readable "
                    "account/workspace project scope."
                ),
            )
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, ValueError):
            return ProviderAttestationResult(
                version=PROVIDER_ATTESTATION_VERSION,
                provider="railway",
                repository=repository,
                inspection_complete=False,
                credential_configured=True,
                state="unknown",
                reason="Railway API visibility is unavailable; integration truth remains unknown.",
            )

def evidence_channel(item: ExternalSideEffectEvidence) -> str:
    if item.source == "repository-static-config" or item.source.startswith("workflow:"):
        return "repository-static"
    if item.source.startswith("github-deployment") or item.source == "github-check-run":
        return "github-provider-native"
    if item.source.startswith("provider-attestation:"):
        return "provider-attestation"
    if item.source == "github-pr-comment":
        return "github-pr-comment"
    if item.state == "observed":
        return "external-observed"
    return item.source


def resolve_canonical_integration_truth(
    repository: str,
    evidence: Iterable[ExternalSideEffectEvidence],
    *,
    attestations: Mapping[str, ProviderAttestationResult] | None = None,
    inspection_complete: bool = True,
    inspection_channels: Iterable[str] = ("repository-static", "github-provider-native"),
) -> CanonicalIntegrationTruthResult:
    """Resolve integration truth without equating missing recent activity with absence."""

    policy = resolve_repository_policy(repository)
    items = tuple(evidence)
    attestation_map = {
        str(key).strip().lower(): value
        for key, value in dict(attestations or {}).items()
        if str(key).strip()
    }
    registered = tuple(sorted(set(policy.known_integration_providers)))
    active = tuple(item for item in items if item.state in {"configured", "observed"})
    detected = {item.provider for item in active}
    added = tuple(sorted(detected - set(registered)))

    channels: dict[str, set[str]] = {}
    for item in active:
        channels.setdefault(item.provider, set()).add(evidence_channel(item))

    provider_truth: list[ProviderIntegrationTruth] = []
    removed: list[str] = []
    unknown: list[str] = []
    conflicts: list[str] = []

    for provider in registered:
        attestation = attestation_map.get(provider)
        observed_channels = tuple(sorted(channels.get(provider, set())))

        if attestation is not None and attestation.state == "configured" and attestation.inspection_complete:
            merged_channels = tuple(sorted(set(observed_channels) | {"provider-attestation"}))
            provider_truth.append(
                ProviderIntegrationTruth(
                    provider=provider,
                    state="CONFIGURED_ATTESTED",
                    configured=True,
                    evidence_channels=merged_channels,
                    reason=(
                        "Provider configuration is positively attested by the provider API; "
                        "recent deployment activity is not required to prove the integration still exists."
                    ),
                    attestation=attestation,
                )
            )
            continue

        if (
            observed_channels
            and attestation is not None
            and attestation.state == "not_configured"
            and attestation.inspection_complete
        ):
            conflicts.append(provider)
            provider_truth.append(
                ProviderIntegrationTruth(
                    provider=provider,
                    state="CONFLICTING_PROVIDER_TRUTH",
                    configured=None,
                    evidence_channels=tuple(sorted(set(observed_channels) | {"provider-attestation"})),
                    reason=(
                        "Repository/GitHub evidence says the provider is configured or active, while a complete "
                        "provider attestation says no linked project exists. Canonical truth must fail closed."
                    ),
                    attestation=attestation,
                )
            )
            continue

        if observed_channels:
            provider_truth.append(
                ProviderIntegrationTruth(
                    provider=provider,
                    state="CONFIGURED_EVIDENCED",
                    configured=True,
                    evidence_channels=observed_channels,
                    reason="Repository-static or recent GitHub provider evidence confirms the integration footprint.",
                    attestation=attestation,
                )
            )
            continue

        if attestation is not None and attestation.state == "not_configured" and attestation.inspection_complete:
            removed.append(provider)
            provider_truth.append(
                ProviderIntegrationTruth(
                    provider=provider,
                    state="NOT_CONFIGURED_ATTESTED",
                    configured=False,
                    evidence_channels=("provider-attestation",),
                    reason="Provider API inspection completed and found no linked project for this repository.",
                    attestation=attestation,
                )
            )
            continue

        unknown.append(provider)
        provider_truth.append(
            ProviderIntegrationTruth(
                provider=provider,
                state="UNKNOWN_IDLE_TRUTH",
                configured=None,
                evidence_channels=observed_channels,
                reason=(
                    "No current repository/static or recent GitHub evidence proves this provider, and no complete "
                    "provider attestation proves absence. Missing activity is not integration-removal evidence."
                ),
                attestation=attestation,
            )
        )

    normalized_inspection_channels = tuple(
        sorted({str(value).strip() for value in inspection_channels if str(value).strip()})
    )

    if not policy.registered:
        status = "BLOCKED_UNREGISTERED_REPOSITORY"
        passed = False
        reason = "Repository is not registered; canonical integration truth cannot be established."
    elif added:
        status = "DRIFT_ADDED_PROVIDER"
        passed = False
        reason = f"Unregistered external provider evidence exists: {', '.join(added)}."
    elif conflicts:
        status = "CONFLICT_PROVIDER_TRUTH"
        passed = False
        reason = (
            "Provider-native attestation contradicts repository/GitHub evidence for: "
            f"{', '.join(sorted(conflicts))}. Investigate before changing the registry."
        )
    elif removed:
        status = "DRIFT_REMOVED_PROVIDER"
        passed = False
        reason = f"Provider-native attestation confirms registered provider(s) are absent: {', '.join(sorted(removed))}."
    elif unknown:
        status = "UNKNOWN_IDLE_INTEGRATION_TRUTH"
        passed = False
        reason = (
            "Canonical integration truth is incomplete for idle provider(s): "
            f"{', '.join(sorted(unknown))}. Supply opt-in provider visibility or restore a trusted evidence channel."
        )
    elif not inspection_complete:
        status = "UNKNOWN_EXTERNAL_VISIBILITY"
        passed = False
        reason = (
            "Registered providers are positively evidenced, but external discovery visibility is incomplete; "
            "an added provider could be hidden, so canonical truth fails closed."
        )
    else:
        status = "IN_SYNC"
        passed = True
        reason = "All registered integrations are positively evidenced or provider-attested; no added provider drift was observed."

    combined = list(items)
    for attestation in attestation_map.values():
        combined.extend(attestation.evidence)
    deduped: list[ExternalSideEffectEvidence] = []
    seen: set[tuple[str, str, str, str | None]] = set()
    for item in combined:
        key = (item.provider, item.effect, item.source, item.url)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return CanonicalIntegrationTruthResult(
        version=CANONICAL_INTEGRATION_TRUTH_VERSION,
        repository=policy.repository,
        status=status,
        passed=passed,
        inspection_complete=bool(inspection_complete),
        inspection_channels=normalized_inspection_channels,
        providers=tuple(provider_truth),
        added_providers=added,
        conflicting_providers=tuple(sorted(conflicts)),
        evidence=tuple(deduped),
        reason=reason,
    )
