from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


ADVICE_SCHEMA_VERSION = "1.0"
_CAPABILITY_ORDER = ("efficient", "balanced", "advanced")
_SURFACE_SCORE = {
    "MICRO": 0,
    "FOCUSED": 1,
    "PAGE": 2,
    "REDESIGN": 3,
    "PRODUCT": 4,
}
_HIGH_RISK_TERMS = (
    "architecture",
    "security",
    "auth",
    "authentication",
    "authorization",
    "provider truth",
    "provider attestation",
    "production",
    "release",
    "deploy",
    "migration",
    "data loss",
    "permission",
    "read-only",
    "read_only",
    "regression",
    "integration",
    "governance",
    "payment",
    "secret",
    "credential",
)
_MEDIUM_COMPLEXITY_TERMS = (
    "responsive",
    "accessibility",
    "research",
    "benchmark",
    "competitor",
    "design system",
    "animation",
    "motion",
    "prototype",
    "multi-step",
    "multi step",
    "root cause",
)
_LOW_COMPLEXITY_TERMS = (
    "typo",
    "copy",
    "padding",
    "spacing",
    "rename",
    "label",
    "small fix",
    "minor fix",
)


@dataclass(frozen=True)
class ExecutionAdvice:
    schema_version: str
    advisory_only: bool
    manual_model_selection_required: bool
    overall_profile: dict[str, Any]
    stage_profiles: list[dict[str, Any]]
    context_strategy: dict[str, Any]
    continuation_strategy: dict[str, Any]
    measurement_strategy: dict[str, Any]
    quality_boundary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _contains_any(text: str, terms: tuple[str, ...]) -> list[str]:
    return [term for term in terms if term in text]


def _capability_for_score(score: int) -> str:
    if score >= 6:
        return "advanced"
    if score >= 3:
        return "balanced"
    return "efficient"


def _max_capability(*values: str) -> str:
    valid = [value for value in values if value in _CAPABILITY_ORDER]
    if not valid:
        return "balanced"
    return max(valid, key=_CAPABILITY_ORDER.index)


def _reasoning_for_capability(capability: str) -> str:
    return {
        "efficient": "low",
        "balanced": "medium",
        "advanced": "high",
    }[capability]


def _stage_profile(stage: Any, *, task_floor: str, high_risk: bool) -> dict[str, Any]:
    agent = str(getattr(stage, "agent", "development"))
    gates = list(getattr(stage, "gates", []) or [])
    skills = list(getattr(stage, "skills", []) or [])

    stage_floor = {
        "research": "balanced",
        "implementation": "balanced",
        "qa": "balanced",
        "development": "balanced",
    }.get(agent, "balanced")
    if high_risk and agent in {"implementation", "qa", "development"}:
        stage_floor = "advanced"

    capability = _max_capability(task_floor, stage_floor)
    return {
        "stage_id": str(getattr(stage, "id", "")),
        "agent": agent,
        "recommended_capability": capability,
        "reasoning_effort": _reasoning_for_capability(capability),
        "skill_count": len(skills),
        "gate_count": len(gates),
        "model_stickiness": "keep the selected model stable for this stage/tool loop",
        "reselect_between_runs_only": True,
    }


def build_execution_advice(
    goal: str,
    context: dict[str, Any],
    flow: Any,
    policy_doc: dict[str, Any],
) -> ExecutionAdvice:
    """Build a deterministic, advisory compute profile for external collaborators.

    This never selects or switches the model inside ChatGPT/Codex/other consumer UIs.
    It recommends a capability/reasoning floor before execution and preserves the
    repository's correctness-first contract.
    """

    normalized = " ".join(str(goal).lower().split())
    reasons: list[str] = []
    score = _SURFACE_SCORE.get(str(context.get("change_surface", "FOCUSED")), 1)

    high_matches = _contains_any(normalized, _HIGH_RISK_TERMS)
    medium_matches = _contains_any(normalized, _MEDIUM_COMPLEXITY_TERMS)
    low_matches = _contains_any(normalized, _LOW_COMPLEXITY_TERMS)

    if high_matches:
        score += 3
        reasons.append("high-risk semantic signals: " + ", ".join(high_matches[:6]))
    if medium_matches:
        score += min(2, len(medium_matches))
        reasons.append("multi-dimensional task signals: " + ", ".join(medium_matches[:6]))
    if low_matches and not high_matches and score <= 2:
        score = max(0, score - 1)
        reasons.append("narrow deterministic edit signals: " + ", ".join(low_matches[:4]))

    risk = str(context.get("risk", "standard"))
    authority = str(context.get("authority", context.get("effective_authority", "read_only")))
    mode = str(context.get("mode", "interactive-prototype"))
    stage_count = len(list(getattr(flow, "stages", []) or []))

    high_risk = bool(high_matches)
    if risk in {"high", "critical", "production"}:
        score += 2
        high_risk = True
        reasons.append(f"task risk={risk}")
    if authority in {"external_write", "release"}:
        score += 2
        high_risk = True
        reasons.append(f"authority={authority}")
    if mode == "production":
        score += 2
        high_risk = True
        reasons.append("production mode")
    elif mode == "production-candidate":
        score += 1
        reasons.append("production-candidate mode")
    if stage_count >= 4:
        score += 1
        reasons.append(f"long flow with {stage_count} stages")

    recommended = _capability_for_score(score)
    capability_floor = "advanced" if high_risk else ("balanced" if stage_count >= 2 else "efficient")
    recommended = _max_capability(recommended, capability_floor)
    downgrade_allowed = capability_floor != "advanced"

    picker_instruction = {
        "efficient": "Choose a fast/efficient model that is still capable of the task.",
        "balanced": "Choose a balanced reasoning/coding model.",
        "advanced": "Choose the strongest available reasoning/coding model for this run.",
    }[recommended]

    advisor_policy = dict(policy_doc.get("external_execution_advisor", {}))
    context_policy = dict(policy_doc.get("provider_context", {}))
    jit_policy = dict(policy_doc.get("jit_skill_context", {}))
    split_stage_threshold = int(advisor_policy.get("split_stage_threshold", 4))
    split_score_threshold = int(advisor_policy.get("split_score_threshold", 6))
    suggest_split = stage_count >= split_stage_threshold or score >= split_score_threshold

    stage_profiles = [
        _stage_profile(stage, task_floor=capability_floor, high_risk=high_risk)
        for stage in list(getattr(flow, "stages", []) or [])
    ]

    if not reasons:
        reasons.append("bounded task contract without elevated risk signals")

    return ExecutionAdvice(
        schema_version=ADVICE_SCHEMA_VERSION,
        advisory_only=True,
        manual_model_selection_required=True,
        overall_profile={
            "recommended_capability": recommended,
            "capability_floor": capability_floor,
            "reasoning_effort": _reasoning_for_capability(recommended),
            "downgrade_allowed": downgrade_allowed,
            "complexity_score": score,
            "selection_reasons": reasons,
            "picker_instruction": picker_instruction,
            "auto_switch_model_in_consumer_ui": False,
            "rule": (
                "This is a preflight recommendation only. ChatGPT/Codex model selection remains "
                "manual; never downgrade below the capability floor to save tokens."
            ),
        },
        stage_profiles=stage_profiles,
        context_strategy={
            "mode": "progressive_disclosure",
            "active_stage_only": True,
            "max_active_skills_per_stage": int(jit_policy.get("max_active_per_stage", 6)),
            "provider_document_char_ceiling": int(
                context_policy.get("max_document_chars_per_request", 180000)
            ),
            "stable_prefix": [
                "AGENTS.md",
                "docs/CONTRACT-OWNERSHIP.md",
                "task contract / manifest",
                "resolved flow",
            ],
            "dynamic_tail": [
                "active-stage SKILL.md files",
                "target files directly needed by the current decision",
                "current-run evidence",
            ],
            "avoid_eager_loading": True,
            "prompt_cache_guidance": (
                "Keep stable policy/instruction context ordered before dynamic task evidence so "
                "provider/platform-native prompt caching can help when available; never assume a cache hit."
            ),
            "compression_guidance": (
                "Prefer an evidence-preserving checkpoint summary over lossy prompt compression. "
                "Do not compress mandatory rules, authority constraints, acceptance criteria or unresolved failures."
            ),
        },
        continuation_strategy={
            "suggest_split_into_separate_runs": suggest_split,
            "checkpoint_boundary": "after each completed flow stage and before context reset",
            "resume_source": "latest verified checkpoint + unresolved work + required evidence refs",
            "model_stickiness": (
                "Do not switch models inside an active tool loop solely for cost. Reselect only at a clean "
                "checkpoint or separate run when the next stage has a different capability floor."
            ),
            "quota_exhaustion": (
                "Persist completed stages and unresolved blockers; resume from the checkpoint instead of "
                "re-reading the whole repository or replaying verified work."
            ),
        },
        measurement_strategy={
            "measure_before_default_downgrade": True,
            "compare": [
                "acceptance-criteria completion",
                "verification pass/fail",
                "repair/retry count",
                "task completion before quota exhaustion",
                "input/output token usage when provider metadata exists",
                "elapsed time and provider cost when available",
            ],
            "promotion_rule": (
                "Promote a cheaper/smaller profile only when representative-task quality is non-inferior "
                "and completion reliability does not regress."
            ),
        },
        quality_boundary={
            "optimization_order": [
                "correctness",
                "grounding",
                "completion",
                "verification",
                "maintainability",
                "clarity",
                "compute_efficiency",
            ],
            "provider_or_model_self_report_is_evidence": False,
            "advisor_may_change_authority": False,
            "advisor_may_satisfy_gates": False,
            "advisor_may_authorize_release": False,
        },
    )
