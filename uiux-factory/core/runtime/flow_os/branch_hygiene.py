from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


BRANCH_HYGIENE_VERSION = "1.0"


@dataclass(frozen=True)
class BranchCandidate:
    name: str
    expected_sha: str
    source_pr: int | None = None
    reason: str = ""

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BranchCandidate":
        name = str(payload.get("name") or "").strip()
        expected_sha = str(payload.get("expected_sha") or "").strip()
        if not name or not expected_sha:
            raise ValueError("branch candidate requires name and expected_sha")
        if name == "main":
            raise ValueError("branch hygiene manifest must never target main")
        source_pr = payload.get("source_pr")
        return cls(
            name=name,
            expected_sha=expected_sha,
            source_pr=int(source_pr) if source_pr is not None else None,
            reason=str(payload.get("reason") or "").strip(),
        )


@dataclass(frozen=True)
class BranchHygieneDecision:
    version: str
    branch: str
    expected_sha: str
    current_sha: str | None
    protected: bool | None
    compare_status: str | None
    ahead_by: int | None
    behind_by: int | None
    safe_to_delete: bool
    state: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_branch_candidate(
    candidate: BranchCandidate,
    *,
    current_sha: str | None,
    protected: bool | None,
    compare_status: str | None,
    ahead_by: int | None,
    behind_by: int | None,
) -> BranchHygieneDecision:
    if current_sha is None:
        return BranchHygieneDecision(
            version=BRANCH_HYGIENE_VERSION,
            branch=candidate.name,
            expected_sha=candidate.expected_sha,
            current_sha=None,
            protected=None,
            compare_status=None,
            ahead_by=None,
            behind_by=None,
            safe_to_delete=True,
            state="ALREADY_ABSENT",
            reason="Branch no longer exists; cleanup is idempotently complete.",
        )

    if current_sha != candidate.expected_sha:
        return BranchHygieneDecision(
            version=BRANCH_HYGIENE_VERSION,
            branch=candidate.name,
            expected_sha=candidate.expected_sha,
            current_sha=current_sha,
            protected=protected,
            compare_status=compare_status,
            ahead_by=ahead_by,
            behind_by=behind_by,
            safe_to_delete=False,
            state="BLOCKED_HEAD_MOVED",
            reason="Branch head moved after audit; refuse deletion until it is re-audited.",
        )

    if protected:
        return BranchHygieneDecision(
            version=BRANCH_HYGIENE_VERSION,
            branch=candidate.name,
            expected_sha=candidate.expected_sha,
            current_sha=current_sha,
            protected=True,
            compare_status=compare_status,
            ahead_by=ahead_by,
            behind_by=behind_by,
            safe_to_delete=False,
            state="BLOCKED_PROTECTED_BRANCH",
            reason="Protected branches are never cleanup targets.",
        )

    if ahead_by != 0 or compare_status not in {"behind", "identical"}:
        return BranchHygieneDecision(
            version=BRANCH_HYGIENE_VERSION,
            branch=candidate.name,
            expected_sha=candidate.expected_sha,
            current_sha=current_sha,
            protected=bool(protected),
            compare_status=compare_status,
            ahead_by=ahead_by,
            behind_by=behind_by,
            safe_to_delete=False,
            state="BLOCKED_UNMERGED_HISTORY",
            reason="Branch still has commits not reachable from main; preserve it for review.",
        )

    return BranchHygieneDecision(
        version=BRANCH_HYGIENE_VERSION,
        branch=candidate.name,
        expected_sha=candidate.expected_sha,
        current_sha=current_sha,
        protected=bool(protected),
        compare_status=compare_status,
        ahead_by=ahead_by,
        behind_by=behind_by,
        safe_to_delete=True,
        state="SAFE_TO_DELETE",
        reason="Exact audited head is fully reachable from main and the branch is not protected.",
    )
