from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from core.contracts.release_evidence_schema import (
    ReleaseEvidenceArtifact,
    ReleaseEvidenceClaim,
    ReleaseEvidenceManifest,
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stable_id(kind: str, path: str, digest: str) -> str:
    raw = f"{kind}\n{path}\n{digest}".encode("utf-8")
    return "REL-" + hashlib.sha256(raw).hexdigest()[:16]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _state_report_passed(payload: dict) -> bool | None:
    if isinstance(payload.get("failures"), list):
        return len(payload["failures"]) == 0
    summary = payload.get("summary")
    if isinstance(summary, dict):
        if "failures" in summary:
            return int(summary.get("failures") or 0) == 0
        if "failed" in summary:
            return int(summary.get("failed") or 0) == 0
    checks = payload.get("checks")
    if isinstance(checks, list) and checks:
        failed = [item for item in checks if isinstance(item, dict) and item.get("passed") is False]
        return len(failed) == 0
    return None


def build_release_evidence_manifest(
    *,
    target_repository: str,
    target_sha: str,
    artifacts: Iterable[tuple[str, Path]],
    generated_at: str | None = None,
) -> ReleaseEvidenceManifest:
    records: list[ReleaseEvidenceArtifact] = []
    claims: list[ReleaseEvidenceClaim] = []
    warnings: list[str] = []
    by_kind: dict[str, list[ReleaseEvidenceArtifact]] = {}
    parsed: dict[str, list[dict]] = {}

    for kind, raw_path in artifacts:
        path = Path(raw_path)
        if not path.is_file():
            warnings.append(f"Missing evidence artifact: {kind} -> {path}")
            continue
        data = path.read_bytes()
        digest = _sha256(data)
        record = ReleaseEvidenceArtifact(
            evidence_id=_stable_id(kind, str(path), digest),
            kind=kind,
            path=str(path),
            sha256=digest,
            size_bytes=len(data),
            state="VERIFIED",
            claims=[],
        )
        records.append(record)
        by_kind.setdefault(kind, []).append(record)
        if path.suffix.lower() == ".json":
            try:
                parsed.setdefault(kind, []).append(_load_json(path))
            except (ValueError, OSError) as exc:
                warnings.append(f"Could not parse JSON evidence {path}: {exc}")

    state_records = by_kind.get("state_coverage_report", [])
    state_payloads = parsed.get("state_coverage_report", [])
    if state_records and state_payloads:
        result = _state_report_passed(state_payloads[-1])
        state = "VERIFIED" if result is True else "FAILED" if result is False else "UNKNOWN"
        claims.append(ReleaseEvidenceClaim(
            claim="state_coverage",
            state=state,
            evidence_ids=[record.evidence_id for record in state_records],
            detail="Semantic state coverage report is green." if state == "VERIFIED" else "State coverage did not provide a verified green result.",
        ))
    else:
        claims.append(ReleaseEvidenceClaim(claim="state_coverage", state="UNKNOWN", detail="No state coverage report registered."))

    browser_records = by_kind.get("browser_qa", []) + by_kind.get("browser_evidence", [])
    claims.append(ReleaseEvidenceClaim(
        claim="browser_qa_artifacts",
        state="VERIFIED" if browser_records else "UNKNOWN",
        evidence_ids=[record.evidence_id for record in browser_records],
        detail="Browser QA artifacts are integrity-hashed; semantic pass/fail remains owned by their originating gate." if browser_records else "No browser QA artifacts registered.",
    ))

    deployment_records = by_kind.get("deployment_truth", [])
    deployment_payloads = parsed.get("deployment_truth", [])
    release_classification = "UNKNOWN"
    if deployment_records and deployment_payloads:
        payload = deployment_payloads[-1]
        release_classification = str(payload.get("classification") or "UNKNOWN")
        expected = str(payload.get("expected_sha") or "")
        verified = bool(payload.get("verified")) and release_classification == "DEPLOYED_VERIFIED"
        if expected and not (target_sha == expected or target_sha.startswith(expected) or expected.startswith(target_sha)):
            verified = False
            release_classification = "DEPLOY_FAILED"
            warnings.append(f"Deployment truth expected SHA {expected} does not match registry target SHA {target_sha}.")
        claims.append(ReleaseEvidenceClaim(
            claim="deployment_truth",
            state="VERIFIED" if verified else "FAILED" if release_classification in {"PRODUCT_QA_FAILED", "BUILD_FAILED", "DEPLOY_FAILED", "AUTH_BLOCKED"} else "UNKNOWN",
            evidence_ids=[record.evidence_id for record in deployment_records],
            detail=f"Deployment truth classification: {release_classification}.",
        ))
    else:
        claims.append(ReleaseEvidenceClaim(claim="deployment_truth", state="UNKNOWN", detail="No deployment truth artifact registered."))

    release_verified = release_classification == "DEPLOYED_VERIFIED" and all(
        claim.state == "VERIFIED" for claim in claims if claim.claim in {"state_coverage", "deployment_truth"}
    )
    claims.append(ReleaseEvidenceClaim(
        claim="release_ready",
        state="VERIFIED" if release_verified else "UNKNOWN",
        evidence_ids=[record.evidence_id for record in records],
        detail="Release has verified product-state and deployment evidence." if release_verified else "Release remains unverified until required product/deployment claims are verified.",
    ))

    return ReleaseEvidenceManifest(
        target_repository=target_repository.strip(),
        target_sha=target_sha.strip(),
        generated_at=generated_at or datetime.now(timezone.utc).isoformat(),
        release_classification=release_classification,
        artifacts=records,
        claims=claims,
        warnings=warnings,
    )
