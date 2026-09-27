from __future__ import annotations

from typing import Any, Literal, cast


SpecProfile = Literal[
    "pixel_faithful",
    "preserve_and_extend",
    "redesign",
    "original_design",
]

VALID_SPEC_PROFILES: tuple[SpecProfile, ...] = (
    "pixel_faithful",
    "preserve_and_extend",
    "redesign",
    "original_design",
)


def infer_spec_profile(payload: dict[str, Any]) -> SpecProfile:
    """Conservatively classify specification strategy from explicit intent and evidence.

    Intent phrases outrank incidental keyword overlap. In particular, an explicit greenfield/no-existing-
    implementation statement must not become preserve-and-extend merely because it contains the word
    "preserve" in a negated clause such as "nothing to preserve".
    """

    explicit = str(payload.get("spec_profile", "")).strip().lower()
    if explicit in VALID_SPEC_PROFILES:
        return cast(SpecProfile, explicit)

    goal = " ".join(str(payload.get("goal", "")).lower().split())
    reference = str(payload.get("reference_analysis", "")).strip()

    pixel_terms = (
        "pixel faithful",
        "pixel-faithful",
        "clone chính xác",
        "clone exact",
        "reproduce exactly",
        "rebuild exactly",
        "verbatim",
        "1:1 clone",
    )
    redesign_terms = (
        "redesign",
        "re-design",
        "thiết kế lại",
        "làm lại giao diện",
        "new visual direction",
    )
    original_terms = (
        "greenfield",
        "from scratch",
        "new original",
        "original design",
        "no existing implementation",
        "no existing visual implementation",
        "nothing to preserve",
        "không có implementation hiện tại",
        "không có giao diện hiện tại",
        "thiết kế mới hoàn toàn",
    )
    preserve_terms = (
        "preserve",
        "giữ nguyên",
        "giữ core",
        "keep existing",
        "extend",
        "mở rộng",
        "complete the current",
        "hoàn thiện project hiện tại",
    )

    if any(term in goal for term in pixel_terms):
        return "pixel_faithful"
    if any(term in goal for term in redesign_terms):
        return "redesign"
    if any(term in goal for term in original_terms):
        return "original_design"
    if any(term in goal for term in preserve_terms):
        return "preserve_and_extend"
    if reference:
        # Having a reference is evidence, not authorization to clone it. When a target/reference
        # already exists but the goal does not authorize a redesign/clone, preserve-and-extend is
        # the conservative default.
        return "preserve_and_extend"
    return "original_design"
