from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from core.runtime.flow_os.repository_policy_registry import registered_repository_policies


P1711_FLEET_SUMMARY_VERSION = "1.0"


@dataclass(frozen=True)
class ProviderTruthFleetRepository:
    repository: str
    state: str
    blocking: bool
    canonical_status: str
    credential_gap_providers: tuple[str, ...]
    source: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["credential_gap_providers"] = list(self.credential_gap_providers)
        return payload


@dataclass(frozen=True)
class ProviderTruthFleetSummary:
    version: str
    status: str
    passed: bool
    expected_repositories: tuple[str, ...]
    observed_repositories: tuple[str, ...]
    missing_repositories: tuple[str, ...]
    duplicate_repositories: tuple[str, ...]
    blocking_repositories: tuple[str, ...]
    degraded_repositories: tuple[str, ...]
    healthy_repositories: tuple[str, ...]
    repositories: tuple[ProviderTruthFleetRepository, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "status": self.status,
            "passed": self.passed,
            "expected_repositories": list(self.expected_repositories),
            "observed_repositories": list(self.observed_repositories),
            "missing_repositories": list(self.missing_repositories),
            "duplicate_repositories": list(self.duplicate_repositories),
            "blocking_repositories": list(self.blocking_repositories),
            "degraded_repositories": list(self.degraded_repositories),
            "healthy_repositories": list(self.healthy_repositories),
            "repositories": [item.to_dict() for item in self.repositories],
            "reason": self.reason,
        }


def _canonical_repository(value: str) -> str:
    return str(value or "").strip().strip("/").lower()


def _parse_report(path: Path) -> ProviderTruthFleetRepository:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid P1.7.10 report {path}: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise ValueError(f"invalid P1.7.10 report {path}: root must be an object")

    repository = str(payload.get("repository") or "").strip()
    monitoring = payload.get("monitoring")
    if not repository or not isinstance(monitoring, Mapping):
        raise ValueError(f"invalid P1.7.10 report {path}: repository/monitoring missing")

    state = str(monitoring.get("state") or "").strip()
    canonical_status = str(monitoring.get("canonical_status") or "").strip()
    blocking = monitoring.get("blocking")
    credential_gaps = monitoring.get("credential_gap_providers")
    if not state or not canonical_status or not isinstance(blocking, bool):
        raise ValueError(f"invalid P1.7.10 report {path}: monitoring disposition incomplete")
    if not isinstance(credential_gaps, list) or not all(isinstance(item, str) for item in credential_gaps):
        raise ValueError(f"invalid P1.7.10 report {path}: credential_gap_providers must be a string list")

    return ProviderTruthFleetRepository(
        repository=repository,
        state=state,
        blocking=blocking,
        canonical_status=canonical_status,
        credential_gap_providers=tuple(sorted(set(credential_gaps))),
        source=str(path),
    )


def build_provider_truth_fleet_summary(
    reports: Iterable[ProviderTruthFleetRepository],
    *,
    expected_repositories: Iterable[str] | None = None,
) -> ProviderTruthFleetSummary:
    expected = tuple(
        policy.repository for policy in registered_repository_policies()
    ) if expected_repositories is None else tuple(str(value).strip() for value in expected_repositories if str(value).strip())
    expected_by_key = {_canonical_repository(value): value for value in expected}

    grouped: dict[str, list[ProviderTruthFleetRepository]] = {}
    for report in reports:
        grouped.setdefault(_canonical_repository(report.repository), []).append(report)

    observed_keys = set(grouped)
    expected_keys = set(expected_by_key)
    missing = tuple(sorted(expected_by_key[key] for key in expected_keys - observed_keys))
    duplicate = tuple(
        sorted(items[0].repository for items in grouped.values() if len(items) > 1)
    )

    unique_reports = tuple(
        sorted(
            (items[0] for items in grouped.values()),
            key=lambda item: _canonical_repository(item.repository),
        )
    )
    blocking = tuple(sorted(item.repository for item in unique_reports if item.blocking))
    degraded = tuple(
        sorted(
            item.repository
            for item in unique_reports
            if not item.blocking and item.state == "DEGRADED_MISSING_OPTIONAL_CREDENTIALS"
        )
    )
    healthy = tuple(
        sorted(
            item.repository
            for item in unique_reports
            if not item.blocking and item.repository not in degraded
        )
    )

    unexpected = tuple(
        sorted(items[0].repository for key, items in grouped.items() if key not in expected_keys)
    )

    if duplicate:
        status = "BLOCKED_DUPLICATE_REPOSITORY_REPORT"
        passed = False
        reason = "Multiple P1.7.10 reports exist for: " + ", ".join(duplicate) + "."
    elif missing:
        status = "BLOCKED_INCOMPLETE_FLEET_EVIDENCE"
        passed = False
        reason = "Scheduled fleet evidence is missing registered repositories: " + ", ".join(missing) + "."
    elif unexpected:
        status = "BLOCKED_UNREGISTERED_FLEET_REPORT"
        passed = False
        reason = "Fleet artifacts contain unregistered repositories: " + ", ".join(unexpected) + "."
    elif blocking:
        status = "ACTION_REQUIRED_FLEET_PROVIDER_TRUTH"
        passed = False
        reason = "One or more registered repositories require provider-truth action: " + ", ".join(blocking) + "."
    elif degraded:
        status = "FLEET_HEALTHY_WITH_OPTIONAL_CREDENTIAL_GAPS"
        passed = True
        reason = (
            "All registered repositories completed scheduled monitoring. Optional provider credentials reduce "
            "provider-native coverage for: " + ", ".join(degraded) + "."
        )
    else:
        status = "FLEET_HEALTHY_VERIFIED"
        passed = True
        reason = "All registered repositories completed scheduled monitoring without blocking provider-truth conditions."

    return ProviderTruthFleetSummary(
        version=P1711_FLEET_SUMMARY_VERSION,
        status=status,
        passed=passed,
        expected_repositories=tuple(expected),
        observed_repositories=tuple(sorted(item.repository for item in unique_reports)),
        missing_repositories=missing,
        duplicate_repositories=duplicate,
        blocking_repositories=blocking,
        degraded_repositories=degraded,
        healthy_repositories=healthy,
        repositories=unique_reports,
        reason=reason,
    )


def load_provider_truth_fleet_reports(root: Path | str) -> tuple[ProviderTruthFleetRepository, ...]:
    base = Path(root)
    paths = sorted(base.rglob("p1710-continuous-provider-truth-*.json"))
    return tuple(_parse_report(path) for path in paths)


def write_provider_truth_fleet_summary(
    *,
    input_dir: Path | str,
    output_path: Path | str,
) -> ProviderTruthFleetSummary:
    reports = load_provider_truth_fleet_reports(input_dir)
    summary = build_provider_truth_fleet_summary(reports)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary
