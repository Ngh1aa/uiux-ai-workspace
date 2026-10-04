from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


P1712_TRANSITION_VERSION = "1.0"
TRANSITION_STATES = frozenset(
    {
        "NEW_BLOCKER",
        "RECOVERED",
        "NEW_CREDENTIAL_GAP",
        "CREDENTIAL_GAP_RESOLVED",
        "UNCHANGED_HEALTHY",
        "UNCHANGED_BLOCKING",
        "BASELINE_NOT_AVAILABLE",
    }
)


@dataclass(frozen=True)
class ProviderTruthRepositoryTransition:
    repository: str
    transition: str
    baseline_state: str | None
    current_state: str
    baseline_blocking: bool | None
    current_blocking: bool
    new_credential_gaps: tuple[str, ...]
    resolved_credential_gaps: tuple[str, ...]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["new_credential_gaps"] = list(self.new_credential_gaps)
        payload["resolved_credential_gaps"] = list(self.resolved_credential_gaps)
        return payload


@dataclass(frozen=True)
class ProviderTruthTransitionReport:
    version: str
    baseline_available: bool
    fleet_transition: str
    baseline_fleet_status: str | None
    current_fleet_status: str
    repository_transitions: tuple[ProviderTruthRepositoryTransition, ...]
    transition_counts: dict[str, int]
    changed_repositories: tuple[str, ...]
    baseline_only_repositories: tuple[str, ...]
    current_only_repositories: tuple[str, ...]
    workflow_blocking: bool
    reason: str
    baseline_source: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "baseline_available": self.baseline_available,
            "fleet_transition": self.fleet_transition,
            "baseline_fleet_status": self.baseline_fleet_status,
            "current_fleet_status": self.current_fleet_status,
            "repository_transitions": [item.to_dict() for item in self.repository_transitions],
            "transition_counts": dict(self.transition_counts),
            "changed_repositories": list(self.changed_repositories),
            "baseline_only_repositories": list(self.baseline_only_repositories),
            "current_only_repositories": list(self.current_only_repositories),
            "workflow_blocking": self.workflow_blocking,
            "reason": self.reason,
            "baseline_source": dict(self.baseline_source) if self.baseline_source is not None else None,
        }


@dataclass(frozen=True)
class _FleetRepository:
    repository: str
    state: str
    blocking: bool
    credential_gap_providers: tuple[str, ...]


def _canonical_repository(value: str) -> str:
    return str(value or "").strip().strip("/").lower()


def _summary_rows(summary: Mapping[str, Any]) -> dict[str, _FleetRepository]:
    rows = summary.get("repositories")
    if not isinstance(rows, list):
        raise ValueError("fleet summary requires repositories[]")

    result: dict[str, _FleetRepository] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise ValueError("fleet repository rows must be objects")
        repository = str(raw.get("repository") or "").strip()
        state = str(raw.get("state") or "").strip()
        blocking = raw.get("blocking")
        gaps = raw.get("credential_gap_providers")
        if not repository or not state or not isinstance(blocking, bool):
            raise ValueError("fleet repository row requires repository/state/blocking")
        if not isinstance(gaps, list) or not all(isinstance(item, str) for item in gaps):
            raise ValueError("fleet repository credential_gap_providers must be a string list")
        key = _canonical_repository(repository)
        if key in result:
            raise ValueError(f"duplicate repository row in fleet summary: {repository}")
        result[key] = _FleetRepository(
            repository=repository,
            state=state,
            blocking=blocking,
            credential_gap_providers=tuple(sorted(set(gaps))),
        )
    return result


def _fleet_status(summary: Mapping[str, Any]) -> tuple[str, bool]:
    status = str(summary.get("status") or "").strip()
    passed = summary.get("passed")
    if not status or not isinstance(passed, bool):
        raise ValueError("fleet summary requires status and boolean passed")
    return status, passed


def _repository_transition(
    current: _FleetRepository,
    baseline: _FleetRepository | None,
) -> ProviderTruthRepositoryTransition:
    if baseline is None:
        return ProviderTruthRepositoryTransition(
            repository=current.repository,
            transition="BASELINE_NOT_AVAILABLE",
            baseline_state=None,
            current_state=current.state,
            baseline_blocking=None,
            current_blocking=current.blocking,
            new_credential_gaps=(),
            resolved_credential_gaps=(),
            reason="No baseline repository record exists for the current fleet member.",
        )

    baseline_gaps = set(baseline.credential_gap_providers)
    current_gaps = set(current.credential_gap_providers)
    new_gaps = tuple(sorted(current_gaps - baseline_gaps))
    resolved_gaps = tuple(sorted(baseline_gaps - current_gaps))

    if current.blocking and not baseline.blocking:
        transition = "NEW_BLOCKER"
        reason = "Repository changed from non-blocking provider truth to a blocking condition."
    elif baseline.blocking and not current.blocking:
        transition = "RECOVERED"
        reason = "Repository recovered from a blocking provider-truth condition."
    elif current.blocking and baseline.blocking:
        transition = "UNCHANGED_BLOCKING"
        reason = "Repository remains in a blocking provider-truth condition."
    elif new_gaps:
        transition = "NEW_CREDENTIAL_GAP"
        reason = "New optional provider credential gaps appeared: " + ", ".join(new_gaps) + "."
    elif resolved_gaps:
        transition = "CREDENTIAL_GAP_RESOLVED"
        reason = "Optional provider credential gaps were resolved: " + ", ".join(resolved_gaps) + "."
    else:
        transition = "UNCHANGED_HEALTHY"
        reason = "Repository remains non-blocking with no credential-gap transition."

    return ProviderTruthRepositoryTransition(
        repository=current.repository,
        transition=transition,
        baseline_state=baseline.state,
        current_state=current.state,
        baseline_blocking=baseline.blocking,
        current_blocking=current.blocking,
        new_credential_gaps=new_gaps,
        resolved_credential_gaps=resolved_gaps,
        reason=reason,
    )


def _fleet_transition(
    *,
    current_status: str,
    current_passed: bool,
    baseline_status: str | None,
    baseline_passed: bool | None,
    current_rows: Mapping[str, _FleetRepository],
    baseline_rows: Mapping[str, _FleetRepository],
    baseline_available: bool,
) -> str:
    if not baseline_available:
        return "BASELINE_NOT_AVAILABLE"
    if current_passed is False and baseline_passed is True:
        return "NEW_BLOCKER"
    if current_passed is True and baseline_passed is False:
        return "RECOVERED"
    if current_passed is False and baseline_passed is False:
        return "UNCHANGED_BLOCKING"

    baseline_degraded = {
        key
        for key, row in baseline_rows.items()
        if not row.blocking and row.credential_gap_providers
    }
    current_degraded = {
        key
        for key, row in current_rows.items()
        if not row.blocking and row.credential_gap_providers
    }
    if current_degraded - baseline_degraded:
        return "NEW_CREDENTIAL_GAP"
    if baseline_degraded - current_degraded:
        return "CREDENTIAL_GAP_RESOLVED"
    return "UNCHANGED_HEALTHY"


def build_provider_truth_transition_report(
    current_summary: Mapping[str, Any],
    baseline_summary: Mapping[str, Any] | None,
    *,
    baseline_source: Mapping[str, Any] | None = None,
) -> ProviderTruthTransitionReport:
    current_status, current_passed = _fleet_status(current_summary)
    current_rows = _summary_rows(current_summary)

    baseline_available = baseline_summary is not None
    baseline_status: str | None = None
    baseline_passed: bool | None = None
    baseline_rows: dict[str, _FleetRepository] = {}
    if baseline_summary is not None:
        baseline_status, baseline_passed = _fleet_status(baseline_summary)
        baseline_rows = _summary_rows(baseline_summary)

    transitions = tuple(
        _repository_transition(current_rows[key], baseline_rows.get(key))
        for key in sorted(current_rows)
    )

    counts = {state: 0 for state in sorted(TRANSITION_STATES)}
    for item in transitions:
        counts[item.transition] += 1

    changed_states = {
        "NEW_BLOCKER",
        "RECOVERED",
        "NEW_CREDENTIAL_GAP",
        "CREDENTIAL_GAP_RESOLVED",
    }
    changed = tuple(
        sorted(item.repository for item in transitions if item.transition in changed_states)
    )

    current_keys = set(current_rows)
    baseline_keys = set(baseline_rows)
    current_only = tuple(sorted(current_rows[key].repository for key in current_keys - baseline_keys))
    baseline_only = tuple(sorted(baseline_rows[key].repository for key in baseline_keys - current_keys))

    fleet_transition = _fleet_transition(
        current_status=current_status,
        current_passed=current_passed,
        baseline_status=baseline_status,
        baseline_passed=baseline_passed,
        current_rows=current_rows,
        baseline_rows=baseline_rows,
        baseline_available=baseline_available,
    )

    if not baseline_available:
        reason = (
            "No previous successfully produced P1.7.11 fleet summary artifact is available. "
            "The current snapshot becomes observational evidence only; P1.7.12 remains non-blocking."
        )
    elif changed:
        reason = "Historical provider-truth changes detected for: " + ", ".join(changed) + "."
    else:
        reason = "No material provider-truth transition was detected relative to the previous fleet summary."

    return ProviderTruthTransitionReport(
        version=P1712_TRANSITION_VERSION,
        baseline_available=baseline_available,
        fleet_transition=fleet_transition,
        baseline_fleet_status=baseline_status,
        current_fleet_status=current_status,
        repository_transitions=transitions,
        transition_counts=counts,
        changed_repositories=changed,
        baseline_only_repositories=baseline_only,
        current_only_repositories=current_only,
        workflow_blocking=False,
        reason=reason,
        baseline_source=baseline_source,
    )


def load_json_object(path: Path | str) -> dict[str, Any]:
    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON artifact {source}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"JSON artifact {source} must contain an object")
    return payload


def write_provider_truth_transition_report(
    *,
    current_summary_path: Path | str,
    output_path: Path | str,
    baseline_summary_path: Path | str | None = None,
    baseline_source_path: Path | str | None = None,
) -> ProviderTruthTransitionReport:
    current = load_json_object(current_summary_path)
    baseline = None
    if baseline_summary_path is not None and Path(baseline_summary_path).is_file():
        baseline = load_json_object(baseline_summary_path)

    baseline_source = None
    if baseline_source_path is not None and Path(baseline_source_path).is_file():
        baseline_source = load_json_object(baseline_source_path)

    report = build_provider_truth_transition_report(
        current,
        baseline,
        baseline_source=baseline_source,
    )
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
