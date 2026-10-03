from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Iterable

from core.runtime.flow_os.external_side_effects import ExternalSideEffectEvidence


EXTERNAL_INTEGRATION_DISCOVERY_VERSION = "1.1"
DEFAULT_EXTERNAL_EVIDENCE_MAX_AGE_DAYS = 90


@dataclass(frozen=True)
class ExternalIntegrationDiscoveryResult:
    version: str
    repository: str
    inspection_complete: bool
    inspected_deployments: int
    ignored_stale_deployments: int
    inspected_check_runs: int
    ignored_stale_check_runs: int
    evidence: tuple[ExternalSideEffectEvidence, ...]
    unknown_deployment_ids: tuple[int, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "repository": self.repository,
            "inspection_complete": self.inspection_complete,
            "inspected_deployments": self.inspected_deployments,
            "ignored_stale_deployments": self.ignored_stale_deployments,
            "inspected_check_runs": self.inspected_check_runs,
            "ignored_stale_check_runs": self.ignored_stale_check_runs,
            "evidence": [item.to_dict() for item in self.evidence],
            "unknown_deployment_ids": list(self.unknown_deployment_ids),
            "reason": self.reason,
        }


def _dedupe(evidence: Iterable[ExternalSideEffectEvidence]) -> tuple[ExternalSideEffectEvidence, ...]:
    seen: set[tuple[str, str, str, str | None]] = set()
    result: list[ExternalSideEffectEvidence] = []
    for item in evidence:
        key = (item.provider, item.effect, item.source, item.url)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return tuple(result)


def _parse_github_time(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _payload_text(*parts: Any) -> str:
    values: list[str] = []
    for part in parts:
        if part is None:
            continue
        if isinstance(part, str):
            values.append(part)
        else:
            try:
                values.append(json.dumps(part, ensure_ascii=False, sort_keys=True, default=str))
            except (TypeError, ValueError):
                values.append(str(part))
    return " ".join(values).lower()


_PROVIDER_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("vercel", ("vercel", "vercel.app")),
    ("netlify", ("netlify", "netlify.app")),
    ("github-pages", ("github-pages", "github pages", "github.io", "pages-build-deployment", "deploy-pages")),
    ("render", ("render[bot]", "render.com", "onrender.com", "render deployment")),
    ("railway", ("railway", "railway.app")),
    ("cloudflare", ("cloudflare", "pages.dev", "workers.dev", "wrangler")),
    ("firebase-hosting", ("firebase", "firebaseapp.com", "web.app")),
)


def infer_provider_from_github_deployment(*parts: Any) -> str | None:
    text = _payload_text(*parts)
    for provider, hints in _PROVIDER_HINTS:
        if any(hint in text for hint in hints):
            return provider
    return None


def _effect_for_provider(provider: str) -> str:
    return "pr-preview" if provider in {"vercel", "netlify"} else "deployment"


def _best_status_url(statuses: list[dict[str, Any]]) -> str | None:
    for status in statuses:
        for key in ("environment_url", "target_url", "log_url"):
            value = str(status.get(key) or "").strip()
            if value:
                return value
    return None


class GitHubDeploymentIntegrationObserver:
    """Read-only discovery from GitHub Deployments, statuses, and provider-owned Check Runs."""

    def __init__(
        self,
        token: str | None,
        *,
        api_base: str = "https://api.github.com",
        timeout_seconds: int = 30,
        max_age_days: int = DEFAULT_EXTERNAL_EVIDENCE_MAX_AGE_DAYS,
        include_check_runs: bool = True,
        request_json: Callable[[str], Any] | None = None,
    ) -> None:
        self.token = token
        self.api_base = api_base.rstrip("/")
        self.timeout_seconds = int(timeout_seconds)
        self.max_age_days = max(1, int(max_age_days))
        self.include_check_runs = bool(include_check_runs)
        self._request_json_override = request_json

    def _request_once(self, path: str, *, token: str | None) -> Any:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "uiux-factory-p175",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        request = urllib.request.Request(self.api_base + path, headers=headers, method="GET")
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            body = response.read().decode("utf-8")
        return json.loads(body) if body.strip() else None

    def _request(self, path: str) -> Any:
        if self._request_json_override is not None:
            return self._request_json_override(path)
        try:
            return self._request_once(path, token=self.token)
        except urllib.error.HTTPError as error:
            if self.token and error.code in {401, 403, 404}:
                return self._request_once(path, token=None)
            raise

    @staticmethod
    def _deployment_parts(deployment: dict[str, Any]) -> tuple[Any, ...]:
        creator = deployment.get("creator") or {}
        return (
            creator.get("login"),
            deployment.get("task"),
            deployment.get("environment"),
            deployment.get("original_environment"),
            deployment.get("description"),
            deployment.get("payload"),
        )

    @staticmethod
    def _status_parts(status: dict[str, Any]) -> tuple[Any, ...]:
        creator = status.get("creator") or {}
        return (
            creator.get("login"),
            status.get("description"),
            status.get("environment"),
            status.get("environment_url"),
            status.get("target_url"),
            status.get("log_url"),
        )

    @staticmethod
    def _check_run_parts(check_run: dict[str, Any]) -> tuple[Any, ...]:
        app = check_run.get("app") or {}
        output = check_run.get("output") or {}
        return (
            check_run.get("name"),
            app.get("slug"),
            app.get("name"),
            app.get("html_url"),
            check_run.get("details_url"),
            check_run.get("external_id"),
            output.get("title"),
            output.get("summary"),
            output.get("text"),
        )

    def _discover_check_runs(
        self,
        repository: str,
        *,
        cutoff: datetime,
    ) -> tuple[list[ExternalSideEffectEvidence], int, int, bool]:
        if not self.include_check_runs:
            return [], 0, 0, True
        try:
            repo_meta = self._request(f"/repos/{repository}")
            if not isinstance(repo_meta, dict):
                return [], 0, 0, False
            default_branch = str(repo_meta.get("default_branch") or "").strip()
            if not default_branch:
                return [], 0, 0, False
            encoded = urllib.parse.quote(default_branch, safe="")
            payload = self._request(f"/repos/{repository}/commits/{encoded}/check-runs?per_page=100")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return [], 0, 0, False
        if not isinstance(payload, dict) or not isinstance(payload.get("check_runs"), list):
            return [], 0, 0, False

        evidence: list[ExternalSideEffectEvidence] = []
        inspected = 0
        stale = 0
        for raw in payload["check_runs"]:
            if not isinstance(raw, dict):
                continue
            check_run = dict(raw)
            observed_at = _parse_github_time(
                check_run.get("completed_at")
                or check_run.get("started_at")
                or check_run.get("updated_at")
                or check_run.get("created_at")
            )
            if observed_at is not None and observed_at < cutoff:
                stale += 1
                continue
            provider = infer_provider_from_github_deployment(*self._check_run_parts(check_run))
            if provider is None:
                continue
            inspected += 1
            url = str(check_run.get("details_url") or check_run.get("html_url") or "").strip() or None
            evidence.append(
                ExternalSideEffectEvidence(
                    provider=provider,
                    effect=_effect_for_provider(provider),
                    source="github-check-run",
                    state="observed",
                    url=url,
                    detail=(
                        f"Recent {provider} provider Check Run was observed on the default branch "
                        f"within the {self.max_age_days}-day freshness window."
                    ),
                )
            )
        return evidence, inspected, stale, True

    def discover_repository(
        self,
        repository: str,
        *,
        limit: int = 20,
        now: datetime | None = None,
    ) -> ExternalIntegrationDiscoveryResult:
        current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        cutoff = current - timedelta(days=self.max_age_days)
        count = max(1, min(int(limit), 50))
        query = urllib.parse.urlencode({"per_page": count})

        try:
            deployments = self._request(f"/repos/{repository}/deployments?{query}")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return ExternalIntegrationDiscoveryResult(
                version=EXTERNAL_INTEGRATION_DISCOVERY_VERSION,
                repository=repository,
                inspection_complete=False,
                inspected_deployments=0,
                ignored_stale_deployments=0,
                inspected_check_runs=0,
                ignored_stale_check_runs=0,
                evidence=(),
                unknown_deployment_ids=(),
                reason="GitHub Deployments visibility is unavailable; external integration state is unknown.",
            )
        if not isinstance(deployments, list):
            return ExternalIntegrationDiscoveryResult(
                version=EXTERNAL_INTEGRATION_DISCOVERY_VERSION,
                repository=repository,
                inspection_complete=False,
                inspected_deployments=0,
                ignored_stale_deployments=0,
                inspected_check_runs=0,
                ignored_stale_check_runs=0,
                evidence=(),
                unknown_deployment_ids=(),
                reason="GitHub Deployments returned an unexpected payload; external integration state is unknown.",
            )

        evidence: list[ExternalSideEffectEvidence] = []
        unknown_ids: list[int] = []
        inspected = 0
        stale = 0
        complete = True

        for raw in deployments:
            if not isinstance(raw, dict):
                complete = False
                continue
            deployment = dict(raw)
            deployment_id = int(deployment.get("id") or 0)
            observed_at = _parse_github_time(deployment.get("updated_at") or deployment.get("created_at"))
            if observed_at is not None and observed_at < cutoff:
                stale += 1
                continue
            inspected += 1

            provider = infer_provider_from_github_deployment(*self._deployment_parts(deployment))
            statuses: list[dict[str, Any]] = []
            source = "github-deployment"
            evidence_url = str(deployment.get("url") or "").strip() or None
            if provider is None and deployment_id:
                try:
                    raw_statuses = self._request(f"/repos/{repository}/deployments/{deployment_id}/statuses?per_page=10")
                except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
                    complete = False
                    continue
                if not isinstance(raw_statuses, list):
                    complete = False
                    continue
                statuses = [dict(item) for item in raw_statuses if isinstance(item, dict)]
                for status in statuses:
                    provider = infer_provider_from_github_deployment(*self._status_parts(status))
                    if provider is not None:
                        source = "github-deployment-status"
                        evidence_url = _best_status_url(statuses) or evidence_url
                        break

            if provider is None:
                if deployment_id:
                    unknown_ids.append(deployment_id)
                evidence.append(
                    ExternalSideEffectEvidence(
                        provider="unknown-external",
                        effect="deployment",
                        source="github-deployment",
                        state="observed",
                        url=_best_status_url(statuses) or evidence_url,
                        detail=(
                            f"Recent GitHub deployment {deployment_id or 'unknown'} could not be attributed "
                            "to a registered provider; treat it as external drift until classified."
                        ),
                    )
                )
                continue

            evidence.append(
                ExternalSideEffectEvidence(
                    provider=provider,
                    effect=_effect_for_provider(provider),
                    source=source,
                    state="observed",
                    url=evidence_url,
                    detail=(
                        f"Recent {provider} activity was observed through GitHub deployment "
                        f"{deployment_id or 'metadata'} within the {self.max_age_days}-day freshness window."
                    ),
                )
            )

        check_evidence, inspected_checks, stale_checks, checks_complete = self._discover_check_runs(
            repository,
            cutoff=cutoff,
        )
        evidence.extend(check_evidence)
        complete = complete and checks_complete

        reason = (
            f"GitHub external evidence inspection completed for {repository}; "
            f"{inspected} recent deployment(s) and {inspected_checks} provider Check Run(s) inspected; "
            f"{stale} stale deployment(s) and {stale_checks} stale Check Run(s) ignored."
            if complete
            else "GitHub deployment/status or Check Run inspection was only partially readable; external integration state is unknown."
        )
        return ExternalIntegrationDiscoveryResult(
            version=EXTERNAL_INTEGRATION_DISCOVERY_VERSION,
            repository=repository,
            inspection_complete=complete,
            inspected_deployments=inspected,
            ignored_stale_deployments=stale,
            inspected_check_runs=inspected_checks,
            ignored_stale_check_runs=stale_checks,
            evidence=_dedupe(evidence),
            unknown_deployment_ids=tuple(sorted(set(unknown_ids))),
            reason=reason,
        )
