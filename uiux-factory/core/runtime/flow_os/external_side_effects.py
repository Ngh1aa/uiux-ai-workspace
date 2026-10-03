from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable


EXTERNAL_SIDE_EFFECT_VERSION = "1.0"


class PreviewPolicy(str, Enum):
    PR_PREVIEW_ALLOWED = "pr-preview-allowed"
    ZERO_DEPLOY_STRICT = "zero-deploy-strict"


class ExternalSideEffectBlocked(RuntimeError):
    """Raised before remote mutation when the selected side-effect policy cannot be satisfied."""


@dataclass(frozen=True)
class ExternalSideEffectEvidence:
    provider: str
    effect: str
    source: str
    state: str
    url: str | None = None
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalSideEffectAssessment:
    version: str
    repository: str
    policy: str
    status: str
    mutation_allowed: bool
    inspection_complete: bool
    evidence: tuple[ExternalSideEffectEvidence, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence"] = [item.to_dict() for item in self.evidence]
        return payload

    def require_mutation_allowed(self) -> None:
        if not self.mutation_allowed:
            raise ExternalSideEffectBlocked(self.reason)


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


def _read_lower(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace").lower()
    except OSError:
        return ""


def detect_static_integrations(repo_root: Path | str) -> tuple[ExternalSideEffectEvidence, ...]:
    """Detect repository-visible integration signals without mutating the target."""
    root = Path(repo_root)
    evidence: list[ExternalSideEffectEvidence] = []

    file_markers: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
        (
            "vercel",
            "pr-preview",
            ("vercel.json", ".vercel/project.json"),
            "Vercel configuration is present in the repository.",
        ),
        (
            "netlify",
            "pr-preview",
            ("netlify.toml",),
            "Netlify configuration is present in the repository.",
        ),
        (
            "render",
            "deployment",
            ("render.yaml", "render.yml"),
            "Render deployment configuration is present in the repository.",
        ),
        (
            "railway",
            "deployment",
            ("railway.json", "railway.toml"),
            "Railway deployment configuration is present in the repository.",
        ),
        (
            "cloudflare",
            "deployment",
            ("wrangler.toml", "wrangler.json", "wrangler.jsonc"),
            "Cloudflare Wrangler deployment configuration is present in the repository.",
        ),
    )
    for provider, effect, relative_paths, detail in file_markers:
        present = [relative_path for relative_path in relative_paths if (root / relative_path).is_file()]
        if present:
            evidence.append(
                ExternalSideEffectEvidence(
                    provider=provider,
                    effect=effect,
                    source="repository-static-config",
                    state="configured",
                    detail=f"{detail} Marker(s): {', '.join(present)}",
                )
            )

    firebase = root / "firebase.json"
    if firebase.is_file() and '"hosting"' in _read_lower(firebase):
        evidence.append(
            ExternalSideEffectEvidence(
                provider="firebase-hosting",
                effect="deployment",
                source="repository-static-config",
                state="configured",
                detail="Firebase Hosting configuration is present in firebase.json.",
            )
        )

    workflows = root / ".github" / "workflows"
    if workflows.is_dir():
        markers = (
            "actions/configure-pages",
            "actions/upload-pages-artifact",
            "actions/deploy-pages",
            "pages-build-deployment",
            "peaceiris/actions-gh-pages",
            "github-pages",
        )
        for path in sorted(workflows.glob("*.y*ml")):
            text = _read_lower(path)
            if any(marker in text for marker in markers):
                evidence.append(
                    ExternalSideEffectEvidence(
                        provider="github-pages",
                        effect="deployment",
                        source=f"workflow:{path.relative_to(root).as_posix()}",
                        state="configured",
                        detail="A GitHub Pages deployment workflow is present.",
                    )
                )
    return _dedupe(evidence)


def assess_external_side_effects(
    repository: str,
    policy: PreviewPolicy | str,
    evidence: Iterable[ExternalSideEffectEvidence],
    *,
    inspection_complete: bool,
) -> ExternalSideEffectAssessment:
    policy_value = PreviewPolicy(policy)
    items = _dedupe(evidence)
    observed = any(item.state == "observed" for item in items)

    if items:
        if policy_value is PreviewPolicy.ZERO_DEPLOY_STRICT:
            return ExternalSideEffectAssessment(
                version=EXTERNAL_SIDE_EFFECT_VERSION,
                repository=repository,
                policy=policy_value.value,
                status="BLOCKED_EXTERNAL_SIDE_EFFECT",
                mutation_allowed=False,
                inspection_complete=inspection_complete,
                evidence=items,
                reason=(
                    "zero-deploy-strict forbids remote mutation because an external preview/deployment "
                    "integration is configured or has been observed"
                ),
            )
        return ExternalSideEffectAssessment(
            version=EXTERNAL_SIDE_EFFECT_VERSION,
            repository=repository,
            policy=policy_value.value,
            status="PREVIEW_OBSERVED" if observed else "PREVIEW_EXPECTED",
            mutation_allowed=True,
            inspection_complete=inspection_complete,
            evidence=items,
            reason="PR preview side effects are explicitly allowed and must remain evidence-backed.",
        )

    if not inspection_complete:
        if policy_value is PreviewPolicy.ZERO_DEPLOY_STRICT:
            return ExternalSideEffectAssessment(
                version=EXTERNAL_SIDE_EFFECT_VERSION,
                repository=repository,
                policy=policy_value.value,
                status="UNKNOWN_EXTERNAL_SIDE_EFFECT",
                mutation_allowed=False,
                inspection_complete=False,
                evidence=(),
                reason="zero-deploy-strict requires proof that external preview/deployment integrations are absent.",
            )
        return ExternalSideEffectAssessment(
            version=EXTERNAL_SIDE_EFFECT_VERSION,
            repository=repository,
            policy=policy_value.value,
            status="UNKNOWN_EXTERNAL_SIDE_EFFECT",
            mutation_allowed=True,
            inspection_complete=False,
            evidence=(),
            reason="External integration visibility is incomplete; preview-allowed policy may proceed with UNKNOWN evidence.",
        )

    return ExternalSideEffectAssessment(
        version=EXTERNAL_SIDE_EFFECT_VERSION,
        repository=repository,
        policy=policy_value.value,
        status="NONE_DETECTED",
        mutation_allowed=True,
        inspection_complete=True,
        evidence=(),
        reason="No external preview/deployment integration was detected by the completed inspection.",
    )


class GitHubExternalSideEffectObserver:
    """Read-only GitHub observer for external preview evidence in PR conversations."""

    def __init__(self, token: str | None, *, api_base: str = "https://api.github.com", timeout_seconds: int = 30) -> None:
        self.token = token
        self.api_base = api_base.rstrip("/")
        self.timeout_seconds = int(timeout_seconds)

    def _request(self, path: str) -> Any:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "uiux-factory-p172",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(self.api_base + path, headers=headers, method="GET")
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            body = response.read().decode("utf-8")
        return json.loads(body) if body.strip() else None

    @staticmethod
    def _comment_evidence(comment: dict[str, Any], *, pr_url: str) -> ExternalSideEffectEvidence | None:
        login = str((comment.get("user") or {}).get("login") or "").lower()
        body = str(comment.get("body") or "")
        body_lower = body.lower()
        comment_url = str(comment.get("html_url") or pr_url)
        if login == "vercel[bot]" or ("vercel" in login and "preview" in body_lower):
            return ExternalSideEffectEvidence(
                provider="vercel",
                effect="pr-preview",
                source="github-pr-comment",
                state="observed",
                url=comment_url,
                detail="Vercel PR preview activity was observed in the GitHub conversation.",
            )
        if login == "netlify[bot]" or ("netlify" in login and ("preview" in body_lower or "deploy" in body_lower)):
            return ExternalSideEffectEvidence(
                provider="netlify",
                effect="pr-preview",
                source="github-pr-comment",
                state="observed",
                url=comment_url,
                detail="Netlify PR preview activity was observed in the GitHub conversation.",
            )
        if login == "github-actions[bot]" and ("github pages" in body_lower or "pages deployment" in body_lower):
            return ExternalSideEffectEvidence(
                provider="github-pages",
                effect="deployment",
                source="github-pr-comment",
                state="observed",
                url=comment_url,
                detail="GitHub Pages deployment activity was observed in the GitHub conversation.",
            )
        return None

    def observe_pull_request(self, repository: str, pr_number: int) -> tuple[tuple[ExternalSideEffectEvidence, ...], bool]:
        try:
            comments = self._request(f"/repos/{repository}/issues/{int(pr_number)}/comments?per_page=100")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return (), False
        if not isinstance(comments, list):
            return (), False
        pr_url = f"https://github.com/{repository}/pull/{int(pr_number)}"
        evidence = [self._comment_evidence(dict(comment), pr_url=pr_url) for comment in comments if isinstance(comment, dict)]
        return _dedupe(item for item in evidence if item is not None), True

    def inspect_recent_pull_requests(
        self,
        repository: str,
        *,
        limit: int = 20,
    ) -> tuple[tuple[ExternalSideEffectEvidence, ...], bool]:
        count = max(1, min(int(limit), 50))
        query = urllib.parse.urlencode({"state": "all", "sort": "updated", "direction": "desc", "per_page": count})
        try:
            pulls = self._request(f"/repos/{repository}/pulls?{query}")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return (), False
        if not isinstance(pulls, list):
            return (), False
        collected: list[ExternalSideEffectEvidence] = []
        complete = True
        for pull in pulls:
            if not isinstance(pull, dict) or pull.get("number") is None:
                continue
            evidence, ok = self.observe_pull_request(repository, int(pull["number"]))
            collected.extend(evidence)
            complete = complete and ok
        return _dedupe(collected), complete
