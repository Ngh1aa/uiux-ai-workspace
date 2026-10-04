from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping


P1712_BASELINE_VERSION = "1.0"
P1712_FLEET_ARTIFACT_NAME = "p1711-provider-truth-fleet-summary"


@dataclass(frozen=True)
class ProviderTruthBaselineSelection:
    version: str
    baseline_available: bool
    current_run_id: int
    baseline_run_id: int | None
    baseline_artifact_id: int | None
    baseline_event: str | None
    baseline_created_at: str | None
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def select_previous_fleet_artifact(
    *,
    current_run_id: int,
    runs: Iterable[Mapping[str, Any]],
    artifacts_by_run: Mapping[int, Iterable[Mapping[str, Any]]],
) -> ProviderTruthBaselineSelection:
    for run in runs:
        try:
            run_id = int(run.get("id"))
        except (TypeError, ValueError):
            continue
        if run_id == current_run_id:
            continue
        if str(run.get("status") or "") != "completed":
            continue
        event = str(run.get("event") or "")
        if event not in {"schedule", "workflow_dispatch"}:
            continue

        for artifact in artifacts_by_run.get(run_id, ()):
            if str(artifact.get("name") or "") != P1712_FLEET_ARTIFACT_NAME:
                continue
            if bool(artifact.get("expired", False)):
                continue
            try:
                artifact_id = int(artifact.get("id"))
            except (TypeError, ValueError):
                continue
            return ProviderTruthBaselineSelection(
                version=P1712_BASELINE_VERSION,
                baseline_available=True,
                current_run_id=current_run_id,
                baseline_run_id=run_id,
                baseline_artifact_id=artifact_id,
                baseline_event=event,
                baseline_created_at=str(run.get("created_at") or "") or None,
                reason=(
                    "Selected the newest previous schedule/manual run that successfully produced "
                    "a non-expired P1.7.11 fleet summary artifact."
                ),
            )

    return ProviderTruthBaselineSelection(
        version=P1712_BASELINE_VERSION,
        baseline_available=False,
        current_run_id=current_run_id,
        baseline_run_id=None,
        baseline_artifact_id=None,
        baseline_event=None,
        baseline_created_at=None,
        reason=(
            "No previous schedule/manual run with a non-expired P1.7.11 fleet summary artifact was found. "
            "This is an expected first-run state."
        ),
    )
