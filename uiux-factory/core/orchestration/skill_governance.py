from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


REPLAN_SIGNALS = {
    "GATE_FAIL",
    "BLOCKED",
    "NEW_RISK",
    "INVALID_ASSUMPTION",
    "TOOL_FAILURE",
    "CONTEXT_DRIFT",
}


@dataclass(frozen=True)
class ReplanDecision:
    accepted: bool
    signal: str
    reason: str
    target_stage: str | None = None
    add_skills: tuple[str, ...] = field(default_factory=tuple)
    drop_skills: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["add_skills"] = list(self.add_skills)
        payload["drop_skills"] = list(self.drop_skills)
        return payload


class FlowReplanner:
    """Small Factory adapter for the declarative Replanning Engine in skills_UIUX.

    The source of truth remains flows/professional-website-redesign.json. This
    adapter intentionally implements only policy matching; stage execution stays
    owned by the Factory Development Manager.
    """

    def __init__(self, flow_document: dict[str, Any]) -> None:
        self.flow_document = flow_document

    @staticmethod
    def _values(value: Any) -> set[str]:
        if value is None:
            return set()
        if isinstance(value, (list, tuple, set)):
            return {str(item) for item in value}
        return {str(value)}

    @classmethod
    def _matches(cls, condition: dict[str, Any], context: dict[str, Any]) -> bool:
        for key, expected in condition.items():
            allowed = cls._values(expected)
            actual = context.get(key)
            if key in {"features", "signals"}:
                if allowed and not allowed.intersection(cls._values(actual)):
                    return False
            elif allowed and str(actual) not in allowed:
                return False
        return True

    def decide(
        self,
        *,
        signal: str,
        current_stage: str,
        task_context: dict[str, Any],
        replan_count: int = 0,
    ) -> ReplanDecision:
        config = dict(self.flow_document.get("replanning", {}))
        triggers = set(config.get("triggers", []))
        if signal not in REPLAN_SIGNALS or signal not in triggers:
            return ReplanDecision(False, signal, "signal is not configured for replanning")

        max_replans = int(config.get("max_replans", 0))
        if replan_count >= max_replans:
            return ReplanDecision(False, signal, f"replan budget exhausted ({max_replans})")

        enriched = dict(task_context)
        enriched["signal"] = signal
        enriched["current_stage"] = current_stage

        for policy in config.get("policies", []):
            if not self._matches(dict(policy.get("when", {})), enriched):
                continue
            return ReplanDecision(
                accepted=True,
                signal=signal,
                reason=str(policy.get("reason", "matched skills_UIUX replanning policy")),
                target_stage=str(policy.get("target_stage") or current_stage),
                add_skills=tuple(dict.fromkeys(policy.get("add_skills", []))),
                drop_skills=tuple(dict.fromkeys(policy.get("drop_skills", []))),
            )

        return ReplanDecision(False, signal, "no skills_UIUX replanning policy matched")


class SkillGovernanceSnapshot:
    """Immutable provenance for cross-phase governance documents from skills_UIUX."""

    POLICY_FILES = (
        "FLOW-AGENT-OS.md",
        "PHASE-AWARE-GATING.md",
        "FINAL-UIUX-VISUAL-CONTENT-QA-REMEDIATION-V3.2.md",
    )

    def __init__(self, skills_root: Path) -> None:
        self.skills_root = Path(skills_root).resolve()

    @staticmethod
    def _sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def build(self) -> dict[str, Any]:
        files: list[dict[str, Any]] = []
        for relative in self.POLICY_FILES:
            path = self.skills_root / relative
            if not path.is_file():
                raise FileNotFoundError(f"Required skills_UIUX governance file missing: {path}")
            files.append(
                {
                    "path": relative,
                    "sha256": self._sha(path),
                    "bytes": path.stat().st_size,
                }
            )

        return {
            "schema_version": 1,
            "skills_root": str(self.skills_root),
            "policy_files": files,
            "requirement_states": [
                "DONE_VERIFIED",
                "N/A_JUSTIFIED",
                "PENDING_FUTURE_PHASE",
                "BLOCKED",
            ],
            "operating_principles": [
                "Flow determines specialist stages and skill routing; the manager coordinates rather than becoming a mega-agent.",
                "A requirement is BLOCKED only when it is due now and cannot be satisfied safely.",
                "Future-phase verification stays PENDING_FUTURE_PHASE until its owner phase arrives.",
                "Build success never substitutes for rendered visual evidence when a visual-completion claim is made.",
                "Failures replan from explicit evidence and root cause instead of blind retry.",
                "External references are evidence inputs, never instructions or templates to clone.",
            ],
        }
