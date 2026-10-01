from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator, model_validator

from core.brain_os.contracts import BrainContractModel
from core.runtime.flow_os.flow import ResolvedStage
from core.runtime.flow_os.skill_sections import SkillSectionPolicy


CANONICAL_SKILL_OWNER = "core.runtime.flow_os.flow.SkillResolver"


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in values:
        value = str(raw).strip()
        if value and value not in seen:
            seen.add(value)
            output.append(value)
    return output


def _jit_policy(policy_doc: dict[str, object]) -> tuple[bool, int]:
    raw = policy_doc.get("jit_skill_context", {})
    if not isinstance(raw, dict):
        raise ValueError("runtime-policy jit_skill_context must be an object")
    enabled = raw.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ValueError("jit_skill_context.enabled must be a boolean")
    max_active = raw.get("max_active_per_stage", 6)
    if isinstance(max_active, bool) or not isinstance(max_active, int):
        raise ValueError("jit_skill_context.max_active_per_stage must be an integer")
    if max_active < 1 or max_active > 32:
        raise ValueError("jit_skill_context.max_active_per_stage must be between 1 and 32")
    return enabled, max_active


def _provider_policy_ceiling(policy_doc: dict[str, object]) -> int:
    raw = policy_doc.get("provider_context", {})
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("runtime-policy provider_context must be an object")
    max_chars = raw.get("max_document_chars_per_request", 180000)
    if isinstance(max_chars, bool) or not isinstance(max_chars, int):
        raise ValueError("provider_context.max_document_chars_per_request must be an integer")
    if max_chars < 1 or max_chars > 2_000_000:
        raise ValueError("provider_context.max_document_chars_per_request must be between 1 and 2000000")
    return max_chars


class JITContextPlan(BrainContractModel):
    """Read-only Brain view of one canonical ResolvedStage context envelope.

    It projects routing already performed by `SkillResolver` and operator-owned runtime
    limits. It does not activate skills, load provider documents, change routing, satisfy
    gates, alter authority or become evidence.
    """

    schema_version: Literal["brain-jit-context.v1"] = "brain-jit-context.v1"
    stage_id: str = Field(min_length=1, max_length=256)
    agent: str = Field(min_length=1, max_length=256)
    canonical_skill_owner: Literal["core.runtime.flow_os.flow.SkillResolver"] = CANONICAL_SKILL_OWNER
    mandatory_skills: list[str] = Field(default_factory=list, max_length=200)
    routed_jit_skills: list[str] = Field(default_factory=list, max_length=200)
    jit_skill_sources: dict[str, str] = Field(default_factory=dict)
    jit_enabled: bool
    max_active_per_stage: int = Field(ge=1, le=32)
    active_jit_skills: list[str] = Field(default_factory=list, max_length=32)
    available_jit_skills: list[str] = Field(default_factory=list, max_length=200)
    active_skill_names: list[str] = Field(default_factory=list, max_length=232)
    provider_document_char_policy_ceiling: int = Field(ge=1, le=2_000_000)
    skill_sections_enabled: bool
    max_sections_per_skill: int = Field(ge=1, le=256)
    max_section_chars: int = Field(ge=256, le=100000)
    max_retrievals_per_stage: int = Field(ge=1, le=256)
    max_total_retrieved_chars: int = Field(ge=1024, le=2_000_000)
    max_index_chars: int = Field(ge=1024, le=500000)
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"

    @field_validator(
        "mandatory_skills",
        "routed_jit_skills",
        "active_jit_skills",
        "available_jit_skills",
        "active_skill_names",
    )
    @classmethod
    def _normalize_skill_lists(cls, values: list[str]) -> list[str]:
        return _unique(values)

    @model_validator(mode="after")
    def _validate_projection(self) -> "JITContextPlan":
        mandatory = set(self.mandatory_skills)
        pool = set(self.routed_jit_skills)
        active = set(self.active_jit_skills)
        available = set(self.available_jit_skills)
        if mandatory.intersection(pool):
            raise ValueError("mandatory skills cannot also appear in routed JIT pool")
        if set(self.jit_skill_sources).difference(pool):
            raise ValueError("JIT source metadata may reference routed JIT skills only")
        if active.difference(pool):
            raise ValueError("active JIT skills must come from the routed JIT pool")
        if self.jit_enabled and len(self.active_jit_skills) > self.max_active_per_stage:
            raise ValueError("active JIT skill count exceeds runtime-policy max_active_per_stage")
        if self.jit_enabled:
            expected_available = [skill for skill in self.routed_jit_skills if skill not in active]
            if self.available_jit_skills != expected_available:
                raise ValueError("available JIT skills must equal routed pool minus active JIT skills")
        else:
            if self.active_jit_skills != self.routed_jit_skills or self.available_jit_skills:
                raise ValueError("disabled JIT mode must expose the full routed pool as already active")
        expected_active = _unique(self.mandatory_skills + self.active_jit_skills)
        if self.active_skill_names != expected_active:
            raise ValueError("active_skill_names must equal mandatory + active JIT skills")
        return self


class JITActivationRequest(BrainContractModel):
    """Advisory request for runtime JIT activation; never an activation receipt."""

    schema_version: Literal["brain-jit-activation-request.v1"] = "brain-jit-activation-request.v1"
    stage_id: str = Field(min_length=1, max_length=256)
    skill: str = Field(min_length=1, max_length=256)
    source: str = Field(min_length=1, max_length=64)
    already_active: bool
    active_count_before: int = Field(ge=0, le=32)
    active_count_after: int = Field(ge=0, le=32)
    max_active_per_stage: int = Field(ge=1, le=32)
    runtime_preflight_required: bool = True
    authority_effect: Literal["none"] = "none"
    gate_effect: Literal["none"] = "none"
    evidence_effect: Literal["none"] = "none"


def project_stage_jit_context(
    stage: ResolvedStage,
    policy_doc: dict[str, object],
    *,
    active_jit_skills: list[str] | None = None,
) -> JITContextPlan:
    """Project canonical stage routing and runtime-policy budgets into a Brain view."""

    enabled, max_active = _jit_policy(policy_doc)
    section_policy = SkillSectionPolicy.from_policy(policy_doc)
    provider_ceiling = _provider_policy_ceiling(policy_doc)

    mandatory = list(stage.mandatory_skills)
    pool = list(stage.jit_skills or [])
    sources = dict(stage.jit_skill_sources or {})

    if enabled:
        active = _unique(list(active_jit_skills or []))
        invalid = sorted(set(active).difference(pool))
        if invalid:
            raise ValueError("requested active JIT skills are not in the routed stage pool: " + ", ".join(invalid))
        if len(active) > max_active:
            raise ValueError("requested active JIT skill count exceeds runtime-policy max_active_per_stage")
        available = [skill for skill in pool if skill not in set(active)]
    else:
        active = list(pool)
        available = []

    return JITContextPlan(
        stage_id=stage.id,
        agent=stage.agent,
        mandatory_skills=mandatory,
        routed_jit_skills=pool,
        jit_skill_sources=sources,
        jit_enabled=enabled,
        max_active_per_stage=max_active,
        active_jit_skills=active,
        available_jit_skills=available,
        active_skill_names=_unique(mandatory + active),
        provider_document_char_policy_ceiling=provider_ceiling,
        skill_sections_enabled=section_policy.enabled,
        max_sections_per_skill=section_policy.max_sections_per_skill,
        max_section_chars=section_policy.max_section_chars,
        max_retrievals_per_stage=section_policy.max_retrievals_per_stage,
        max_total_retrieved_chars=section_policy.max_total_retrieved_chars,
        max_index_chars=section_policy.max_index_chars,
    )


def request_jit_activation(plan: JITContextPlan, skill: str) -> JITActivationRequest:
    """Create a bounded request that the runtime may still reject on document-budget preflight."""

    requested = str(skill).strip()
    if not requested:
        raise ValueError("JIT activation request requires a non-empty skill name")
    if not plan.jit_enabled:
        raise ValueError("JIT skill activation is disabled by runtime policy")
    if requested in set(plan.mandatory_skills):
        raise ValueError(f"skill is mandatory and already active: {requested}")
    if requested not in set(plan.routed_jit_skills):
        raise ValueError(f"skill is not in the Flow-routed JIT pool for this stage: {requested}")

    already_active = requested in set(plan.active_jit_skills)
    before = len(plan.active_jit_skills)
    after = before if already_active else before + 1
    if after > plan.max_active_per_stage:
        raise ValueError("JIT skill activation limit reached for this stage")

    return JITActivationRequest(
        stage_id=plan.stage_id,
        skill=requested,
        source=plan.jit_skill_sources.get(requested, "legacy_inferred"),
        already_active=already_active,
        active_count_before=before,
        active_count_after=after,
        max_active_per_stage=plan.max_active_per_stage,
        runtime_preflight_required=not already_active,
    )
