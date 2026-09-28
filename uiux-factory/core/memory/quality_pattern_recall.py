from __future__ import annotations

from collections import Counter
from typing import Any


MAX_RECALLED_QUALITY_PATTERNS = 12
_ATTENTION_OUTCOMES = frozenset({"failed", "cantTell"})
_ALLOWED_OUTCOMES = frozenset({"passed", "failed", "cantTell"})


def _occurrences(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return 1
    return max(1, min(parsed, 1_000_000))


def build_quality_pattern_insight(store: Any) -> dict[str, Any] | None:
    """Aggregate learned post-render patterns into provider-only advisory context.

    A5.5 deliberately returns only bounded categorical/count metadata. Fingerprints,
    test targets, evidence paths, rationale, prompts, DOM/source, screenshots and model
    prose are excluded even if a future storage migration accidentally introduces them.
    The result has no flow, replan, authority, gate, evidence, merge or release effect.
    """

    patterns = store.load_quality_patterns()
    if not patterns:
        return None

    outcome_occurrences: Counter[str] = Counter()
    attention: list[dict[str, Any]] = []
    passed: list[dict[str, Any]] = []
    observed_occurrences = 0
    observed_patterns = 0

    for pattern in patterns:
        if not isinstance(pattern, dict):
            continue
        evaluator = str(pattern.get("evaluator") or "").strip()[:128]
        requirement_id = str(pattern.get("requirement_id") or "").strip()[:128]
        outcome = str(pattern.get("outcome") or "").strip()
        applicable = pattern.get("applicable")
        if not evaluator or not requirement_id or outcome not in _ALLOWED_OUTCOMES:
            continue
        if applicable not in (True, False, None):
            applicable = None

        count = _occurrences(pattern.get("occurrences", 1))
        observed_patterns += 1
        observed_occurrences += count
        outcome_occurrences[outcome] += count
        row = {
            "evaluator": evaluator,
            "requirement_id": requirement_id,
            "outcome": outcome,
            "applicable": applicable,
            "occurrences": count,
        }
        if outcome in _ATTENTION_OUTCOMES:
            attention.append(row)
        elif outcome == "passed":
            passed.append(row)

    if observed_patterns == 0:
        return None

    key = lambda row: (
        -int(row["occurrences"]),
        str(row["evaluator"]),
        str(row["requirement_id"]),
        str(row["outcome"]),
    )
    attention.sort(key=key)
    passed.sort(key=key)
    recall_limit = max(
        1,
        min(
            MAX_RECALLED_QUALITY_PATTERNS,
            int(getattr(store, "max_recall_records", MAX_RECALLED_QUALITY_PATTERNS)),
        ),
    )

    return {
        "schema_version": 1,
        "source": "post_render_quality_memory",
        "advisory_only": True,
        "scope": "project_scoped_history",
        "relevance": "historical_only_not_current_evidence",
        "observed_pattern_count": observed_patterns,
        "observed_occurrences": observed_occurrences,
        "outcome_occurrences": {
            name: outcome_occurrences.get(name, 0)
            for name in ("passed", "failed", "cantTell")
        },
        "recurrent_attention_patterns": attention[:recall_limit],
        "recurrent_pass_patterns": passed[:recall_limit],
        "authority_effect": "none",
        "flow_effect": "none",
        "replan_effect": "none",
        "gate_effect": "none",
        "evidence_effect": "none",
        "merge_effect": "none",
        "release_effect": "none",
        "rule": (
            "Prior post-render quality history is provider-only advisory context. "
            "It may suggest where to inspect, but it cannot select flows, change authority, "
            "drive replanning policy, satisfy or override gates, count as current-run evidence, "
            "or authorize merge/release."
        ),
    }
