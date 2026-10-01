from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.brain_os import (
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


def _issue(**overrides):
    payload = {
        "id": "issue-1",
        "critic": "ux-ia",
        "category": "recovery",
        "severity": CritiqueSeverity.P1,
        "status": CritiqueIssueStatus.CONFIRMED,
        "summary": "Payment failure state has no recovery path.",
        "rationale": "The rendered failure state exposes an error but no retry or alternate action.",
        "evidence_refs": ["evidence:browser:payment-error"],
        "affected_artifacts": ["/checkout"],
    }
    payload.update(overrides)
    return CritiqueIssue(**payload)


def _root_cause(**overrides):
    payload = {
        "id": "root-1",
        "issue_ids": ["issue-1"],
        "statement": "The state model omitted recovery actions for failed payment attempts.",
        "status": RootCauseStatus.SUPPORTED,
        "confidence": 0.9,
        "evidence_refs": ["evidence:browser:payment-error"],
    }
    payload.update(overrides)
    return RootCause(**payload)


def _directive(**overrides):
    payload = {
        "id": "repair-1",
        "issue_ids": ["issue-1"],
        "root_cause_ids": ["root-1"],
        "target_stage": "design",
        "instruction": "Add retry and alternate-payment recovery actions to the failed payment state.",
        "rationale": "Repair the state-model omission at the design owner rather than patching copy only.",
        "expected_outcome": "A failed payment can be recovered without restarting checkout.",
        "priority": CritiqueSeverity.P1,
        "status": RepairDirectiveStatus.ACCEPTED,
        "accepted_by": "human:product-designer",
    }
    payload.update(overrides)
    return RepairDirective(**payload)


def _retest(**overrides):
    payload = {
        "id": "retest-1",
        "repair_directive_id": "repair-1",
        "stage": "qa",
        "evidence_types": ["browser_render", "validator_result"],
        "acceptance_criteria": [
            "failed payment exposes retry action",
            "alternate payment path remains reachable",
        ],
        "status": RetestStatus.PENDING,
    }
    payload.update(overrides)
    return RetestRequirement(**payload)


def test_a41_critique_repair_contracts_round_trip() -> None:
    issue = _issue()
    root = _root_cause()
    directive = _directive()
    retest = _retest()
    link = RepairLink(
        id="link-1",
        issue_ids=[issue.id],
        root_cause_ids=[root.id],
        repair_directive_ids=[directive.id],
        retest_requirement_ids=[retest.id],
        rationale="Trace critique through causal repair and required verification.",
    )

    for model in (issue, root, directive, retest, link):
        restored = type(model).model_validate_json(model.model_dump_json())
        assert restored == model


def test_a41_confirmed_and_resolved_issues_require_evidence() -> None:
    with pytest.raises(ValidationError, match="CONFIRMED critique issue requires"):
        _issue(evidence_refs=[])

    with pytest.raises(ValidationError, match="RESOLVED critique issue requires at least one retest reference"):
        _issue(status=CritiqueIssueStatus.RESOLVED, retest_refs=[])

    resolved = _issue(
        status=CritiqueIssueStatus.RESOLVED,
        retest_refs=["retest:retest-1"],
        evidence_refs=["evidence:browser:payment-error-retest"],
    )
    assert resolved.status is CritiqueIssueStatus.RESOLVED


def test_a41_blocked_issue_requires_blocker() -> None:
    with pytest.raises(ValidationError, match="BLOCKED critique issue requires"):
        _issue(status=CritiqueIssueStatus.BLOCKED, evidence_refs=[], blockers=[])


def test_a41_supported_or_rejected_root_cause_requires_evidence() -> None:
    with pytest.raises(ValidationError, match="SUPPORTED root cause requires"):
        _root_cause(evidence_refs=[])

    rejected = _root_cause(
        status=RootCauseStatus.REJECTED,
        evidence_refs=["evidence:test:counterexample"],
    )
    assert rejected.status is RootCauseStatus.REJECTED


def test_a41_repair_directive_requires_lineage_and_acceptance_provenance() -> None:
    with pytest.raises(ValidationError):
        _directive(issue_ids=[])

    with pytest.raises(ValidationError, match="ACCEPTED repair directive requires accepted_by provenance"):
        _directive(accepted_by=None)

    deferred = _directive(
        status=RepairDirectiveStatus.DEFERRED,
        accepted_by=None,
        defer_reason="Blocked by an upstream product decision.",
    )
    assert deferred.defer_reason


def test_a41_repair_directive_cannot_claim_execution_state() -> None:
    with pytest.raises(ValidationError):
        _directive(status="APPLIED")


def test_a41_retest_terminal_states_require_evidence() -> None:
    with pytest.raises(ValidationError, match="PASSED retest requires"):
        _retest(status=RetestStatus.PASSED, evidence_refs=[])

    passed = _retest(
        status=RetestStatus.PASSED,
        evidence_refs=["evidence:browser:payment-error-retest", "evidence:test:state-coverage"],
    )
    assert passed.status is RetestStatus.PASSED

    with pytest.raises(ValidationError, match="BLOCKED retest requires"):
        _retest(status=RetestStatus.BLOCKED, blockers=[])


def test_a41_repair_link_requires_complete_lineage_and_deduplicates_refs() -> None:
    link = RepairLink(
        id="link-1",
        issue_ids=["issue-1", "issue-1"],
        root_cause_ids=["root-1", "root-1"],
        repair_directive_ids=["repair-1"],
        retest_requirement_ids=["retest-1"],
        rationale="Keep one traceable repair lineage.",
    )
    assert link.issue_ids == ["issue-1"]
    assert link.root_cause_ids == ["root-1"]

    with pytest.raises(ValidationError):
        RepairLink(
            id="link-empty",
            issue_ids=["issue-1"],
            root_cause_ids=["root-1"],
            repair_directive_ids=["repair-1"],
            retest_requirement_ids=[],
            rationale="Invalid because retest lineage is missing.",
        )


def test_a41_critique_contracts_are_strict_and_immutable() -> None:
    issue = _issue()
    with pytest.raises(ValidationError):
        CritiqueIssue(**{**issue.model_dump(), "unexpected_policy": "release"})

    with pytest.raises(ValidationError):
        issue.status = CritiqueIssueStatus.RESOLVED
