from __future__ import annotations

import hashlib
from typing import Iterable, Literal

from pydantic import Field

from core.brain_os.contracts import BrainContractModel
from core.brain_os.critique_contracts import (
    CritiqueIssue,
    CritiqueIssueStatus,
    CritiqueSeverity,
    RepairDirective,
    RepairDirectiveStatus,
    RepairLink,
    RetestRequirement,
    RetestStatus,
    RootCause,
    RootCauseStatus,
)


class RepairProposalBundle(BrainContractModel):
    """Proposal-only critique repair lineage.

    This bundle is reasoning/control metadata only. It does not execute the repair,
    accept the directive, run the retest or resolve the source critique issue.
    """

    schema_version: Literal["brain-repair-proposal.v1"] = "brain-repair-proposal.v1"
    source_issue_id: str = Field(min_length=1, max_length=128)
    root_cause: RootCause
    directive: RepairDirective
    retest: RetestRequirement
    link: RepairLink
    advisory_only: Literal[True] = True
    execution_effect: Literal["none"] = "none"
    acceptance_effect: Literal["none"] = "none"
    resolution_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"


def _stable_id(prefix: str, issue: CritiqueIssue, suffix: str) -> str:
    raw = f"{issue.id}\n{issue.critic}\n{issue.category}\n{suffix}".encode("utf-8")
    return f"{prefix}-{hashlib.sha256(raw).hexdigest()[:16]}"


def _target_stage(issue: CritiqueIssue) -> str:
    return {
        "visual": "visual_composition",
        "ux_ia": "ux_strategy",
        "design_system": "design_system",
        "accessibility": "qa",
        "product": "product_strategy",
        "runtime": "qa",
        "evidence_truth": "qa",
    }.get(issue.critic, "qa")


def _retest_evidence_types(issue: CritiqueIssue) -> list[str]:
    return {
        "visual": ["browser_render"],
        "ux_ia": ["browser_render"],
        "design_system": ["validator_result"],
        "accessibility": ["validator_result", "browser_render"],
        "product": ["artifact"],
        "runtime": ["validator_result"],
        "evidence_truth": ["validator_result"],
    }.get(issue.critic, ["validator_result"])


def _root_confidence(issue: CritiqueIssue) -> float:
    if issue.status is CritiqueIssueStatus.CONFIRMED:
        return 0.65
    if issue.status is CritiqueIssueStatus.BLOCKED:
        return 0.30
    return 0.40


class CritiqueRepairOrchestrator:
    """Turn unresolved critique observations into bounded repair proposals.

    The orchestrator deliberately does not own repair execution, runtime tools, gate
    evaluation, directive acceptance, retest execution or issue resolution.
    """

    def propose(self, issue: CritiqueIssue) -> RepairProposalBundle:
        if issue.status is CritiqueIssueStatus.RESOLVED:
            raise ValueError("resolved critique issues do not require a new repair proposal")

        root_id = _stable_id("RC", issue, "root-cause")
        directive_id = _stable_id("RP", issue, "repair-directive")
        retest_id = _stable_id("RT", issue, "retest")
        link_id = _stable_id("RL", issue, "repair-link")
        target_stage = _target_stage(issue)

        root = RootCause(
            id=root_id,
            issue_ids=[issue.id],
            statement=(
                f"Proposed root cause for {issue.category}: the current source contract, "
                "implementation or evidence state does not yet satisfy the observed requirement."
            ),
            status=RootCauseStatus.PROPOSED,
            confidence=_root_confidence(issue),
            evidence_refs=list(issue.evidence_refs),
            assumptions=[
                "This is a bounded causal proposal derived from the critique issue, not a confirmed cause.",
                "Canonical source/evidence must be checked before accepting any repair directive.",
            ],
        )

        directive = RepairDirective(
            id=directive_id,
            issue_ids=[issue.id],
            root_cause_ids=[root.id],
            target_stage=target_stage,
            instruction=(
                f"Address the observed {issue.category} issue: {issue.summary}. "
                "Use the source artifacts named by the issue, preserve existing constraints, "
                "and do not broaden scope without explicit authority."
            ),
            rationale=(
                "The repair is proposed from an unresolved critique observation. It must remain "
                "separate from proof that the cause is correct or that the repair executed."
            ),
            expected_outcome=(
                f"The {issue.category} observation no longer reproduces when the affected artifacts "
                "are reviewed and the required canonical retest evidence is collected."
            ),
            priority=issue.severity,
            status=RepairDirectiveStatus.PROPOSED,
            constraints=[
                "Do not self-confirm or self-resolve the source critique issue.",
                "Do not treat proposal text as execution evidence.",
                "Do not change runtime/evidence/release authority boundaries.",
            ],
            evidence_refs=list(issue.evidence_refs),
            requires_human_approval=(issue.severity is CritiqueSeverity.P0),
        )

        retest = RetestRequirement(
            id=retest_id,
            repair_directive_id=directive.id,
            stage=target_stage,
            evidence_types=_retest_evidence_types(issue),
            acceptance_criteria=[
                f"Re-run the relevant {issue.critic} review and verify that {issue.category} no longer reproduces.",
                "Attach canonical evidence references before changing the critique issue to RESOLVED.",
                "A passing retest does not by itself grant merge, deployment or release authority.",
            ],
            status=RetestStatus.PENDING,
            evidence_refs=[],
        )

        link = RepairLink(
            id=link_id,
            issue_ids=[issue.id],
            root_cause_ids=[root.id],
            repair_directive_ids=[directive.id],
            retest_requirement_ids=[retest.id],
            rationale=(
                "Proposal-only lineage connecting one unresolved critique issue to a proposed cause, "
                "repair directive and required canonical retest."
            ),
        )

        return RepairProposalBundle(
            source_issue_id=issue.id,
            root_cause=root,
            directive=directive,
            retest=retest,
            link=link,
        )

    def propose_many(self, issues: Iterable[CritiqueIssue]) -> list[RepairProposalBundle]:
        output: list[RepairProposalBundle] = []
        seen: set[str] = set()
        for issue in issues:
            if issue.id in seen:
                continue
            seen.add(issue.id)
            if issue.status is CritiqueIssueStatus.RESOLVED:
                continue
            output.append(self.propose(issue))
        return output
