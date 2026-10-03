from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Callable, Iterable

from core.runtime.flow_os.adaptive_surface import classify_change_surface


LIFECYCLE_ORDER = ("audit", "design", "implementation", "qa")

AUDIT_TERMS = (
    "audit", "review", "inspect", "analyze", "analyse", "assess", "research",
    "rà soát", "kiểm tra", "phân tích", "đánh giá",
)
IMPLEMENTATION_TERMS = (
    "implement", "implementation", "code", "apply changes", "build in code",
    "write code", "sửa code", "chỉnh code", "viết code", "triển khai", "hiện thực",
)
QA_TERMS = (
    "qa", "quality assurance", "test", "testing", "verify", "verification",
    "validate", "validation", "regression", "browser qa", "visual qa",
    "kiểm thử", "xác minh", "nghiệm thu",
)
DESIGN_TERMS = (
    "redesign", "re-design", "design", "rebuild", "fix", "repair", "improve",
    "enhance", "refine", "polish", "thiết kế lại", "làm lại", "sửa", "cải thiện",
    "nâng cấp", "tinh chỉnh",
)
ACTION_START_TERMS = tuple(dict.fromkeys(AUDIT_TERMS + DESIGN_TERMS + IMPLEMENTATION_TERMS + QA_TERMS))


def _normalise(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower())


def _contains_token(text: str, terms: Iterable[str]) -> bool:
    for term in terms:
        cleaned = _normalise(term)
        if cleaned and re.search(rf"(?<!\w){re.escape(cleaned)}(?!\w)", text, flags=re.IGNORECASE):
            return True
    return False


def _phase(text: str) -> str:
    # Implementation/QA must win over generic design verbs such as "fix" when code/test
    # language is explicit in the same clause.
    if _contains_token(text, QA_TERMS):
        return "qa"
    if _contains_token(text, IMPLEMENTATION_TERMS):
        return "implementation"
    if _contains_token(text, AUDIT_TERMS):
        return "audit"
    return "design"


def _split_action_units(goal: str) -> list[str]:
    text = str(goal).strip()
    if not text:
        return []

    text = re.sub(r"\s*(?:→|->|=>)\s*", " ; ", text)
    coarse = [part.strip() for part in re.split(r"[;\n]+|(?<=[.!?])\s+", text) if part.strip()]

    cue_pattern = "|".join(sorted((re.escape(term) for term in ACTION_START_TERMS), key=len, reverse=True))
    connector = re.compile(
        rf"\s+(?:and\s+then|then|and|plus|while|và|rồi|sau\s+đó)\s+(?=(?:{cue_pattern})(?!\w))",
        flags=re.IGNORECASE,
    )

    units: list[str] = []
    for part in coarse:
        split = [item.strip(" ,") for item in connector.split(part) if item.strip(" ,")]
        units.extend(split)
    return units


@dataclass(frozen=True)
class WorkSegment:
    id: str
    order: int
    phase: str
    intent: str
    scope: list[str]
    change_surface: str
    text: str
    inherits_from: str | None = None
    preserve: list[str] | None = None
    forbidden: list[str] | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def decompose_work_segments(
    goal: str,
    *,
    infer_intent: Callable[[str], str],
    infer_scope: Callable[[str, list[str], list[str]], list[str]],
    preserve: list[str] | None = None,
    forbidden: list[str] | None = None,
) -> list[WorkSegment]:
    """Split explicit multi-intent work into ordered, independently routable segments.

    The decomposition is deliberately conservative: a task becomes a sequence only when
    at least two actionable clauses survive and they differ by lifecycle phase, intent,
    scope, or change surface. Bare implementation/QA clauses inherit the nearest change
    target rather than inventing a new product scope.
    """

    preserve_values = list(preserve or [])
    forbidden_values = list(forbidden or [])
    units = _split_action_units(goal)
    actionable = [unit for unit in units if _contains_token(_normalise(unit), ACTION_START_TERMS)]
    if len(actionable) < 2:
        return []

    raw: list[dict[str, object]] = []
    last_intent = "improve"
    last_scope: list[str] = []
    last_surface = "FOCUSED"
    last_change_id: str | None = None

    for index, unit in enumerate(actionable, start=1):
        normalized = _normalise(unit)
        phase = _phase(normalized)
        local_scope = list(infer_scope(normalized, preserve_values, forbidden_values))
        explicit_change = phase == "design"

        if explicit_change:
            local_intent = infer_intent(normalized)
            last_intent = local_intent
        elif phase == "implementation":
            local_intent = last_intent if last_change_id else "build"
        else:
            local_intent = last_intent if last_change_id else "improve"

        inherits_from: str | None = None
        if not local_scope and last_scope:
            local_scope = list(last_scope)
            inherits_from = last_change_id

        if local_scope:
            local_surface = classify_change_surface(normalized, local_intent, local_scope)
        elif last_change_id and phase in {"implementation", "qa"}:
            local_surface = last_surface
            inherits_from = last_change_id
        else:
            local_surface = classify_change_surface(normalized, local_intent, local_scope)

        segment_id = f"work-{index}"
        raw.append(
            {
                "id": segment_id,
                "order": index,
                "phase": phase,
                "intent": local_intent,
                "scope": local_scope,
                "change_surface": local_surface,
                "text": unit.strip(),
                "inherits_from": inherits_from,
            }
        )

        if phase == "design":
            last_change_id = segment_id
            last_scope = list(local_scope)
            last_surface = local_surface

    # Forward-fill an initial audit target from the first later design segment when the
    # audit clause intentionally omits its object ("audit first, then redesign checkout").
    next_change: dict[int, dict[str, object]] = {}
    seen: dict[str, object] | None = None
    for idx in range(len(raw) - 1, -1, -1):
        if raw[idx]["phase"] == "design":
            seen = raw[idx]
        if seen is not None:
            next_change[idx] = seen

    for idx, item in enumerate(raw):
        if item["phase"] == "audit" and not item["scope"] and idx in next_change:
            owner = next_change[idx]
            item["scope"] = list(owner["scope"])
            item["change_surface"] = str(owner["change_surface"])
            item["intent"] = str(owner["intent"])
            item["inherits_from"] = str(owner["id"])

    signatures = {
        (
            str(item["phase"]),
            str(item["intent"]),
            tuple(str(value) for value in item["scope"]),
            str(item["change_surface"]),
        )
        for item in raw
    }
    if len(signatures) < 2:
        return []

    return [
        WorkSegment(
            id=str(item["id"]),
            order=int(item["order"]),
            phase=str(item["phase"]),
            intent=str(item["intent"]),
            scope=[str(value) for value in item["scope"]],
            change_surface=str(item["change_surface"]),
            text=str(item["text"]),
            inherits_from=str(item["inherits_from"]) if item["inherits_from"] else None,
            preserve=list(preserve_values),
            forbidden=list(forbidden_values),
        )
        for item in raw
    ]
