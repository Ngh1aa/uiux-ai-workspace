from __future__ import annotations

import re
from typing import Iterable


def _contains(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _normalise(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower())


DOMAIN_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "commerce-retail",
        (
            "ecommerce",
            "e-commerce",
            "online store",
            "shopping",
            "catalog",
            "catalogue",
            "product detail",
            "product listing",
            "cart",
            "checkout",
            "giỏ hàng",
            "thanh toán",
            "cửa hàng trực tuyến",
        ),
    ),
    (
        "enterprise-software",
        (
            "b2b enterprise",
            "enterprise software",
            "enterprise platform",
            "enterprise dashboard",
            "back office",
            "back-office",
            "operations platform",
            "admin workspace",
            "internal tool",
            "workflow platform",
        ),
    ),
)

# Generic words such as "payment" also occur in ordinary ecommerce checkout copy.
# Keep financial ownership only when the task contains stronger financial-product context.
STRONG_FINANCIAL_DOMAIN_HINTS: tuple[str, ...] = (
    "fintech",
    "financial",
    "banking",
    "settlement",
    "payment rail",
    "payment rails",
    "multi-rail",
    "payment orchestration",
    "treasury",
    "ledger",
    "payout",
    "remittance",
    "cross-border",
    "money movement",
    "mto",
    "psp",
    "kyc",
    "aml",
    "sanctions",
    "reconciliation",
    "subledger",
    "wealth",
    "brokerage",
    "investment",
    "card issuing",
    "acquiring",
)


ARCHETYPE_HINTS: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "education-edtech": (
        (
            "learning-operations",
            (
                "lms admin",
                "teacher dashboard",
                "instructor dashboard",
                "course management",
                "grading",
                "student management",
                "learning analytics",
            ),
        ),
        (
            "learning-experience",
            (
                "course",
                "lesson",
                "learning path",
                "student learning",
                "online learning",
                "classroom",
                "quiz",
                "assignment",
            ),
        ),
    ),
    "art-culture": (
        (
            "collection-discovery",
            (
                "collection",
                "archive",
                "artwork",
                "artist discovery",
                "visual archive",
                "browse art",
                "drift",
            ),
        ),
        (
            "exhibition-experience",
            (
                "exhibition",
                "exhibit",
                "immersive",
                "gallery experience",
                "museum experience",
            ),
        ),
    ),
    "industrial-services": (
        (
            "b2b-service-operations",
            (
                "repair",
                "maintenance",
                "work order",
                "service request",
                "rfq",
                "request a quote",
                "industrial service",
            ),
        ),
    ),
    "enterprise-software": (
        (
            "enterprise-operations",
            (
                "workflow",
                "dashboard",
                "admin",
                "operations",
                "approval",
                "case management",
                "data table",
                "back office",
            ),
        ),
    ),
    "commerce-retail": (
        (
            "checkout-commerce",
            ("checkout", "cart", "payment", "order", "purchase", "thanh toán", "giỏ hàng"),
        ),
        (
            "catalog-commerce",
            ("catalog", "catalogue", "product listing", "category", "browse products", "product detail"),
        ),
    ),
    "ai-software": (
        (
            "ai-workspace",
            ("copilot", "agent", "assistant", "chat", "workspace", "prompt", "automation"),
        ),
    ),
    "mobility-ev": (
        (
            "charging-network",
            ("charging station", "charging network", "charger", "fleet", "route planning"),
        ),
    ),
    "travel-tourism": (
        (
            "destination-discovery",
            ("destination", "attraction", "itinerary", "city guide", "visitor guide", "discover places"),
        ),
    ),
}


def infer_specialist_context(
    goal: str,
    domain: str,
    product_archetype: str,
) -> tuple[str, str, list[str]]:
    """Enrich canonical task context without depending on flow or skill routing.

    Existing explicit/canonical classifications normally win. The only arbitration
    performed here is a bounded ambiguity correction: ordinary ecommerce checkout
    language may contain the generic word "payment", which must not by itself turn a
    commerce task into financial services when stronger financial-product evidence is absent.
    """

    text = _normalise(goal)
    resolved_domain = str(domain or "generic")
    resolved_archetype = str(product_archetype or "generic")
    evidence: list[str] = []

    commerce_terms = dict(DOMAIN_HINTS)["commerce-retail"]
    if (
        resolved_domain == "financial-services"
        and _contains(text, commerce_terms)
        and not _contains(text, STRONG_FINANCIAL_DOMAIN_HINTS)
    ):
        resolved_domain = "commerce-retail"
        resolved_archetype = "generic"
        evidence.append("domain:commerce-retail")
        evidence.append("domain_disambiguation:generic-payment->commerce-retail")

    if resolved_domain == "generic":
        for candidate, terms in DOMAIN_HINTS:
            if _contains(text, terms):
                resolved_domain = candidate
                evidence.append(f"domain:{candidate}")
                break

    if resolved_archetype == "generic":
        for candidate, terms in ARCHETYPE_HINTS.get(resolved_domain, ()):
            if _contains(text, terms):
                resolved_archetype = candidate
                evidence.append(f"product_archetype:{candidate}")
                break

    return resolved_domain, resolved_archetype, evidence
