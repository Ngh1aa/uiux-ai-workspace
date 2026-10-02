from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from typing import Literal

from pydantic import Field, model_validator

from core.brain_os.contracts import BrainContractModel
from core.brain_os.critics.core_design import CoreCriticReport
from core.brain_os.critics.product_truth import ProductTruthCriticReport
from core.brain_os.reasoning.evidence_integrity import (
    EvidenceIntegrityReport,
    IntegritySeverity,
)
from core.evaluation.run_evaluator import RunEvaluation


CANONICAL_RUNTIME_EVALUATION_OWNER = "core.evaluation.run_evaluator.RunEvaluator"
CriticReport = CoreCriticReport | ProductTruthCriticReport


class ScorecardCriticInput(BrainContractModel):
    """One explicitly provenance-addressed advisory critic report."""

    source_ref: str = Field(min_length=1, max_length=512)
    report: CriticReport


class ScorecardIntegrityInput(BrainContractModel):
    """One explicitly provenance-addressed A42 integrity report."""

    source_ref: str = Field(min_length=1, max_length=512)
    report: EvidenceIntegrityReport


class CriticScorecardChannel(BrainContractModel):
    source_ref: str = Field(min_length=1, max_length=512)
    critic_id: str = Field(min_length=1, max_length=128)
    source_owners: list[str] = Field(default_factory=list, max_length=50)
    reviewed_artifacts: list[str] = Field(default_factory=list, max_length=200)
    issue_count: int = Field(ge=0, le=10000)
    severity_counts: dict[str, int] = Field(default_factory=dict)
    status_counts: dict[str, int] = Field(default_factory=dict)
    issue_ids: list[str] = Field(default_factory=list, max_length=1000)
    advisory_only: Literal[True] = True
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"


class IntegrityScorecardChannel(BrainContractModel):
    source_ref: str = Field(min_length=1, max_length=512)
    graph_id: str = Field(min_length=1, max_length=256)
    integrity_valid: bool
    lineage_complete: bool
    error_count: int = Field(ge=0, le=10000)
    warning_count: int = Field(ge=0, le=10000)
    finding_codes: list[str] = Field(default_factory=list, max_length=1000)
    advisory_only: Literal[True] = True
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"


class BrainScorecard(BrainContractModel):
    """Provenance-aware aggregation of existing evaluation/review outputs.

    The scorecard mirrors the canonical RunEvaluation outcome and summarizes advisory
    critic/integrity channels. It deliberately has no PASS field, release-readiness
    field or numeric overall score, and cannot alter any source channel.
    """

    schema_version: Literal["brain-scorecard.v1"] = "brain-scorecard.v1"
    runtime_source_ref: str = Field(min_length=1, max_length=512)
    run_id: str = Field(min_length=1, max_length=128)
    flow_id: str = Field(default="", max_length=128)
    managed_state: str = Field(min_length=1, max_length=32)
    runtime_outcome: str = Field(min_length=1, max_length=32)
    evaluated_at: str = Field(min_length=1, max_length=128)
    runtime_evidence_count: int = Field(ge=0, le=1000000)
    critic_channels: list[CriticScorecardChannel] = Field(default_factory=list, max_length=100)
    integrity_channels: list[IntegrityScorecardChannel] = Field(default_factory=list, max_length=100)
    source_refs: list[str] = Field(min_length=1, max_length=500)
    canonical_runtime_outcome_owner: Literal[
        "core.evaluation.run_evaluator.RunEvaluator"
    ] = CANONICAL_RUNTIME_EVALUATION_OWNER
    advisory_only: Literal[True] = True
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"
    release_effect: Literal["none"] = "none"

    @model_validator(mode="after")
    def _validate_provenance(self) -> "BrainScorecard":
        if len(self.source_refs) != len(set(self.source_refs)):
            raise ValueError("BrainScorecard source_refs must be unique")
        expected = {self.runtime_source_ref}
        expected.update(item.source_ref for item in self.critic_channels)
        expected.update(item.source_ref for item in self.integrity_channels)
        if set(self.source_refs) != expected:
            raise ValueError("BrainScorecard source_refs must exactly cover all aggregated channels")
        return self


def _critic_channel(item: ScorecardCriticInput) -> CriticScorecardChannel:
    report = item.report
    severity = Counter(issue.severity.value for issue in report.issues)
    statuses = Counter(issue.status.value for issue in report.issues)
    if isinstance(report, CoreCriticReport):
        source_owners = [report.source_owner] if report.source_owner else []
    else:
        source_owners = list(report.source_owners)
    return CriticScorecardChannel(
        source_ref=item.source_ref,
        critic_id=report.critic_id,
        source_owners=source_owners,
        reviewed_artifacts=list(report.reviewed_artifacts),
        issue_count=len(report.issues),
        severity_counts=dict(sorted(severity.items())),
        status_counts=dict(sorted(statuses.items())),
        issue_ids=[issue.id for issue in report.issues],
    )


def _integrity_channel(item: ScorecardIntegrityInput) -> IntegrityScorecardChannel:
    report = item.report
    errors = sum(1 for finding in report.findings if finding.severity is IntegritySeverity.ERROR)
    warnings = sum(1 for finding in report.findings if finding.severity is IntegritySeverity.WARNING)
    return IntegrityScorecardChannel(
        source_ref=item.source_ref,
        graph_id=report.graph_id,
        integrity_valid=report.integrity_valid,
        lineage_complete=report.lineage_complete,
        error_count=errors,
        warning_count=warnings,
        finding_codes=[finding.code.value for finding in report.findings],
    )


def build_brain_scorecard(
    *,
    runtime_evaluation: RunEvaluation,
    runtime_source_ref: str,
    critic_inputs: Iterable[ScorecardCriticInput] = (),
    integrity_inputs: Iterable[ScorecardIntegrityInput] = (),
) -> BrainScorecard:
    """Aggregate existing outputs without recomputing truth or authority.

    `runtime_evaluation.outcome` is copied verbatim. Critic and integrity reports are
    summarized only; zero findings never upgrade the runtime outcome or imply release
    readiness. Every input channel must have a unique explicit provenance reference.
    """

    runtime_ref = str(runtime_source_ref).strip()
    if not runtime_ref:
        raise ValueError("runtime_source_ref is required")
    critics = list(critic_inputs)
    integrity = list(integrity_inputs)
    refs = [runtime_ref]
    refs.extend(item.source_ref for item in critics)
    refs.extend(item.source_ref for item in integrity)
    if len(refs) != len(set(refs)):
        raise ValueError("scorecard input source_ref values must be unique")
    if not str(runtime_evaluation.run_id).strip():
        raise ValueError("runtime_evaluation.run_id is required")
    if not str(runtime_evaluation.managed_state).strip():
        raise ValueError("runtime_evaluation.managed_state is required")
    if not str(runtime_evaluation.outcome).strip():
        raise ValueError("runtime_evaluation.outcome is required")

    return BrainScorecard(
        runtime_source_ref=runtime_ref,
        run_id=runtime_evaluation.run_id,
        flow_id=runtime_evaluation.flow_id,
        managed_state=runtime_evaluation.managed_state,
        runtime_outcome=runtime_evaluation.outcome,
        evaluated_at=runtime_evaluation.evaluated_at,
        runtime_evidence_count=runtime_evaluation.effective_evidence_count,
        critic_channels=[_critic_channel(item) for item in critics],
        integrity_channels=[_integrity_channel(item) for item in integrity],
        source_refs=refs,
    )
