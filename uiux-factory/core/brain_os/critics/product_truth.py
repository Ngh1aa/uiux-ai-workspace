from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from typing import Literal

from pydantic import Field

from core.brain_os.contracts import (
    BrainContractModel,
    BrainTaskFrame,
    Decision,
    DecisionStatus,
    Hypothesis,
    HypothesisStatus,
    Reversibility,
    UncertaintyState,
)
from core.brain_os.critique_contracts import (
    CritiqueIssue,
    CritiqueIssueStatus,
    CritiqueSeverity,
)
from core.brain_os.reasoning.evidence_graph import EvidenceGraph, EvidenceGraphNode
from core.brain_os.reasoning.evidence_integrity import (
    EvidenceIntegrityReport,
    IntegritySeverity,
    validate_evidence_integrity,
)
from core.brain_os.reasoning.lineage_integrity import validate_end_to_end_lineage
from core.runtime.flow_os.evidence import EvidenceRecord, effective_evidence


RUNTIME_EVIDENCE_OWNER = "core.runtime.flow_os.evidence.effective_evidence"
EVIDENCE_INTEGRITY_OWNER = "core.brain_os.reasoning.evidence_integrity.validate_evidence_integrity"
LINEAGE_INTEGRITY_OWNER = "core.brain_os.reasoning.lineage_integrity.validate_end_to_end_lineage"


def _issue_id(critic: str, category: str, summary: str) -> str:
    raw = f"{critic}\n{category}\n{summary}".encode("utf-8")
    return f"CR-{hashlib.sha256(raw).hexdigest()[:16]}"


def _issue(
    *,
    critic: str,
    category: str,
    severity: CritiqueSeverity,
    summary: str,
    rationale: str,
    affected_artifacts: list[str],
    evidence_refs: list[str] | None = None,
) -> CritiqueIssue:
    return CritiqueIssue(
        id=_issue_id(critic, category, summary),
        critic=critic,
        category=category,
        severity=severity,
        status=CritiqueIssueStatus.OBSERVED,
        summary=summary,
        rationale=rationale,
        evidence_refs=evidence_refs or [],
        affected_artifacts=affected_artifacts,
    )


class ProductTruthCriticReport(BrainContractModel):
    """Advisory product/runtime/truth review output.

    A report can contain zero issues and still does not represent a runtime, evidence or
    release gate PASS. Canonical owners remain authoritative for execution and trust.
    """

    schema_version: Literal["brain-product-truth-critic.v1"] = "brain-product-truth-critic.v1"
    critic_id: Literal["product", "runtime", "evidence_truth"]
    issues: list[CritiqueIssue] = Field(default_factory=list, max_length=1000)
    reviewed_artifacts: list[str] = Field(default_factory=list, max_length=100)
    source_owners: list[str] = Field(default_factory=list, max_length=20)
    effective_evidence_refs: list[str] = Field(default_factory=list, max_length=1000)
    integrity_valid: bool | None = None
    lineage_complete: bool | None = None
    advisory_only: Literal[True] = True
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"


class ProductCritic:
    """Review product reasoning completeness without selecting or executing decisions."""

    BROAD_SURFACES = {"REDESIGN", "PRODUCT"}
    HIGH_RISK_TERMS = ("high", "critical", "severe", "p0", "irreversible")

    def review(
        self,
        *,
        frame: BrainTaskFrame,
        hypotheses: Iterable[Hypothesis] = (),
        decisions: Iterable[Decision] = (),
    ) -> ProductTruthCriticReport:
        hypotheses = list(hypotheses)
        decisions = list(decisions)
        issues: list[CritiqueIssue] = []
        broad = frame.change_surface in self.BROAD_SURFACES

        if not frame.success_criteria:
            issues.append(_issue(
                critic="product",
                category="product.success_criteria_missing",
                severity=CritiqueSeverity.P0 if broad else CritiqueSeverity.P1,
                summary="Task frame has no explicit success criteria",
                rationale="Product work needs explicit acceptance/outcome criteria before design decisions can be evaluated. This critic records the gap only; it does not invent metrics.",
                affected_artifacts=["brain_task_frame"],
            ))

        if broad and not hypotheses:
            issues.append(_issue(
                critic="product",
                category="product.hypotheses_missing",
                severity=CritiqueSeverity.P1,
                summary="Broad product work has no explicit hypotheses",
                rationale="A REDESIGN/PRODUCT-sized task without hypotheses makes assumptions hard to test and easy to present as fact.",
                affected_artifacts=["brain_task_frame", "hypotheses"],
            ))

        if broad and not decisions:
            issues.append(_issue(
                critic="product",
                category="product.decisions_missing",
                severity=CritiqueSeverity.P1,
                summary="Broad product work has no explicit decision records",
                rationale="Trade-offs and alternatives are not traceable when broad work has no Decision contracts.",
                affected_artifacts=["brain_task_frame", "decisions"],
            ))

        if broad and frame.source_confidence < 0.6:
            issues.append(_issue(
                critic="product",
                category="product.low_source_confidence",
                severity=CritiqueSeverity.P1,
                summary=f"Broad task frame source confidence is low ({frame.source_confidence:.2f})",
                rationale="Large-scope product decisions should not silently rely on a weakly inferred task frame. The uncertainty should remain visible until supported by evidence or user direction.",
                affected_artifacts=["brain_task_frame"],
            ))

        for uncertainty in frame.uncertainties:
            if uncertainty.state in {UncertaintyState.BLOCKED, UncertaintyState.CONFLICTED}:
                issues.append(_issue(
                    critic="product",
                    category="product.blocking_uncertainty",
                    severity=CritiqueSeverity.P0,
                    summary=f"Blocking/conflicted uncertainty remains: {uncertainty.subject}",
                    rationale="A blocked or conflicted uncertainty can invalidate downstream product assumptions and should not be silently treated as resolved.",
                    affected_artifacts=["brain_task_frame"],
                ))
            elif broad and uncertainty.state in {UncertaintyState.INFERRED, UncertaintyState.PROPOSED} and uncertainty.confidence < 0.5:
                issues.append(_issue(
                    critic="product",
                    category="product.weak_broad_uncertainty",
                    severity=CritiqueSeverity.P1,
                    summary=f"Low-confidence uncertainty affects broad work: {uncertainty.subject}",
                    rationale="A broad task still depends on a low-confidence inferred/proposed premise.",
                    affected_artifacts=["brain_task_frame"],
                ))

        for hypothesis in hypotheses:
            risk = hypothesis.risk.lower()
            high_risk = any(term in risk for term in self.HIGH_RISK_TERMS)
            if high_risk and hypothesis.status in {HypothesisStatus.PROPOSED, HypothesisStatus.TESTING} and not hypothesis.evidence_refs:
                issues.append(_issue(
                    critic="product",
                    category="product.high_risk_hypothesis_unverified",
                    severity=CritiqueSeverity.P0,
                    summary=f"High-risk hypothesis remains unverified: {hypothesis.statement}",
                    rationale="High-risk product assumptions should not drive irreversible/broad work without evidence-backed validation.",
                    affected_artifacts=["hypotheses"],
                ))
            if hypothesis.status is HypothesisStatus.BLOCKED:
                issues.append(_issue(
                    critic="product",
                    category="product.hypothesis_blocked",
                    severity=CritiqueSeverity.P1,
                    summary=f"Hypothesis validation is blocked: {hypothesis.statement}",
                    rationale="Blocked validation leaves a product assumption unresolved and should remain visible in planning.",
                    affected_artifacts=["hypotheses"],
                ))

        for decision in decisions:
            if decision.status is DecisionStatus.SELECTED and not decision.evidence_refs:
                issues.append(_issue(
                    critic="product",
                    category="product.selected_decision_without_evidence",
                    severity=CritiqueSeverity.P1,
                    summary=f"Selected decision has no evidence references: {decision.question}",
                    rationale="Selection provenance exists, but the decision has no linked evidence. This is a traceability gap, not proof that the decision is wrong.",
                    affected_artifacts=["decisions"],
                ))
            if (
                decision.status is DecisionStatus.SELECTED
                and decision.owner == "brain_advisory"
                and decision.reversibility in {Reversibility.COSTLY, Reversibility.IRREVERSIBLE}
            ):
                issues.append(_issue(
                    critic="product",
                    category="product.high_cost_brain_owned_selection",
                    severity=CritiqueSeverity.P0,
                    summary=f"Costly/irreversible decision is selected with brain_advisory ownership: {decision.question}",
                    rationale="Brain advisory state must not stand in for human/runtime ownership on costly or irreversible decisions.",
                    affected_artifacts=["decisions"],
                ))
            if decision.status is DecisionStatus.BLOCKED:
                issues.append(_issue(
                    critic="product",
                    category="product.decision_blocked",
                    severity=CritiqueSeverity.P1,
                    summary=f"Decision remains blocked: {decision.question}",
                    rationale="A blocked decision indicates unresolved product/governance dependencies.",
                    affected_artifacts=["decisions"],
                ))

        deduped = {item.id: item for item in issues}
        return ProductTruthCriticReport(
            critic_id="product",
            issues=list(deduped.values()),
            reviewed_artifacts=["brain_task_frame", "hypotheses", "decisions"],
            source_owners=["core.brain_os.contracts"],
        )


class RuntimeCritic:
    """Inspect canonical effective runtime evidence without evaluating runtime gates."""

    def review(
        self,
        *,
        records: list[dict[str, object]],
        expected_stage_ids: Iterable[str] = (),
        required_evidence_types_by_stage: Mapping[str, Iterable[str]] | None = None,
    ) -> ProductTruthCriticReport:
        effective = effective_evidence(records)
        issues: list[CritiqueIssue] = []
        by_stage: dict[str, list[EvidenceRecord]] = {}
        for record in effective:
            by_stage.setdefault(record.stage_id, []).append(record)
            if record.status == "FAIL":
                issues.append(_issue(
                    critic="runtime",
                    category="runtime.effective_failure",
                    severity=CritiqueSeverity.P0,
                    summary=f"Effective runtime evidence failed in stage {record.stage_id}: {record.summary}",
                    rationale="The latest trusted evidence for this exact runtime channel is FAIL. The critic reports current-state evidence but does not mark a gate failed or trigger a repair itself.",
                    affected_artifacts=["runtime_evidence"],
                    evidence_refs=[record.id],
                ))

        for raw_stage in expected_stage_ids:
            stage = str(raw_stage).strip()
            if stage and not by_stage.get(stage):
                issues.append(_issue(
                    critic="runtime",
                    category="runtime.stage_evidence_missing",
                    severity=CritiqueSeverity.P1,
                    summary=f"No effective trusted runtime evidence exists for expected stage {stage}",
                    rationale="An expected stage has no current trusted evidence. This is an observation only; gate ownership remains with canonical runtime policy.",
                    affected_artifacts=["runtime_evidence"],
                ))

        for raw_stage, raw_types in (required_evidence_types_by_stage or {}).items():
            stage = str(raw_stage).strip()
            required = {str(item).strip() for item in raw_types if str(item).strip()}
            available = {
                record.type
                for record in by_stage.get(stage, [])
                if record.status != "FAIL"
            }
            missing = sorted(required.difference(available))
            if missing:
                issues.append(_issue(
                    critic="runtime",
                    category="runtime.expected_evidence_type_missing",
                    severity=CritiqueSeverity.P1,
                    summary=f"Expected runtime evidence is missing for stage {stage}: {', '.join(missing)}",
                    rationale="Caller-declared review expectations are not represented in current effective trusted evidence. This critic does not convert these expectations into runtime gates.",
                    affected_artifacts=["runtime_evidence"],
                ))

        return ProductTruthCriticReport(
            critic_id="runtime",
            issues=issues,
            reviewed_artifacts=["runtime_evidence"],
            source_owners=[RUNTIME_EVIDENCE_OWNER],
            effective_evidence_refs=[record.id for record in effective],
        )


class EvidenceTruthCritic:
    """Adapt A42 integrity validators into advisory critique issues."""

    @staticmethod
    def _issues_from_report(
        report: EvidenceIntegrityReport,
        *,
        category_prefix: str,
    ) -> list[CritiqueIssue]:
        issues: list[CritiqueIssue] = []
        for finding in report.findings:
            severity = (
                CritiqueSeverity.P0
                if finding.severity is IntegritySeverity.ERROR
                else CritiqueSeverity.P1
            )
            issues.append(_issue(
                critic="evidence_truth",
                category=f"evidence_truth.{category_prefix}.{finding.code.value.lower()}",
                severity=severity,
                summary=finding.detail,
                rationale=f"A42 integrity validator reported {finding.code.value} for {finding.subject_ref}. Brain preserves this as an OBSERVED critique and does not upgrade or repair evidence trust.",
                affected_artifacts=["evidence_graph"],
            ))
        return issues

    def review(
        self,
        *,
        graph: EvidenceGraph,
        canonical_index: Mapping[str, EvidenceGraphNode],
    ) -> ProductTruthCriticReport:
        integrity = validate_evidence_integrity(graph, canonical_index)
        lineage = validate_end_to_end_lineage(graph)
        issues = [
            *self._issues_from_report(integrity, category_prefix="integrity"),
            *self._issues_from_report(lineage, category_prefix="lineage"),
        ]

        if not integrity.integrity_valid and not integrity.findings:
            issues.append(_issue(
                critic="evidence_truth",
                category="evidence_truth.integrity.invalid_without_detail",
                severity=CritiqueSeverity.P0,
                summary="Evidence integrity is invalid without a detailed finding",
                rationale="The source integrity report is invalid but contains no explanatory finding. This defensive observation prevents silent truth-state collapse.",
                affected_artifacts=["evidence_graph"],
            ))
        if not lineage.lineage_complete and not lineage.findings:
            issues.append(_issue(
                critic="evidence_truth",
                category="evidence_truth.lineage.incomplete_without_detail",
                severity=CritiqueSeverity.P1,
                summary="End-to-end evidence lineage is incomplete without a detailed finding",
                rationale="The source lineage report is incomplete but contains no explanatory finding. Brain records the incompleteness but does not infer the missing relationship.",
                affected_artifacts=["evidence_graph"],
            ))

        deduped = {item.id: item for item in issues}
        return ProductTruthCriticReport(
            critic_id="evidence_truth",
            issues=list(deduped.values()),
            reviewed_artifacts=["evidence_graph", "canonical_evidence_index"],
            source_owners=[EVIDENCE_INTEGRITY_OWNER, LINEAGE_INTEGRITY_OWNER],
            integrity_valid=integrity.integrity_valid,
            lineage_complete=lineage.lineage_complete,
        )
