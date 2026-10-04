from __future__ import annotations

from core.runtime.flow_os.branch_hygiene import BranchCandidate, evaluate_branch_candidate


def _candidate() -> BranchCandidate:
    return BranchCandidate(name="feat/example", expected_sha="abc123", source_pr=1)


def test_branch_hygiene_allows_exact_zero_ahead_stale_branch() -> None:
    result = evaluate_branch_candidate(
        _candidate(),
        current_sha="abc123",
        protected=False,
        compare_status="behind",
        ahead_by=0,
        behind_by=4,
    )
    assert result.safe_to_delete is True
    assert result.state == "SAFE_TO_DELETE"


def test_branch_hygiene_is_idempotent_when_branch_is_already_absent() -> None:
    result = evaluate_branch_candidate(
        _candidate(),
        current_sha=None,
        protected=None,
        compare_status=None,
        ahead_by=None,
        behind_by=None,
    )
    assert result.safe_to_delete is True
    assert result.state == "ALREADY_ABSENT"


def test_branch_hygiene_blocks_head_movement() -> None:
    result = evaluate_branch_candidate(
        _candidate(),
        current_sha="different",
        protected=False,
        compare_status="behind",
        ahead_by=0,
        behind_by=4,
    )
    assert result.safe_to_delete is False
    assert result.state == "BLOCKED_HEAD_MOVED"


def test_branch_hygiene_blocks_protected_branch() -> None:
    result = evaluate_branch_candidate(
        _candidate(),
        current_sha="abc123",
        protected=True,
        compare_status="behind",
        ahead_by=0,
        behind_by=4,
    )
    assert result.safe_to_delete is False
    assert result.state == "BLOCKED_PROTECTED_BRANCH"


def test_branch_hygiene_blocks_unmerged_history() -> None:
    result = evaluate_branch_candidate(
        _candidate(),
        current_sha="abc123",
        protected=False,
        compare_status="diverged",
        ahead_by=2,
        behind_by=4,
    )
    assert result.safe_to_delete is False
    assert result.state == "BLOCKED_UNMERGED_HISTORY"
