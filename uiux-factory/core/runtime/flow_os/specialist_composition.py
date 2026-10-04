from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Iterable


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            output.append(text)
    return output


def _as_set(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        return {value}
    return {str(item) for item in value}


def _condition_matches(condition: dict[str, Any], context: dict[str, Any]) -> bool:
    for key, expected in condition.items():
        if key == "signal":
            if str(context.get("signal", "")) not in _as_set(expected):
                return False
            continue
        actual = context.get(key)
        expected_set = _as_set(expected)
        if key in {"features", "signals"}:
            if expected_set and not expected_set.intersection(_as_set(actual)):
                return False
        elif expected_set and str(actual) not in expected_set:
            return False
    return True


class SpecialistComposer:
    """Compose JIT specialists from domain × archetype × surface × feature.

    Flow documents keep lifecycle ownership. Canonical task interpretation owns
    domain/archetype inference; this layer only augments already-selected stages
    with contextual specialists in a stable, de-duplicated order. Optional runtime
    rules extend selected flows through this same composer and JIT provenance.
    """

    DIMENSION_ORDER = ("domain", "archetype", "surface", "feature")

    DOMAIN_SKILLS: dict[str, dict[str, tuple[str, ...]]] = {
        "financial-services": {
            "research": ("financial-product-intelligence", "trust-credibility-and-transparency"),
            "design": ("trust-credibility-and-transparency",),
        },
        "education-edtech": {
            "research": ("education-website", "product-discovery"),
            "design": ("journey-driven-content-and-layout", "complex-workflow-and-progress-ux"),
        },
        "art-culture": {
            "research": ("site-search-and-findability",),
            "design": ("asset-media-and-art-direction", "experience-principles-and-signature-moments"),
            "qa": ("media-crop-and-layout-integrity",),
        },
        "industrial-services": {
            "research": ("corporate-website", "trust-credibility-and-transparency"),
            "design": ("service-experience-to-digital-journey",),
        },
        "enterprise-software": {
            "research": ("product-discovery",),
            "design": ("complex-workflow-and-progress-ux", "data-tables-and-enterprise-ux"),
            "implementation": ("data-tables-and-enterprise-ux",),
        },
        "commerce-retail": {
            "research": ("ecommerce-website", "conversion-and-content"),
            "design": ("conversion-and-content", "site-search-and-findability"),
            "implementation": ("state-feedback-and-error-recovery",),
        },
        "ai-software": {
            "research": ("saas-website", "product-discovery"),
            "design": ("complex-workflow-and-progress-ux",),
        },
        "mobility-ev": {
            "research": ("corporate-website", "trust-credibility-and-transparency"),
            "design": ("service-experience-to-digital-journey",),
        },
        "travel-tourism": {
            "research": ("hospitality-website",),
            "design": ("service-experience-to-digital-journey", "asset-media-and-art-direction"),
        },
    }

    ARCHETYPE_SKILLS: dict[str, dict[str, tuple[str, ...]]] = {
        "payments-infrastructure": {
            "research": ("financial-product-intelligence",),
            "design": ("trust-credibility-and-transparency",),
            "implementation": ("state-feedback-and-error-recovery",),
        },
        "compliance-operations": {
            "research": ("trust-credibility-and-transparency",),
            "implementation": ("security-and-privacy",),
        },
        "financial-operations": {
            "design": ("data-tables-and-enterprise-ux", "data-visualization-and-dashboard-ux"),
            "implementation": ("data-tables-and-enterprise-ux",),
        },
        "consumer-banking": {
            "design": ("interaction-patterns-and-form-ux", "trust-credibility-and-transparency"),
            "implementation": ("state-feedback-and-error-recovery",),
        },
        "investment-wealth": {
            "design": ("data-visualization-and-dashboard-ux", "trust-credibility-and-transparency"),
        },
        "learning-experience": {
            "design": ("journey-driven-content-and-layout", "complex-workflow-and-progress-ux"),
            "implementation": ("state-feedback-and-error-recovery",),
        },
        "learning-operations": {
            "design": ("data-tables-and-enterprise-ux", "data-visualization-and-dashboard-ux"),
            "implementation": ("complex-forms-and-wizards", "state-feedback-and-error-recovery"),
        },
        "collection-discovery": {
            "design": ("asset-media-and-art-direction", "site-search-and-findability", "experience-principles-and-signature-moments"),
            "implementation": ("site-search-and-findability",),
        },
        "exhibition-experience": {
            "design": ("visual-design-direction", "experience-principles-and-signature-moments"),
        },
        "b2b-service-operations": {
            "design": ("service-experience-to-digital-journey", "complex-workflow-and-progress-ux"),
            "implementation": ("state-feedback-and-error-recovery",),
        },
        "enterprise-operations": {
            "design": ("complex-workflow-and-progress-ux", "data-tables-and-enterprise-ux"),
            "implementation": ("complex-forms-and-wizards", "state-feedback-and-error-recovery"),
        },
        "catalog-commerce": {
            "design": ("site-search-and-findability", "conversion-and-content"),
            "implementation": ("site-search-and-findability",),
        },
        "checkout-commerce": {
            "design": ("interaction-patterns-and-form-ux", "trust-credibility-and-transparency"),
            "implementation": ("complex-forms-and-wizards", "state-feedback-and-error-recovery"),
        },
        "ai-workspace": {
            "design": ("complex-workflow-and-progress-ux",),
            "implementation": ("state-feedback-and-error-recovery",),
        },
        "charging-network": {
            "design": ("data-visualization-and-dashboard-ux", "service-experience-to-digital-journey"),
        },
        "destination-discovery": {
            "design": ("asset-media-and-art-direction", "journey-driven-content-and-layout"),
        },
    }

    SURFACE_SKILLS: dict[str, dict[str, tuple[str, ...]]] = {
        "FOCUSED": {
            "research": ("ui-improvement",),
            "implementation": ("ui-improvement",),
        },
        "PAGE": {
            "design": ("journey-driven-content-and-layout", "responsive-and-device-strategy"),
            "implementation": ("component-driven-development",),
        },
        "REDESIGN": {
            "research": ("website-audit-and-redesign",),
            "design": ("visual-taste-calibration", "design-system-and-components"),
            "implementation": ("frontend-architecture-and-refactoring",),
            "qa": ("visual-regression-and-design-drift",),
        },
        "PRODUCT": {
            "research": ("product-discovery", "information-architecture"),
            "design": ("design-system-and-components", "experience-principles-and-signature-moments"),
            "implementation": ("frontend-architecture-and-refactoring",),
            "qa": ("web-quality-and-performance",),
        },
    }

    FEATURE_SKILLS: dict[str, dict[str, tuple[str, ...]]] = {
        "dashboard": {
            "design": ("data-visualization-and-dashboard-ux", "data-tables-and-enterprise-ux"),
            "implementation": ("data-tables-and-enterprise-ux", "data-visualization-and-dashboard-ux"),
        },
        "forms": {
            "design": ("interaction-patterns-and-form-ux",),
            "implementation": ("complex-forms-and-wizards", "state-feedback-and-error-recovery"),
        },
        "search": {
            "research": ("site-search-and-findability",),
            "implementation": ("site-search-and-findability",),
        },
        "auth": {
            "implementation": ("authentication-account-and-recovery-ux", "security-and-privacy"),
        },
        "motion": {
            "design": ("motion-and-microinteractions",),
            "implementation": ("motion-and-microinteractions",),
        },
    }

    def __init__(self, skills_root: Path) -> None:
        self.skills_root = Path(skills_root)
        self.config_path = self.skills_root / "runtime" / "specialist-composition.json"
        if not self.config_path.is_file():
            self.document: dict[str, Any] = {"schema_version": 1, "flows": [], "rules": []}
            return

        document = json.loads(self.config_path.read_text(encoding="utf-8"))
        if document.get("schema_version") != 1:
            raise ValueError("specialist composition schema_version must be 1")
        flows = document.get("flows", [])
        rules = document.get("rules", [])
        if not isinstance(flows, list) or any(not isinstance(item, str) for item in flows):
            raise ValueError("specialist composition flows must be an array of flow ids")
        if not isinstance(rules, list):
            raise ValueError("specialist composition rules must be an array")

        referenced: list[str] = []
        for index, rule in enumerate(rules):
            if not isinstance(rule, dict):
                raise ValueError(f"specialist composition rule {index} must be an object")
            rule_id = str(rule.get("id", "")).strip()
            if not rule_id:
                raise ValueError(f"specialist composition rule {index} must have an id")
            if not isinstance(rule.get("when", {}), dict):
                raise ValueError(f"specialist composition rule {rule_id} when must be an object")
            rule_flows = rule.get("flows", [])
            if not isinstance(rule_flows, list) or any(not isinstance(item, str) for item in rule_flows):
                raise ValueError(f"specialist composition rule {rule_id} flows must be an array")
            stage_map = rule.get("skills_by_stage", {})
            if not isinstance(stage_map, dict):
                raise ValueError(f"specialist composition rule {rule_id} skills_by_stage must be an object")
            unknown_stages = sorted(set(stage_map).difference({"research", "design", "implementation", "qa"}))
            if unknown_stages:
                raise ValueError(
                    f"specialist composition rule {rule_id} has unknown stages: {', '.join(unknown_stages)}"
                )
            for stage_id, skills in stage_map.items():
                if not isinstance(skills, list) or any(not isinstance(item, str) for item in skills):
                    raise ValueError(
                        f"specialist composition rule {rule_id} stage {stage_id} must be an array of skill ids"
                    )
                referenced.extend(skills)

        missing = [
            skill
            for skill in _unique(referenced)
            if not (self.skills_root / skill / "SKILL.md").is_file()
        ]
        if missing:
            raise ValueError("specialist composition references missing skills: " + ", ".join(missing))
        self.document = document

    def skills_for(
        self, stage_id: str, context: dict[str, Any], flow_id: str | None = None,
    ) -> list[str]:
        selected: list[str] = []
        domain = str(context.get("domain", "generic"))
        archetype = str(context.get("product_archetype", "generic"))
        surface = str(context.get("change_surface", "PRODUCT")).upper()
        features = [str(item) for item in context.get("features", []) or []]

        selected.extend(self.DOMAIN_SKILLS.get(domain, {}).get(stage_id, ()))
        selected.extend(self.ARCHETYPE_SKILLS.get(archetype, {}).get(stage_id, ()))
        selected.extend(self.SURFACE_SKILLS.get(surface, {}).get(stage_id, ()))
        for feature in features:
            selected.extend(self.FEATURE_SKILLS.get(feature, {}).get(stage_id, ()))
        if flow_id in _as_set(self.document.get("flows")):
            for rule in self.document.get("rules", []):
                rule_flows = _as_set(rule.get("flows"))
                if rule_flows and flow_id not in rule_flows:
                    continue
                if _condition_matches(rule.get("when", {}), context):
                    selected.extend(rule.get("skills_by_stage", {}).get(stage_id, []))
        return _unique(selected)

    def compose_flow(
        self,
        flow: Any,
        context: dict[str, Any],
        exclude_skills: Iterable[str] | None = None,
    ) -> Any:
        excluded = set(_unique(exclude_skills or []))
        stages: list[Any] = []
        for stage in flow.stages:
            overlay = [
                skill
                for skill in self.skills_for(stage.id, context, flow.id)
                if skill not in excluded
            ]
            missing = [skill for skill in overlay if not (self.skills_root / skill / "SKILL.md").is_file()]
            if missing:
                raise FileNotFoundError(
                    f"specialist composition references missing skills for {stage.id}: " + ", ".join(missing)
                )

            additions = [skill for skill in overlay if skill not in set(stage.skills)]
            if not additions:
                stages.append(stage)
                continue

            jit = _unique(list(stage.jit_skills or []) + additions)
            sources = dict(stage.jit_skill_sources or {})
            for skill in additions:
                sources[skill] = "conditional"
            stages.append(
                replace(
                    stage,
                    skills=_unique(list(stage.skills) + additions),
                    jit_skills=jit,
                    jit_skill_sources=sources,
                )
            )
        return replace(flow, stages=stages)
