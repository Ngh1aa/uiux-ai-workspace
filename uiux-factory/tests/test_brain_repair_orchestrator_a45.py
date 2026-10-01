from __future__ import annotations

from pathlib import Path

import pytest

from core.brain_os.critique_contracts import (
    CritiqueIssue,
    CritiqueIssueStatus,
    CritiqueSeverity,
    RepairDirectiveStatus,
    RetestStatus,
    RootCauseStatus,
)
from core.brain_os.repair_orchestrator import CritiqueRepairOrchestrator


def _issue(
    *,
    issue_id: str = "CR-1",
    critic: str = "accessibility",
    severity: CritiqueSeverity = CritiqueSeverity.P0,
    status: CritiqueIssueStatus = CritiqueIssueStatus.OBSERVED,
    evidence_refs: list[str] | None = None,
) -> CritiqueIssue:
    return CritiqueIssue(
        id=issue_id,
        critic=critic,
        category=f"{critic}.example_gap",
        severity=severity,
        status=status,
        summary="Example critique gap",
        rationale="Example bounded critique rationale",
        evidence_refs=evidence_refs or [],
        affected_artifacts=["design_system"],
        retest_refs=["old-retest"] if status is CritiqueIssueStatus.RESOLVED else [],
    )


def test_a45_proposal_bundle_uses_existing_a41_contract_states_only() -> None:
    issue = _issue(evidence_refs=["ev_runtime_1"])
    bundle = CritiqueRepairOrchestrator().propose(issue)

    assert bundle.source_issue_id == issue.id
    assert bundle.root_cause.status is RootCauseStatus.PROPOSED
    assert bundle.directive.status is RepairDirectiveStatus.PROPOSED
    assert bundle.retest.status is RetestStatus.PENDING
    assert bundle.root_cause.issue_ids == [issue.id]
    assert bundle.directive.issue_ids == [issue.id]
    assert bundle.directive.root_cause_ids == [bundle.root_cause.id]
    assert bundle.retest.repair_directive_id == bundle.directive.id
    assert bundle.link.issue_ids == [issue.id]
    assert bundle.link.root_cause_ids == [bundle.root_cause.id]
    assert bundle.link.repair_directive_ids == [bundle.directive.id]
    assert bundle.link.retest_requirement_ids == [bundle.retest.id]
    assert bundle.root_cause.evidence_refs == ["ev_runtime_1"]
    assert bundle.directive.evidence_refs == ["ev_runtime_1"]
    assert bundle.retest.evidence_refs == []


def test_a45_p0_proposal_requires_human_approval_but_is_not_accepted() -> None:
    bundle = CritiqueRepairOrchestrator().propose(_issue(severity=CritiqueSeverity.P0))

    assert bundle.directive.requires_human_approval is True
    assert bundle.directive.status is RepairDirectiveStatus.PROPOSED
    assert bundle.directive.accepted_by is None
    assert bundle.acceptance_effect == "none"
    assert bundle.execution_effect == "none"
    assert bundle.resolution_effect == "none"
    assert bundle.gate_effect == "none"
    assert bundle.evidence_effect == "none"


def test_a45_non_p0_proposal_does_not_invent_human_approval_requirement() -> None:
    bundle = CritiqueRepairOrchestrator().propose(
        _issue(severity=CritiqueSeverity.P1, critic="visual")
    )

    assert bundle.directive.requires_human_approval is False
    assert bundle.directive.target_stage == "visual_composition"
    assert bundle.retest.evidence_types == ["browser_render"]


def test_a45_retest_mapping_is_bounded_by_critic_type() -> None:
    orchestrator = CritiqueRepairOrchestrator()
    expected = {
        "visual": ["browser_render"],
        "ux_ia": ["browser_render"],
        "design_system": ["validator_result"],
        "accessibility": ["validator_result", "browser_render"],
        "product": ["artifact"],
        "runtime": ["validator_result"],
        "evidence_truth": ["validator_result"],
    }
    for critic, evidence_types in expected.items():
        bundle = orchestrator.propose(
            _issue(issue_id=f"CR-{critic}", critic=critic, severity=CritiqueSeverity.P1)
        )
        assert bundle.retest.evidence_types == evidence_types
        assert bundle.retest.status is RetestStatus.PENDING


def test_a45_ids_are_deterministic_for_same_issue() -> None:
    issue = _issue(issue_id="CR-stable", severity=CritiqueSeverity.P1)
    orchestrator = CritiqueRepairOrchestrator()

    first = orchestrator.propose(issue)
    second = orchestrator.propose(issue)

    assert first.root_cause.id == second.root_cause.id
    assert first.directive.id == second.directive.id
    assert first.retest.id == second.retest.id
    assert first.link.id == second.link.id


def test_a45_resolved_issue_cannot_receive_new_repair_proposal() -> None:
    issue = _issue(
        issue_id="CR-resolved",
        severity=CritiqueSeverity.P1,
        status=CritiqueIssueStatus.RESOLVED,
        evidence_refs=["ev_done"],
    )
    with pytest.raises(ValueError, match="resolved critique issues"):
        CritiqueRepairOrchestrator().propose(issue)


def test_a45_propose_many_dedupes_and_skips_resolved() -> None:
    open_issue = _issue(issue_id="CR-open", severity=CritiqueSeverity.P1)
    resolved_issue = _issue(
        issue_id="CR-resolved",
        severity=CritiqueSeverity.P1,
        status=CritiqueIssueStatus.RESOLVED,
        evidence_refs=["ev_done"],
    )

    bundles = CritiqueRepairOrchestrator().propose_many(
        [open_issue, open_issue, resolved_issue]
    )

    assert len(bundles) == 1
    assert bundles[0].source_issue_id == "CR-open"


def test_a45_orchestrator_does_not_define_execution_acceptance_resolution_or_gate_owners() -> None:
    factory = Path(__file__).resolve().parents[1]
    source = (factory / "core" / "brain_os" / "repair_orchestrator.py").read_text(
        encoding="utf-8"
    )
    forbidden = (
        "ProviderManagedRunner",
        "ManagedFlowController",
        "ProductionReleaseController",
        "gate_evidence_errors",
        "run_target_command",
        "release_action",
        "merge_pull_request",
        "RepairDirectiveStatus.ACCEPTED",
        "RetestStatus.PASSED",
        "CritiqueIssueStatus.RESOLVED =",
    )
    for token in forbidden:
        assert token not in source
