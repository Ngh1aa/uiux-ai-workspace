from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


ALLOWED_OUTCOMES = {"passed", "failed", "cantTell", "untested"}
MAX_EVALUATOR_LENGTH = 128
MAX_REQUIREMENT_LENGTH = 128
MAX_TARGET_LENGTH = 160
MAX_TARGETS = 12


def _bounded_text(value: Any, limit: int) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())[:limit]


def _targets(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        text = _bounded_text(item, MAX_TARGET_LENGTH)
        if text and text not in normalized:
            normalized.append(text)
        if len(normalized) >= MAX_TARGETS:
            break
    return normalized


def normalize_post_render_result(
    *,
    evaluator: Any,
    requirement_id: Any,
    result: Mapping[str, Any] | Any,
    observed: bool,
) -> dict[str, Any] | None:
    """Return a bounded advisory pattern from runtime-observed post-render evidence.

    This boundary intentionally ignores every non-allowlisted field. In particular,
    rationale/prose, screenshots, evidence-file paths, DOM/HTML, prompts, source code,
    provider/model observations and raw artifacts can never enter evaluation memory.
    """
    if not observed or not isinstance(result, Mapping):
        return None

    normalized_evaluator = _bounded_text(evaluator, MAX_EVALUATOR_LENGTH)
    normalized_requirement = _bounded_text(requirement_id, MAX_REQUIREMENT_LENGTH)
    outcome = _bounded_text(result.get("outcome"), 32)
    applicable = result.get("applicable")

    if not normalized_evaluator or not normalized_requirement:
        return None
    if outcome not in ALLOWED_OUTCOMES:
        return None
    if applicable not in (True, False, None):
        return None

    body = {
        "source": "post_render",
        "evaluator": normalized_evaluator,
        "requirement_id": normalized_requirement,
        "outcome": outcome,
        "applicable": applicable,
        "test_targets": _targets(result.get("test_targets")),
        "advisory_only": True,
        "authority_effect": "none",
        "gate_effect": "none",
    }
    canonical = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    body["fingerprint"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return body


def normalize_post_render_report(report: Mapping[str, Any] | Any) -> list[dict[str, Any]]:
    """Normalize one completed post-render report into deterministic advisory patterns."""
    if not isinstance(report, Mapping):
        return []
    evaluator = report.get("evaluator")
    requirements = report.get("requirements")
    if not isinstance(requirements, Mapping):
        return []

    patterns: list[dict[str, Any]] = []
    for requirement_id in sorted(requirements, key=lambda value: str(value)):
        result = requirements[requirement_id]
        # A result is runtime-observed only after an evaluator has produced a concrete
        # result entry. Outcomes that explicitly say `untested` remain diagnostic but
        # are not learned as observed quality history.
        observed = isinstance(result, Mapping) and result.get("outcome") != "untested"
        pattern = normalize_post_render_result(
            evaluator=evaluator,
            requirement_id=requirement_id,
            result=result,
            observed=observed,
        )
        if pattern is not None:
            patterns.append(pattern)
    return patterns
