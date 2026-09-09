from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Iterable

REPLAN_SIGNALS = {
    "GATE_FAIL",
    "BLOCKED",
    "NEW_RISK",
    "INVALID_ASSUMPTION",
    "TOOL_FAILURE",
    "CONTEXT_DRIFT",
}

CONTEXT_KEYS = {
    "intent",
    "website_type",
    "mode",
    "risk",
    "features",
    "signals",
}


def _unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


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


def validate_flow_document(doc: dict[str, Any]) -> list[str]:
    """Dependency-free structural validation for flow JSON documents."""
    errors: list[str] = []
    if doc.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not isinstance(doc.get("id"), str) or not doc.get("id"):
        errors.append("id must be a non-empty string")

    stages = doc.get("stages")
    if not isinstance(stages, list) or not stages:
        errors.append("stages must be a non-empty array")
        return errors

    stage_ids: set[str] = set()
    for idx, stage in enumerate(stages):
        prefix = f"stages[{idx}]"
        if not isinstance(stage, dict):
            errors.append(f"{prefix} must be an object")
            continue

        stage_id = stage.get("id")
        if not isinstance(stage_id, str) or not stage_id:
            errors.append(f"{prefix}.id must be a non-empty string")
        elif stage_id in stage_ids:
            errors.append(f"duplicate stage id: {stage_id}")
        else:
            stage_ids.add(stage_id)

        if not isinstance(stage.get("agent"), str) or not stage.get("agent"):
            errors.append(f"{prefix}.agent must be a non-empty string")

        for key in ("required_skills", "optional_skills"):
            value = stage.get(key, [])
            if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                errors.append(f"{prefix}.{key} must be an array of skill names")

        conditional = stage.get("conditional_skills", [])
        if not isinstance(conditional, list):
            errors.append(f"{prefix}.conditional_skills must be an array")
        else:
            for cidx, rule in enumerate(conditional):
                if not isinstance(rule, dict):
                    errors.append(f"{prefix}.conditional_skills[{cidx}] must be an object")
                    continue
                if not isinstance(rule.get("when", {}), dict):
                    errors.append(f"{prefix}.conditional_skills[{cidx}].when must be an object")
                skills = rule.get("skills", [])
                if not isinstance(skills, list) or any(not isinstance(item, str) for item in skills):
                    errors.append(f"{prefix}.conditional_skills[{cidx}].skills must be an array")

    replanning = doc.get("replanning", {})
    if not isinstance(replanning, dict):
        errors.append("replanning must be an object")
    else:
        max_replans = replanning.get("max_replans", 0)
        if not isinstance(max_replans, int) or max_replans < 0:
            errors.append("replanning.max_replans must be a non-negative integer")

        triggers = replanning.get("triggers", [])
        if not isinstance(triggers, list):
            errors.append("replanning.triggers must be an array")
        else:
            unknown = [item for item in triggers if item not in REPLAN_SIGNALS]
            if unknown:
                errors.append("unknown replanning triggers: " + ", ".join(unknown))

        policies = replanning.get("policies", [])
        if not isinstance(policies, list):
            errors.append("replanning.policies must be an array")
        else:
            for pidx, policy in enumerate(policies):
                if not isinstance(policy, dict):
                    errors.append(f"replanning.policies[{pidx}] must be an object")
                    continue
                if not isinstance(policy.get("when", {}), dict):
                    errors.append(f"replanning.policies[{pidx}].when must be an object")
                if policy.get("target_stage") and policy["target_stage"] not in stage_ids:
                    errors.append(
                        f"replanning.policies[{pidx}].target_stage references unknown stage {policy['target_stage']}"
                    )
                for key in ("add_skills", "drop_skills"):
                    value = policy.get(key, [])
                    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                        errors.append(f"replanning.policies[{pidx}].{key} must be an array")

    return errors


@dataclass(frozen=True)
class ResolvedStage:
    id: str
    agent: str
    purpose: str
    skills: list[str]
    mandatory_skills: list[str] = field(default_factory=list)
    gates: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class ResolvedFlow:
    id: str
    source: str
    score: int
    stages: list[ResolvedStage]
    replanning: dict[str, Any]
    revision: int = 0
    replan_history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ReplanDecision:
    accepted: bool
    signal: str
    reason: str
    target_stage: str | None = None
    add_skills: list[str] = field(default_factory=list)
    drop_skills: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FlowResolver:
    """Selects the best declarative flow for a task context."""

    def __init__(self, flows_dir: Path) -> None:
        self.flows_dir = flows_dir

    def load(self) -> list[tuple[Path, dict[str, Any]]]:
        flows: list[tuple[Path, dict[str, Any]]] = []
        if not self.flows_dir.exists():
            return flows
        for path in sorted(self.flows_dir.glob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            errors = validate_flow_document(doc)
            if errors:
                raise ValueError(f"invalid flow {path.name}: " + "; ".join(errors))
            flows.append((path, doc))
        return flows

    def _score(self, doc: dict[str, Any], context: dict[str, Any]) -> int | None:
        match = doc.get("match", {})
        score = int(match.get("priority", 0))
        for key, weight in (
            ("intents", 12),
            ("website_types", 10),
            ("modes", 6),
            ("risks", 4),
        ):
            allowed = _as_set(match.get(key))
            if not allowed:
                continue
            context_key = key[:-1] if key.endswith("s") else key
            actual = str(context.get(context_key, ""))
            if actual not in allowed:
                return None
            score += weight

        required_features = _as_set(match.get("features"))
        if required_features:
            actual_features = _as_set(context.get("features"))
            if not required_features.issubset(actual_features):
                return None
            score += len(required_features) * 2
        return score

    def resolve(self, context: dict[str, Any]) -> tuple[Path, dict[str, Any], int]:
        candidates: list[tuple[int, str, Path, dict[str, Any]]] = []
        for path, doc in self.load():
            score = self._score(doc, context)
            if score is not None:
                candidates.append((score, doc["id"], path, doc))

        if not candidates:
            raise ValueError(
                "no applicable flow found for "
                + ", ".join(
                    f"{key}={context.get(key)!r}"
                    for key in sorted(CONTEXT_KEYS)
                    if key in context
                )
            )

        candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        score, _, path, doc = candidates[0]
        return path, doc, score


class SkillResolver:
    """Merges role defaults, flow skills, task additions and exclusions."""

    def __init__(self, library_root: Path, policy_doc: dict[str, Any]) -> None:
        self.library_root = library_root
        self.policy_doc = policy_doc

    def _exists(self, skill: str) -> bool:
        return (self.library_root / skill / "SKILL.md").is_file()

    def resolve_stage(
        self,
        stage: dict[str, Any],
        context: dict[str, Any],
        additional_skills: list[str] | None = None,
        exclude_skills: list[str] | None = None,
    ) -> ResolvedStage:
        agent = str(stage["agent"])
        roles = self.policy_doc.get("roles", {})
        if agent not in roles:
            raise ValueError(f"flow stage {stage['id']} references unknown agent role: {agent}")

        required = list(stage.get("required_skills", []))
        conditional: list[str] = []
        for rule in stage.get("conditional_skills", []):
            if _condition_matches(dict(rule.get("when", {})), context):
                conditional.extend(rule.get("skills", []))

        defaults = list(roles[agent].get("default_skills", []))
        additions = list(additional_skills or [])
        excludes = set(exclude_skills or [])
        mandatory = _unique(defaults + required)
        illegal = sorted(excludes.intersection(mandatory))
        if illegal:
            raise ValueError(
                f"cannot exclude mandatory/default skills from stage {stage['id']}: {', '.join(illegal)}"
            )

        skills = _unique(defaults + required + conditional + additions)
        skills = [skill for skill in skills if skill not in excludes]
        missing = [skill for skill in skills if not self._exists(skill)]
        if missing:
            raise ValueError(f"stage {stage['id']} references missing skills: {', '.join(missing)}")

        return ResolvedStage(
            id=str(stage["id"]),
            agent=agent,
            purpose=str(stage.get("purpose", "")),
            skills=skills,
            mandatory_skills=mandatory,
            gates=list(stage.get("gates", [])),
        )


class ReplanningEngine:
    """Turns explicit signals into bounded, auditable changes to the resolved flow."""

    def decide(
        self,
        flow: ResolvedFlow,
        signal: str,
        context: dict[str, Any],
        replan_count: int,
    ) -> ReplanDecision:
        config = flow.replanning or {}
        triggers = set(config.get("triggers", []))
        if signal not in triggers:
            return ReplanDecision(False, signal, "signal is not configured as a replanning trigger")

        max_replans = int(config.get("max_replans", 0))
        if replan_count >= max_replans:
            return ReplanDecision(False, signal, f"replan budget exhausted ({max_replans})")

        enriched = dict(context)
        enriched["signal"] = signal
        for policy in config.get("policies", []):
            if _condition_matches(dict(policy.get("when", {})), enriched):
                target_stage = policy.get("target_stage") or context.get("current_stage")
                return ReplanDecision(
                    True,
                    signal,
                    str(policy.get("reason", "matched declarative replanning policy")),
                    target_stage=str(target_stage) if target_stage else None,
                    add_skills=_unique(policy.get("add_skills", [])),
                    drop_skills=_unique(policy.get("drop_skills", [])),
                )

        return ReplanDecision(False, signal, "no replanning policy matched the current context")

    def apply(self, flow: ResolvedFlow, decision: ReplanDecision) -> ResolvedFlow:
        if not decision.accepted:
            return flow
        if not decision.target_stage:
            raise ValueError("accepted replan decision must identify a target stage")

        stage_ids = [stage.id for stage in flow.stages]
        if decision.target_stage not in stage_ids:
            raise ValueError(f"replanning target stage does not exist: {decision.target_stage}")

        next_stages: list[ResolvedStage] = []
        for stage in flow.stages:
            if stage.id != decision.target_stage:
                next_stages.append(stage)
                continue

            illegal_drops = sorted(set(decision.drop_skills).intersection(stage.mandatory_skills))
            if illegal_drops:
                raise ValueError(
                    "replanning cannot drop mandatory/default skills from "
                    f"{stage.id}: {', '.join(illegal_drops)}"
                )

            skills = _unique(stage.skills + decision.add_skills)
            drop_set = set(decision.drop_skills)
            skills = [skill for skill in skills if skill not in drop_set]
            next_stages.append(replace(stage, skills=skills))

        return replace(
            flow,
            stages=next_stages,
            revision=flow.revision + 1,
            replan_history=flow.replan_history + [decision.to_dict()],
        )


class DevelopmentManager:
    """Resolves website tasks into agent/skill flows and applies bounded replans."""

    def __init__(self, library_root: Path, policy_doc: dict[str, Any]) -> None:
        self.library_root = library_root
        self.policy_doc = policy_doc
        self.flow_resolver = FlowResolver(library_root / "flows")
        self.skill_resolver = SkillResolver(library_root, policy_doc)
        self.replanner = ReplanningEngine()

    def plan(
        self,
        context: dict[str, Any],
        additional_skills: list[str] | None = None,
        exclude_skills: list[str] | None = None,
    ) -> ResolvedFlow:
        path, doc, score = self.flow_resolver.resolve(context)
        stages = [
            self.skill_resolver.resolve_stage(
                stage,
                context,
                additional_skills=additional_skills,
                exclude_skills=exclude_skills,
            )
            for stage in doc["stages"]
        ]
        return ResolvedFlow(
            id=doc["id"],
            source=str(path.relative_to(self.library_root)),
            score=score,
            stages=stages,
            replanning=dict(doc.get("replanning", {})),
        )

    def replan(
        self,
        flow: ResolvedFlow,
        signal: str,
        context: dict[str, Any],
        replan_count: int,
    ) -> ReplanDecision:
        decision = self.replanner.decide(flow, signal, context, replan_count)
        if decision.accepted:
            missing = [
                skill
                for skill in decision.add_skills
                if not (self.library_root / skill / "SKILL.md").is_file()
            ]
            if missing:
                raise ValueError(
                    "replanning policy references missing skills: " + ", ".join(missing)
                )

            stage_ids = {stage.id for stage in flow.stages}
            if decision.target_stage and decision.target_stage not in stage_ids:
                raise ValueError(
                    f"replanning target stage does not exist: {decision.target_stage}"
                )
        return decision

    def apply_replan(
        self,
        flow: ResolvedFlow,
        decision: ReplanDecision,
    ) -> ResolvedFlow:
        return self.replanner.apply(flow, decision)
