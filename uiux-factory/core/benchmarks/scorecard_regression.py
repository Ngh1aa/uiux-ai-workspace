from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.brain_os.critics.core_design import CoreCriticReport
from core.brain_os.critique_contracts import CritiqueIssue, CritiqueIssueStatus, CritiqueSeverity
from core.brain_os.reasoning.evidence_integrity import (
    EvidenceIntegrityFinding,
    EvidenceIntegrityReport,
    IntegrityCode,
    IntegritySeverity,
)
from core.brain_os.scorecard import (
    ScorecardCriticInput,
    ScorecardIntegrityInput,
    build_brain_scorecard,
)
from core.evaluation.run_evaluator import RunEvaluation


@dataclass(frozen=True)
class ScorecardBenchmarkResult:
    case_id: str
    passed: bool
    detail: str


def load_scorecard_benchmark(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("cases"), list):
        raise ValueError("scorecard benchmark corpus must contain a cases list")
    if not str(payload.get("version", "")).strip():
        raise ValueError("scorecard benchmark corpus version is required")
    return payload


def _runtime(case_id: str, outcome: str) -> RunEvaluation:
    state = "COMPLETED"
    if outcome == "failed":
        state = "FAILED"
    elif outcome == "blocked":
        state = "BLOCKED"
    return RunEvaluation(
        schema_version=1,
        run_id=f"run-{case_id}",
        flow_id="page-ui-work",
        flow_revision=1,
        managed_state=state,
        outcome=outcome,
        evaluated_at="2026-10-02T00:00:00+00:00",
        signature={"change_surface": "PAGE"},
        completed_stage_count=1,
        stage_count=1,
        replan_count=0,
        effective_evidence_count=1,
        status_counts={},
        evidence_type_counts={},
        passing_evidence_types=[],
        failing_channels=[],
        reasons=["benchmark fixture"],
        memory_eligible=False,
    )


def _critic_report(case_id: str, severities: list[str]) -> CoreCriticReport:
    issues = [
        CritiqueIssue(
            id=f"CR-{case_id}-{index}",
            critic="ux_ia",
            category="ux_ia.benchmark",
            severity=CritiqueSeverity(severity),
            status=CritiqueIssueStatus.OBSERVED,
            summary=f"Benchmark issue {index}",
            rationale="Deterministic scorecard benchmark fixture",
        )
        for index, severity in enumerate(severities, start=1)
    ]
    return CoreCriticReport(
        critic_id="ux_ia",
        issues=issues,
        reviewed_artifacts=["benchmark"],
        source_owner="scorecard-benchmark-fixture",
    )


def _integrity_report(case_id: str, state: str) -> EvidenceIntegrityReport:
    if state == "valid":
        return EvidenceIntegrityReport(
            graph_id=f"graph-{case_id}",
            integrity_valid=True,
            lineage_complete=True,
            findings=[],
        )
    if state == "warning":
        return EvidenceIntegrityReport(
            graph_id=f"graph-{case_id}",
            integrity_valid=True,
            lineage_complete=False,
            findings=[
                EvidenceIntegrityFinding(
                    code=IntegrityCode.LINEAGE_INCOMPLETE,
                    severity=IntegritySeverity.WARNING,
                    subject_ref="RETEST_REQUIREMENT",
                    detail="Benchmark warning",
                )
            ],
        )
    if state == "error":
        return EvidenceIntegrityReport(
            graph_id=f"graph-{case_id}",
            integrity_valid=False,
            lineage_complete=False,
            findings=[
                EvidenceIntegrityFinding(
                    code=IntegrityCode.CANONICAL_REF_MISSING,
                    severity=IntegritySeverity.ERROR,
                    subject_ref="runtime:missing",
                    detail="Benchmark integrity error",
                )
            ],
        )
    raise ValueError(f"unsupported integrity_state: {state}")


def evaluate_scorecard_case(case: dict[str, Any]) -> ScorecardBenchmarkResult:
    case_id = str(case.get("id", "")).strip()
    if not case_id:
        return ScorecardBenchmarkResult("<missing>", False, "case id is required")
    outcome = str(case.get("runtime_outcome", "")).strip()
    severities = [str(item) for item in case.get("critic_severities", [])]
    integrity_state = str(case.get("integrity_state", "valid"))
    expected_rejected = bool(case.get("expected_rejected", False))
    runtime_ref = f"runtime:{case_id}"
    critic_ref = f"critic:{case_id}"
    integrity_ref = critic_ref if case.get("duplicate_source_ref") else f"integrity:{case_id}"

    try:
        scorecard = build_brain_scorecard(
            runtime_evaluation=_runtime(case_id, outcome),
            runtime_source_ref=runtime_ref,
            critic_inputs=[
                ScorecardCriticInput(
                    source_ref=critic_ref,
                    report=_critic_report(case_id, severities),
                )
            ],
            integrity_inputs=[
                ScorecardIntegrityInput(
                    source_ref=integrity_ref,
                    report=_integrity_report(case_id, integrity_state),
                )
            ],
        )
    except ValueError as exc:
        if expected_rejected:
            return ScorecardBenchmarkResult(case_id, True, f"rejected as expected: {exc}")
        return ScorecardBenchmarkResult(case_id, False, f"unexpected rejection: {exc}")

    if expected_rejected:
        return ScorecardBenchmarkResult(case_id, False, "expected provenance rejection but scorecard was built")

    expected_outcome = str(case.get("expected_runtime_outcome", ""))
    if scorecard.runtime_outcome != expected_outcome:
        return ScorecardBenchmarkResult(
            case_id,
            False,
            f"runtime outcome changed: expected={expected_outcome} actual={scorecard.runtime_outcome}",
        )

    actual_p0 = sum(channel.severity_counts.get("P0", 0) for channel in scorecard.critic_channels)
    expected_p0 = int(case.get("expected_p0", 0))
    if actual_p0 != expected_p0:
        return ScorecardBenchmarkResult(case_id, False, f"P0 count mismatch: {actual_p0} != {expected_p0}")

    expected_integrity = bool(case.get("expected_integrity_valid", True))
    actual_integrity = scorecard.integrity_channels[0].integrity_valid
    if actual_integrity != expected_integrity:
        return ScorecardBenchmarkResult(
            case_id,
            False,
            f"integrity flag mismatch: {actual_integrity} != {expected_integrity}",
        )

    if any(
        value != "none"
        for value in (
            scorecard.authority_effect,
            scorecard.gate_effect,
            scorecard.evidence_effect,
            scorecard.release_effect,
        )
    ):
        return ScorecardBenchmarkResult(case_id, False, "scorecard gained authority/gate/evidence/release effect")

    return ScorecardBenchmarkResult(case_id, True, "scorecard boundary preserved")


def evaluate_scorecard_benchmark(path: Path) -> list[ScorecardBenchmarkResult]:
    payload = load_scorecard_benchmark(path)
    return [evaluate_scorecard_case(dict(case)) for case in payload["cases"]]
