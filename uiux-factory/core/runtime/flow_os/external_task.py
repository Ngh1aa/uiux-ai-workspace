from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from core.runtime.flow_os.execution_advisor import build_execution_advice
from core.runtime.flow_os.flow import FlowPlanner, ResolvedFlow
from core.runtime.flow_os.target_truth import ROUTING_PRECEDENCE, build_truth_aware_context
from core.runtime.flow_os.task_context import GoalInterpreter, NON_MUTATING_INTENTS
from core.skills.design_knowledge import design_workflow_packet
from core.skills.research_workflow import research_workflow_packet


EXTERNAL_TASK_MANIFEST_VERSION = "1.3"
EXTERNAL_TASK_STATUS = "READY_FOR_EXTERNAL_COLLABORATOR"
AUTHORITY_ORDER = ("read_only", "branch_write", "external_write", "release")
VISUAL_SIGNATURE_CONTRACT = "docs/VISUAL-SIGNATURE-REGRESSION-CONTRACT.md"

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


def _manifest_library_path(path: str) -> str:
    """Return a workspace-root path that external collaborators can open directly."""

    value = str(path).strip().replace("\\", "/").lstrip("./")
    if not value:
        raise ValueError("manifest library path is required")
    if value.startswith("skills_UIUX/"):
        return value
    return f"skills_UIUX/{value}"


def _effective_authority(caller_authority: str, task_authority: str) -> str:
    if caller_authority not in AUTHORITY_ORDER:
        raise ValueError(f"unknown authority: {caller_authority}")
    if task_authority not in AUTHORITY_ORDER:
        return caller_authority
    return AUTHORITY_ORDER[min(AUTHORITY_ORDER.index(caller_authority), AUTHORITY_ORDER.index(task_authority))]


def _stage_manifest(flow: ResolvedFlow, context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
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
                "design_workflow": design_workflow_packet(context or {}, list(stage.skills), list(stage.gates)),
                "research_workflow": research_workflow_packet(context or {}, stage.id, stage.skills),
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
        "no_participant_rule": "Without participants, keep human findings/sessions empty and label human validation PLANNED_VALIDATION or BLOCKED_USER_EVIDENCE. Traceable DESK_EVIDENCE and its limited findings may be recorded; never fabricate sessions or results.",
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

    context, truth = build_truth_aware_context(
        cleaned_goal,
        target_root=target_root,
        overrides=overrides,
    )
    if context.get("intent") in NON_MUTATING_INTENTS:
        context["authority"] = "read_only"
    inferred_task_authority = str(context.get("authority", "unspecified"))
    effective_authority = _effective_authority(authority, inferred_task_authority)
    context["requested_authority"] = inferred_task_authority
    context["effective_authority"] = effective_authority
    context["authority"] = effective_authority

    planner = FlowPlanner(Path(library_root), policy_doc)
    normalized_context = planner.flow_resolver.normalize_context(context)
    if normalized_context["intent"] != context["intent"]:
        provenance = normalized_context["routing_provenance"]
        provenance["field_sources"]["intent"] = "authority_boundary"
        provenance["merge_diagnostics"].append(
            f"read_only_routing:{context['intent']}->{normalized_context['intent']}"
        )
    context = normalized_context
    flow = planner.plan(context)
    manifest_flow = flow.to_dict()
    manifest_flow["source"] = _manifest_library_path(flow.source)
    stages = _stage_manifest(flow, context)
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
        manifest_flow["source"],
    ])

    return ExternalTaskManifest(
        schema_version=EXTERNAL_TASK_MANIFEST_VERSION,
        status=EXTERNAL_TASK_STATUS,
        target_repository=cleaned_repository,
        task=cleaned_goal,
        authority=effective_authority,
        task_contract=context,
        resolved_flow=manifest_flow,
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
