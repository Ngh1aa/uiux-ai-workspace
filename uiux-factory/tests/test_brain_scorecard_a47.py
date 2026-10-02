from __future__ import annotations

from pathlib import Path

import pytest

from core.brain_os.critics.core_design import CoreCriticReport
from core.brain_os.critics.product_truth import ProductTruthCriticReport
from core.brain_os.critique_contracts import (
    CritiqueIssue,
    CritiqueIssueStatus,
    CritiqueSeverity,
)
from core.brain_os.reasoning.evidence_integrity import (
    EvidenceIntegrityFinding,
    EvidenceIntegrityReport,
    IntegrityCode,
    IntegritySeverity,
)
from core.brain_os.scorecard import (
    CANONICAL_RUNTIME_EVALUATION_OWNER,
    ScorecardCriticInput,
    ScorecardIntegrityInput,
    build_brain_scorecard,
)
from core.evaluation.run_evaluator import RunEvaluation


def _run_evaluation(*, outcome: str = "insufficient_evidence") -> RunEvaluation:
    return RunEvaluation(
        schema_version=1,
        run_id="run-47",
        flow_id="page-ui-work",
        flow_revision=3,
        managed_state="COMPLETED",
        outcome=outcome,
        evaluated_at="2026-10-02T00:00:00+00:00",
        signature={"change_surface": "PAGE"},
        completed_stage_count=3,
        stage_count=4,
        replan_count=0,
        effective_evidence_count=2,
        status_counts={"PASS": 1},
        evidence_type_counts={"validator_result": 1, "artifact": 1},
        passing_evidence_types=["validator_result"],
        failing_channels=[],
        reasons=["canonical test outcome"],
        memory_eligible=False,
    )


def _issue(*, issue_id: str, critic: str, severity: CritiqueSeverity) -> CritiqueIssue:
    return CritiqueIssue(
        id=issue_id,
        critic=critic,
        category=f"{critic}.test",
        severity=severity,
        status=CritiqueIssueStatus.OBSERVED,
        summary=f"{critic} finding",
        rationale="Test advisory finding",
    )


def test_a47_scorecard_preserves_canonical_runtime_outcome_without_upgrade() -> None:
    scorecard = build_brain_scorecard(
        runtime_evaluation=_run_evaluation(outcome="insufficient_evidence"),
        runtime_source_ref="runtime-evaluation:run-47",
        critic_inputs=[
            ScorecardCriticInput(
                source_ref="critic:ux-47",
                report=CoreCriticReport(critic_id="ux_ia", issues=[]),
            )
        ],
        integrity_inputs=[
            ScorecardIntegrityInput(
                source_ref="integrity:g-47",
                report=EvidenceIntegrityReport(
                    graph_id="g-47",
                    integrity_valid=True,
                    lineage_complete=True,
                    findings=[],
                ),
            )
        ],
    )

    assert scorecard.runtime_outcome == "insufficient_evidence"
    assert scorecard.canonical_runtime_outcome_owner == CANONICAL_RUNTIME_EVALUATION_OWNER
    assert scorecard.runtime_evidence_count == 2
    assert scorecard.advisory_only is True
    assert scorecard.authority_effect == scorecard.gate_effect == "none"
    assert scorecard.evidence_effect == scorecard.release_effect == "none"
    assert not hasattr(scorecard, "passed")
    assert not hasattr(scorecard, "release_ready")
    assert not hasattr(scorecard, "overall_score")


def test_a47_scorecard_summarizes_core_and_product_critic_channels() -> None:
    core = CoreCriticReport(
        critic_id="accessibility",
        source_owner="a11y-owner",
        reviewed_artifacts=["design_contract"],
        issues=[
            _issue(issue_id="c-p0", critic="accessibility", severity=CritiqueSeverity.P0),
            _issue(issue_id="c-p1", critic="accessibility", severity=CritiqueSeverity.P1),
        ],
    )
    product = ProductTruthCriticReport(
        critic_id="product",
        source_owners=["brain_task_frame", "hypothesis_contract"],
        reviewed_artifacts=["brain_task_frame"],
        issues=[_issue(issue_id="p-p1", critic="product", severity=CritiqueSeverity.P1)],
    )

    scorecard = build_brain_scorecard(
        runtime_evaluation=_run_evaluation(outcome="passed"),
        runtime_source_ref="runtime-evaluation:run-47",
        critic_inputs=[
            ScorecardCriticInput(source_ref="critic:accessibility", report=core),
            ScorecardCriticInput(source_ref="critic:product", report=product),
        ],
    )

    assert [item.critic_id for item in scorecard.critic_channels] == ["accessibility", "product"]
    accessibility = scorecard.critic_channels[0]
    assert accessibility.issue_count == 2
    assert accessibility.severity_counts == {"P0": 1, "P1": 1}
    assert accessibility.status_counts == {"OBSERVED": 2}
    assert accessibility.source_owners == ["a11y-owner"]
    product_channel = scorecard.critic_channels[1]
    assert product_channel.issue_count == 1
    assert product_channel.source_owners == ["brain_task_frame", "hypothesis_contract"]
    assert scorecard.runtime_outcome == "passed"


def test_a47_scorecard_preserves_integrity_metadata_and_findings() -> None:
    report = EvidenceIntegrityReport(
        graph_id="graph-47",
        integrity_valid=False,
        lineage_complete=False,
        findings=[
            EvidenceIntegrityFinding(
                code=IntegrityCode.CANONICAL_REF_MISSING,
                severity=IntegritySeverity.ERROR,
                subject_ref="runtime:missing",
                detail="Canonical reference is absent",
            ),
            EvidenceIntegrityFinding(
                code=IntegrityCode.LINEAGE_INCOMPLETE,
                severity=IntegritySeverity.WARNING,
                subject_ref="RETEST_REQUIREMENT",
                detail="Verification step is incomplete",
            ),
        ],
    )

    scorecard = build_brain_scorecard(
        runtime_evaluation=_run_evaluation(outcome="failed"),
        runtime_source_ref="runtime-evaluation:run-47",
        integrity_inputs=[ScorecardIntegrityInput(source_ref="integrity:graph-47", report=report)],
    )

    channel = scorecard.integrity_channels[0]
    assert channel.integrity_valid is False
    assert channel.lineage_complete is False
    assert channel.error_count == 1
    assert channel.warning_count == 1
    assert channel.finding_codes == ["CANONICAL_REF_MISSING", "LINEAGE_INCOMPLETE"]
    assert scorecard.runtime_outcome == "failed"


def test_a47_scorecard_requires_unique_explicit_source_provenance() -> None:
    with pytest.raises(ValueError, match="source_ref values must be unique"):
        build_brain_scorecard(
            runtime_evaluation=_run_evaluation(),
            runtime_source_ref="same-ref",
            critic_inputs=[
                ScorecardCriticInput(
                    source_ref="same-ref",
                    report=CoreCriticReport(critic_id="visual", issues=[]),
                )
            ],
        )

    with pytest.raises(ValueError, match="runtime_source_ref is required"):
        build_brain_scorecard(
            runtime_evaluation=_run_evaluation(),
            runtime_source_ref="   ",
        )


def test_a47_scorecard_does_not_import_or_call_gate_release_execution_owners() -> None:
    factory = Path(__file__).resolve().parents[1]
    source = (factory / "core" / "brain_os" / "scorecard.py").read_text(encoding="utf-8")
    forbidden = (
        "gate_evidence_errors",
        "effective_evidence(",
        "RunEvaluator(",
        "ProviderManagedRunner",
        "ManagedFlowController",
        "ProductionReleaseController",
        "release_action",
        "run_target_command",
        "merge_pull_request",
        "overall_score",
        "release_ready",
    )
    for token in forbidden:
        assert token not in source
