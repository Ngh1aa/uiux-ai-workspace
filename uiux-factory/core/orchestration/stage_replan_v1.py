from __future__ import annotations

import json
from pathlib import Path


REPLAN_STAGE_ORDER = (
    "research",
    "ux_ia",
    "art_direction",
    "design_contract",
    "design_system",
    "implementation_plan",
    "visual_composition",
    "implementation",
)

STAGE_ARTIFACT_KEYS = {
    "research": ("research",),
    "ux_ia": ("ux_ia",),
    "art_direction": ("art_direction",),
    "design_contract": ("design_contract",),
    "design_system": ("design_system", "design_document", "design_tokens"),
    "implementation_plan": ("implementation_plan",),
    "visual_composition": ("visual_composition",),
    "implementation": ("implementation",),
}

QA_OWNER_STAGES = {"browser_qa", "visual_qa", "repair", "quality_loop"}


def canonical_replan_stage(owner_stage: str | None) -> str | None:
    """Map requirement ownership onto the earliest rerunnable Factory stage."""

    if not owner_stage:
        return None
    stage = str(owner_stage).strip()
    if stage in REPLAN_STAGE_ORDER:
        return stage
    if stage == "reference_analysis":
        return "research"
    if stage in QA_OWNER_STAGES:
        return "implementation"
    return None


def stages_from(target_stage: str) -> tuple[str, ...]:
    """Return the canonical downstream invalidation/rerun sequence."""

    target = canonical_replan_stage(target_stage)
    if target is None:
        raise ValueError(f"Unsupported root-cause replan stage: {target_stage!r}")
    index = REPLAN_STAGE_ORDER.index(target)
    return REPLAN_STAGE_ORDER[index:]


def evidence_replan_target(quality_result, quality_output_dir: Path) -> str | None:
    """Resolve the earliest owner from a concrete Evidence Contract remediation plan."""

    stop_reason = str(getattr(quality_result, "stop_reason", "") or "")
    if not stop_reason.startswith("prototype_evidence_contract_requires_root_replan"):
        return None

    plan_path = Path(quality_output_dir) / "evidence-remediation-plan.json"
    if not plan_path.is_file():
        return None
    try:
        payload = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return canonical_replan_stage(payload.get("earliest_owner_stage"))
