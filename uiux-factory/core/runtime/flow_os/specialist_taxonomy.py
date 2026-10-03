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
            "enterprise saas",
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

PRIMARY_DOMAIN_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "financial-services",
        STRONG_FINANCIAL_DOMAIN_HINTS + ("bank", "payments", "payment operations"),
    ),
    (
        "ai-software",
        (
            "ai workspace",
            "ai-native",
            "ai native",
            "ai platform",
            "ai product",
            "ai copilot",
            "ai assistant",
            "generative ai",
            "artificial intelligence",
            "llm platform",
        ),
    ),
    ("commerce-retail", dict(DOMAIN_HINTS)["commerce-retail"] + ("ecommerce storefront", "storefront")),
    ("enterprise-software", dict(DOMAIN_HINTS)["enterprise-software"] + ("saas operations", "enterprise operations")),
    (
        "education-edtech",
        (
            "edtech",
            "lms",
            "learning platform",
            "learning management system",
            "course platform",
            "online learning",
            "digital classroom",
        ),
    ),
)

DOMAIN_SIGNAL_HINTS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "financial-services",
        STRONG_FINANCIAL_DOMAIN_HINTS + ("bank", "payment", "payments", "financial analysts"),
    ),
    (
        "ai-software",
        (
            "ai workspace",
            "ai-native",
            "ai native",
            "ai platform",
            "ai product",
            "ai copilot",
            "ai assistant",
            "generative ai",
            "artificial intelligence",
            "agentic",
        ),
    ),
    ("commerce-retail", dict(DOMAIN_HINTS)["commerce-retail"] + ("ecommerce storefront", "storefront")),
    (
        "enterprise-software",
        dict(DOMAIN_HINTS)["enterprise-software"]
        + ("enterprise operations", "enterprise admin", "admin workflows", "saas admin"),
    ),
    (
        "education-edtech",
        (
            "edtech",
            "lms",
            "learning platform",
            "learning management system",
            "course platform",
            "online learning",
            "digital classroom",
        ),
    ),
)

PRIMARY_PRODUCT_PATTERNS: tuple[str, ...] = (
    r"\b(?:the\s+)?primary product is\s+([^.;]+)",
    r"\b(?:the\s+)?(?:main|core) product is\s+([^.;]+)",
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


def _explicit_primary_domain(text: str) -> str | None:
    segment = ""
    for pattern in PRIMARY_PRODUCT_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            segment = _normalise(match.group(1))
            break
    if not segment:
        return None

    # P1.2: a primary clause can itself contain multiple domain cues, e.g.
    # "AI workspace for financial analysts". Choose the earliest product-defining
    # cue in the explicit primary clause instead of letting taxonomy tuple order win.
    matches: list[tuple[int, int, str]] = []
    for rank, (candidate, terms) in enumerate(PRIMARY_DOMAIN_HINTS):
        positions = [segment.find(term) for term in terms if term in segment]
        positions = [position for position in positions if position >= 0]
        if positions:
            matches.append((min(positions), rank, candidate))
    if not matches:
        return None
    matches.sort()
    return matches[0][2]


def _secondary_domains(text: str, primary_domain: str) -> list[str]:
    secondary: list[str] = []
    for candidate, terms in DOMAIN_SIGNAL_HINTS:
        if candidate != primary_domain and _contains(text, terms):
            secondary.append(candidate)
    return secondary


def domain_signal_candidates(goal: str) -> tuple[str, ...]:
    """Return deterministic mixed-domain candidates for ambiguity arbitration.

    The P1.1 ecommerce/payment correction remains authoritative: a generic payment
    token inside an otherwise clear commerce task is not enough to manufacture a
    FinTech conflict unless stronger financial-product evidence is also present.
    """

    text = _normalise(goal)
    candidates = {
        candidate
        for candidate, terms in DOMAIN_SIGNAL_HINTS
        if _contains(text, terms)
    }
    if (
        "financial-services" in candidates
        and "commerce-retail" in candidates
        and not _contains(text, STRONG_FINANCIAL_DOMAIN_HINTS)
    ):
        candidates.remove("financial-services")
    return tuple(sorted(candidates))


def assess_domain_ambiguity(goal: str) -> tuple[str, tuple[str, ...], list[str]]:
    """Classify unresolved mixed-domain language without inventing an owner.

    Explicit primary-product language is already handled by P1.2 and therefore is
    never marked ambiguous here. Otherwise two or more credible domain signals form
    a conflict that must be resolved by target-project truth or caller evidence.
    """

    text = _normalise(goal)
    if _explicit_primary_domain(text):
        return "resolved", (), []
    candidates = domain_signal_candidates(text)
    if len(candidates) < 2:
        return "resolved", candidates, []
    joined = "|".join(candidates)
    return (
        "ambiguous",
        candidates,
        [
            f"domain_conflict:{joined}",
            "routing_status:ambiguous",
            "routing_action:needs-evidence",
        ],
    )


def infer_specialist_context(
    goal: str,
    domain: str,
    product_archetype: str,
) -> tuple[str, str, list[str]]:
    """Enrich canonical task context without depending on flow or skill routing.

    Explicit `primary product is ...` language owns mixed-domain arbitration. Secondary
    domains stay visible as provenance but do not automatically compose specialists.
    Without an explicit primary owner, the existing bounded ecommerce/payment ambiguity
    correction and canonical fallback behaviour remain unchanged.
    """

    text = _normalise(goal)
    resolved_domain = str(domain or "generic")
    resolved_archetype = str(product_archetype or "generic")
    evidence: list[str] = []

    explicit_primary = _explicit_primary_domain(text)
    if explicit_primary:
        if resolved_domain != explicit_primary:
            resolved_domain = explicit_primary
            resolved_archetype = "generic"
            evidence.append(f"domain:{explicit_primary}")
        evidence.append(f"domain_precedence:explicit-primary->{explicit_primary}")
        for secondary in _secondary_domains(text, explicit_primary):
            evidence.append(f"secondary_domain:{secondary}")

    commerce_terms = dict(DOMAIN_HINTS)["commerce-retail"]
    if (
        explicit_primary is None
        and resolved_domain == "financial-services"
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
