from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.brain_os.adapters.flow_selection import select_canonical_flow
from core.brain_os.adapters.jit_context import project_stage_jit_context
from core.runtime.flow_os.flow import FlowPlanner
from core.runtime.flow_os.task_context import GoalInterpreter


ROUTING_BENCHMARK_SCHEMA_VERSION = 1
ALLOWED_SURFACES = {"MICRO", "FOCUSED", "PAGE", "REDESIGN", "PRODUCT"}
REQUIRED_CASE_KEYS = {"id", "goal", "expected_surface", "expected_flow"}
OPTIONAL_CASE_KEYS = {
    "expected_domain",
    "expected_website_type",
    "stage_id",
    "mandatory_contains",
    "jit_contains",
    "tags",
}


class RoutingBenchmarkError(ValueError):
    """Raised when the deterministic routing benchmark contract is invalid."""


def _stable_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _string_list(value: Any, *, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise RoutingBenchmarkError(f"{field} must be an array of strings")
    output: list[str] = []
    for item in value:
        cleaned = item.strip()
        if cleaned and cleaned not in output:
            output.append(cleaned)
    return output


@dataclass(frozen=True)
class RoutingBenchmarkCase:
    id: str
    goal: str
    expected_surface: str
    expected_flow: str
    expected_domain: str | None
    expected_website_type: str | None
    stage_id: str | None
    mandatory_contains: tuple[str, ...]
    jit_contains: tuple[str, ...]
    tags: tuple[str, ...]
    content_hash: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "RoutingBenchmarkCase":
        if not isinstance(raw, dict):
            raise RoutingBenchmarkError("routing benchmark case must be an object")
        missing = sorted(REQUIRED_CASE_KEYS.difference(raw))
        if missing:
            raise RoutingBenchmarkError("routing benchmark case missing keys: " + ", ".join(missing))
        unknown = sorted(set(raw).difference(REQUIRED_CASE_KEYS | OPTIONAL_CASE_KEYS))
        if unknown:
            raise RoutingBenchmarkError("routing benchmark case has unknown keys: " + ", ".join(unknown))

        case_id = str(raw["id"]).strip()
        goal = str(raw["goal"]).strip()
        surface = str(raw["expected_surface"]).strip().upper()
        flow = str(raw["expected_flow"]).strip()
        if not case_id or not goal or not flow:
            raise RoutingBenchmarkError("routing benchmark id/goal/expected_flow must be non-empty")
        if surface not in ALLOWED_SURFACES:
            raise RoutingBenchmarkError(f"{case_id}.expected_surface must be one of {sorted(ALLOWED_SURFACES)}")

        expected_domain = str(raw.get("expected_domain", "")).strip() or None
        expected_website_type = str(raw.get("expected_website_type", "")).strip() or None
        stage_id = str(raw.get("stage_id", "")).strip() or None
        mandatory = _string_list(raw.get("mandatory_contains", []), field=f"{case_id}.mandatory_contains")
        jit = _string_list(raw.get("jit_contains", []), field=f"{case_id}.jit_contains")
        tags = _string_list(raw.get("tags", []), field=f"{case_id}.tags")
        if (mandatory or jit) and not stage_id:
            raise RoutingBenchmarkError(f"{case_id} skill expectations require stage_id")

        normalized = {
            "id": case_id,
            "goal": goal,
            "expected_surface": surface,
            "expected_flow": flow,
            "expected_domain": expected_domain,
            "expected_website_type": expected_website_type,
            "stage_id": stage_id,
            "mandatory_contains": mandatory,
            "jit_contains": jit,
            "tags": tags,
        }
        return cls(
            id=case_id,
            goal=goal,
            expected_surface=surface,
            expected_flow=flow,
            expected_domain=expected_domain,
            expected_website_type=expected_website_type,
            stage_id=stage_id,
            mandatory_contains=tuple(mandatory),
            jit_contains=tuple(jit),
            tags=tuple(tags),
            content_hash=_stable_hash(normalized),
        )


@dataclass(frozen=True)
class RoutingBenchmarkCorpus:
    benchmark_id: str
    version: str
    cases: tuple[RoutingBenchmarkCase, ...]
    content_hash: str

    @classmethod
    def load(cls, path: Path) -> "RoutingBenchmarkCorpus":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RoutingBenchmarkError("routing benchmark must be an object")
        allowed = {"schema_version", "benchmark_id", "version", "description", "cases"}
        unknown = sorted(set(payload).difference(allowed))
        if unknown:
            raise RoutingBenchmarkError("routing benchmark has unknown keys: " + ", ".join(unknown))
        if payload.get("schema_version") != ROUTING_BENCHMARK_SCHEMA_VERSION:
            raise RoutingBenchmarkError(f"schema_version must be {ROUTING_BENCHMARK_SCHEMA_VERSION}")
        benchmark_id = str(payload.get("benchmark_id", "")).strip()
        version = str(payload.get("version", "")).strip()
        raw_cases = payload.get("cases")
        if not benchmark_id or not version or not isinstance(raw_cases, list) or not raw_cases:
            raise RoutingBenchmarkError("benchmark_id/version/cases are required")
        cases = tuple(RoutingBenchmarkCase.from_dict(item) for item in raw_cases)
        ids = [case.id for case in cases]
        if len(ids) != len(set(ids)):
            raise RoutingBenchmarkError("routing benchmark case ids must be unique")
        surfaces = {case.expected_surface for case in cases}
        missing_surfaces = sorted(ALLOWED_SURFACES.difference(surfaces))
        if missing_surfaces:
            raise RoutingBenchmarkError("routing benchmark must cover all change surfaces: " + ", ".join(missing_surfaces))
        if len(cases) < 20:
            raise RoutingBenchmarkError("routing benchmark requires at least 20 representative cases")
        hash_payload = {
            "schema_version": ROUTING_BENCHMARK_SCHEMA_VERSION,
            "benchmark_id": benchmark_id,
            "version": version,
            "cases": [case.content_hash for case in cases],
        }
        return cls(benchmark_id, version, cases, _stable_hash(hash_payload))


def evaluate_routing_case(
    case: RoutingBenchmarkCase,
    *,
    planner: FlowPlanner,
    policy_doc: dict[str, object],
    interpreter: GoalInterpreter | None = None,
) -> dict[str, Any]:
    """Evaluate one case through production routing without mutating routing state."""

    compiler = interpreter or GoalInterpreter()
    profile = compiler.interpret(case.goal)
    context = profile.to_context()
    selection = select_canonical_flow(planner, context=context, goal=case.goal, scope=profile.scope)

    checks: dict[str, bool] = {
        "surface": profile.change_surface == case.expected_surface and selection.change_surface == case.expected_surface,
        "flow": selection.flow_id == case.expected_flow,
    }
    actual: dict[str, Any] = {
        "surface": profile.change_surface,
        "flow": selection.flow_id,
        "domain": profile.domain,
        "website_type": profile.website_type,
        "stage_id": case.stage_id,
        "mandatory_skills": [],
        "jit_skills": [],
    }

    if case.expected_domain is not None:
        checks["domain"] = profile.domain == case.expected_domain
    if case.expected_website_type is not None:
        checks["website_type"] = profile.website_type == case.expected_website_type

    if case.stage_id:
        resolved = planner.plan(context)
        stage = next((item for item in resolved.stages if item.id == case.stage_id), None)
        if stage is None:
            checks["stage"] = False
        else:
            checks["stage"] = True
            jit = project_stage_jit_context(stage, policy_doc)
            actual["mandatory_skills"] = list(jit.mandatory_skills)
            actual["jit_skills"] = list(jit.routed_jit_skills)
            checks["mandatory_skills"] = set(case.mandatory_contains).issubset(jit.mandatory_skills)
            checks["jit_skills"] = set(case.jit_contains).issubset(jit.routed_jit_skills)

    return {
        "case_id": case.id,
        "case_hash": case.content_hash,
        "passed": all(checks.values()),
        "checks": checks,
        "expected": {
            "surface": case.expected_surface,
            "flow": case.expected_flow,
            "domain": case.expected_domain,
            "website_type": case.expected_website_type,
            "stage_id": case.stage_id,
            "mandatory_contains": list(case.mandatory_contains),
            "jit_contains": list(case.jit_contains),
        },
        "actual": actual,
        "tags": list(case.tags),
    }


def build_routing_report(
    corpus: RoutingBenchmarkCorpus,
    *,
    planner: FlowPlanner,
    policy_doc: dict[str, object],
    run_label: str = "candidate",
) -> dict[str, Any]:
    rows = [
        evaluate_routing_case(case, planner=planner, policy_doc=policy_doc)
        for case in corpus.cases
    ]
    failures = [row["case_id"] for row in rows if not row["passed"]]
    surface_counts = {
        surface: sum(1 for case in corpus.cases if case.expected_surface == surface)
        for surface in sorted(ALLOWED_SURFACES)
    }
    return {
        "schema_version": 1,
        "benchmark_id": corpus.benchmark_id,
        "benchmark_version": corpus.version,
        "benchmark_hash": corpus.content_hash,
        "run_label": str(run_label),
        "case_count": len(rows),
        "pass_count": len(rows) - len(failures),
        "fail_count": len(failures),
        "passed": not failures,
        "failure_ids": failures,
        "surface_counts": surface_counts,
        "cases": rows,
        "authority_effect": "none",
        "routing_mutation": False,
    }
