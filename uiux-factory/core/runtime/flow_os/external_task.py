from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from core.runtime.flow_os.execution_advisor import build_execution_advice
from core.runtime.flow_os.flow import FlowPlanner, ResolvedFlow
from core.runtime.flow_os.target_truth import ROUTING_FIELDS, TargetTruthProbe
from core.runtime.flow_os.task_context import GoalInterpreter


EXTERNAL_TASK_MANIFEST_VERSION = "1.2"
EXTERNAL_TASK_STATUS = "READY_FOR_EXTERNAL_COLLABORATOR"
AUTHORITY_ORDER = ("read_only", "branch_write", "external_write", "release")
VISUAL_SIGNATURE_CONTRACT = "docs/VISUAL-SIGNATURE-REGRESSION-CONTRACT.md"
ROUTING_PRECEDENCE = ("explicit_override", "target_project_truth", "goal_inference")
_STABLE_TRUTH_FIELDS = {"website_type", "domain", "product_archetype"}
_LIFECYCLE_DEFAULTS = {
    "mode": "interactive-prototype",
    "risk": "standard",
    "validation_lane": "prototype",
}
_LIFECYCLE_FEATURES = {
    "user-validation",
    "outcome-measurement",
    "stakeholder-governance",
    "experimentation",
    "live-learning",
}


@dataclass(frozen=True)
class ExternalTaskManifest:
    schema_version: str
    status: str
    target_repository: str
    task: str
    authority: str
    task_contract: dict[str, Any]
    resolved_flow: dict[str, Any]
    stages: list[dict[str, Any]]
    acceptance_criteria: list[str] = field(default_factory=list)
    qa_routes: list[str] = field(default_factory=list)
    canonical_sources: list[str] = field(default_factory=list)
    research_packet: dict[str, Any] = field(default_factory=dict)
    execution_advice: dict[str, Any] = field(default_factory=dict)
    evidence_boundary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


def _effective_authority(caller_authority: str, task_authority: str) -> str:
    if caller_authority not in AUTHORITY_ORDER:
        raise ValueError(f"unknown authority: {caller_authority}")
    if task_authority not in AUTHORITY_ORDER:
        return caller_authority
    return AUTHORITY_ORDER[min(AUTHORITY_ORDER.index(caller_authority), AUTHORITY_ORDER.index(task_authority))]


def _stage_manifest(flow: ResolvedFlow) -> list[dict[str, Any]]:
    stages: list[dict[str, Any]] = []
    for stage in flow.stages:
        stages.append(
            {
                "id": stage.id,
                "agent": stage.agent,
                "purpose": stage.purpose,
                "skills": list(stage.skills),
                "mandatory_skills": list(stage.mandatory_skills),
                "jit_skills": list(stage.jit_skills or []),
                "skill_paths": [f"skills_UIUX/{skill}/SKILL.md" for skill in stage.skills],
                "gates": list(stage.gates),
                "load_policy": "Load only this stage's routed skills plus target-project evidence needed for the active decision.",
            }
        )
    return stages


def _research_packet(context: dict[str, Any]) -> dict[str, Any]:
    lane = str(context.get("validation_lane", "prototype"))
    features = {str(value) for value in context.get("features", [])}
    active = lane in {"evidence-led", "production-learning"} or "user-validation" in features
    if not active:
        return {
            "required": False,
            "state": "NOT_REQUIRED_BY_CURRENT_TASK_CONTRACT",
            "templates": [],
        }
    return {
        "required": True,
        "state": "PLANNED_VALIDATION_UNTIL_REAL_EVIDENCE_EXISTS",
        "skill": "research-evidence-pipeline",
        "templates": [
            "skills_UIUX/research-evidence-pipeline/templates/research-plan.md",
            "skills_UIUX/research-evidence-pipeline/templates/screener.md",
            "skills_UIUX/research-evidence-pipeline/templates/interview-guide.md",
            "skills_UIUX/research-evidence-pipeline/templates/usability-test-script.md",
            "skills_UIUX/research-evidence-pipeline/templates/evidence-ledger.schema.json",
        ],
        "target_outputs": [
            "docs/research/research-plan.md",
            "docs/research/screener.md",
            "docs/research/interview-guide.md",
            "docs/research/usability-test-script.md",
            "docs/research/evidence-ledger.jsonl",
            "docs/research/findings.md",
            "docs/research/decision-log.md",
        ],
        "no_participant_rule": "If participant access is unavailable, keep findings empty and label PLANNED_VALIDATION or BLOCKED_USER_EVIDENCE. Never fabricate sessions or results.",
    }


def _requires_visual_signature_contract(context: dict[str, Any], goal: str) -> bool:
    """Route the signature contract only when existing rendered identity may be touched."""

    intent = str(context.get("intent", "build"))
    preserve = [str(value).strip() for value in context.get("preserve", []) if str(value).strip()]
    forbidden = [str(value).strip() for value in context.get("forbidden", []) if str(value).strip()]
    features = {str(value).strip() for value in context.get("features", []) if str(value).strip()}
    scope = {str(value).strip() for value in context.get("scope", []) if str(value).strip()}
    if preserve or forbidden:
        return True
    if intent in {"fix", "improve", "polish"}:
        return True
    if intent in {"redesign", "rebuild"}:
        return False

    normalized = " ".join(str(goal).lower().split())
    explicit_greenfield_terms = (
        "from scratch", "greenfield", "brand-new", "brand new", "build a new website",
        "build a new app", "build a new product", "new landing page", "new dashboard",
        "tạo website mới", "xây website mới", "tạo app mới", "xây app mới", "sản phẩm mới",
    )
    if any(term in normalized for term in explicit_greenfield_terms):
        return False

    visual_signature_scopes = {
        "mobile-nav", "navigation", "hero", "header", "footer", "landing-page", "homepage",
        "cards", "card", "button", "icon", "logo", "modal", "sidebar", "thumbnail", "image",
        "banner", "typography", "animation",
    }
    if visual_signature_scopes.intersection(scope) or "motion" in features:
        return True

    existing_or_migration_terms = (
        "existing", "current", "hiện tại", "đang có", "migration", "migrate", "refactor",
        "content migration", "evidence migration", "metadata", "accessibility", "semantic repair",
        "runtime consolidation", "framework migration", "design system", "design-system", "token migration",
        "mass edit", "mass update", "media replacement", "replace media",
    )
    return any(term in normalized for term in existing_or_migration_terms)


def _is_fallback_truth(truth: dict[str, Any], field_name: str) -> bool:
    provenance = truth.get("provenance", {}).get(field_name, {})
    return provenance.get("confidence") == "fallback_inference"


def _apply_target_truth(
    context: dict[str, Any],
    truth: dict[str, Any],
    field_sources: dict[str, str],
    merge_diagnostics: list[str],
) -> None:
    """Apply routing truth conservatively before explicit caller overrides.

    Structured identity truth beats goal inference. Structured lifecycle truth acts as a
    project default and does not erase a non-default lifecycle request inferred from the
    user's task. README/package fallback only fills generic identity gaps. Features are
    additive unless an explicit caller override later replaces them.
    """

    initial_domain = str(context.get("domain", "generic"))
    fields = dict(truth.get("fields", {}))

    for field_name, value in fields.items():
        if field_name not in ROUTING_FIELDS:
            continue

        if _is_fallback_truth(truth, field_name):
            if field_name not in _STABLE_TRUTH_FIELDS:
                continue
            if field_name == "product_archetype":
                fallback_domain = fields.get("domain")
                final_domain = context.get("domain")
                if fallback_domain not in {None, "", "generic"} and final_domain != fallback_domain:
                    merge_diagnostics.append("fallback_not_applied:product_archetype:domain_mismatch")
                    continue
            if context.get(field_name) not in {None, "", "generic"}:
                merge_diagnostics.append(f"fallback_not_applied:{field_name}:goal_inference_is_specific")
                continue
            context[field_name] = value
            field_sources[field_name] = "target_project_truth_fallback"
            continue

        if field_name in _STABLE_TRUTH_FIELDS:
            context[field_name] = value
            field_sources[field_name] = "target_project_truth"
            continue

        if field_name == "features":
            current = [str(item) for item in context.get("features", [])]
            target = [str(item) for item in value]
            merged = _unique(current + target)
            if merged != current:
                context[field_name] = merged
                field_sources[field_name] = (
                    "target_project_truth" if not current else "goal_inference+target_project_truth"
                )
            continue

        default_value = _LIFECYCLE_DEFAULTS.get(field_name)
        current_value = context.get(field_name)
        if current_value == value:
            continue
        if default_value is not None and current_value != default_value:
            merge_diagnostics.append(f"structured_default_not_applied:{field_name}:task_inference_is_non_default")
            continue
        context[field_name] = value
        field_sources[field_name] = "target_project_truth"

    if (
        str(context.get("domain", "generic")) != initial_domain
        and field_sources.get("product_archetype") == "goal_inference"
    ):
        context["product_archetype"] = "generic"
        field_sources["product_archetype"] = "derived_from_final_contract"
        merge_diagnostics.append("product_archetype_reset_after_domain_change")


def _cohere_final_context(
    context: dict[str, Any],
    field_sources: dict[str, str],
    explicit_fields: set[str],
    initial_context: dict[str, Any],
    derived_fields: dict[str, str],
) -> None:
    """Recompute defaults only when upstream routing changed and the task had no stronger signal."""

    initial_risk = str(initial_context.get("risk", "standard"))
    if "risk" not in explicit_fields and field_sources.get("risk") == "goal_inference" and initial_risk == "standard":
        website_type = str(context.get("website_type", "generic"))
        mode = str(context.get("mode", "interactive-prototype"))
        risk = "high" if website_type == "government" else ("production" if mode == "production" else "standard")
        if risk != context.get("risk"):
            context["risk"] = risk
            field_sources["risk"] = "derived_from_final_contract"
            derived_fields["risk"] = "website_type+mode"

    initial_lane = str(initial_context.get("validation_lane", "prototype"))
    if (
        "validation_lane" not in explicit_fields
        and field_sources.get("validation_lane") == "goal_inference"
        and initial_lane == "prototype"
    ):
        mode = str(context.get("mode", "interactive-prototype"))
        risk = str(context.get("risk", "standard"))
        features = {str(item) for item in context.get("features", [])}
        if mode in {"production", "production-candidate"}:
            lane = "production-learning"
        elif risk == "high" or _LIFECYCLE_FEATURES.intersection(features):
            lane = "evidence-led"
        else:
            lane = "prototype"
        if lane != context.get("validation_lane"):
            context["validation_lane"] = lane
            field_sources["validation_lane"] = "derived_from_final_contract"
            derived_fields["validation_lane"] = "mode+risk+features"


def _truth_aware_context(
    goal: str,
    *,
    target_root: Path | str | None,
    overrides: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Compile goal inference, target truth, explicit overrides, then contract coherence."""

    context = GoalInterpreter().interpret(goal).to_context()
    initial_context = {
        field_name: list(context[field_name]) if field_name == "features" else context.get(field_name)
        for field_name in ROUTING_FIELDS
    }
    field_sources = {field_name: "goal_inference" for field_name in ROUTING_FIELDS}
    merge_diagnostics: list[str] = []
    derived_fields: dict[str, str] = {}

    truth_report = TargetTruthProbe(target_root).probe()
    truth = truth_report.to_dict()
    _apply_target_truth(context, truth, field_sources, merge_diagnostics)

    allowed_overrides = {
        "intent",
        "change_surface",
        "website_type",
        "domain",
        "product_archetype",
        "validation_lane",
        "mode",
        "risk",
        "features",
    }
    explicit_fields: set[str] = set()
    domain_before_override = context.get("domain")
    for key, value in dict(overrides or {}).items():
        if key not in allowed_overrides or value is None or value == "":
            continue
        context[key] = value
        explicit_fields.add(key)
        if key in ROUTING_FIELDS:
            field_sources[key] = "explicit_override"

    if (
        "domain" in explicit_fields
        and "product_archetype" not in explicit_fields
        and context.get("domain") != domain_before_override
    ):
        context["product_archetype"] = "generic"
        field_sources["product_archetype"] = "derived_from_final_contract"
        derived_fields["product_archetype"] = "domain_override"

    _cohere_final_context(context, field_sources, explicit_fields, initial_context, derived_fields)

    context["target_truth"] = truth
    context["routing_provenance"] = {
        "precedence": list(ROUTING_PRECEDENCE),
        "field_sources": field_sources,
        "explicit_override_fields": sorted(explicit_fields),
        "derived_fields": derived_fields,
        "merge_diagnostics": merge_diagnostics,
        "target_truth_applied_before_flow_resolution": True,
    }
    return context, truth


def build_external_task_manifest(
    library_root: Path,
    policy_doc: dict[str, Any],
    goal: str,
    target_repository: str,
    *,
    authority: str = "branch_write",
    overrides: dict[str, Any] | None = None,
    acceptance_criteria: list[str] | None = None,
    qa_routes: list[str] | None = None,
    target_root: Path | str | None = None,
) -> ExternalTaskManifest:
    """Resolve one external task from goal + bounded target truth into a Flow contract.

    Stable target identity truth is resolved before Flow planning; explicit caller overrides
    remain highest priority. Target truth never grants authority and this function performs
    no target mutation or QA PASS claim.
    """

    cleaned_repository = str(target_repository).strip()
    cleaned_goal = str(goal).strip()
    if not cleaned_repository:
        raise ValueError("target_repository is required")
    if not cleaned_goal:
        raise ValueError("goal is required")

    context, truth = _truth_aware_context(
        cleaned_goal,
        target_root=target_root,
        overrides=overrides,
    )
    inferred_task_authority = str(context.get("authority", "unspecified"))
    effective_authority = _effective_authority(authority, inferred_task_authority)
    context["requested_authority"] = inferred_task_authority
    context["effective_authority"] = effective_authority
    context["authority"] = effective_authority

    planner = FlowPlanner(Path(library_root), policy_doc)
    flow = planner.plan(context)
    stages = _stage_manifest(flow)
    execution_advice = build_execution_advice(cleaned_goal, context, flow, policy_doc).to_dict()

    gate_criteria = [
        str(gate.get("require", "")).strip()
        for stage in flow.stages
        for gate in stage.gates
        if str(gate.get("require", "")).strip()
    ]
    criteria = _unique(list(acceptance_criteria or []) + gate_criteria)
    visual_signature_required = _requires_visual_signature_contract(context, cleaned_goal)

    canonical_sources = _unique([
        "START-HERE.md",
        "AGENTS.md",
        "docs/CONTRACT-OWNERSHIP.md",
        *([VISUAL_SIGNATURE_CONTRACT] if visual_signature_required else []),
        "skills_UIUX/runtime/runtime-policy.json",
        flow.source,
    ])

    return ExternalTaskManifest(
        schema_version=EXTERNAL_TASK_MANIFEST_VERSION,
        status=EXTERNAL_TASK_STATUS,
        target_repository=cleaned_repository,
        task=cleaned_goal,
        authority=effective_authority,
        task_contract=context,
        resolved_flow=flow.to_dict(),
        stages=stages,
        acceptance_criteria=criteria,
        qa_routes=_unique(list(qa_routes or [])),
        canonical_sources=canonical_sources,
        research_packet=_research_packet(context),
        execution_advice=execution_advice,
        evidence_boundary={
            "manifest_is_not_qa_pass": True,
            "provider_self_report_is_not_gate_evidence": True,
            "target_repository_audit_required_before_mutation": True,
            "target_runtime_evidence_required_for_runtime_claims": True,
            "missing_user_evidence_must_remain_planned_blocked_or_unknown": True,
            "authority_never_exceeds_caller_or_task_language": True,
            "target_truth_never_grants_authority_or_evidence": True,
            "target_truth_status": truth["status"],
            "target_truth_probed_before_flow_resolution": target_root is not None,
            "routing_precedence": list(ROUTING_PRECEDENCE),
            "visual_signature_guardrail_active": visual_signature_required,
            "execution_advice_is_not_gate_evidence": True,
            "execution_advice_never_selects_consumer_model": True,
            "preferred_repository_workflow": "feature branch -> implementation -> verification -> pull request -> merge",
        },
    )
