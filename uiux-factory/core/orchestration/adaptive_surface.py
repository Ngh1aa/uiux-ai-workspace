from __future__ import annotations

import re
from typing import Iterable


CHANGE_SURFACES = ("MICRO", "FOCUSED", "PAGE", "REDESIGN", "PRODUCT")

ATOMIC_HINTS = (
    "button", "cta", "icon", "logo", "input", "field", "label", "badge", "chip",
    "tooltip", "divider", "thumbnail", "image", "spacing", "padding", "margin",
    "border", "radius", "shadow", "cursor", "card",
)
FOCUSED_HINTS = (
    "hero", "mobile-nav", "navigation", "navbar", "header", "footer", "pricing",
    "cards", "form", "modal", "sidebar", "banner", "typography", "content",
    "animation", "motion", "section",
)
STRONG_PAGE_HINTS = (
    "landing-page", "landing page", "homepage", "home page", "trang chủ", "checkout",
    "page", "route", "screen", "màn hình", "trang đích",
)
PAGE_HINTS = STRONG_PAGE_HINTS + ("dashboard", "bảng điều khiển")
FULL_REDESIGN_TERMS = (
    "whole website", "entire website", "full website", "all pages", "site-wide", "site wide",
    "whole site", "entire site", "toàn bộ website", "toàn bộ trang web", "cả website",
    "mọi trang", "tất cả các trang", "design system toàn bộ", "full redesign",
)
PRODUCT_TERMS = (
    "whole product", "entire product", "end-to-end product", "end to end product",
    "full product", "product-wide", "product wide", "new product", "build a product",
    "build the product", "xây sản phẩm", "toàn bộ sản phẩm", "cả sản phẩm",
    "web app", "mobile app", "application", "platform", "nền tảng",
)


def _normalise(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower())


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _matched_count(text: str, terms: Iterable[str]) -> int:
    return sum(1 for term in terms if term in text)


def default_change_surface_for_intent(intent: str) -> str:
    if intent in {"improve", "fix", "polish"}:
        return "FOCUSED"
    if intent in {"redesign", "rebuild"}:
        return "REDESIGN"
    return "PRODUCT"


def classify_change_surface(text: str, intent: str, scope: Iterable[str]) -> str:
    """Classify task size while preferring the narrowest credible change owner."""
    normalized = _normalise(text)
    normalized_scope = [_normalise(item) for item in scope if str(item).strip()]
    scope_text = " ".join(normalized_scope)
    has_product_cue = _contains_any(normalized, PRODUCT_TERMS)

    if scope_text:
        if intent == "build" and _contains_any(scope_text, STRONG_PAGE_HINTS):
            return "PAGE"
        if intent == "build" and has_product_cue:
            return "PRODUCT"
        atomic_count = _matched_count(scope_text, ATOMIC_HINTS)
        focused_count = _matched_count(scope_text, FOCUSED_HINTS)
        if atomic_count and focused_count <= 1 and intent in {"improve", "fix", "polish"}:
            return "MICRO"
        if atomic_count and not focused_count and len(normalized_scope) <= 2:
            return "MICRO"
        if focused_count:
            return "PAGE" if focused_count >= 3 else "FOCUSED"
        if _contains_any(scope_text, PAGE_HINTS):
            return "PAGE"
        if len(normalized_scope) == 1 and intent in {"improve", "fix", "polish", "redesign", "rebuild"}:
            return "FOCUSED"
        if len(normalized_scope) >= 2:
            return "PAGE"

    if intent in {"redesign", "rebuild"} and _contains_any(normalized, FULL_REDESIGN_TERMS):
        return "REDESIGN"
    if has_product_cue:
        return "PRODUCT"
    if intent == "build" and _contains_any(normalized, STRONG_PAGE_HINTS):
        return "PAGE"
    if _contains_any(normalized, ATOMIC_HINTS):
        return "MICRO"
    if _contains_any(normalized, FOCUSED_HINTS):
        return "FOCUSED"
    if _contains_any(normalized, PAGE_HINTS):
        return "PAGE"
    return default_change_surface_for_intent(intent)
